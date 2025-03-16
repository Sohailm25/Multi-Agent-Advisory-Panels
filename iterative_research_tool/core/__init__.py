"""Core components for the Iterative Research Tool."""

# Import key components for easier access
from iterative_research_tool.core.config import ConfigManager, ToolConfig
from iterative_research_tool.core.logging_utils import setup_logging, ProgressLogger
from iterative_research_tool.core.research import IterativeResearchTool, CostLimitExceededError
from iterative_research_tool.core.strategic_planner import StrategicPlanner
from iterative_research_tool.core.user_memory import UserMemory
from iterative_research_tool.core.visualization import Visualizer
from iterative_research_tool.core.panel_factory import panel_factory

# Import the interactive CLI
try:
    from iterative_research_tool.core.interactive_cli import run_interactive_cli, InteractiveCLI
except ImportError:
    pass 