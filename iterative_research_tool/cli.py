"""Command-line interface for the Iterative Research Tool."""

import os
import sys
import argparse
import logging
import tempfile
import json
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List
from dotenv import load_dotenv
from colorama import Fore, Style
import re
from datetime import datetime
import traceback

from iterative_research_tool.core.config import ConfigManager, ToolConfig, APIConfig
from iterative_research_tool.core.logging_utils import setup_logging, ProgressLogger
from iterative_research_tool.core.research import IterativeResearchTool, CostLimitExceededError
from iterative_research_tool.core.strategic_planner import StrategicPlanner
from iterative_research_tool.core.user_memory import UserMemory
from iterative_research_tool.core.visualization import Visualizer
# Temporarily commented out for initial GitHub deployment
# from iterative_research_tool.core.panel_factory import panel_factory

# Import the strategic advisors
from iterative_research_tool.strategic_advisor import StrategicAdvisorCustom, StrategicAdvisorSwarm

# Add output location config
CONFIG_FILE = os.path.expanduser("~/.iterative_research_tool_config")

# Import the interactive CLI
try:
    from iterative_research_tool.core.interactive_cli import run_interactive_cli
except ImportError as e:
    run_interactive_cli = None
    INTERACTIVE_CLI_IMPORT_ERROR = str(e)
else:
    INTERACTIVE_CLI_IMPORT_ERROR = None

# Import the LLM client factory
global LLMClientFactory
try:
    from iterative_research_tool.core.llm_client import LLMClientFactory
except ImportError as e:
    # This will be handled during runtime
    LLM_IMPORT_ERROR = str(e)
    LLMClientFactory = None
else:
    LLM_IMPORT_ERROR = None

# Try to import LLM provider libraries
try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

logger = logging.getLogger(__name__)

# Add functions to manage output directory configuration
def load_output_config():
    """Load the output directory configuration."""
    config = {"output_dir": os.environ.get("ITERATIVE_RESEARCH_TOOL_OUTPUT_DIR")}
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            logger.warning(f"Error loading config file: {e}")
    
    # Default to ~/iterative_research_tool_output if not set
    if not config.get("output_dir"):
        config["output_dir"] = os.path.expanduser("~/iterative_research_tool_output")
    
    return config

def save_output_config(output_dir):
    """Save the output directory configuration."""
    config = {}
    
    # Load existing config if it exists
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
        except Exception as e:
            logger.warning(f"Error loading existing config file: {e}")
    
    # Update with new output dir
    config["output_dir"] = output_dir
    
    # Save config
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving config file: {e}")
        return False

def setup_default_output_dir(output_dir):
    """Set up the default output directory configuration."""
    visualizer = Visualizer()
    
    if not output_dir:
        visualizer.display_error("No output directory specified")
        return False
    
    # Check if the directory exists or can be created
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        visualizer.display_error(f"Could not create output directory: {e}")
        return False
    
    # Save the configuration
    if save_output_config(output_dir):
        visualizer.display_success(f"Default output directory set to: {output_dir}")
        return True
    else:
        visualizer.display_error("Failed to save configuration")
        return False

