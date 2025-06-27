"""
LangGraph Integration for the GENXAIS Framework.

This module provides integration with LangGraph for creating and managing agent workflows.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger("GENXAIS.LangGraphIntegration")

class AgentType(Enum):
    """Available agent types in the framework."""
    TOOL_AGENT = "tool_agent"
    WORKFLOW_AGENT = "workflow_agent"
    COMMUNICATION_AGENT = "communication_agent"
    TESTING_AGENT = "testing_agent"
    SUPERVISOR_AGENT = "supervisor_agent"

@dataclass
class AgentConfig:
    """Configuration for an agent."""
    agent_type: AgentType
    name: str
    description: str
    tools: List[str]
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout: float = 300.0
    max_retries: int = 3

@dataclass
class AgentState:
    """State of an agent during execution."""
    agent_id: str
    agent_type: AgentType
    status: str = "pending"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    current_task: Optional[str] = None
    results: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

class WorkflowStep:
    """Represents a step in a workflow."""
    
    def __init__(self, name: str, function: Callable, 
                 requires: List[str] = None, provides: List[str] = None):
        """
        Initialize a workflow step.
        
        Args:
            name: Name of the step
            function: Function to execute
            requires: List of required inputs
            provides: List of outputs provided
        """
        self.name = name
        self.function = function
        self.requires = requires or []
        self.provides = provides or []

class Workflow:
    """Represents a complete workflow of steps."""
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize a workflow.
        
        Args:
            name: Name of the workflow
            description: Description of the workflow
        """
        self.name = name
        self.description = description
        self.steps: Dict[str, WorkflowStep] = {}
        self.step_order: List[str] = []
        
    def add_step(self, step: WorkflowStep, after: Optional[str] = None) -> None:
        """
        Add a step to the workflow.
        
        Args:
            step: The step to add
            after: The step after which to add this step (or None for the beginning)
        """
        self.steps[step.name] = step
        
        if after is None:
            self.step_order.insert(0, step.name)
        else:
            try:
                idx = self.step_order.index(after)
                self.step_order.insert(idx + 1, step.name)
            except ValueError:
                # If 'after' step not found, add to the end
                self.step_order.append(step.name)
                
    def get_step(self, name: str) -> Optional[WorkflowStep]:
        """
        Get a step by name.
        
        Args:
            name: Name of the step
            
        Returns:
            The step or None if not found
        """
        return self.steps.get(name)
    
    def get_steps_in_order(self) -> List[WorkflowStep]:
        """
        Get all steps in execution order.
        
        Returns:
            List of steps in execution order
        """
        return [self.steps[name] for name in self.step_order if name in self.steps]

class LangGraphIntegration:
    """
    Integration of LangGraph for multi-agent coordination.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LangGraph integration.
        
        Args:
            config: Optional configuration
        """
        self.config = config or {}
        self.agents: Dict[str, AgentConfig] = {}
        self.agent_states: Dict[str, AgentState] = {}
        self.workflows: Dict[str, Workflow] = {}
        
        logger.info("LangGraph Integration initialized")
        
    def register_agent(self, agent_config: AgentConfig) -> None:
        """
        Register a new agent.
        
        Args:
            agent_config: Configuration of the agent
        """
        self.agents[agent_config.name] = agent_config
        logger.info(f"Agent '{agent_config.name}' registered")
        
    def get_agent_config(self, agent_name: str) -> Optional[AgentConfig]:
        """
        Get the configuration of an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent configuration or None if not found
        """
        return self.agents.get(agent_name)
        
    def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        """
        Get the state of an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Agent state or None if not found
        """
        return self.agent_states.get(agent_id)
        
    def update_agent_state(self,
                          agent_id: str,
                          status: Optional[str] = None,
                          task: Optional[str] = None,
                          result: Optional[Dict[str, Any]] = None,
                          error: Optional[str] = None) -> None:
        """
        Update the state of an agent.
        
        Args:
            agent_id: ID of the agent
            status: New status
            task: Current task
            result: Result of the task
            error: Error that occurred
        """
        if agent_id not in self.agent_states:
            return
            
        state = self.agent_states[agent_id]
        
        if status:
            state.status = status
            if status == "running" and not state.start_time:
                state.start_time = datetime.now()
            elif status in ("completed", "failed"):
                state.end_time = datetime.now()
                
        if task:
            state.current_task = task
            
        if result:
            state.results.update(result)
            
        if error:
            state.error = error
            state.status = "failed"
            state.end_time = datetime.now()
            
        logger.info(f"Agent '{agent_id}' state updated: status={status}, task={task}")
    
    def create_workflow(self, name: str, description: str = "") -> Workflow:
        """
        Create a new workflow.
        
        Args:
            name: Name of the workflow
            description: Description of the workflow
            
        Returns:
            The created workflow
        """
        workflow = Workflow(name, description)
        self.workflows[name] = workflow
        logger.info(f"Workflow '{name}' created")
        return workflow
    
    def get_workflow(self, name: str) -> Optional[Workflow]:
        """
        Get a workflow by name.
        
        Args:
            name: Name of the workflow
            
        Returns:
            The workflow or None if not found
        """
        return self.workflows.get(name)
    
    async def execute_workflow(self, workflow_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow.
        
        Args:
            workflow_name: Name of the workflow
            context: Initial context
            
        Returns:
            The final context after execution
            
        Raises:
            ValueError: If the workflow was not found
        """
        workflow = self.get_workflow(workflow_name)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_name}' not found")
        
        logger.info(f"Executing workflow '{workflow_name}'")
        result_context = context.copy()
        
        for step in workflow.get_steps_in_order():
            # Check if all required inputs are available
            missing_inputs = [req for req in step.requires if req not in result_context]
            if missing_inputs:
                logger.error(f"Missing required inputs for step '{step.name}': {missing_inputs}")
                continue
            
            # Execute the step
            try:
                logger.info(f"Executing step '{step.name}'")
                step_inputs = {req: result_context[req] for req in step.requires if req in result_context}
                step_result = await step.function(step_inputs)
                
                # Update context with step results
                if isinstance(step_result, dict):
                    result_context.update(step_result)
            except Exception as e:
                logger.error(f"Error executing step '{step.name}': {str(e)}")
                # Continue with next step
        
        logger.info(f"Workflow '{workflow_name}' execution completed")
        return result_context
