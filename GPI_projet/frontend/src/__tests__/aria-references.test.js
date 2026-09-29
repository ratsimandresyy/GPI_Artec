import { describe, expect, it } from 'vitest';
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { dirname, join, relative, resolve, sep } from 'node:path';

/*
 * Vitest s'exÃ©cutant sous jsdom, `import.meta.url` n'est pas un URL
 * `file:` : la racine du frontend est donc localisÃ©e en remontant
 * depuis le rÃ©pertoire courant jusqu'au dossier contenant Ã  la fois
 * package.json et src/.
 */
function trouverRacineSrc() {
    let courant = resolve(process.cwd());

    while (true) {
        if (
            existsSync(join(courant, 'package.json')) &&
            existsSync(join(courant, 'src'))
        ) {
            return join(courant, 'src');
        }

        const parent = dirname(courant);

        if (parent === courant) {
            throw new Error(
                "racine du frontend introuvable (package.json + src/)"
            );
        }

        courant = parent;
    }
}

const RACINE_SRC = trouverRacineSrc();

/*
 * Garde-fou statique des rÃ©fÃ©rences ARIA.
 *
 * Un attribut aria-describedby / aria-labelledby / aria-controls Ã©crit
 * en dur pointe vers un id qui peut ne pas exister : le cas typique est
 * un message d'erreur rendu sous v-if, absent tant qu'aucune erreur
 * n'est levÃ©e. Le lien est alors orphelin et un lecteur d'Ã©cran
 * annonce une cible inexistante.
 *
 * Ce test relit les templates des .vue et refuse :
 *   (i)  une rÃ©fÃ©rence statique dont l'id cible est absent du template ;
 *   (ii) une rÃ©fÃ©rence statique dont l'Ã©lÃ©ment cible est conditionnel
 *        (v-if / v-else / v-show), car il peut Ãªtre absent du DOM.
 *
 * Les rÃ©fÃ©rences liÃ©es (`:aria-describedby`, `v-bind:aria-controls`)
 * sont ignorÃ©es : elles sont calculÃ©es Ã  l'exÃ©cution et vÃ©rifiÃ©es par
 * les tests de composant.
 */

/** Attributs de rÃ©fÃ©rence ARIA qui pointent vers un id. */
const ATTRIBUTS_REFERENCES = ['aria-describedby', 'aria-labelledby', 'aria-controls'];

/** ConditionnalitÃ©s de rendu qui rendent une cible potentiellement absente. */
const DIRECTIVES_CONDITIONNELLES = ['v-if', 'v-else', 'v-show'];

/**
 * DÃ©coupe le template racine d'un SFC et renvoie son contenu ainsi que
 * l'offset permettant de convertir un index local en ligne du fichier.
 */
function extraireTemplate(contenu) {
    const debutBalise = contenu.indexOf('<template>');

    if (debutBalise === -1) {
        return null;
    }

    const debut = contenu.indexOf('\n', debutBalise) + 1;
    const fin = contenu.lastIndexOf('</template>');

    if (fin === -1 || fin < debut) {
        return null;
    }

    return {
        corps: contenu.slice(debut, fin),
        // Nombre de lignes prÃ©cÃ©dant le template dans le fichier.
        lignesAvant: contenu.slice(0, debut).split('\n').length - 1,
    };
}

/** Liste rÃ©cursivement les fichiers .vue sous un dossier. */
function listerFichiersVue(dossier) {
    const fichiers = [];

    for (const entree of readdirSync(dossier)) {
        const chemin = join(dossier, entree);

        if (statSync(chemin).isDirectory()) {
            fichiers.push(...listerFichiersVue(chemin));
        } else if (entree.endsWith('.vue')) {
            fichiers.push(chemin);
        }
    }

    return fichiers;
}

/** Retire les commentaires HTML, qui peuvent contenir des chevrons. */
function sansCommentaires(corps) {
    return corps.replace(/<!--[\s\S]*?-->/g, (commentaire) =>
        ' '.repeat(commentaire.length)
    );
}

/**
 * DÃ©coupe les balises ouvrantes du template.
 *
 * Chaque balise expose son nom, ses attributs, son index de dÃ©part et
 * l'index de fin de sa zone d'attributs, ce qui permet de relever la
 * ligne exacte et les conditionnalitÃ©s de rendu.
 */