def install_dependencies(provider: str) -> bool:
    """
    Install dependencies for a specific LLM provider.
    
    Args:
        provider: The LLM provider to install dependencies for
        
    Returns:
        True if installation was successful, False otherwise
    """
    visualizer = Visualizer()
    visualizer.display_message(f"Installing dependencies for {provider}...")
    
    # Map providers to their package names
    provider_packages = {
        "anthropic": "anthropic",
        "openai": "openai",
        "perplexity": "perplexity-python"
    }
    
    package = provider_packages.get(provider.lower())
    if not package:
        visualizer.display_error(f"Unknown provider: {provider}")
        return False
    
    try:
        # Run pip install for the specific package
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
            check=True
        )
        visualizer.display_success(f"Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        visualizer.display_error(f"Failed to install {package}: {e}")
        visualizer.display_error(f"Error output: {e.stderr}")
        return False


def install_all_dependencies() -> bool:
    """
    Install all LLM provider dependencies.
    
    Returns:
        True if installation was successful, False otherwise
    """
    visualizer = Visualizer()
    visualizer.display_message("Installing all LLM provider dependencies...")
    
    try:
        # Get the current script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to the package root
        package_root = os.path.dirname(script_dir)
        
        # Run pip install with the 'all' extra
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", f"{package_root}[all]"],
            capture_output=True,
            text=True,
            check=True
        )
        visualizer.display_success("Successfully installed all LLM provider dependencies")
        return True
    except subprocess.CalledProcessError as e:
        visualizer.display_error(f"Failed to install dependencies: {e}")
        visualizer.display_error(f"Error output: {e.stderr}")
        return False


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Advisory Planner CLI Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Main planner command (default, no subcommand needed)
    main_parser = parser
    
    # Interactive UI command
    panelsui_parser = subparsers.add_parser('panelsui', help='Run the interactive UI with arrow key selection')
    panelsui_parser.add_argument('--output-file', help='File to save the plan to')
    panelsui_parser.add_argument('--output-dir', help='Directory to save outputs to')
    # Temporarily disabled for initial GitHub deployment
    # panelsui_parser.add_argument('--custom-panel-path', action='append', help='Path to custom panel files or directories')
    panelsui_parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    panelsui_parser.add_argument('--show-agent-details', action='store_true', help='Show detailed agent processing steps, prompts, and responses')
    
    # Strategic advisor - custom architecture
    strat_custom_parser = subparsers.add_parser('strat-custom', help='Run strategic advisor with custom architecture')
    strat_custom_parser.add_argument('query', nargs='?', help='Query to analyze')
    strat_custom_parser.add_argument('--output-file', help='File to save the plan to')
    strat_custom_parser.add_argument('--output-dir', help='Directory to save outputs to')
    strat_custom_parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    # Strategic advisor - swarm architecture
    strat_swarm_parser = subparsers.add_parser('strat-swarm', help='Run strategic advisor with swarm architecture')
    strat_swarm_parser.add_argument('query', nargs='?', help='Query to analyze')
    strat_swarm_parser.add_argument('--output-file', help='File to save the plan to')
    strat_swarm_parser.add_argument('--output-dir', help='Directory to save outputs to')
    strat_swarm_parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    # Add configuration command
    config_parser = subparsers.add_parser('config', help='Configure default settings')
    config_parser.add_argument('--set-output-dir', help='Set default output directory')
    
    # Add main arguments
    parser.add_argument('--panel', help='Panel type to use')
    parser.add_argument('--list-panels', action='store_true', help='List available panels')
    parser.add_argument('--panel-info', help='Get information about a specific panel')
    parser.add_argument('--custom-panel-path', action='append', help='Path to custom panel files or directories')
    parser.add_argument('--time-travel', help='Travel to a specific checkpoint')
    parser.add_argument('--show-checkpoints', action='store_true', help='Show available checkpoints')
    parser.add_argument('--alternative', help='Explore an alternative')
    parser.add_argument('--collect-feedback', action='store_true', help='Collect feedback after planning')
    parser.add_argument('--output-file', help='File to save the plan to')
    parser.add_argument('--output-dir', help='Directory to save outputs to')
    parser.add_argument('--model', help='Model to use (if not specified, use the default model for the provider)')
    parser.add_argument('--memory-file', help='File to store user memory')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--show-agent-details', action='store_true', help='Show detailed agent processing steps, prompts, and responses')
    parser.add_argument('--llm-provider', default='anthropic', help='LLM provider to use')
    parser.add_argument('--api-key', help='API key for the LLM provider')
    parser.add_argument('--install-deps', action='store_true', help='Install missing dependencies')
    parser.add_argument('query', nargs='?', help='Query to analyze')
    
    return parser


