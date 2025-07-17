# 🔄 Version modifiée avec tree_sitter_languages
import asyncio
import logging
import os
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase

from parser_unified import analyze_file_with_treesitter, LANGUAGE_EXTENSIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DirectNeo4jExtractor:
    def __init__(self, uri, user, password):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def initialize(self):
        """Initialise la connexion à Neo4j et crée les contraintes de base"""
        logger.info("🔌 Initialisation de Neo4j...")
        async with self.driver.session() as session:
            await session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (f:File) REQUIRE f.path IS UNIQUE")
            await session.run("CREATE INDEX IF NOT EXISTS FOR (f:File) ON (f.name)")
            await session.run("CREATE INDEX IF NOT EXISTS FOR (c:Class) ON (c.name)")
            await session.run("CREATE INDEX IF NOT EXISTS FOR (func:Function) ON (func.name)")
        logger.info("✅ Contraintes Neo4j créées.")
    def get_supported_files(self, repo_path: str) -> List[Path]:
        supported = []
        exclude_dirs = {'venv', '__pycache__', '.git', 'node_modules', 'dist', 'build'}
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in LANGUAGE_EXTENSIONS:
                    path = Path(root) / file
                    if path.stat().st_size < 500_000:
                        supported.append(path)
        return supported

    def clone_repo(self, repo_url: str, dest_dir: str) -> Path:
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)
        subprocess.run(["git", "clone", "--depth", "1", repo_url, dest_dir], check=True)
        return Path(dest_dir)

    async def insert_graph(self, repo_name: str, modules_data: List[Dict[str, Any]]):
        async with self.driver.session() as session:
            await session.run("CREATE (r:Repository {name: $name, created_at: datetime()})", name=repo_name)
            for mod in modules_data:
                await session.run("""
                    CREATE (f:File {
                        name: $name, path: $path, module_name: $module,
                        language: $lang, line_count: $lines, created_at: datetime()
                    })
                """, name=os.path.basename(mod['file_path']), path=mod['file_path'],
                     module=mod['module_name'], lang=mod['language'], lines=mod['line_count'])

                await session.run("""
                    MATCH (r:Repository {name: $repo})
                    MATCH (f:File {path: $path})
                    CREATE (r)-[:CONTAINS]->(f)
                """, repo=repo_name, path=mod['file_path'])

                for cls in mod['classes']:
                    await session.run("""
                        MERGE (c:Class {name: $name})
                        WITH c
                        MATCH (f:File {path: $path})
                        MERGE (f)-[:DEFINES]->(c)
                    """, name=cls['name'], path=mod['file_path'])

                for func in mod['functions']:
                    await session.run("""
                        MERGE (func:Function {name: $name})
                        WITH func
                        MATCH (f:File {path: $path})
                        MERGE (f)-[:DEFINES]->(func)
                    """, name=func['name'], path=mod['file_path'])

    async def analyze_repository(self, repo_url: str, temp_dir: str = "./repos"):
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        repo_path = self.clone_repo(repo_url, os.path.join(temp_dir, repo_name))
        files = self.get_supported_files(str(repo_path))
        logger.info(f"📂 {len(files)} source files détectés")

        modules_data = []
        for i, file in enumerate(files):
            result = analyze_file_with_treesitter(file)
            if result:
                modules_data.append(result)
            if i % 20 == 0:
                logger.info(f"🧠 Analysé {i + 1}/{len(files)} : {file.name}")

        logger.info(f"✅ {len(modules_data)} fichiers analysés. Insertion dans Neo4j...")
        await self.insert_graph(repo_name, modules_data)

    async def close(self):
        await self.driver.close()


async def main():
    load_dotenv()
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    pwd = os.getenv("NEO4J_PASSWORD", "password")
    extractor = DirectNeo4jExtractor(uri, user, pwd)
    await extractor.analyze_repository("https://github.com/getzep/graphiti.git")
    await extractor.close()

if __name__ == "__main__":
    asyncio.run(main())
