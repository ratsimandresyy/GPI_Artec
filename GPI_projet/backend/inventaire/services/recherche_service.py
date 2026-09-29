from django.db import models


class RechercheService:
    """
    Recherche d'equipements pour le mode visiteur.

    La regle de recherche (champs interrogees, normalisation du terme)
    vit ici afin que le ViewSet ne fasse que traduire la requete HTTP
    et serialiser le resultat.
    """

    @staticmethod
    def rechercher_equipements(queryset, terme: str):
        """
        Filtre un queryset d'equipements sur un terme libre.

        Le terme est recherche sur le nom et sur le numero
        d'inventaire, sans distinction de casse.
        """
        if not terme or not terme.strip():
            raise ValueError("Le paramètre 'q' est obligatoire.")

        terme = terme.strip()

        return queryset.filter(
            models.Q(nom__icontains=terme)
            | models.Q(numero_inventaire__icontains=terme)
        )