def main() -> int:
    """Main entry point for the CLI.
        
    Returns:
        Exit code
    """
    # Load environment variables
    load_dotenv()
    
    # Create parser and parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle config command
    if args.command == "config":
        if args.set_output_dir:
            return 0 if setup_default_output_dir(args.set_output_dir) else 1
        else:
            # Display current configuration
            config = load_output_config()
            visualizer = Visualizer()
            visualizer.display_message("\nCurrent Configuration:")
            visualizer.display_message(f"Output Directory: {config['output_dir']}")
            visualizer.display_message("\nUse '--set-output-dir' to change the default output directory.")
            return 0
    
    # Set up logging
    setup_logging(args.verbose, "iterative_research_tool.log")
    
    # Create visualizer
    visualizer = Visualizer()
    
    # Initialize panel factory with custom panel paths
    custom_panel_paths = args.custom_panel_path or []
    # panel_factory.discover_panels(custom_panel_paths, args.verbose)
    
    # Run the interactive UI if requested
    if args.command == "panelsui":
        if run_interactive_cli is None:
            visualizer.display_error(f"Failed to import interactive CLI: {INTERACTIVE_CLI_IMPORT_ERROR}")
            return 1
        
        try:
            # Set up logging to a file for cleaner UI
            setup_file_logging()
            
            # Run the interactive CLI
            selections = run_interactive_cli()
            
            # Process the selections
            if selections['strategy'] == 'panels':
                # Temporarily disabled for initial GitHub deployment
                # Run the panel-based approach
                # return run_with_panel(
                #     query=selections['query'],
                #     panel_type=selections['panel'],
                #     llm_provider=selections['llm_provider'],
                #     api_key=selections['api_key'],
                #     model=selections['model'],
                #     output_dir=args.output_dir,
                #     output_file=args.output_file,
                #     verbose=args.verbose,
                #     verbose_output=args.show_agent_details
                # )
                visualizer.display_error("Panel-based approach is temporarily disabled")
                return 1
            elif selections['strategy'] == 'strat-custom':
                # Run the custom strategic advisor
                advisor = StrategicAdvisorCustom(
                    llm_provider=selections['llm_provider'],
                    api_key=selections['api_key'],
                    model=selections['model'],
                    output_dir=None,  # Use default
                    verbose=False,
                    verbose_output=False
                )
                
                # Create and link an LLM component for the advisor
                from iterative_research_tool.core.llm_component import LLMComponent
                llm_component = LLMComponent(
                    provider=selections['llm_provider'],
                    api_key=selections['api_key'],
                    model=selections['model']
                )
                advisor.link_llm_component(llm_component)
                
                # Generate the strategic advice
                visualizer.display_message("Generating strategic advice...")
                advice = advisor.generate_advice(selections['query'])
                
                # Display the results
                visualizer.display_success("Strategic advice generated (Custom Architecture)")
                
                # Display a summary of the advice
                display_strategic_advice(advice)
                
                # Save to file if requested
                if args.output_file:
                    save_output_to_file(args.output_file, advice)
                
                return 0
            elif selections['strategy'] == 'strat-swarm':
                # Run the swarm strategic advisor
                advisor = StrategicAdvisorSwarm(
                    llm_provider=selections['llm_provider'],
                    api_key=selections['api_key'],
                    model=selections['model'],
                    output_dir=None,  # Use default
                    verbose=False,
                    verbose_output=False
                )
                
                # Create and link an LLM component for the advisor
                from iterative_research_tool.core.llm_component import LLMComponent
                llm_component = LLMComponent(
                    provider=selections['llm_provider'],
                    api_key=selections['api_key'],
                    model=selections['model']
                )
                advisor.link_llm_component(llm_component)
                
                # Generate the strategic advice
                visualizer.display_message("Generating strategic advice...")
                advice = advisor.generate_advice(selections['query'])
                
                # Display the results
                visualizer.display_success("Strategic advice generated (Swarm Architecture)")
                
                # Display a summary of the advice
                display_strategic_advice(advice)
                
                # Save to file if requested
                if args.output_file:
                    save_output_to_file(args.output_file, advice)
                
                return 0
            else:
                visualizer.display_error(f"Unknown strategy: {selections['strategy']}")
                return 1
                
        except KeyboardInterrupt:
            visualizer.display_message("\nOperation cancelled by user.")
            return 1
        except Exception as e:
            visualizer.display_error(f"Error running interactive UI: {e}")
            logger.exception("Error running interactive UI")
            return 1
    
    # List available panels if requested (only applies to panel-based approach)
    if args.list_panels and args.command is None:
        # Temporarily disabled for initial GitHub deployment
        # available_panels = panel_factory.list_available_panels()
        # if available_panels:
        #     visualizer.display_message("Available panels:")
        #     for panel in available_panels:
        #         visualizer.display_message(f"- {panel}")
        # else:
        #     visualizer.display_message("No panels available")
        visualizer.display_message("Panel functionality is temporarily disabled")
        return 0
    
    # Show panel info if requested (only applies to panel-based approach)
    if args.panel_info and args.command is None:
        # Temporarily disabled for initial GitHub deployment
        # try:
        #     panel_info = panel_factory.get_panel_info(args.panel_info)
        #     visualizer.display_message(f"Panel: {panel_info['name']}")
        #     visualizer.display_message(f"Module: {panel_info['module']}")
        #     visualizer.display_message("Description:")
        #     visualizer.display_message(panel_info['docstring'])
        # except ValueError as e:
        #     visualizer.display_error(str(e))
        #     return 1
        visualizer.display_message("Panel functionality is temporarily disabled")
        return 0
        
    # Get LLM provider
    llm_provider = args.llm_provider.lower()
    
    # Install dependencies if requested
    if args.install_deps:
        if install_all_dependencies():
            visualizer.display_success("Successfully installed all dependencies")
            
            # Re-import the LLM client factory after installation
            try:
                from iterative_research_tool.core.llm_client import LLMClientFactory
            except ImportError as e:
                visualizer.display_error(f"Failed to import LLM client factory after installation: {e}")
                return 1
        else:
            visualizer.display_error("Failed to install dependencies")
        return 1
    
    # Get API key from environment
    api_key = args.api_key or os.environ.get(f"{llm_provider.upper()}_API_KEY")
    if not api_key:
        logger.error(f"No API key found for {llm_provider}. "
                    f"Please set {llm_provider.upper()}_API_KEY environment variable or use --api-key.")
        print("Error: No API key found for the selected LLM provider")
        print("Please set the appropriate environment variable or use the --api-key option")
        return 1

    # Determine the output directory from args or config
    output_dir = args.output_dir
    if not output_dir:
        config = load_output_config()
        output_dir = config["output_dir"]
        if args.verbose:
            logger.info(f"Using configured output directory: {output_dir}")
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Special handling for command-line arguments
    import sys
    
    # Handle different command architectures based on the command
    try:
        if args.command == "strat-swarm":
            # Use the swarm architecture
            # Special handling for command-line arguments
            query = None
            
            # If using python -m iterative_research_tool.cli, find the query after 'strat-swarm'
            if len(sys.argv) > 2 and sys.argv[1] == "strat-swarm":
                next_arg = sys.argv[2]
                # Check if the next argument is not an option (doesn't start with -)
                if not next_arg.startswith('-'):
                    query = next_arg
            
            # If using panels command, find the query after 'strat-swarm'
            panels_index = -1
            strat_swarm_index = -1
            for i, arg in enumerate(sys.argv):
                if arg.endswith('panels'):
                    panels_index = i
                if arg == 'strat-swarm':
                    strat_swarm_index = i
            
            if panels_index >= 0 and strat_swarm_index >= 0 and len(sys.argv) > strat_swarm_index + 1:
                next_arg = sys.argv[strat_swarm_index + 1]
                # Check if the next argument is not an option (doesn't start with -)
                if not next_arg.startswith('-'):
                    query = next_arg
            
            # Use args.query as fallback if it exists
            if hasattr(args, 'query') and args.query and query is None:
                query = args.query
            
            if not query:
                visualizer.display_error("No query provided for strat-swarm command")
                return 1
    
            visualizer.display_message(f"Running Strategic Advisor (Swarm Architecture) with query: {query}")
            
            # Initialize the swarm advisor
            advisor = StrategicAdvisorSwarm(
                llm_provider=llm_provider,
                api_key=api_key,
                model=args.model,
                output_dir=output_dir,
                verbose=args.verbose,
                verbose_output=args.show_agent_details
            )
            
            # Generate the strategic advice using the correct method
            visualizer.display_message("Generating strategic advice...")
            advice = advisor.generate_advice(query)
            
            # Display the results
            visualizer.display_success("Strategic advice generated (Swarm Architecture)")
            
            # Display a summary of the advice
            display_strategic_advice(advice)
            
            # Save to file if requested
            if args.output_file:
                try:
                    with open(args.output_file, "w") as f:
                        json.dump(advice, f, indent=2)
                    visualizer.display_success(f"Advice saved to {args.output_file}")
                except Exception as e:
                    logger.error(f"Error saving advice to file: {e}")
                    visualizer.display_error(f"Error saving advice to file: {e}")
                    return 1
            
            return 0
            
        elif args.command == "strat-custom":
            # Use the custom architecture
            # Special handling for command-line arguments
            query = None
            
            # First check if we have a query from the argparse
            if hasattr(args, 'query') and args.query:
                query = args.query
            
            # Manual parsing based on position in argv
            for i, arg in enumerate(sys.argv):
                if arg == 'strat-custom' and i + 1 < len(sys.argv):
                    next_arg = sys.argv[i + 1]
                    if not next_arg.startswith('-'):
                        query = next_arg
            
            if not query:
                visualizer.display_error("No query provided for strat-custom command")
                return 1
            
            visualizer.display_message(f"Running Strategic Advisor (Custom Architecture) with query: {query}")
            
            # Set up logging to a file for cleaner UI
            setup_file_logging()
            
            # Initialize the strategic advisor
            advisor = StrategicAdvisorCustom(
                llm_provider=llm_provider,
                api_key=api_key,
                model=args.model,
                output_dir=output_dir,
                verbose=args.verbose,
                verbose_output=args.show_agent_details
            )
            
            # Create LLM component for the advisor
            from iterative_research_tool.core.llm_component import LLMComponent
            llm_component = LLMComponent(
                provider=llm_provider,
                api_key=api_key,
                model=args.model
            )
            
            # Link the LLM component to the advisor
            advisor.link_llm_component(llm_component)
            
            # Generate the strategic advice using the correct method
            visualizer.display_message("Generating strategic advice...")
            advice = advisor.generate_advice(query)
            
            # Display the results
            visualizer.display_success("Strategic advice generated (Custom Architecture)")
            
            # Display a summary of the advice
            display_strategic_advice(advice)
            
            # Save to file if requested
            if args.output_file:
                try:
                    with open(args.output_file, "w") as f:
                        json.dump(advice, f, indent=2)
                    visualizer.display_success(f"Advice saved to {args.output_file}")
                except Exception as e:
                    logger.error(f"Error saving advice to file: {e}")
                    visualizer.display_error(f"Error saving advice to file: {e}")
                    return 1
            
            return 0
        
        else:
            # Default command - use panels (original approach)
            # Create strategic planner
            # If panel type is not specified, use the first available panel
            panel_type = args.panel
            if not panel_type:
                available_panels = panel_factory.list_available_panels()
                if available_panels:
                    panel_type = available_panels[0]
                    logger.info(f"No panel specified, using default: {panel_type}")
                else:
                    visualizer.display_error("No panels available")
                    return 1
        
            planner = StrategicPlanner(
                llm_provider=llm_provider,
                api_key=api_key,
                model=args.model,
                memory_file=args.memory_file,
                output_dir=output_dir,
                panel_type=panel_type,
                custom_panel_paths=custom_panel_paths,
                verbose=args.verbose
            )
            
            # Handle time travel
            if args.time_travel:
                if not planner.time_travel_to(args.time_travel):
                    visualizer.display_error(f"Could not travel to checkpoint: {args.time_travel}")
                    return 1
                return 0
    
            # Handle alternative exploration
            if args.alternative:
                plan = planner.explore_alternative(args.alternative)
                
                # Save to file if requested
                if args.output_file:
                    try:
                        with open(args.output_file, "w") as f:
                            json.dump(plan, f, indent=2)
                        visualizer.display_success(f"Alternative plan saved to {args.output_file}")
                    except Exception as e:
                        logger.error(f"Error saving plan to file: {e}")
                        visualizer.display_error(f"Error saving plan to file: {e}")
                        return 1
                return 0

            # Handle regular planning
            if args.query:
                # Generate plan
                plan = planner.generate_strategic_plan(args.query)
                
                # Display the plan in a pretty format
                if isinstance(plan, dict):
                    display_panel_output(plan)
                
                # Collect feedback if enabled
                if args.collect_feedback:
                    feedback = planner.collect_feedback()
                    logger.info(f"Feedback collected: {feedback}")
                
                # Save to file if requested
                if args.output_file:
                    try:
                        with open(args.output_file, "w") as f:
                            json.dump(plan, f, indent=2)
                        visualizer.display_success(f"Plan saved to {args.output_file}")
                    except Exception as e:
                        logger.error(f"Error saving plan to file: {e}")
                        visualizer.display_error(f"Error saving plan to file: {e}")
                    return 1
            else:
                # If no query and no other command, use a default query for testing
                if not args.list_panels and not args.panel_info and not args.show_checkpoints:
                    default_query = "How do i get more connected to the masjid? I feel like i've been distant and want practical steps"
                    visualizer.display_message(f"Using default query: {default_query}")
                    plan = planner.generate_strategic_plan(default_query)
                    return 0
                else:
                    # If no query but other commands were specified, show help
                    visualizer.display_error("No query provided")
                    parser.print_help()
                    return 1
                
    except ImportError as e:
        visualizer.display_error(f"Missing dependencies: {e}")
        
        # Ask if the user wants to install the missing dependencies
        if not args.install_deps:  # Only prompt if --install-deps wasn't already used
            visualizer.display_message("\nWould you like to install the missing dependencies? (y/n)")
            response = input().lower()
            
            if response.startswith('y'):
                # Install dependencies for the specific provider
                if install_dependencies(llm_provider) or install_all_dependencies():
                    visualizer.display_success("Dependencies installed successfully. Please run your command again.")
                else:
                    visualizer.display_error("Failed to install dependencies")
        else:
            visualizer.display_message("You can install the dependencies manually with:")
            visualizer.display_message(f"  pip install -e .[{llm_provider}]")
            visualizer.display_message("Or install all provider dependencies with:")
            visualizer.display_message("  pip install -e .[all]")
        
        return 1
    except ValueError as e:
        visualizer.display_error(f"Error initializing: {e}")
        return 1
        
    return 0


