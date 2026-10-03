"""
Import ponctuel des plans PDF dans les objets Plan.

Le modèle Plan, son serialiseur et sa vue ne sont pas modifies : la
commande se contente de renseigner le champ image (upload_to="plans/")
avec la conversion PNG de la page d'un PDF, pour l'etage correspondant.

Convention de nommage des fichiers fournis : « <reference> <date>
plan <niveau>.pdf », par exemple « 247 200612 plan R+1.pdf ». Seul le
niveau est exploite : la reference du projet et la date d'edition du
document ne designent aucun Batiment en base.

La page entiere est convertie, cartouche et tableau de revisions
compris : aucun recadrage de legende n'est applique.
"""

import re
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from inventaire.models.batiment import Batiment
from inventaire.models.etage import Etage
from inventaire.models.plan import Plan


# Le niveau est la seule information exploitable du nom de fichier :
# « plan Rdc », « plan R+3 », « plan R-1 ».
MOTIF_NIVEAU = re.compile(
    r"plan\s+(?P<niveau>rdc|r\s*(?P<signe>[+-])\s*(?P<numero>\d+))",
    re.IGNORECASE,
)

# 100 ppp donnent 2363 x 1260 px pour les planches de 600 x 320 mm
# fournies : les libelles de salles et le cartouche restent lisibles.
DPI_PAR_DEFAUT = 100


class PlanIllisible(Exception):
    """PDF inexploitable : aucune page, ou plusieurs pages (donc ambigu)."""


def numero_etage_depuis_nom(nom_fichier):
    """
    Deduit le numero d'etage porte par un nom de fichier de plan.

    « plan Rdc.pdf » -> 0, « plan R+1.pdf » -> 1, « plan R-1.pdf » -> -1.
    Retourne None si le nom ne suit pas la convention : l'association
    n'est jamais devinee dans ce cas.
    """
    correspondance = MOTIF_NIVEAU.search(nom_fichier)

    if correspondance is None:
        return None

    if correspondance.group("niveau").lower() == "rdc":
        return 0

    numero = int(correspondance.group("numero"))

    return -numero if correspondance.group("signe") == "-" else numero


def nom_image(numero):
    """
    Nom de fichier de l'image d'un etage.

    Il ne depend que du numero d'etage : une seconde execution avec
    --remplacer ecrit donc le meme fichier au lieu d'en accumuler.
    Le nom reste dans l'alphabet accepte par Django (lettres, chiffres,
    tiret, point) : un « + » serait supprime par get_valid_filename.
    """
    return f"plan_etage_{numero}.png"


def convertir_en_png(chemin_pdf, dpi):
    """
    Rend la page du PDF en PNG et retourne (contenu, largeur, hauteur).

    PyMuPDF est choisi parce qu'il embarque son propre moteur de rendu :
    aucun binaire externe (Poppler, Ghostscript) n'est a installer sur la
    machine. Il est importe ici plutot qu'au chargement du module afin
    que la commande reste importable sans cette dependance.
    """
    try:
        import pymupdf
    except ImportError:
        raise CommandError(
            "PyMuPDF est requis pour convertir les plans en images : "
            "installez les dependances avec « pip install -r "
            "requirements.txt »."
        )

    document = pymupdf.open(chemin_pdf)

    try:
        if document.page_count != 1:
            raise PlanIllisible(
                f"{document.page_count} page(s) au lieu d'une seule : un "
                "PDF doit correspondre a un seul etage."
            )

        pixmap = document[0].get_pixmap(dpi=dpi)

        return pixmap.tobytes("png"), pixmap.width, pixmap.height

    finally:
        document.close()