function extraireBalises(corps) {
    const balises = [];
    const motif = /<([a-zA-Z][\w-]*)((?:[^>"']|"[^"]*"|'[^']*')*)>/g;
    let correspondance;

    while ((correspondance = motif.exec(corps)) !== null) {
        const attributs = correspondance[2];
        const zoneAttributs = correspondance[0].length - 1;

        balises.push({
            nom: correspondance[1],
            attributs,
            debut: correspondance.index,
            finAttributs: correspondance.index + zoneAttributs,
        });
    }

    return balises;
}

/** Attribut statique `nom="valeur"` ; ignore `:nom` et `v-bind:nom`. */
function attributStatique(attributs, nom) {
    const motif = new RegExp(`(^|\\s)${nom}="([^"]*)"`);
    const correspondance = motif.exec(attributs);

    return correspondance ? correspondance[2] : null;
}

/** RelÃ¨ve la conditionnalitÃ© de rendu d'une balise (v-if / v-else / v-show). */
function conditionnalite(balise) {
    return DIRECTIVES_CONDITIONNELLES.find((directive) =>
        new RegExp(`(^|\\s)${directive}[\\s=]`).test(balise.attributs)
    );
}

/** Analyse un .vue et renvoie les rÃ©fÃ©rences ARIA statiques fautives. */
function referencesOrphelines(chemin) {
    const contenu = readFileSync(chemin, 'utf-8');
    const template = extraireTemplate(contenu);

    if (!template) {
        return [];
    }

    const corps = sansCommentaires(template.corps);
    const balises = extraireBalises(corps);
    const fautifs = [];

    /* Index des ids dÃ©clarÃ©s : id statique -> balise qui le porte. */
    const ids = new Map();

    for (const balise of balises) {
        const id = attributStatique(balise.attributs, 'id');

        if (id !== null && !ids.has(id)) {
            ids.set(id, balise);
        }
    }

    const ligneDe = (index) =>
        template.lignesAvant + corps.slice(0, index).split('\n').length;

    /* Ligne exacte de l'attribut fautif, et non de la balise ouvrante :
     * les attributs de ce projet sont Ã©crits sur plusieurs lignes. */
    const ligneDeAttribut = (balise, attribut) => {
        const dansBalise = balise.attributs.indexOf(`${attribut}="`);

        if (dansBalise === -1) {
            return ligneDe(balise.debut);
        }

        // +1 pour '<' puis la longueur du nom de balise.
        return ligneDe(balise.debut + 1 + balise.nom.length + dansBalise);
    };

    for (const balise of balises) {
        for (const attribut of ATTRIBUTS_REFERENCES) {
            const valeur = attributStatique(balise.attributs, attribut);

            if (valeur === null) {
                continue;
            }

            for (const cible of valeur.split(/\s+/).filter(Boolean)) {
                const portant = ids.get(cible);

                if (!portant) {
                    fautifs.push({
                        chemin,
                        ligne: ligneDeAttribut(balise, attribut),
                        attribut,
                        cible,
                        raison: "l'id cible est absent du template",
                    });
                    continue;
                }

                const directive = conditionnalite(portant);

                if (directive) {
                    fautifs.push({
                        chemin,
                        ligne: ligneDeAttribut(balise, attribut),
                        attribut,
                        cible,
                        raison: `l'Ã©lÃ©lement cible est rendu sous ${directive}`,
                    });
                }
            }
        }
    }

    return fautifs;
}

const fichiers = listerFichiersVue(RACINE_SRC);

describe('RÃ©fÃ©rences ARIA statiques (src/**/*.vue)', () => {
    it('analyse bien les templates du projet', () => {
        expect(
            fichiers.length,
            'aucun .vue trouvÃ© : le scan ne couvrirait rien'
        ).toBeGreaterThan(10);
    });

    it("ne contient aucune rÃ©fÃ©rence ARIA statique orpheline", () => {
        const fautifs = fichiers.flatMap(referencesOrphelines);

        const rapport = fautifs
            .map(
                (f) =>
                    `${relative(RACINE_SRC, f.chemin).split(sep).join('/')}:${f.ligne} ` +
                    `${f.attribut}="${f.cible}" -> ${f.raison}`
            )
            .join('\n');

        expect(
            fautifs,
            `RÃ©fÃ©rences ARIA statiques orphelines :\n${rapport}`
        ).toEqual([]);
    });
});