def display_strategic_advice(advice):
    """Display a summary of strategic advice."""
    visualizer = Visualizer()
    
    # Clean header with single line
    visualizer.display_message("=" * 80)
    visualizer.display_message(f"{Fore.CYAN}{Style.BRIGHT}STRATEGIC ADVICE SUMMARY{Style.RESET_ALL}")
    visualizer.display_message("=" * 80)
    
    # Helper function to clean markdown formatting
    def clean_markdown(text):
        if not text:
            return ""
        # Remove markdown formatting
        text = re.sub(r'##+\s+', '', text)  # Remove all heading levels
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)  # Remove italic
        # Clean up extra whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)  # Replace 3+ newlines with 2
        return text.strip()
    
    # Custom display method for advice sections that doesn't use the emoji
    def display_advice_section(title, content, color=Fore.WHITE):
        print(f"{color}{Style.BRIGHT}{title}:{Style.RESET_ALL}")
        
        if isinstance(content, list) and content:
            for i, item in enumerate(content, 1):
                print(f"{color}{i}.{Style.RESET_ALL} {Fore.WHITE}{clean_markdown(item)}{Style.RESET_ALL}")
        else:
            content_text = clean_markdown(str(content)) if content else ""
            if content_text:
                for line in content_text.split('\n'):
                    if line.strip():
                        print(f"{Fore.WHITE}{line}{Style.RESET_ALL}")
    
    # Display hard truth if present
    if "hard_truth" in advice and advice["hard_truth"]:
        display_advice_section("HARD TRUTH", advice["hard_truth"], Fore.YELLOW)
    
    # Display actionable steps if present
    if "actions" in advice and advice["actions"]:
        display_advice_section("ACTIONABLE STEPS", advice["actions"], Fore.GREEN)
    
    # Display strategic challenge if present        
    if "challenge" in advice and advice["challenge"]:
        if isinstance(advice["challenge"], dict):
            challenge_text = clean_markdown(advice['challenge'].get('description', str(advice['challenge'])))
        else:
            challenge_text = clean_markdown(str(advice['challenge']))
        display_advice_section("STRATEGIC CHALLENGE", challenge_text, Fore.MAGENTA)
    
    # Add the final analysis section if present       
    if "final_analysis" in advice and advice["final_analysis"]:
        display_advice_section("FINAL ANALYSIS", advice["final_analysis"], Fore.BLUE)
    
    # Display agent insights in a cleaner format
    if "original_agent_insights" in advice and advice["original_agent_insights"]:
        print(f"{Fore.CYAN}{Style.BRIGHT}AGENT INSIGHTS:{Style.RESET_ALL}")
        
        # Convert markdown list format to cleaner bullet points
        insights_text = clean_markdown(advice["original_agent_insights"])
        
        # Process agent insights by agent name
        current_agent = None
        for line in insights_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if line starts with an agent name indicator
            if ":" in line and not line.startswith("•") and not line.startswith("-"):
                # Potential agent name
                parts = line.split(":", 1)
                if len(parts[0].split()) <= 3:  # Likely an agent name if 3 or fewer words
                    current_agent = parts[0].strip()
                    print(f"{Fore.YELLOW}{Style.BRIGHT}{current_agent}:{Style.RESET_ALL}")
                    
                    # If there's content after the agent name, display it
                    if parts[1].strip():
                        print(f"{Fore.WHITE}  {parts[1].strip()}{Style.RESET_ALL}")
            elif line.startswith("-") or line.startswith("•"):
                # It's a bullet point
                point = line[1:].strip() if line.startswith("-") else line[1:].strip()
                print(f"{Fore.WHITE}  • {point}{Style.RESET_ALL}")
            else:
                # It's a regular line
                print(f"{Fore.WHITE}  {line}{Style.RESET_ALL}")
    
    # End with clean single line
    visualizer.display_message("=" * 80)