class Command(BaseCommand):

    help = (
        "Importe des plans PDF en objets Plan : une page = un etage. "
        "La page entiere est convertie, sans recadrage de la legende."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "dossier",
            type=str,
            help="Dossier contenant les fichiers PDF de plans.",
        )

        parser.add_argument(
            "--batiment",
            type=str,
            default=None,
            help=(
                "Nom du Batiment auquel rattacher les etages. Par defaut, "
                "le seul Batiment present en base."
            ),
        )

        parser.add_argument(
            "--dpi",
            type=int,
            default=DPI_PAR_DEFAUT,
            help=(
                "Resolution de rendu, en points par pouce "
                f"(defaut : {DPI_PAR_DEFAUT})."
            ),
        )

        parser.add_argument(
            "--remplacer",
            action="store_true",
            help=(
                "Ecrase l'image des etages ayant deja un plan. Sans cette "
                "option, ces etages sont seulement signales."
            ),
        )

        parser.add_argument(
            "--simulation",
            action="store_true",
            help="Affiche ce qui serait fait sans rien ecrire en base.",
        )

    def handle(self, *args, **options):
        dossier = Path(options["dossier"])

        if not dossier.is_dir():
            raise CommandError(f"Dossier introuvable : {dossier}")

        dpi = options["dpi"]

        if dpi <= 0:
            raise CommandError("--dpi attend un entier strictement positif.")

        fichiers = sorted(
            chemin
            for chemin in dossier.iterdir()
            if chemin.suffix.lower() == ".pdf"
        )

        if not fichiers:
            raise CommandError(f"Aucun fichier PDF dans : {dossier}")

        batiment = self.resoudre_batiment(options["batiment"])

        self.stdout.write(f"Batiment cible : {batiment.nom}")
        self.stdout.write(
            f"Resolution : {dpi} ppp, page entiere (cartouche compris)"
        )

        if options["simulation"]:
            self.stdout.write("Mode simulation : aucune ecriture en base.")

        resultats = {"cree": [], "remplace": [], "existant": [], "laisse": []}

        for chemin in fichiers:
            statut, message = self.traiter(
                chemin,
                batiment,
                dpi,
                remplacer=options["remplacer"],
                simulation=options["simulation"],
            )
            resultats[statut].append(message)

        self.afficher_resume(resultats, len(fichiers))

    def resoudre_batiment(self, nom):
        """
        Determine le Batiment cible sans le deviner : soit son nom est
        donne par --batiment, soit il ne doit exister qu'un seul
        Batiment en base.
        """
        if nom is not None:
            batiment = Batiment.objects.filter(nom=nom).first()

            if batiment is None:
                raise CommandError(
                    f"Aucun Batiment nomme « {nom} » en base."
                )

            return batiment

        batiments = list(Batiment.objects.order_by("nom"))

        if len(batiments) != 1:
            noms = ", ".join(batiment.nom for batiment in batiments)
            raise CommandError(
                "Le nom des fichiers ne porte pas celui du batiment : "
                "precisez --batiment. Batiments en base : "
                f"{noms or 'aucun'}."
            )

        return batiments[0]

    def traiter(self, chemin, batiment, dpi, remplacer, simulation):
        """
        Traite un fichier et retourne (statut, message).

        Statuts : « cree », « remplace », « existant » (un plan est deja
        en base et n'est pas ecrase) ou « laisse » (fichier non traite,
        notamment quand l'etage correspondant n'existe pas).
        """
        numero = numero_etage_depuis_nom(chemin.name)

        if numero is None:
            return "laisse", (
                f"{chemin.name} : nom non conforme, aucun niveau "
                "identifiable. Association non devinee."
            )

        etage = Etage.objects.filter(batiment=batiment, numero=numero).first()

        if etage is None:
            return "laisse", (
                f"{chemin.name} -> etage {numero} : aucun Etage {numero} "
                f"dans « {batiment.nom} ». Cette commande ne cree aucun "
                "etage : le fichier est laisse de cote."
            )

        plan = Plan.objects.filter(etage=etage).first()

        if plan is not None and not remplacer:
            return "existant", (
                f"{chemin.name} -> {etage} : un plan existe deja "
                f"(image « {plan.image.name} »). Rien n'a ete ecrase ; "
                "utilisez --remplacer pour le remplacer."
            )

        try:
            contenu, largeur, hauteur = convertir_en_png(chemin, dpi)
        except PlanIllisible as erreur:
            return "laisse", f"{chemin.name} : {erreur}"

        nom = nom_image(numero)

        if simulation:
            return ("remplace" if plan is not None else "cree"), (
                f"{chemin.name} -> {etage} : {largeur} x {hauteur} px, "
                f"image « plans/{nom} » (simulation)."
            )

        if plan is None:
            plan = Plan(etage=etage)
            statut = "cree"
        else:
            # --remplacer : l'ancienne image est retiree du stockage pour
            # que le nom du fichier reste stable d'une execution a l'autre.
            plan.image.delete(save=False)
            statut = "remplace"

        plan.image.save(nom, ContentFile(contenu), save=False)
        plan.largeur = largeur
        plan.hauteur = hauteur
        plan.save()

        return statut, (
            f"{chemin.name} -> {etage} : {largeur} x {hauteur} px, "
            f"image « {plan.image.name} »."
        )

    def afficher_resume(self, resultats, total):
        """
        Resume final : importes, remplaces, ignores car deja en base,
        et fichiers laisses de cote.
        """
        titres = (
            ("cree", "Plans importes"),
            ("remplace", "Plans remplaces"),
            ("existant", "Plans ignores (deja en base)"),
            ("laisse", "Fichiers laisses de cote"),
        )

        self.stdout.write("")
        self.stdout.write(f"Fichiers PDF examines : {total}")

        for statut, titre in titres:
            self.stdout.write("")
            self.stdout.write(f"{titre} : {len(resultats[statut])}")

            for message in resultats[statut]:
                self.stdout.write(f"  - {message}")

        ecrits = len(resultats["cree"]) + len(resultats["remplace"])

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Total : {ecrits} plan(s) ecrit(s), "
                f"{len(resultats['existant'])} ignore(s) car deja en base, "
                f"{len(resultats['laisse'])} laisse(s) de cote."
            )
        )
