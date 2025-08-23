"""
CeSail - A comprehensive web automation and DOM parsing platform with AI-powered agents.

This package provides:
- DOM Parser: JavaScript-based DOM analysis and element extraction
- MCP Server: FastMCP server for web automation APIs
- Simple Agent: AI-powered web automation agent
"""

__version__ = "0.2.0"
__author__ = "CeSail Contributors"
__email__ = "ajjayawardane@gmail.com"

# Import subpackages
from . import dom_parser
from . import cesail_mcp

# Import simple_agent with error handling
try:
    from . import simple_agent
except Exception as e:
    simple_agent = None
    import warnings
    warnings.warn(f"SimpleAgent subpackage not available: {e}")

# Public shortcuts
try:
    from .dom_parser.src.dom_parser import DOMParser
    from .dom_parser.src.py.types import Action, ActionType, ParsedPage
except ImportError:
    DOMParser = None
    Action = ActionType = ParsedPage = None

try:
    from .cesail_mcp.fastmcp_server import FastMCP as fastmcp_server
except Exception:
    fastmcp_server = None

try:
    from .simple_agent.simple_agent import SimpleAgent
    from .simple_agent import llm_interface
except Exception:
    SimpleAgent = None
    llm_interface = None

__all__ = [
    # Subpackages
    "dom_parser",
    "cesail_mcp", 
    "simple_agent",
    
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