# Temporarily disabled for initial GitHub deployment
# def display_panel_output(output):
#     """Display panel output in a visually appealing format.
#     
#     Args:
#         output: Panel output (dict)
#     """
#     visualizer = Visualizer()
#     
#     visualizer.display_message("\n" + "="*80)
#     visualizer.display_message(f"{Fore.CYAN}{Style.BRIGHT}PANEL ANALYSIS RESULTS{Style.RESET_ALL}")
#     visualizer.display_message("="*80)
#     
#     # Function to recursively display nested dictionaries with formatting
#     def display_section(data, indent=0, title=None):
#         if title:
#             indentation = " " * indent
#             visualizer.display_message(f"\n{indentation}{Fore.YELLOW}{Style.BRIGHT}{title}{Style.RESET_ALL}")
#     
#         if isinstance(data, dict):
#             for key, value in data.items():
#                 if isinstance(value, (dict, list)) and value:
#                     indentation = " " * (indent + 2)
#                     visualizer.display_message(f"\n{indentation}{Fore.GREEN}{Style.BRIGHT}{key.replace('_', ' ').title()}{Style.RESET_ALL}")
#                     display_section(value, indent + 4)
#                 else:
#                     indentation = " " * (indent + 2)
#                     visualizer.display_message(f"{indentation}{Fore.GREEN}{key.replace('_', ' ').title()}: {Style.RESET_ALL}{Fore.WHITE}{value}{Style.RESET_ALL}")
#         elif isinstance(data, list):
#             for i, item in enumerate(data):
#                 if isinstance(item, dict):
#                     if len(data) > 1:
#                         indentation = " " * indent
#                         visualizer.display_message(f"\n{indentation}{Fore.BLUE}Item {i+1}:{Style.RESET_ALL}")
#                     display_section(item, indent + 2)
#                 else:
#                     indentation = " " * (indent + 2)
#                     visualizer.display_message(f"{indentation}{Fore.WHITE}• {item}{Style.RESET_ALL}")
#     
#     # Handle common panel output structures
#     if "Temporal Perspectives" in output:
#         visualizer.display_message(f"\n{Fore.MAGENTA}{Style.BRIGHT}TEMPORAL PERSPECTIVES{Style.RESET_ALL}")
#         display_section(output["Temporal Perspectives"], indent=2)
#     
#     if "Temporal Conflicts and Resolutions" in output:
#         visualizer.display_message(f"\n{Fore.MAGENTA}{Style.BRIGHT}TEMPORAL CONFLICTS AND RESOLUTIONS{Style.RESET_ALL}")
#         display_section(output["Temporal Conflicts and Resolutions"], indent=2)
#     
#     if "Temporal Roadmap" in output:
#         visualizer.display_message(f"\n{Fore.MAGENTA}{Style.BRIGHT}TEMPORAL ROADMAP{Style.RESET_ALL}")
#         display_section(output["Temporal Roadmap"], indent=2)
#     
#     if "Temporal Trade-Off Management" in output:
#         visualizer.display_message(f"\n{Fore.MAGENTA}{Style.BRIGHT}TEMPORAL TRADE-OFF MANAGEMENT{Style.RESET_ALL}")
#         display_section(output["Temporal Trade-Off Management"], indent=2)
#     
#     if "Potential Challenges and Mitigations" in output:
#         visualizer.display_message(f"\n{Fore.MAGENTA}{Style.BRIGHT}POTENTIAL CHALLENGES AND MITIGATIONS{Style.RESET_ALL}")
#         display_section(output["Potential Challenges and Mitigations"], indent=2)
#     
#     if "Success Metrics Across Time Horizons" in output:
#         visualizer.display_message(f"\n{Fore.MAGENTA}{Style.BRIGHT}SUCCESS METRICS ACROSS TIME HORIZONS{Style.RESET_ALL}")
#         display_section(output["Success Metrics Across Time Horizons"], indent=2)
#     
#     # Handle generic output structure if the panel output doesn't match the expected format
#     generic_sections = [k for k in output.keys() if k not in [
#         "Temporal Perspectives", "Temporal Conflicts and Resolutions", 
#         "Temporal Roadmap", "Temporal Trade-Off Management",
#         "Potential Challenges and Mitigations", "Success Metrics Across Time Horizons"
#     ]]
#     
#     for section in generic_sections:
#         visualizer.display_message(f"\n{Fore.MAGENTA}{Style.BRIGHT}{section.upper()}{Style.RESET_ALL}")
#         display_section(output[section], indent=2)
#     
#     visualizer.display_message("\n" + "="*80)

