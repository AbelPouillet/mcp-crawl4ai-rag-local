from tree_sitter import Language
from pathlib import Path

GRAMMAR_ROOT = Path("knowledge_graphs/tree-sitter-grammar")
BUILD_DIR = Path("build")
BUILD_DIR.mkdir(exist_ok=True)
LIB_NAME = "my-languages.so"
LIB_PATH = BUILD_DIR / LIB_NAME

def find_grammars(grammar_root: Path):
    grammar_dirs = []
    for parser_file in grammar_root.rglob("src/parser.c"):
        if "node_modules" in str(parser_file):  # skip vendored files
            continue
        grammar_dirs.append(parser_file.parent.parent)
    return grammar_dirs

def get_language_id(grammar_path: Path):
    name = grammar_path.name.lower().replace("-", "_")
    if "ocaml" in str(grammar_path):
        if "grammars/interface" in str(grammar_path):
            return "ocaml_interface"
        elif "grammars/type" in str(grammar_path):
            return "ocaml_type"
        elif "grammars/ocaml" in str(grammar_path):
            return "ocaml_ocaml"
    if "php/php_only" in str(grammar_path):
        return "php_only"
    if "php/php" in str(grammar_path):
        return "php"
    if "typescript/tsx" in str(grammar_path):
        return "tsx"
    if "typescript/typescript" in str(grammar_path):
        return "typescript"
    return name

# === Génération ===
print("🔍 Recherche des grammaires compilables...")
grammar_dirs = find_grammars(GRAMMAR_ROOT)
print(f"🔧 Compilation des grammaires ({len(grammar_dirs)}) :")
for g in grammar_dirs:
    print(f"  - {get_language_id(g)}")

print("📦 Compilation de la bibliothèque...")
Language.build_library(
    str(LIB_PATH),
    [str(g) for g in grammar_dirs]
)
print(f"✅ Fichier généré : {LIB_PATH}")
