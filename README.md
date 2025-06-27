# GENXAIS Framework

Ein generalisiertes KI-erweitertes Framework für die Softwareentwicklung.

## Überblick

Das GENXAIS Framework ist eine umfassende Lösung für die KI-gestützte Softwareentwicklung. Es integriert:

- APM (Agile Project Management) Framework
- Multi-Agent-System mit MCP (Model Context Protocol)
- LangGraph für Workflow-Management
- Pipeline-System für parallele Entwicklung
- Robuste Fehlerbehandlung und Wiederherstellung

## Systemanforderungen

- Python 3.8 oder höher
- 8GB RAM (minimum)
- 20GB freier Festplattenspeicher

## Installation

1. Repository klonen:
```bash
git clone https://github.com/IhrUsername/GENXAIS-Framework.git
cd GENXAIS-Framework
```

2. Umgebung einrichten:
```bash
python scripts/setup_environment.py
```

3. Umgebungsvariablen konfigurieren:
```bash
cp .env.example .env
# Bearbeiten Sie .env und fügen Sie Ihre API-Keys ein
```

## Komponenten

### APM Framework

Das APM Framework implementiert einen 5-Phasen-Zyklus:
- VAN (Vision, Analyse, Navigation)
- PLAN (Planung und Priorisierung)
- CREATE (Entwicklung und Innovation)
- IMPLEMENT (Umsetzung und Integration)
- REFLECT (Evaluation und Optimierung)

### Multi-Agent-System mit MCP

- Integriert verschiedene spezialisierte Agenten
- Model Context Protocol (MCP) für Tool-Integration
- Erweiterbar durch benutzerdefinierte Agenten und Tools
- Automatische Koordination und Zusammenarbeit

### Pipeline-System

- Parallele Entwicklungspipelines
- Abhängigkeitsverwaltung
- Automatische Fehlerbehandlung
- Zustandsverfolgung und Metriken
- Pause/Fortsetzen-Funktionalität

### LangGraph Integration

- Workflow-Management für Agenten
- Zustandsverwaltung
- Sequenzielle und parallele Ausführung
- Fehlerbehandlung und Wiederherstellung

## Verwendung

### Pipeline-basierte Entwicklung

```python
from genxais_sdk import GENXAISFramework
from core.pipeline_manager import PipelineStep

# Framework initialisieren
framework = GENXAISFramework()

# Pipeline-Schritte definieren
steps = [
    PipelineStep(
        name="requirements_analysis",
        function=analyze_requirements,
        requires=[],
        provides=["requirements_doc"],
        error_handlers=[handle_analysis_error],
        retry_policy={"max_retries": 3}
    ),
    PipelineStep(
        name="code_generation",
        function=generate_code,
        requires=["requirements_doc"],
        provides=["generated_code"],
        error_handlers=[handle_generation_error],
        retry_policy={"max_retries": 2}
    )
]

# Pipeline erstellen und ausführen
pipeline_id = await framework.create_development_pipeline("feature_dev", steps)
result = await framework.execute_pipeline(
    pipeline_id,
    input_data={"feature": "neue_funktion"}
)
```

### Multi-Agent Entwicklung

```python
# APM-Phase starten
framework.start_apm_phase('van')

# Entwicklungsaufgabe definieren
task = {
    "type": "feature_development",
    "description": "Implementiere eine neue API-Route",
    "requirements": ["FastAPI", "MongoDB"],
    "agent_type": "developer"
}

# Aufgabe verarbeiten
result = await framework.process_task(task)
```

### Benutzerdefinierte Tools registrieren

```python
# Tool für Code-Analyse registrieren
framework.register_custom_tool(
    "code_analyzer",
    {
        "description": "Analysiert Code-Qualität",
        "allowed_agents": ["developer", "reviewer"],
        "parameters": {
            "code_path": "str",
            "metrics": "List[str]"
        }
    }
)
```

## Pipeline-Status und Monitoring

```python
# Pipeline-Status abrufen
status = framework.get_pipeline_status("feature_dev")
print(f"Pipeline-Status: {status}")

# Gesundheitscheck durchführen
health = framework.health_check()
print("System-Status:", health)
```

## Fehlerbehandlung

Das Framework bietet robuste Fehlerbehandlung:
- Automatische Wiederholungsversuche
- Fehlerhandler pro Pipeline-Schritt
- Zustandswiederherstellung
- Detaillierte Fehlerprotokolle

## Beitragen

Wir freuen uns über Beiträge! Bitte beachten Sie:
1. Fork des Repositories
2. Feature-Branch erstellen
3. Änderungen committen
4. Pull Request erstellen

## Lizenz

MIT License - siehe LICENSE Datei

## Support

- GitHub Issues für Bugs und Feature-Requests
- Dokumentation im docs/ Verzeichnis
- Community-Forum (coming soon) 