def save_output_to_file(output_file, data):
    """Save output data to a file."""
    visualizer = Visualizer()
    
    try:
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        visualizer.display_success(f"Output saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving output to file: {e}")
        visualizer.display_error(f"Error saving output to file: {e}")


def run_with_panel(query: str, panel_type: str, llm_provider: str, api_key: Optional[str] = None, 
                model: Optional[str] = None, output_dir: Optional[str] = None, output_file: Optional[str] = None,
                verbose: bool = False, verbose_output: bool = False) -> int:
    """Run the tool with a specific panel.
    
    NOTE: This function is temporarily disabled for the initial GitHub deployment.
    It will be re-enabled in the future.
    
    Args:
        query: The research query
        panel_type: Type of panel to use
        llm_provider: The LLM provider to use
        api_key: API key for the LLM provider (optional if set in environment)
        model: The model to use (optional)
        output_dir: Directory to save outputs to (optional)
        output_file: File to save the plan to (optional)
        verbose: Whether to enable verbose output
        verbose_output: Whether to show detailed agent processing steps
        
    Returns:
        Exit code
    """
    # Panels functionality is temporarily disabled
    visualizer = Visualizer()
    visualizer.display_error("Panel-based approach is temporarily disabled")
    return 1


def run_interactive_main():
    """Entry point for the interactive CLI.
    
    This function is called when the user types 'panelsui' in the terminal.
    It provides a direct way to launch the interactive CLI without having to
    specify command line arguments.
    
    Returns:
        Exit code
    """
    try:
        # Load environment variables
        load_dotenv()
        
        # Set up logging to a file for cleaner UI
        setup_file_logging()
        
        # Create visualizer
        visualizer = Visualizer()
        
        # Make sure panel factory is initialized
        # Temporarily disabled for initial GitHub deployment
        # panel_factory.discover_panels(verbose=False)
        
        # Check if interactive CLI is available
        if run_interactive_cli is None:
            visualizer.display_error(f"Failed to import interactive CLI: {INTERACTIVE_CLI_IMPORT_ERROR}")
            return 1
        
        try:
            # Run the interactive CLI
            selections = run_interactive_cli()
            
            # Process the selections
            if selections['strategy'] == 'panels':
                # Temporarily disabled for initial GitHub deployment
                # Run the panel-based approach
                # return run_with_panel(
                #     query=selections['query'],
                #     panel_type=selections['panel'],
                #     llm_provider=selections['llm_provider'],
                #     api_key=selections['api_key'],
                #     model=selections['model'],
                #     output_dir=None,  # Use default
                #     output_file=None,  # Don't save to file by default
                #     verbose=False,
                #     verbose_output=False
                # )
                visualizer.display_error("Panel-based approach is temporarily disabled")
                return 1
            elif selections['strategy'] == 'strat-custom':
                # Run the custom strategic advisor
                
                # Set up logging to a file for cleaner UI
                setup_file_logging()
                
                advisor = StrategicAdvisorCustom(
                    llm_provider=selections['llm_provider'],
                    api_key=selections['api_key'],
                    model=selections['model'],
                    output_dir=None,  # Use default
                    verbose=False,
                    verbose_output=False
                )
                
                # Create and link an LLM component for the advisor
                from iterative_research_tool.core.llm_component import LLMComponent
                llm_component = LLMComponent(
                    provider=selections['llm_provider'],
                    api_key=selections['api_key'],
                    model=selections['model']
                )
                advisor.link_llm_component(llm_component)
                
                # Generate the strategic advice
                visualizer.display_message("Generating strategic advice...")
                advice = advisor.generate_advice(selections['query'])
                
                # Display the results
                visualizer.display_success("Strategic advice generated (Custom Architecture)")
                
                # Display a summary of the advice
                display_strategic_advice(advice)
                
                return 0
            elif selections['strategy'] == 'strat-swarm':
                # Run the swarm strategic advisor
                advisor = StrategicAdvisorSwarm(
                    llm_provider=selections['llm_provider'],
                    api_key=selections['api_key'],
                    model=selections['model'],
                    output_dir=None,  # Use default
                    verbose=False,
                    verbose_output=False
                )
                
                # Create and link an LLM component for the advisor
                from iterative_research_tool.core.llm_component import LLMComponent
                llm_component = LLMComponent(
                    provider=selections['llm_provider'],
                    api_key=selections['api_key'],
                    model=selections['model']
                )
                advisor.link_llm_component(llm_component)
                
                # Generate the strategic advice
                visualizer.display_message("Generating strategic advice...")
                advice = advisor.generate_advice(selections['query'])
                
                # Display the results
                visualizer.display_success("Strategic advice generated (Swarm Architecture)")
                
                # Display a summary of the advice
                display_strategic_advice(advice)
                
                return 0
            else:
                visualizer.display_error(f"Unknown strategy: {selections['strategy']}")
                return 1
                
        except KeyboardInterrupt:
            visualizer.display_message("\nOperation cancelled by user.")
            return 1
        except Exception as e:
            visualizer.display_error(f"Error running interactive UI: {e}")
            logger.exception("Error running interactive UI")
            return 1
            
    except ImportError as e:
        visualizer.display_error(f"Missing dependencies: {e}")
        
        # Ask if the user wants to install the missing dependencies
        if not args.install_deps:  # Only prompt if --install-deps wasn't already used
            visualizer.display_message("\nWould you like to install the missing dependencies? (y/n)")
            response = input().lower()
            
            if response.startswith('y'):
                # Install dependencies for the specific provider
                if install_dependencies(llm_provider) or install_all_dependencies():
                    visualizer.display_success("Dependencies installed successfully. Please run your command again.")
                else:
                    visualizer.display_error("Failed to install dependencies")
        else:
            visualizer.display_message("You can install the dependencies manually with:")
            visualizer.display_message(f"  pip install -e .[{llm_provider}]")
            visualizer.display_message("Or install all provider dependencies with:")
            visualizer.display_message("  pip install -e .[all]")
        
        return 1
    except ValueError as e:
        visualizer.display_error(f"Error initializing: {e}")
        return 1
        
    return 0

