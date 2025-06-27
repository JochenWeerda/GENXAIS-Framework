"""
Setup-Skript für die GENXAIS Framework Umgebung
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Überprüft die Python-Version"""
    if sys.version_info < (3, 8):
        raise RuntimeError("Python 3.8 oder höher wird benötigt")

def install_requirements():
    """Installiert alle benötigten Pakete"""
    requirements = [
        "langchain>=0.1.0",
        "langgraph>=0.0.10",
        "pymongo>=4.0.0",
        "sentence-transformers>=2.2.0",
        "faiss-cpu>=1.7.0",
        "python-dotenv>=0.19.0",
        "pydantic>=2.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0"
    ]
    
    for req in requirements:
        subprocess.check_call([sys.executable, "-m", "pip", "install", req])

def setup_mongodb():
    """Richtet MongoDB ein"""
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client.genxais_db
        print("MongoDB-Verbindung erfolgreich")
    except Exception as e:
        print(f"Fehler bei MongoDB-Setup: {e}")
        print("Bitte stellen Sie sicher, dass MongoDB installiert und gestartet ist")

def create_env_file():
    """Erstellt die .env Datei mit Beispielkonfiguration"""
    env_content = """
# API Keys
OPENAI_API_KEY=your-api-key-here
HUGGINGFACE_API_KEY=your-api-key-here

# MongoDB
MONGODB_URI=mongodb://localhost:27017/

# RAG System
VECTOR_STORE_PATH=./vector_store
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Logging
LOG_LEVEL=INFO
    """
    
    with open(".env.example", "w", encoding="utf-8") as f:
        f.write(env_content.strip())

def main():
    """Hauptfunktion für das Setup"""
    print("Starte GENXAIS Framework Setup...")
    
    check_python_version()
    print("Python-Version OK")
    
    print("Installiere Abhängigkeiten...")
    install_requirements()
    
    print("Richte MongoDB ein...")
    setup_mongodb()
    
    print("Erstelle Beispiel-Umgebungsdatei...")
    create_env_file()
    
    print("""
Setup abgeschlossen!

Nächste Schritte:
1. Kopieren Sie .env.example zu .env
2. Fügen Sie Ihre API-Keys in die .env Datei ein
3. Starten Sie MongoDB, falls noch nicht geschehen
4. Führen Sie die Tests mit 'python -m pytest tests/' aus
    """)

if __name__ == "__main__":
    main() 