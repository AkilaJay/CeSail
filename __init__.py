"""
CeSail - A comprehensive web automation and DOM parsing platform with AI-powered agents.

This package provides:
- DOM Parser: JavaScript-based DOM analysis and element extraction
- MCP Server: FastMCP server for web automation APIs
- Simple Agent: AI-powered web automation agent
"""

__version__ = "0.1.1"
__author__ = "CeSail Contributors"
__email__ = "ajjayawardane@gmail.com"

# Import core components for public API
try:
    from dom_parser.src.dom_parser import DOMParser
    from dom_parser.src.py.types import Action, ActionType, ParsedPage
except ImportError:
    # Handle case where dom_parser is not available
    pass

# Import MCP server for easy access
try:
    from cesail_mcp.fastmcp_server import FastMCP as fastmcp_server
except ImportError as e:
    # Handle case where cesail_mcp is not available
    fastmcp_server = None
    import warnings
    warnings.warn(
        "FastMCP server is not available. This may be due to missing dependencies. "
        f"Error: {str(e)}"
    )

# Import Simple Agent components
try:
    from simple_agent.simple_agent import SimpleAgent
    from simple_agent import llm_interface
except (ImportError, Exception) as e:
    # Handle case where simple_agent is not available or needs API key
    SimpleAgent = None
    llm_interface = None
    import warnings
    warnings.warn(
        "SimpleAgent is not available. To use it, set OPENAI_API_KEY environment variable "
        "or create a .env file with your OpenAI API key. "
        f"Error: {str(e)}"
    )

__all__ = [
    # Core API - What 90% of users need
    "DOMParser",           # Main automation class
    "Action", "ActionType", # Action system
    "ParsedPage",          # Main data model
    "SimpleAgent",         # AI automation
    "llm_interface",       # LLM interface utilities
    "fastmcp_server",      # MCP integration
    
    # Version info
    "__version__",
    "__author__",
    "__email__"
]