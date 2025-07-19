import subprocess
from pathlib import Path
import json
import os

NPX = "C:\\Program Files\\nodejs\\npx.cmd"  # Utilisez simplement 'npx' (gestion automatique du chemin)
GRAMMAR_ROOT = Path(".")

def find_grammars(root: Path):
    """Retourne tous les dossiers contenant un grammar.js"""
    return [
        p.parent for p in root.rglob("grammar.js")
        if "node_modules" not in str(p)
    ]

def ensure_tree_sitter_json(path: Path, name: str):
    json_path = path / "tree-sitter.json"
    data = {
        "name": name,
        "version": "0.0.1",
        "description": f"Tree-sitter grammar for {name}",
        "keywords": ["tree-sitter", "parser", name],
        "repository": f"https://github.com/tree-sitter/{name}",
        "license": "MIT",
        "dependencies": {
            "nan": "^2.17.0"  # Ajout crucial pour la compatibilité
        },
        "devDependencies": {
            "tree-sitter-cli": "^0.20.1"  # Version spécifique recommandée
        },
        "scripts": {
            "build": "tree-sitter generate --abi 14"  # Force l'ABI 14
        },
        "tree-sitter": [{
            "scope": f"source.{name}",
            "file-types": [name],
            "injection-regex": name
        }],
        "metadata": {
            "abi": 14,
            "version": "0.0.1",
        }
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"🧩 tree-sitter.json configuré pour {name}")

def install_dependencies(path: Path):
    try:
        print(f"📦 Installation des dépendances dans {path.name}...")
        subprocess.run(
            ["C:\\Program Files\\nodejs\\npm.cmd", "install"],
            cwd=path,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except Exception as e:
        print(f"⚠️ Échec de l'installation: {e}")
        return False

def generate_parser(path: Path):
    env = os.environ.copy()
    env["TREE_SITTER_ABI"] = "14"
    try:
        grammar_name = path.name.replace("tree-sitter-", "")
        ensure_tree_sitter_json(path, grammar_name)
        
        # Installation préalable des dépendances
        if not install_dependencies(path):
            print(f"⏩ Passage à la génération sans dépendances...")

        print(f"🛠️ Génération de {grammar_name}...")
        result = subprocess.run(
            [NPX, "tree-sitter", "generate"],
            cwd=path,
            capture_output=True,
            text=True,
            env=env
        )
        
        if result.returncode == 0:
            print(f"✅ {grammar_name} généré avec succès (ABI 14)")
        else:
            print(f"❌ Échec de génération pour {grammar_name}")
            print(f"Message d'erreur:\n{result.stderr[:500]}...")  # Affiche les premiers 500 caractères
            
    except Exception as e:
        print(f"🔥 Erreur critique dans {path.name}: {str(e)}")

# === Lancement ===
grammar_dirs = find_grammars(GRAMMAR_ROOT)
print(f"🔍 Grammaires trouvées: {len(grammar_dirs)}")

for gpath in grammar_dirs:
    print("\n" + "="*50)
    generate_parser(gpath)