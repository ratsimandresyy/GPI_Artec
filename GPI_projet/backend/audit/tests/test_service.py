import os
import django
from pathlib import Path
from audit.services import WinAuditService

#initialisation de django
os.environ.setdefault(
    "DJANGO_SETTING_MODULE",
    "GPI_projet.settings"
)

django.setup()

file_path = Path(
    "C:/Book/AD1_AD1$_20210319_0732.txt"
)

service = WinAuditService(file_path)

rapport = service.importer()

print("\n===== Import términer =====")

print(f"ID du rapport : {rapport.id}")
print(f"Equipement : {rapport.equipement}")
print(f"Date audit : {rapport.date_audit}")
print(f"Système : {rapport.system_exploitation}")
print(f"Processeur : {rapport.processeur}")
print(f"Mémoire : {rapport.memoire}")
print(f"Stockage : {rapport.stockage}")