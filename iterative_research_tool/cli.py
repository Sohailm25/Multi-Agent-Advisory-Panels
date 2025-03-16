"""Command-line interface for the Iterative Research Tool."""

import os
import sys
import argparse
import logging
import tempfile
import json
from pathlib import Path
from typing import Optional, Tuple, List
from dotenv import load_dotenv

from iterative_research_tool.core.config import ConfigManager, ToolConfig
from iterative_research_tool.core.logging_utils import setup_logging, ProgressLogger
from iterative_research_tool.core.research import IterativeResearchTool, CostLimitExceededError
from iterative_research_tool.core.strategic_planner import StrategicPlanner
from iterative_research_tool.core.user_memory import UserMemory
from iterative_research_tool.core.visualization import Visualizer
from iterative_research_tool.core.panel_factory import panel_factory
from iterative_research_tool.core.llm_client import LLMClientFactory

# Anthropic imports
from anthropic import Anthropic

# Import the Strategic Advisor implementations
from iterative_research_tool.strategic_advisor import StrategicAdvisorCustom, StrategicAdvisorSwarm

logger = logging.getLogger(__name__)


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
    
    # Create LLM provider option group
    llm_group = main_parser.add_argument_group('LLM provider options')
    llm_group.add_argument('--llm-provider', default='openai', help='LLM provider to use')
    llm_group.add_argument('--api-key', help='API key for the LLM provider')
    
    # Add LLM provider options to strategic advisor parsers as well
    for subparser in [strat_custom_parser, strat_swarm_parser]:
        llm_group = subparser.add_argument_group('LLM provider options')
        llm_group.add_argument('--llm-provider', default='openai', help='LLM provider to use')
        llm_group.add_argument('--api-key', help='API key for the LLM provider')
        llm_group.add_argument('--model', help='Model to use')
    
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
    
    # Debug: Print all args
    print("DEBUG - All arguments:")
    for arg in vars(args):
        print(f"  {arg}: {getattr(args, arg)}")
    
    # Set up logging
    setup_logging(args.verbose, "iterative_research_tool.log")
    
    # Get API key from environment
    llm_provider = args.llm_provider.lower()
    api_key = args.api_key or os.environ.get(f"{llm_provider.upper()}_API_KEY")
    if not api_key:
        logger.error(f"No API key found for {llm_provider}. "
                    f"Please set {llm_provider.upper()}_API_KEY environment variable or use --api-key.")
        print("Error: No API key found for the selected LLM provider")
        print("Please set the appropriate environment variable or use the --api-key option")
        return 1
    
    # Create visualizer
    visualizer = Visualizer()
    
    # Handle strategic advisor commands
    if args.command == 'strat-custom':
        # Use the provided query if available, otherwise use the default test query
        query = args.query if args.query else "How do i get more connected to the masjid? I feel like i've been distant and want practical steps"
        print(f"DEBUG - Using query: {query}")
        
        try:
            advisor = StrategicAdvisorCustom(
                llm_provider=llm_provider,
                api_key=api_key,
                model=args.model,
                output_dir=args.output_dir,
                verbose=args.verbose
            )
            
            response = advisor.generate_advice(query)
            
            # Display the response
            visualizer.display_message("\n🧠 STRATEGIC ADVISOR (CUSTOM ARCHITECTURE)")
            visualizer.display_message("\n📢 HARD TRUTH:")
            visualizer.display_message(response.get("hard_truth", "No hard truth provided"))
            
            if "actions" in response and response["actions"]:
                visualizer.display_message("\n🛠️ ACTIONABLE STEPS:")
                for i, action in enumerate(response["actions"], 1):
                    visualizer.display_message(f"{i}. {action}")
            
            if "challenge" in response and response["challenge"]:
                visualizer.display_message("\n🔥 CHALLENGE:")
                challenge = response["challenge"]
                visualizer.display_message(challenge.get("name", "Strategic Challenge"))
                visualizer.display_message(challenge.get("description", ""))
            
            # Save to file if requested
            if args.output_file:
                try:
                    with open(args.output_file, "w") as f:
                        json.dump(response, f, indent=2)
                    visualizer.display_success(f"Strategic advice saved to {args.output_file}")
                except Exception as e:
                    logger.error(f"Error saving advice to file: {e}")
                    visualizer.display_error(f"Error saving advice to file: {e}")
                    return 1
            
            return 0
            
        except Exception as e:
            visualizer.display_error(f"Error generating strategic advice: {e}")
            return 1
    
    elif args.command == 'strat-swarm':
        # Use the provided query if available, otherwise use the default test query
        query = args.query if args.query else "How do i get more connected to the masjid? I feel like i've been distant and want practical steps"
        print(f"DEBUG - Using query: {query}")
        
        try:
            advisor = StrategicAdvisorSwarm(
                llm_provider=llm_provider,
                api_key=api_key,
                model=args.model,
                output_dir=args.output_dir,
                verbose=args.verbose
            )
            
            response = advisor.generate_advice(query)
            
            # Display the response
            visualizer.display_message("\n🧠 STRATEGIC ADVISOR (SWARM ARCHITECTURE)")
            visualizer.display_message("\n📢 HARD TRUTH:")
            visualizer.display_message(response.get("hard_truth", "No hard truth provided"))
            
            if "actions" in response and response["actions"]:
                visualizer.display_message("\n🛠️ ACTIONABLE STEPS:")
                for i, action in enumerate(response["actions"], 1):
                    visualizer.display_message(f"{i}. {action}")
            
            if "analysis" in response:
                visualizer.display_message("\n🔍 ANALYSIS:")
                visualizer.display_message(response["analysis"])
            
            # Save to file if requested
            if args.output_file:
                try:
                    with open(args.output_file, "w") as f:
                        json.dump(response, f, indent=2)
                    visualizer.display_success(f"Strategic advice saved to {args.output_file}")
                except Exception as e:
                    logger.error(f"Error saving advice to file: {e}")
                    visualizer.display_error(f"Error saving advice to file: {e}")
                    return 1
            
            return 0
            
        except Exception as e:
            visualizer.display_error(f"Error generating strategic advice: {e}")
            return 1
    
    # Initialize panel factory with custom panel paths
    custom_panel_paths = args.custom_panel_path or []
    panel_factory.discover_panels(custom_panel_paths)
    
    # List available panels if requested
    if args.list_panels:
        available_panels = panel_factory.list_available_panels()
        if available_panels:
            visualizer.display_message("Available panels:")
            for panel in available_panels:
                visualizer.display_message(f"- {panel}")
        else:
            visualizer.display_message("No panels available")
        return 0
    
    # Show panel info if requested
    if args.panel_info:
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
    
    # Create strategic planner
    try:
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
            output_dir=args.output_dir,
            panel_type=panel_type,
            custom_panel_paths=custom_panel_paths,
            verbose=args.verbose
        )
    except ValueError as e:
        visualizer.display_error(f"Error initializing planner: {e}")
        return 1
    
    # Handle time travel
    if args.time_travel:
        if not planner.time_travel_to(args.time_travel):
            visualizer.display_error(f"Could not travel to checkpoint: {args.time_travel}")
            return 1
        return 0
        
    # Show available checkpoints
    if args.show_checkpoints:
        checkpoints = planner.get_available_checkpoints()
        if checkpoints:
            visualizer.display_message("Available checkpoints:")
            for checkpoint in checkpoints:
                visualizer.display_message(f"- {checkpoint}")
        else:
            visualizer.display_message("No checkpoints available")
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
        
        return 0
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
        
    return 0


if __name__ == "__main__":
    sys.exit(main()) 