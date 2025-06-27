"""
Pipeline-Manager für Multi-Pipeline-Verarbeitung im GENXAIS Framework
"""
from typing import Dict, List, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from pathlib import Path

from .error_handling import ErrorHandler, PipelineError
from .state_manager import StateManager

class PipelineStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class PipelineStep:
    name: str
    function: Callable
    requires: List[str]
    provides: List[str]
    error_handlers: List[Callable]
    retry_policy: Dict

class PipelineManager:
    """
    Verwaltet multiple Entwicklungs-Pipelines mit Fehlerbehandlung und Zustandsverwaltung.
    """
    
    def __init__(self):
        self.pipelines: Dict[str, List[PipelineStep]] = {}
        self.state_manager = StateManager()
        self.error_handler = ErrorHandler()
        self.logger = logging.getLogger(__name__)
        
    async def create_pipeline(self, name: str, steps: List[PipelineStep]) -> str:
        """Erstellt eine neue Pipeline mit definierten Schritten"""
        if name in self.pipelines:
            raise PipelineError(f"Pipeline {name} existiert bereits")
            
        # Validiere Pipeline-Struktur
        self._validate_pipeline(steps)
        
        self.pipelines[name] = steps
        self.state_manager.initialize_pipeline_state(name)
        
        self.logger.info(f"Pipeline {name} erstellt mit {len(steps)} Schritten")
        return name
        
    def _validate_pipeline(self, steps: List[PipelineStep]):
        """Überprüft die Abhängigkeiten und Struktur der Pipeline"""
        provided_outputs = set()
        for step in steps:
            # Prüfe, ob alle erforderlichen Inputs verfügbar sind
            for req in step.requires:
                if req not in provided_outputs:
                    raise PipelineError(
                        f"Schritt {step.name} benötigt {req}, "
                        "aber dieser Output wurde noch nicht bereitgestellt"
                    )
            provided_outputs.update(step.provides)
            
    async def execute_pipeline(
        self,
        pipeline_name: str,
        input_data: Dict,
        context: Optional[Dict] = None
    ) -> Dict:
        """Führt eine Pipeline asynchron aus"""
        if pipeline_name not in self.pipelines:
            raise PipelineError(f"Pipeline {pipeline_name} nicht gefunden")
            
        pipeline = self.pipelines[pipeline_name]
        state = {}
        
        try:
            self.state_manager.set_pipeline_status(
                pipeline_name,
                PipelineStatus.RUNNING
            )
            
            for step in pipeline:
                try:
                    # Führe Schritt mit Fehlerbehandlung aus
                    result = await self._execute_step_with_retry(
                        step, input_data, state, context
                    )
                    state.update(result)
                    
                except Exception as e:
                    # Fehlerbehandlung für den Schritt
                    handled = await self._handle_step_error(
                        step, e, input_data, state, context
                    )
                    if not handled:
                        raise
                        
            self.state_manager.set_pipeline_status(
                pipeline_name,
                PipelineStatus.COMPLETED
            )
            return state
            
        except Exception as e:
            self.state_manager.set_pipeline_status(
                pipeline_name,
                PipelineStatus.FAILED
            )
            self.logger.error(f"Pipeline {pipeline_name} fehlgeschlagen: {str(e)}")
            raise
            
    async def _execute_step_with_retry(
        self,
        step: PipelineStep,
        input_data: Dict,
        state: Dict,
        context: Optional[Dict]
    ) -> Dict:
        """Führt einen Pipeline-Schritt mit Retry-Logik aus"""
        retries = step.retry_policy.get('max_retries', 3)
        delay = step.retry_policy.get('delay', 1)
        
        for attempt in range(retries):
            try:
                return await step.function(input_data, state, context)
            except Exception as e:
                if attempt == retries - 1:
                    raise
                self.logger.warning(
                    f"Schritt {step.name} fehlgeschlagen, "
                    f"Versuch {attempt + 1}/{retries}"
                )
                await asyncio.sleep(delay * (attempt + 1))
                
    async def _handle_step_error(
        self,
        step: PipelineStep,
        error: Exception,
        input_data: Dict,
        state: Dict,
        context: Optional[Dict]
    ) -> bool:
        """Behandelt Fehler in einem Pipeline-Schritt"""
        for handler in step.error_handlers:
            try:
                await handler(error, step, input_data, state, context)
                return True
            except Exception as e:
                self.logger.error(
                    f"Fehlerhandler für Schritt {step.name} "
                    f"fehlgeschlagen: {str(e)}"
                )
        return False
        
    def get_pipeline_status(self, pipeline_name: str) -> PipelineStatus:
        """Gibt den aktuellen Status einer Pipeline zurück"""
        return self.state_manager.get_pipeline_status(pipeline_name)
        
    def pause_pipeline(self, pipeline_name: str):
        """Pausiert eine laufende Pipeline"""
        self.state_manager.set_pipeline_status(
            pipeline_name,
            PipelineStatus.PAUSED
        )
        
    def resume_pipeline(self, pipeline_name: str):
        """Setzt eine pausierte Pipeline fort"""
        self.state_manager.set_pipeline_status(
            pipeline_name,
            PipelineStatus.RUNNING
        )
        
    def get_pipeline_metrics(self, pipeline_name: str) -> Dict:
        """Gibt Metriken für eine Pipeline zurück"""
        return self.state_manager.get_pipeline_metrics(pipeline_name) 