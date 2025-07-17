import re
from pathlib import Path

so_path = Path("build/my-languages.so")

with open(so_path, "rb") as f:
    content = f.read()

# Rechercher tous les symboles tree_sitter_* (fonctions exportées)
symbols = set(re.findall(rb"tree_sitter_[a-zA-Z0-9_]+", content))
for sym in sorted(symbols):
    print(sym.decode())