def setup_file_logging():
    """Configure logging to redirect to a file instead of the console."""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.expanduser("~/iterative_research_tool_logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create a log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_dir, f"iterative_research_tool_{timestamp}.log")
    
    # Configure the root logger to write to the file
    root_logger = logging.getLogger()
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set up file handler
    file_handler = logging.FileHandler(log_file)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Add the file handler to the root logger
    root_logger.addHandler(file_handler)
    
    # Explicitly disable console output for certain modules
    for module in [
        'httpx', 
        'iterative_research_tool.strategic_advisor.swarm',
        'iterative_research_tool.core.llm_component',
        'iterative_research_tool.core.llm_client'
    ]:
        module_logger = logging.getLogger(module)
        module_logger.propagate = False  # Don't propagate to root logger's console handler
        module_logger.addHandler(file_handler)
    
    # Only show warnings and higher for httpx
    logging.getLogger('httpx').setLevel(logging.WARNING)
    
    return log_file


if __name__ == "__main__":
    sys.exit(main()) 

def _remove_debug_messages(text):
    """Remove debug and log messages from text output.
    
    Args:
        text: The text to clean
        
    Returns:
        Clean text without debug messages
    """
    # Define patterns for common debug messages
    debug_patterns = [
        r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - [\w\.]+ - (DEBUG|INFO|WARNING|ERROR) - .*?\n',
        r'HTTP Request:.*?"HTTP.*?".*?\n',
        r'Successfully ran panel.*?\n',
        r'🚀 RUNNING .*?\n',
        r'==+\n',
        r'🔄 HANDOFF:.*?\n',
        r'🤖 PROCESSING WITH AGENT:.*?\n',
        r'📣 RESPONSE FROM.*?\n',
        r'✅ FINAL RESPONSE GENERATED\n',
        r'Response saved to .*?\n',
        r'DEBUG:.*?\n',
        r'🚀 INITIALIZING.*?\n',
        r'🔍 DIAGNOSTIC PHASE.*?\n',
        r'🧠 BELIEF SYSTEM ANALYZER.*?\n',
        r'🔄 PATTERN RECOGNITION AGENT.*?\n',
        r'🌱 ROOT CAUSE DIAGNOSTICIAN.*?\n',
        r'📝 STRATEGY PLANNER.*?\n',
        r'⚙️ EXECUTION ENGINEER.*?\n',
        r'🔀 DECISION FRAMEWORK DESIGNER.*?\n',
        r'💎 HARD TRUTH TELLER.*?\n',
        r'🚀 ACTION DESIGNER.*?\n',
        r'🏆 CHALLENGE DESIGNER.*?\n',
        r'📊 FINAL SYNTHESIS PHASE.*?\n',
        r'^\s*Processing response...\s*\n',
        r'^\s*\n',  # Remove empty lines
    ]
    
    # Apply all patterns
    for pattern in debug_patterns:
        text = re.sub(pattern, '', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text 