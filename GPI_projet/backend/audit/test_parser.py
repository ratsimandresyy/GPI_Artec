from pathlib import Path
from parser import WinAuditParser

file_path = Path("C:/Book/AD1_AD1$_20210319_0732.txt")

parser = WinAuditParser(file_path)

data = parser.parse()

for section, values in data.items():
    print(f"\n===== {section} =====")

    for key, value in values.items():
        print(f"{key} = {value}")
