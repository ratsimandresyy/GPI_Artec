import pluginVueA11y from 'eslint-plugin-vuejs-accessibility';

/*
 * Audit d'accessibilité des composants Vue, en mode RAPPORT.
 *
 * Aucun correctif automatique n'est déclenché : `npm run lint:a11y`
 * se limite à lister les manquements. Ce fichier n'est pas branché à
 * `build` ni à `test`.
 *
 * Le preset recommandé de vuejs-accessibility est appliqué tel quel
 * (parseur vue-eslint-parser, globals, 20 règles) ; seule sa portée
 * est restreinte aux composants de src/, les tests et la logique
 * applicative n'étant pas audités.
 */

const [configBase, configRegles] =
    pluginVueA11y.configs['flat/recommended'];

const PERIMETRE = ['src/**/*.vue'];

export default [
    {
        ignores: ['dist/**', 'node_modules/**'],
    },
    {
        ...configBase,
        files: PERIMETRE,
    },
    {
        ...configRegles,
        files: PERIMETRE,
    },
];
