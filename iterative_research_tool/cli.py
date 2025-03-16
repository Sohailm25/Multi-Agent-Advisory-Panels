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

from iterative_research_tool.core.config import ConfigManager, ToolConfig, APIConfig
from iterative_research_tool.core.logging_utils import setup_logging, ProgressLogger
from iterative_research_tool.core.research import IterativeResearchTool, CostLimitExceededError
from iterative_research_tool.core.strategic_planner import StrategicPlanner
from iterative_research_tool.core.user_memory import UserMemory
from iterative_research_tool.core.visualization import Visualizer
from iterative_research_tool.core.panel_factory import panel_factory

# Import the strategic advisors
from iterative_research_tool.strategic_advisor import StrategicAdvisorCustom, StrategicAdvisorSwarm

# Import the interactive CLI
try:
    from iterative_research_tool.core.interactive_cli import run_interactive_cli
except ImportError as e:
    run_interactive_cli = None
    INTERACTIVE_CLI_IMPORT_ERROR = str(e)
else:
    INTERACTIVE_CLI_IMPORT_ERROR = None

# Import the LLM client factory
try:
    from iterative_research_tool.core.llm_client import LLMClientFactory
except ImportError as e:
    # This will be handled during runtime
    LLMClientFactory = None
    LLM_IMPORT_ERROR = str(e)
else:
    LLM_IMPORT_ERROR = None

# Try to import LLM provider libraries
try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

