from pathlib import Path
from parser import WinAuditParser
from mapping import WinAuditMapper

file_path = Path("C:/Book/AD1_AD1$_20210319_0732.txt")

parser = WinAuditParser(file_path)
data = parser.parse()
date_audit = parser.parse_date_audit()

mapper = WinAuditMapper(data, date_audit,)
equipement = mapper.map_equipement()
rapport = mapper.map_rapport_audit()
date_audit = parser.parse_date_audit()

print("\n ===== équipement mappé =====")

for key, value in equipement.items():
    print(f"{key} = {value}")

print("\n ===== Rapport d'audit mappé =====")

for key, value in rapport.items():
    print(f"{key} = {value}")

print("\n ===== Date de l'audit =====")
print(f"date_audit = {date_audit}")