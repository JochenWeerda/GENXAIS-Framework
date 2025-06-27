"""
GENXAIS Framework - Generalized AI-Enhanced Software Development SDK
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Union, Callable
from pathlib import Path

# APM Framework Imports
from apm_framework.core import APMCore
from apm_framework.phases import VanPhase, PlanPhase, CreatePhase, ImplementPhase, ReflectPhase
from apm_framework.workflow import APMWorkflow

# Multi-Agent System Imports
from agents.base import BaseAgent
from agents.coordinator import AgentCoordinator
from agents.developer import DeveloperAgent
from agents.analyst import AnalystAgent

# LangGraph Integration
from langgraph.core import StateGraph
from langgraph.agents import AgentState

# MCP Integration
from mcp_integration import MCPIntegration

# Pipeline Management
from core.pipeline_manager import PipelineManager, PipelineStep, PipelineStatus

class GENXAISFramework:
    """
    Hauptklasse des GENXAIS Frameworks für KI-gestützte Softwareentwicklung.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
        # Initialisiere APM Framework
        self.apm_core = APMCore()
        self.workflow = APMWorkflow()
        
        # Initialisiere Multi-Agent System
        self.coordinator = AgentCoordinator()
        self.setup_agents()
        
        # Initialisiere Pipeline Manager
        self.pipeline_manager = PipelineManager()
        
        # Initialisiere MCP Integration
        self.mcp_integration = MCPIntegration(
            mcp_server_url=self.config.get('mcp_server_url', 'http://localhost:8000'),
            config=self.config.get('mcp_config', {})
        )
        
        # Initialisiere LangGraph
        self.state_graph = self._setup_langgraph()
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Lädt die Konfiguration aus der config.json"""
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__),
                'config',
                'config.json'
            )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Fehler beim Laden der Konfiguration: {e}")
    
    def _setup_logging(self) -> logging.Logger:
        """Richtet das Logging-System ein"""
        logger = logging.getLogger('GENXAIS')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        logger.addHandler(handler)
        return logger
    
    def setup_agents(self):
        """Initialisiert und registriert die Agenten"""
        developer = DeveloperAgent()
        analyst = AnalystAgent()
        
        self.coordinator.register_agent(developer)
        self.coordinator.register_agent(analyst)
    
    def _setup_langgraph(self) -> StateGraph:
        """Initialisiert den LangGraph für Agenten-Workflows"""
        graph = StateGraph()
        # Workflow-Zustände und Übergänge konfigurieren
        return graph
    
    async def create_development_pipeline(
        self,
        name: str,
        steps: List[PipelineStep]
    ) -> str:
        """Erstellt eine neue Entwicklungs-Pipeline"""
        return await self.pipeline_manager.create_pipeline(name, steps)
    
    async def execute_pipeline(
        self,
        pipeline_name: str,
        input_data: Dict,
        context: Optional[Dict] = None
    ) -> Dict:
        """Führt eine Entwicklungs-Pipeline aus"""
        return await self.pipeline_manager.execute_pipeline(
            pipeline_name,
            input_data,
            context
        )
    
    def start_apm_phase(self, phase_name: str):
        """Startet eine spezifische APM-Phase"""
        phase_map = {
            'van': VanPhase,
            'plan': PlanPhase,
            'create': CreatePhase,
            'implement': ImplementPhase,
            'reflect': ReflectPhase
        }
        
        if phase_name.lower() not in phase_map:
            raise ValueError(f"Unbekannte Phase: {phase_name}")
            
        phase = phase_map[phase_name.lower()]()
        self.workflow.start_phase(phase)
    
    async def process_task(self, task_data: Dict) -> Dict:
        """Verarbeitet eine Entwicklungsaufgabe"""
        try:
            # MCP-Kontext erstellen
            mcp_context = self.mcp_integration.create_mcp_context(task_data.get('agent_type', 'developer'))
            
            # Aufgabe durch Agenten verarbeiten
            result = await self.coordinator.handle_task(task_data, mcp_context)
            
            # Ergebnis in aktuelle APM-Phase integrieren
            self.workflow.current_phase.process_result(result)
            
            return result
        except Exception as e:
            self.logger.error(f"Fehler bei der Aufgabenverarbeitung: {e}")
            raise

    def register_custom_tool(self, tool_name: str, tool_config: Dict):
        """Registriert ein benutzerdefiniertes Tool"""
        self.mcp_integration.register_tool(tool_name, tool_config)

    def get_pipeline_status(self, pipeline_name: str) -> PipelineStatus:
        """Gibt den Status einer Pipeline zurück"""
        return self.pipeline_manager.get_pipeline_status(pipeline_name)

    def health_check(self) -> Dict[str, bool]:
        """Führt einen Gesundheitscheck aller Komponenten durch"""
        return {
            'apm': self.apm_core.is_healthy(),
            'agents': self.coordinator.is_healthy(),
            'pipeline': bool(self.pipeline_manager),
            'mcp': bool(self.mcp_integration),
            'langgraph': bool(self.state_graph)
        }

if __name__ == "__main__":
    framework = GENXAISFramework()
    framework.logger.info("GENXAIS Framework erfolgreich initialisiert")