logger = logging.getLogger(__name__)


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
    panelsui_parser.add_argument('--custom-panel-path', action='append', help='Path to custom panel files or directories')
    panelsui_parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    panelsui_parser.add_argument('--show-agent-details', action='store_true', help='Show detailed agent processing steps, prompts, and responses')
    
    # Strategic advisor - custom architecture
    strat_custom_parser = subparsers.add_parser('strat-custom', help='Run strategic advisor with custom architecture')
    strat_custom_parser.add_argument('query', nargs='?', help='Query to analyze')
    strat_custom_parser.add_argument('--output-file', help='File to save the plan to')
    strat_custom_parser.add_argument('--output-dir', help='Directory to save outputs to')
    strat_custom_parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    strat_custom_parser.add_argument('--show-agent-details', action='store_true', help='Show detailed agent processing steps, prompts, and responses')
    
    # Strategic advisor - swarm architecture
    strat_swarm_parser = subparsers.add_parser('strat-swarm', help='Run strategic advisor with swarm architecture')
    strat_swarm_parser.add_argument('query', nargs='?', help='Query to analyze')
    strat_swarm_parser.add_argument('--output-file', help='File to save the plan to')
    strat_swarm_parser.add_argument('--output-dir', help='Directory to save outputs to')
    strat_swarm_parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    strat_swarm_parser.add_argument('--show-agent-details', action='store_true', help='Show detailed agent processing steps, prompts, and responses')
    
    # Add arguments for the main planner command
    main_parser.add_argument('query', nargs='?', help='Query to plan')
    
    # Add panel options
    main_parser.add_argument('--panel', help='Panel type to use')
    main_parser.add_argument('--list-panels', action='store_true', help='List available panels')
    main_parser.add_argument('--panel-info', help='Show information about a specific panel')
    main_parser.add_argument('--custom-panel-path', action='append', help='Path to custom panel files or directories')
    
    # Add time travel options
    main_parser.add_argument('--time-travel', help='Travel to a specific checkpoint')
    main_parser.add_argument('--show-checkpoints', action='store_true', help='Show available checkpoints')
    
    # Add alternatives options
    main_parser.add_argument('--alternative', help='Explore an alternative approach')
    
    # Add feedback options
    main_parser.add_argument('--collect-feedback', action='store_true', help='Collect feedback after planning')
    
    # Add output options
    main_parser.add_argument('--output-file', help='File to save the plan to')
    main_parser.add_argument('--output-dir', help='Directory to save outputs to')
    
    # Add model options
    main_parser.add_argument('--model', help='Model to use')
    main_parser.add_argument('--memory-file', help='File to use for memory')
    
    # Add verbosity options
    main_parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    main_parser.add_argument('--show-agent-details', action='store_true', help='Show detailed agent processing steps, prompts, and responses')
    
    # Create LLM provider option group
    llm_group = main_parser.add_argument_group('LLM provider options')
    llm_group.add_argument('--llm-provider', default='anthropic', help='LLM provider to use')
    llm_group.add_argument('--api-key', help='API key for the LLM provider')
    llm_group.add_argument('--install-deps', action='store_true', help='Install dependencies for the selected LLM provider')
    
    # Add LLM provider options to strategic advisor parsers as well
    for subparser in [strat_custom_parser, strat_swarm_parser]:
        llm_group = subparser.add_argument_group('LLM provider options')
        llm_group.add_argument('--llm-provider', default='anthropic', help='LLM provider to use')
        llm_group.add_argument('--api-key', help='API key for the LLM provider')
        llm_group.add_argument('--model', help='Model to use')
        llm_group.add_argument('--install-deps', action='store_true', help='Install dependencies for the selected LLM provider')
    
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
    
    # Debug: Print all arguments
    # print("DEBUG - All arguments:")
    # for arg in vars(args):
    #     print(f"  {arg}: {getattr(args, arg)}")
    
    # Additional debug for subcommands
    # if args.command:
    #     print(f"DEBUG - Using command: {args.command}")
    #     if args.command in ['strat-swarm', 'strat-custom']:
    #         print(f"DEBUG - Command: {args.command}, Query: {args.query if hasattr(args, 'query') else 'None'}")
    #         # Print the sys.argv to see what's actually being passed
    #         import sys
    #         print(f"DEBUG - sys.argv: {sys.argv}")
    
    # Set up logging
    setup_logging(args.verbose, "iterative_research_tool.log")
    
    # Create visualizer
    visualizer = Visualizer()
    
    # Initialize panel factory with custom panel paths
    custom_panel_paths = args.custom_panel_path or []
    panel_factory.discover_panels(custom_panel_paths, args.verbose)
    
    # Run the interactive UI if requested
    if args.command == "panelsui":
        if run_interactive_cli is None:
            visualizer.display_error(f"Failed to import interactive CLI: {INTERACTIVE_CLI_IMPORT_ERROR}")
            return 1
        
        try:
            # Run the interactive CLI
            selections = run_interactive_cli()
            
            # Process the selections
            if selections['strategy'] == 'panels':
                # Run the panel-based approach
                return run_with_panel(
                    query=selections['query'],
                    panel_type=selections['panel'],
                    llm_provider=selections['llm_provider'],
                    api_key=selections['api_key'],
                    model=selections['model'],
                    output_dir=args.output_dir,
                    output_file=args.output_file,
                    verbose=args.verbose,
                    verbose_output=args.show_agent_details
                )
            elif selections['strategy'] == 'strat-custom':
                # Run the custom strategic advisor
                advisor = StrategicAdvisorCustom(
                    llm_provider=selections['llm_provider'],
                    api_key=selections['api_key'],
                    model=selections['model'],
                    output_dir=args.output_dir,
                    verbose=args.verbose,
                    verbose_output=args.show_agent_details
                )
                
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
                    output_dir=args.output_dir,
                    verbose=args.verbose,
                    verbose_output=args.show_agent_details
                )
                
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
        available_panels = panel_factory.list_available_panels()
        if available_panels:
            visualizer.display_message("Available panels:")
            for panel in available_panels:
                visualizer.display_message(f"- {panel}")
        else:
            visualizer.display_message("No panels available")
        return 0
    
    # Show panel info if requested (only applies to panel-based approach)
    if args.panel_info and args.command is None:
        try:
            panel_info = panel_factory.get_panel_info(args.panel_info)
            visualizer.display_message(f"Panel: {panel_info['name']}")
            visualizer.display_message(f"Module: {panel_info['module']}")
            visualizer.display_message("Description:")
            visualizer.display_message(panel_info['docstring'])
        except ValueError as e:
            visualizer.display_error(str(e))
            return 1
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
                global LLMClientFactory
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

    # Determine the output directory
    output_dir = args.output_dir
    if not output_dir:
        output_dir = os.path.expanduser("~/iterative_research_tool_output")
    
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
            visualizer.display_message("\n" + "="*50)
            visualizer.display_message("STRATEGIC ADVICE SUMMARY:")
            
            if "hard_truth" in advice:
                visualizer.display_message("\nHARD TRUTH:")
                visualizer.display_message(advice["hard_truth"])
                
            if "actions" in advice:
                visualizer.display_message("\nACTIONABLE STEPS:")
                for i, action in enumerate(advice["actions"], 1):
                    visualizer.display_message(f"{i}. {action}")
                    
            if "challenge" in advice:
                visualizer.display_message("\nSTRATEGIC CHALLENGE:")
                if isinstance(advice["challenge"], dict):
                    visualizer.display_message(advice["challenge"].get("description", str(advice["challenge"])))
                else:
                    visualizer.display_message(str(advice["challenge"]))
                    
            visualizer.display_message("\n" + "="*50)
            
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
            
            # If using python -m iterative_research_tool.cli, find the query after 'strat-custom'
            if len(sys.argv) > 2 and sys.argv[1] == "strat-custom":
                next_arg = sys.argv[2]
                # Check if the next argument is not an option (doesn't start with -)
                if not next_arg.startswith('-'):
                    query = next_arg
            
            # If using panels command, find the query after 'strat-custom'
            panels_index = -1
            strat_custom_index = -1
            for i, arg in enumerate(sys.argv):
                if arg.endswith('panels'):
                    panels_index = i
                if arg == 'strat-custom':
                    strat_custom_index = i
            
            if panels_index >= 0 and strat_custom_index >= 0 and len(sys.argv) > strat_custom_index + 1:
                next_arg = sys.argv[strat_custom_index + 1]
                # Check if the next argument is not an option (doesn't start with -)
                if not next_arg.startswith('-'):
                    query = next_arg
            
            # Use args.query as fallback if it exists
            if hasattr(args, 'query') and args.query and query is None:
                query = args.query
            
            if not query:
                visualizer.display_error("No query provided for strat-custom command")
                return 1
            
            visualizer.display_message(f"Running Strategic Advisor (Custom Architecture) with query: {query}")
            
            # Initialize the custom advisor
            advisor = StrategicAdvisorCustom(
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
            visualizer.display_success("Strategic advice generated (Custom Architecture)")
            
            # Display a summary of the advice
            visualizer.display_message("\n" + "="*50)
            visualizer.display_message("STRATEGIC ADVICE SUMMARY:")
            
            if "hard_truth" in advice:
                visualizer.display_message("\nHARD TRUTH:")
                visualizer.display_message(advice["hard_truth"])
                
            if "actions" in advice:
                visualizer.display_message("\nACTIONABLE STEPS:")
                for i, action in enumerate(advice["actions"], 1):
                    visualizer.display_message(f"{i}. {action}")
                    
            if "challenge" in advice:
                visualizer.display_message("\nSTRATEGIC CHALLENGE:")
                if isinstance(advice["challenge"], dict):
                    visualizer.display_message(advice["challenge"].get("description", str(advice["challenge"])))
                else:
                    visualizer.display_message(str(advice["challenge"]))
                    
            visualizer.display_message("\n" + "="*50)
            
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
    
    visualizer.display_message("\n" + "="*50)
    visualizer.display_message("STRATEGIC ADVICE SUMMARY:")
    
    if "hard_truth" in advice:
        visualizer.display_message("\nHARD TRUTH:")
        visualizer.display_message(advice["hard_truth"])
        
    if "actions" in advice:
        visualizer.display_message("\nACTIONABLE STEPS:")
        for i, action in enumerate(advice["actions"], 1):
            visualizer.display_message(f"{i}. {action}")
            
    if "challenge" in advice:
        visualizer.display_message("\nSTRATEGIC CHALLENGE:")
        if isinstance(advice["challenge"], dict):
            visualizer.display_message(advice["challenge"].get("description", str(advice["challenge"])))
        else:
            visualizer.display_message(str(advice["challenge"]))
            
    visualizer.display_message("\n" + "="*50)

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
    visualizer = Visualizer()
    
    # Load environment variables and configuration
    api_key = api_key or os.environ.get(f"{llm_provider.upper()}_API_KEY")
    if not api_key:
        visualizer.display_error(f"No API key found for {llm_provider}")
        return 1
    
    # Create API config based on the provider
    if llm_provider == "anthropic":
        api_config = APIConfig(perplexity_api_key="", claude_api_key=api_key)
    elif llm_provider == "perplexity":
        api_config = APIConfig(perplexity_api_key=api_key, claude_api_key="")
    else:
        # For other providers like OpenAI, we still need to provide the APIConfig structure
        # We'll store the API key in a different way for these providers
        api_config = APIConfig(perplexity_api_key="", claude_api_key="")
    
    # Create config
    config = ToolConfig(
        api=api_config,
        llm_provider=llm_provider,
        api_key=api_key,  # This is used for non-Claude/Perplexity providers
        model=model,
        panel_type=panel_type,
        output_dir=output_dir,
        verbose=verbose,
        verbose_output=verbose_output
    )
    
    try:
        # Check if panel exists
        try:
            # Get the panel class first without creating an instance
            if panel_type not in panel_factory.panel_classes:
                visualizer.display_error(f"Unknown panel type: {panel_type}")
                return 1
                
            panel_class = panel_factory.panel_classes[panel_type]
            
            # Prepare all possible parameters
            all_params = {
                "api_key": api_key,
                "anthropic_api_key": api_key,  # Some panels use this name
                "llm_provider": llm_provider,
                "model": model,
                "visualizer": visualizer,
            }
            
            # Inspect the constructor parameters for this specific panel class
            import inspect
            panel_init_params = inspect.signature(panel_class.__init__).parameters
            
            # Filter to only include parameters that this panel's constructor accepts
            valid_params = {}
            for param_name, param in panel_init_params.items():
                if param_name == 'self':
                    continue
                if param_name in all_params:
                    valid_params[param_name] = all_params[param_name]
            
            # Create the panel with only the valid parameters
            panel = panel_factory.create_panel(panel_type, **valid_params)
        except ValueError as e:
            visualizer.display_error(str(e))
            return 1
        
        # Run the research using the panel directly
        visualizer.display_message(f"Running research with panel: {panel_type}")
        visualizer.display_message(f"Query: {query}")
        
        try:
            # Call the panel's run method with the query
            # Providing an empty context since we don't have context information here
            result = panel.run(query=query, context="")
            
            # If we get here without an exception, log success
            logger.info(f"Successfully ran panel {panel_type} with query: {query[:100]}...")
            
        except AttributeError as e:
            # This would indicate that the panel doesn't have a run method
            error_msg = f"Panel {panel_type} does not implement the required run method: {e}"
            logger.error(error_msg)
            visualizer.display_error(error_msg)
            return 1
        except TypeError as e:
            # This would indicate wrong parameters to the run method
            error_msg = f"Error calling run method on panel {panel_type}: {e}"
            logger.error(error_msg)
            visualizer.display_error(error_msg)
            return 1
        except Exception as e:
            # Any other exception during panel execution
            error_msg = f"Error running panel {panel_type}: {e}"
            logger.error(error_msg)
            visualizer.display_error(error_msg)
            logger.exception("Detailed traceback:")
            return 1
        
        # Display results
        visualizer.display_success("Research completed")
        
        # Save to file if requested
        if output_file:
            try:
                with open(output_file, "w") as f:
                    json.dump(result, f, indent=2)
                visualizer.display_success(f"Results saved to {output_file}")
            except Exception as e:
                logger.error(f"Error saving results to file: {e}")
                visualizer.display_error(f"Error saving results to file: {e}")
                return 1
        
        return 0
        
    except CostLimitExceededError as e:
        visualizer.display_error(f"Cost limit exceeded: {e}")
        return 1
    except Exception as e:
        visualizer.display_error(f"Error running research: {e}")
        logger.exception("Error running research")
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
        
        # Set up logging
        setup_logging(False, "iterative_research_tool.log")
        
        # Create visualizer
        visualizer = Visualizer()
        
        # Make sure panel factory is initialized
        panel_factory.discover_panels(verbose=False)
        
        # Check if interactive CLI is available
        if run_interactive_cli is None:
            visualizer.display_error(f"Failed to import interactive CLI: {INTERACTIVE_CLI_IMPORT_ERROR}")
            return 1
        
        try:
            # Run the interactive CLI
            selections = run_interactive_cli()
            
            # Process the selections
            if selections['strategy'] == 'panels':
                # Run the panel-based approach
                return run_with_panel(
                    query=selections['query'],
                    panel_type=selections['panel'],
                    llm_provider=selections['llm_provider'],
                    api_key=selections['api_key'],
                    model=selections['model'],
                    output_dir=None,  # Use default
                    output_file=None,  # Don't save to file by default
                    verbose=False,
                    verbose_output=False
                )
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


if __name__ == "__main__":
    sys.exit(main()) 