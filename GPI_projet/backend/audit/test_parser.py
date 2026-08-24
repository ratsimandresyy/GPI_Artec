from pathlib import Path
from parser import WinAuditParser

file_path = Path("C:/Book/AD1_AD1$_20210319_0732.txt")

parser = WinAuditParser(file_path)

data = parser.parse()

for key, value in data.items():
    print(f"{key} = {value}")