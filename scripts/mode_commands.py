#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENXAIS Framework - Modus-Kommando-Handler

Diese Datei implementiert die Kommandos für den Moduswechsel im GENXAIS-Framework:
- VAN-mode: Verstehen, Analysieren, Nachfragen
- PLAN-mode: Projektplanung, Lösungskonzeption
- CREATE-mode: Codegenerierung, Ressourcenbereitstellung
- IMPLEMENT-mode: Integration, Deployment
- REFLECT-mode: Reflexion, Dokumentation
- ARCHIVE NOW: Archivierung des aktuellen Standes
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Importiere das GENXAIS SDK
try:
    from genxais_sdk import GENXAISFramework
except ImportError:
    logger.error("GENXAIS SDK konnte nicht importiert werden. Bitte stellen Sie sicher, dass es installiert ist.")
    sys.exit(1)

def activate_van_mode(args):
    """Aktiviert den VAN-Modus (Verstehen, Analysieren, Nachfragen)"""
    logger.info("Aktiviere VAN-Modus...")
    
    # Framework initialisieren
    framework = GENXAISFramework()
    
    # Modus setzen
    if framework.set_mode("VAN"):
        logger.info("VAN-Modus aktiviert.")
    else:
        logger.error("Fehler beim Aktivieren des VAN-Modus.")
        sys.exit(1)

def activate_plan_mode(args):
    """Aktiviert den PLAN-Modus (Projektplanung, Lösungskonzeption)"""
    logger.info("Aktiviere PLAN-Modus...")
    
    # Framework initialisieren
    framework = GENXAISFramework()
    
    # Modus setzen
    if framework.set_mode("PLAN"):
        logger.info("PLAN-Modus aktiviert.")
    else:
        logger.error("Fehler beim Aktivieren des PLAN-Modus.")
        sys.exit(1)

def activate_create_mode(args):
    """Aktiviert den CREATE-Modus (Codegenerierung, Ressourcenbereitstellung)"""
    logger.info("Aktiviere CREATE-Modus...")
    
    # Framework initialisieren
    framework = GENXAISFramework()
    
    # Modus setzen
    if framework.set_mode("CREATE"):
        logger.info("CREATE-Modus aktiviert.")
    else:
        logger.error("Fehler beim Aktivieren des CREATE-Modus.")
        sys.exit(1)

def activate_implement_mode(args):
    """Aktiviert den IMPLEMENT-Modus (Integration, Deployment)"""
    logger.info("Aktiviere IMPLEMENT-Modus...")
    
    # Framework initialisieren
    framework = GENXAISFramework()
    
    # Modus setzen
    if framework.set_mode("IMPLEMENT"):
        logger.info("IMPLEMENT-Modus aktiviert.")
    else:
        logger.error("Fehler beim Aktivieren des IMPLEMENT-Modus.")
        sys.exit(1)

def activate_reflect_mode(args):
    """Aktiviert den REFLECT-Modus (Reflexion, Dokumentation)"""
    logger.info("Aktiviere REFLECT-Modus...")
    
    # Framework initialisieren
    framework = GENXAISFramework()
    
    # Modus setzen
    if framework.set_mode("REFLECT"):
        logger.info("REFLECT-Modus aktiviert.")
    else:
        logger.error("Fehler beim Aktivieren des REFLECT-Modus.")
        sys.exit(1)

def activate_archive_now(args):
    """Aktiviert die Archivierung des aktuellen Standes"""
    logger.info("Starte Archivierung...")
    
    # Framework initialisieren
    framework = GENXAISFramework()
    
    # Modus setzen
    if framework.set_mode("ARCHIVE"):
        logger.info("Archivierung aktiviert.")
    else:
        logger.error("Fehler beim Aktivieren der Archivierung.")
        sys.exit(1)
    
    # Hier würde die eigentliche Archivierung erfolgen
    logger.info("Archivierung abgeschlossen.")

def main():
    """Hauptfunktion für die Kommandozeilen-Schnittstelle"""
    parser = argparse.ArgumentParser(description="GENXAIS Framework Modus-Kommandos")
    subparsers = parser.add_subparsers(help="Verfügbare Kommandos")
    
    # VAN-Mode
    van_parser = subparsers.add_parser("VAN-mode", help="Aktiviert den VAN-Modus (Verstehen, Analysieren, Nachfragen)")
    van_parser.set_defaults(func=activate_van_mode)
    
    # PLAN-Mode
    plan_parser = subparsers.add_parser("PLAN-mode", help="Aktiviert den PLAN-Modus (Projektplanung, Lösungskonzeption)")
    plan_parser.set_defaults(func=activate_plan_mode)
    
    # CREATE-Mode
    create_parser = subparsers.add_parser("CREATE-mode", help="Aktiviert den CREATE-Modus (Codegenerierung, Ressourcenbereitstellung)")
    create_parser.set_defaults(func=activate_create_mode)
    
    # IMPLEMENT-Mode
    implement_parser = subparsers.add_parser("IMPLEMENT-mode", help="Aktiviert den IMPLEMENT-Modus (Integration, Deployment)")
    implement_parser.set_defaults(func=activate_implement_mode)
    
    # REFLECT-Mode
    reflect_parser = subparsers.add_parser("REFLECT-mode", help="Aktiviert den REFLECT-Modus (Reflexion, Dokumentation)")
    reflect_parser.set_defaults(func=activate_reflect_mode)
    
    # ARCHIVE NOW
    archive_parser = subparsers.add_parser("ARCHIVE", help="Aktiviert die Archivierung des aktuellen Standes")
    archive_parser.add_argument("NOW", nargs="?", help="Führt die Archivierung sofort aus")
    archive_parser.set_defaults(func=activate_archive_now)
    
    # Parse Argumente
    args = parser.parse_args()
    
    # Führe die entsprechende Funktion aus
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
