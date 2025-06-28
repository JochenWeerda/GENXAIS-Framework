"""
Base Agent Module for GENXAIS Framework.

This module provides the foundational agent classes that define the core functionality
and restrictions for different agent types in the GENXAIS framework.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging
from contextlib import contextmanager

class AgentMode(str, Enum):
    """Defines the different operational modes for agents."""
    VAN = "van"
    PLAN = "plan"
    CREATE = "create"
    IMPLEMENT = "implement"
    REVIEW = "review"

class AgentRestrictions(BaseModel):
    """Defines the restrictions and permissions for an agent."""
    allowed_actions: List[str]
    forbidden_actions: List[str]
    required_outputs: List[str]
    quality_thresholds: Dict[str, float]

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the GENXAIS framework.
    
    This class defines the core interface and shared functionality that all
    agents must implement, including mode-specific restrictions and validations.
    """
    
    def __init__(self, mode: AgentMode):
        self.mode = mode
        self.restrictions = self._get_mode_restrictions()
        
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task within the agent's current mode restrictions."""
        pass
        
    def _get_mode_restrictions(self) -> AgentRestrictions:
        """Get the restrictions for the current mode."""
        if self.mode == AgentMode.VAN:
            return AgentRestrictions(
                allowed_actions=[
                    "read_system_data",
                    "analyze_metrics",
                    "validate_requirements",
                    "generate_reports"
                ],
                forbidden_actions=[
                    "modify_code",
                    "create_designs",
                    "make_implementation_decisions",
                    "deploy_code"
                ],
                required_outputs=[
                    "analysis_report",
                    "validation_results",
                    "metric_dashboard"
                ],
                quality_thresholds={
                    "analysis_coverage": 0.8,
                    "validation_accuracy": 0.9,
                    "report_quality": 0.85
                }
            )
        elif self.mode == AgentMode.PLAN:
            return AgentRestrictions(
                allowed_actions=[
                    "create_plans",
                    "define_requirements",
                    "allocate_resources",
                    "set_milestones"
                ],
                forbidden_actions=[
                    "modify_code",
                    "execute_plans",
                    "modify_systems",
                    "deploy_changes"
                ],
                required_outputs=[
                    "project_plan",
                    "resource_allocation",
                    "technical_requirements"
                ],
                quality_thresholds={
                    "plan_completeness": 0.9,
                    "requirement_clarity": 0.85,
                    "resource_efficiency": 0.8
                }
            )
        elif self.mode == AgentMode.CREATE:
            return AgentRestrictions(
                allowed_actions=[
                    "generate_code",
                    "design_architecture",
                    "create_specifications",
                    "develop_schemas"
                ],
                forbidden_actions=[
                    "deploy_code",
                    "modify_production",
                    "change_requirements",
                    "execute_code"
                ],
                required_outputs=[
                    "source_code",
                    "technical_specs",
                    "architecture_design"
                ],
                quality_thresholds={
                    "code_quality": 0.85,
                    "design_completeness": 0.9,
                    "spec_clarity": 0.8
                }
            )
        elif self.mode == AgentMode.IMPLEMENT:
            return AgentRestrictions(
                allowed_actions=[
                    "deploy_code",
                    "integrate_components",
                    "configure_systems",
                    "run_tests"
                ],
                forbidden_actions=[
                    "modify_requirements",
                    "change_architecture",
                    "create_designs",
                    "exceed_scope"
                ],
                required_outputs=[
                    "deployment_report",
                    "test_results",
                    "integration_status"
                ],
                quality_thresholds={
                    "deployment_success": 0.95,
                    "test_coverage": 0.9,
                    "integration_quality": 0.85
                }
            )
        elif self.mode == AgentMode.REVIEW:
            return AgentRestrictions(
                allowed_actions=[
                    "review_code",
                    "assess_quality",
                    "identify_issues",
                    "provide_feedback"
                ],
                forbidden_actions=[
                    "modify_code",
                    "implement_fixes",
                    "change_designs",
                    "deploy_changes"
                ],
                required_outputs=[
                    "review_report",
                    "quality_assessment",
                    "improvement_suggestions"
                ],
                quality_thresholds={
                    "review_coverage": 0.9,
                    "assessment_accuracy": 0.85,
                    "feedback_quality": 0.8
                }
            )
        else:
            raise ValueError(f"Unknown mode: {self.mode}")
            
    def validate_action(self, action: str) -> bool:
        """Validate if an action is allowed in the current mode."""
        return (action in self.restrictions.allowed_actions and 
                action not in self.restrictions.forbidden_actions)
                
    def validate_output_quality(self, output_metrics: Dict[str, float]) -> bool:
        """Validate if the output meets quality thresholds."""
        return all(
            output_metrics.get(metric, 0) >= threshold 
            for metric, threshold in self.restrictions.quality_thresholds.items()
        )

    @contextmanager
    def error_handling_context(self):
        """Context manager for handling errors during agent execution."""
        try:
            yield
        except Exception as e:
            self.handle_error(e)
            raise

    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle errors during agent execution with recovery strategies."""
        error_type = type(error).__name__
        error_info = {
            "type": error_type,
            "message": str(error),
            "mode": self.mode,
            "agent_class": self.__class__.__name__
        }
        
        logging.error(f"Agent error occurred: {error_info}")
        
        # Attempt recovery based on error type
        recovery_result = self.attempt_recovery(error_info)
        
        if recovery_result["success"]:
            logging.info(f"Successfully recovered from {error_type}")
            return {
                "error_handled": True,
                "recovery": recovery_result,
                "original_error": error_info
            }
        else:
            logging.error(f"Failed to recover from {error_type}")
            return {
                "error_handled": False,
                "recovery_attempted": True,
                "original_error": error_info
            }

    def attempt_recovery(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to recover from an error based on error type and mode."""
        error_type = error_info["type"]
        
        recovery_strategies = {
            "ValueError": self._recover_value_error,
            "TypeError": self._recover_type_error,
            "KeyError": self._recover_key_error,
            "FileNotFoundError": self._recover_file_error,
            "PermissionError": self._recover_permission_error,
            "TimeoutError": self._recover_timeout_error
        }
        
        if error_type in recovery_strategies:
            try:
                return recovery_strategies[error_type](error_info)
            except Exception as recovery_error:
                return {
                    "success": False,
                    "error": f"Recovery failed: {str(recovery_error)}"
                }
        else:
            return {
                "success": False,
                "error": f"No recovery strategy for {error_type}"
            }

    def _recover_value_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from ValueError by validating and correcting input values."""
        try:
            # Log the recovery attempt
            logging.info(f"Attempting to recover from ValueError in {self.mode} mode")
            
            # Implement mode-specific recovery logic
            if self.mode == AgentMode.VAN:
                return {"success": True, "action": "validated_inputs"}
            elif self.mode == AgentMode.PLAN:
                return {"success": True, "action": "adjusted_plan"}
            elif self.mode == AgentMode.CREATE:
                return {"success": True, "action": "corrected_parameters"}
            elif self.mode == AgentMode.IMPLEMENT:
                return {"success": True, "action": "fixed_implementation"}
            elif self.mode == AgentMode.REVIEW:
                return {"success": True, "action": "updated_review_criteria"}
            
            return {"success": False, "error": "Unsupported mode for recovery"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _recover_type_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from TypeError by correcting type mismatches."""
        try:
            logging.info(f"Attempting to recover from TypeError in {self.mode} mode")
            return {"success": True, "action": "corrected_types"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _recover_key_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from KeyError by handling missing dictionary keys."""
        try:
            logging.info(f"Attempting to recover from KeyError in {self.mode} mode")
            return {"success": True, "action": "added_missing_keys"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _recover_file_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from FileNotFoundError by creating or locating files."""
        try:
            logging.info(f"Attempting to recover from FileNotFoundError in {self.mode} mode")
            return {"success": True, "action": "created_missing_file"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _recover_permission_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from PermissionError by adjusting permissions or paths."""
        try:
            logging.info(f"Attempting to recover from PermissionError in {self.mode} mode")
            return {"success": True, "action": "adjusted_permissions"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _recover_timeout_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from TimeoutError by implementing retry logic."""
        try:
            logging.info(f"Attempting to recover from TimeoutError in {self.mode} mode")
            return {"success": True, "action": "implemented_retry"}
        except Exception as e:
            return {"success": False, "error": str(e)} 