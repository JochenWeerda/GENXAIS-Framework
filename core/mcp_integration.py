"""
MCP Integration for the GENXAIS Framework.

This class provides the integration between the framework and the Model Context Protocol (MCP),
enabling agents to access external tools.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable

logger = logging.getLogger("GENXAIS.MCPIntegration")

class ToolRegistry:
    """Registry for tools in the GENXAIS Framework."""
    
    def __init__(self):
        """Initialize the tool registry."""
        self.tools = {}
        
    def register_tool(self, name: str, func: Callable, description: str) -> None:
        """
        Register a tool in the registry.
        
        Args:
            name: Name of the tool
            func: Function that implements the tool
            description: Description of the tool
        """
        self.tools[name] = {
            "func": func,
            "description": description
        }
        logger.info(f"Tool \"{name}\" registered: {description}")
        
    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a tool from the registry.
        
        Args:
            name: Name of the tool
            
        Returns:
            Tool configuration or None if not found
        """
        return self.tools.get(name)
        
    def list_tools(self) -> List[str]:
        """
        List all available tools.
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())
        
    def get_tool_descriptions(self) -> Dict[str, str]:
        """
        Get descriptions of all tools.
        
        Returns:
            Dictionary with tool names and descriptions
        """
        return {name: tool["description"] for name, tool in self.tools.items()}

class MCPIntegration:
    """
    Class for integrating the Model Context Protocol (MCP) into the GENXAIS Framework.
    
    This class enables framework agents to access external tools via MCP.
    It manages tool configurations for different agent roles and provides
    MCP agents for the various roles.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MCP integration.
        
        Args:
            config: Optional configuration parameters.
        """
        self.config = config or {}
        self.api_key = self.config.get("api_key") or os.environ.get("MCP_API_KEY")
        self.timeout = self.config.get("timeout", 30)
        self.retry_attempts = self.config.get("retry_attempts", 3)
        
        # Initialize tool registry
        self.tool_registry = ToolRegistry()
        
        # Register default tools
        self._register_default_tools()
        
        logger.info("MCP Integration initialized")
    
    def _register_default_tools(self) -> None:
        """Register the default tools."""
        # File operations
        self.register_tool(
            "read_file",
            self._read_file,
            "Read the content of a file"
        )
        
        self.register_tool(
            "write_file",
            self._write_file,
            "Write content to a file"
        )
        
        # Search operations
        self.register_tool(
            "search",
            self._search,
            "Search for information"
        )
    
    def register_tool(self, name: str, func: Callable, description: str) -> None:
        """
        Register a tool for use with MCP.
        
        Args:
            name: Name of the tool
            func: Function that implements the tool
            description: Description of the tool
        """
        self.tool_registry.register_tool(name, func, description)
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute a tool.
        
        Args:
            tool_name: Name of the tool
            parameters: Parameters for the tool
            
        Returns:
            Result of the tool execution
            
        Raises:
            ValueError: If the tool was not found
            Exception: For errors during tool execution
        """
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        try:
            logger.info(f"Executing tool '{tool_name}' with parameters: {parameters}")
            result = await tool["func"](**parameters)
            return result
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {str(e)}")
            raise
    
    async def _read_file(self, path: str) -> str:
        """
        Read the content of a file.
        
        Args:
            path: Path to the file
            
        Returns:
            Content of the file
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file '{path}': {str(e)}")
            raise
    
    async def _write_file(self, path: str, content: str) -> bool:
        """
        Write content to a file.
        
        Args:
            path: Path to the file
            content: Content to write
            
        Returns:
            True on success
        """
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Error writing to file '{path}': {str(e)}")
            raise
    
    async def _search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for information.
        
        Args:
            query: Search query
            
        Returns:
            List of search results
        """
        # In a real implementation, this would perform an actual search
        # For this example, we just return a dummy result
        return [
            {"title": f"Result for '{query}'", "content": "Example content"}
        ]
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """
        Get descriptions of all available tools.
        
        Returns:
            Dictionary with tool names and descriptions
        """
        return self.tool_registry.get_tool_descriptions()
    
    def list_tools(self) -> List[str]:
        """
        List all available tools.
        
        Returns:
            List of tool names
        """
        return self.tool_registry.list_tools()
