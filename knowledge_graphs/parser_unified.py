# knowledge_graphs/parser_unified.py
import os
from pathlib import Path
from tree_sitter import Language, Parser
from ctypes import CDLL
# === Chemin vers la lib compilée avec build_library ===
LANGUAGE_SO_PATH = Path(__file__).parent / "build" / "my-languages.so"

# === Extension → Langage ===
LANGUAGE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".mjs": "javascript",
    ".mts": "typescript",
    ".php": "php",
    ".php_only": "php_only",
    ".java": "java",
    ".rs": "rust",
    ".cpp": "cpp",
    ".c": "c",
    ".cs": "c_sharp",
    ".go": "go",
    ".json": "json",
    ".html": "html",
    ".css": "css",
    ".scss": "css",
    ".toml": "toml",
    ".h": "c",
    ".hxx": "cpp",
    ".jl": "julia",
    ".rb": "ruby",
    ".sh": "bash",
    ".swift": "swift",
    ".scala": "scala",
    ".verilog": "verilog",
    ".ml": "ocaml",
    ".mli": "ocaml_interface",
    ".mly": "ocaml_type",
    ".tsq": "tsq",
    ".jsdoc": "jsdoc",
    ".ql": "ql",
    ".agda": "agda",
}

# === Chargement des grammaires ===
RAW_LANGUAGES = {
    "agda": "tree_sitter_agda",
    "bash": "tree_sitter_bash",
    "c": "tree_sitter_c",
    "c_sharp": "tree_sitter_c_sharp",
    "cpp": "tree_sitter_cpp",
    "css": "tree_sitter_css",
    "embedded_template": "tree_sitter_embedded_template",
    "go": "tree_sitter_go",
    "haskell": "tree_sitter_haskell",
    "html": "tree_sitter_html",
    "java": "tree_sitter_java",
    "javascript": "tree_sitter_javascript",
    "jsdoc": "tree_sitter_jsdoc",
    "json": "tree_sitter_json",
    "julia": "tree_sitter_julia",
    "ocaml": "tree_sitter_ocaml",
    "ocaml_interface": "tree_sitter_ocaml_interface",
    "ocaml_type": "tree_sitter_ocaml_type",
    "php": "tree_sitter_php",
    "php_only": "tree_sitter_php_only",
    "python": "tree_sitter_python",
    "ql": "tree_sitter_ql",
    "razor": "tree_sitter_razor",
    "ruby": "tree_sitter_ruby",
    "rust": "tree_sitter_rust",
    "scala": "tree_sitter_scala",
    "swift": "tree_sitter_swift",
    "toml": "tree_sitter_toml",
    "tsq": "tree_sitter_tsq",
    "typescript": "tree_sitter_typescript",
    "tsx": "tree_sitter_tsx",
    "verilog": "tree_sitter_verilog",
}

# Charge les symboles présents dans my-languages.so
LANGUAGES = {}
LIB = CDLL(str(LANGUAGE_SO_PATH)) # charger une fois

print("🔍 Chargement des grammaires Tree-sitter...\n")
for lang, symbol in RAW_LANGUAGES.items():
    try:
        lang_obj = Language(str(LANGUAGE_SO_PATH), lang)
        LANGUAGES[lang] = lang_obj
        print(f"✅ Langage chargé : {lang}")
    except Exception as e:
        print(f"❌ Erreur de chargement : '{lang}' ({symbol})")
        print(f"   ↳ Exception : {type(e).__name__}: {e}\n")

def analyze_file_with_treesitter(filepath: Path):
    ext = f".{filepath.name.split('.')[-1]}"
    lang_key = LANGUAGE_EXTENSIONS.get(ext)
    if not lang_key:
        print(f"[!] Extension non supportée : {ext}")
        return None

    language = LANGUAGES.get(lang_key)
    if not language:
        print(f"[!] Langage non chargé : {lang_key}")
        return None

    parser = Parser()
    try:
        parser.set_language(language)
    except Exception as e:
        print(f"[!] Erreur lors du set_language pour le fichier : {filepath}")
        print(f"    ↳ Langue : {lang_key}, Extension : {ext}")
        print(f"    ↳ Exception : {type(e).__name__}: {e}")
        return None

    try:
        source_code = filepath.read_bytes()
        tree = parser.parse(source_code)
        return tree
    except Exception as e:
        print(f"[!] Erreur d'analyse de {filepath.name} : {type(e).__name__}: {e}")
        return None
