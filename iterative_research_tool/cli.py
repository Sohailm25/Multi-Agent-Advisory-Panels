"""Command-line interface for the Iterative Research Tool."""

import os
import sys
import argparse
import logging
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from dotenv import load_dotenv

from iterative_research_tool.core.config import ConfigManager, ToolConfig
from iterative_research_tool.core.logging_utils import setup_logging, ProgressLogger
from iterative_research_tool.core.research import IterativeResearchTool, CostLimitExceededError
from iterative_research_tool.core.strategic_planner import StrategicPlanner


logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Iterative Research Document Generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument(
        "--init", action="store_true",
        help="Initialize configuration file"
    )
    config_parser.add_argument(
        "--perplexity-api-key", 
        help="Perplexity API key"
    )
    config_parser.add_argument(
        "--claude-api-key", 
        help="Claude API key"
    )
    config_parser.add_argument(
        "--path",
        help="Path to config file"
    )
    
    # Research command
    research_parser = subparsers.add_parser("research", help="Generate research document")
    
    # Create a mutually exclusive group for input source
    input_group = research_parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "input_file", nargs="?", default=None,
        help="Input markdown file to enhance"
    )
    input_group.add_argument(
        "--input-text", "-x", nargs="?", const=True, default=False, metavar="TEXT",
        help="Input text directly. If no text is provided, reads from console"
    )
    
    research_parser.add_argument(
        "--output-file", "-o",
        help="Output file path (defaults to editing input file in-place)"
    )
    research_parser.add_argument(
        "--version-history-file", "-v",
        help="File to store version history in"
    )
    research_parser.add_argument(
        "--max-iterations", "-i", type=int,
        help="Maximum number of research iterations"
    )
    research_parser.add_argument(
        "--confidence-threshold", "-c", type=float,
        help="Minimum confidence score to consider content verified"
    )
    research_parser.add_argument(
        "--max-cost", "-m", type=float,
        help="Maximum cost in USD to spend on this research"
    )
    research_parser.add_argument(
        "--temperature", "-t", type=float,
        help="Temperature for model generation (0.0-1.0)"
    )
    research_parser.add_argument(
        "--verbose", action="store_true",
        help="Enable verbose output"
    )
    research_parser.add_argument(
        "--config-path",
        help="Path to config file"
    )
    research_parser.add_argument(
        "--no-version-history", action="store_true",
        help="Disable version history tracking"
    )
    research_parser.add_argument(
        "--perplexity-model", 
        help="Perplexity model to use"
    )
    research_parser.add_argument(
        "--claude-model", 
        help="Claude model to use"
    )
    # New options for prompts
    research_parser.add_argument(
        "--use-custom-prompts", action="store_true",
        help="Use custom prompts for enhanced workflow"
    )
    research_parser.add_argument(
        "--no-custom-prompts", action="store_true",
        help="Disable custom prompts for traditional workflow"
    )
    research_parser.add_argument(
        "--prompts-directory",
        help="Directory containing custom prompt files"
    )
    research_parser.add_argument(
        "--use-controller", action="store_true",
        help="Use the loop controller for termination decisions"
    )
    research_parser.add_argument(
        "--no-controller", action="store_true",
        help="Disable the loop controller"
    )
    research_parser.add_argument(
        "--min-new-info-rate", type=float,
        help="Minimum percentage of new information to continue (0-100)"
    )
    research_parser.add_argument(
        "--batch-queries", action="store_true",
        help="Run batch queries for deeper research"
    )
    research_parser.add_argument(
        "--no-batch-queries", action="store_true",
        help="Disable batch queries for deeper research"
    )
    research_parser.add_argument(
        "--max-batch-size", type=int,
        help="Maximum number of queries to run in a batch"
    )
    
    # Strategic Planner command
    planner_parser = subparsers.add_parser("strategic-planner", help="Generate a strategic research plan")
    planner_parser.add_argument(
        "query", nargs="?", default=None,
        help="Research query to plan for"
    )
    planner_parser.add_argument(
        "--input-text", "-x", nargs="?", const=True, default=False, metavar="TEXT",
        help="Input query directly. If no text is provided, reads from console"
    )
    planner_parser.add_argument(
        "--output-file", "-o",
        help="Output file path (defaults to stdout)"
    )
    planner_parser.add_argument(
        "--config-path",
        help="Path to config file"
    )
    planner_parser.add_argument(
        "--claude-model",
        help="Claude model to use for planning"
    )
    planner_parser.add_argument(
        "--prompts-directory", "-p",
        help="Directory containing prompt templates"
    )
    planner_parser.add_argument(
        "--verbose", action="store_true",
        help="Enable verbose output"
    )
    planner_parser.add_argument(
        "--no-visualize", action="store_true",
        help="Disable terminal visualization"
    )
    planner_parser.add_argument(
        "--no-feedback", action="store_true",
        help="Disable feedback collection"
    )
    planner_parser.add_argument(
        "--feedback-file",
        help="Path to the feedback file"
    )
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")
    
    return parser


def handle_config_command(args: argparse.Namespace) -> int:
    """Handle the config command.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Exit code (0 for success)
    """
    # Initialize config manager
    config_manager = ConfigManager(args.path)
    
    if args.init:
        try:
            # Try to load existing config first
            try:
                config = config_manager.load_config()
                logger.info(f"Loaded existing configuration from {config_manager.config_path}")
            except FileNotFoundError:
                # Create new config
                config = config_manager.create_default_config()
                logger.info(f"Created new configuration at {config_manager.config_path}")
            
            # Update with provided values
            if args.perplexity_api_key:
                config.api.perplexity_api_key = args.perplexity_api_key
            
            if args.claude_api_key:
                config.api.claude_api_key = args.claude_api_key
            
            # Save config
            config_manager.save_config(config)
            logger.info(f"Configuration saved to {config_manager.config_path}")
            
            return 0
        except Exception as e:
            logger.error(f"Error initializing configuration: {e}")
            return 1
    else:
        logger.error("No config operation specified. Use --init to initialize configuration.")
        return 1


def get_input_content_and_paths(args: argparse.Namespace) -> Tuple[str, Path, Optional[Path]]:
    """Get input content and determine input/output paths.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Tuple of (input_content, output_path, version_history_path)
    """
    # Check if using direct text input
    if args.input_text is not False:
        # If text was provided directly as an argument
        if isinstance(args.input_text, str):
            input_content = f"# {args.input_text}\n\n"  # Format as markdown with title
            logger.info("Using input text provided as command-line argument")
            logger.debug(f"Input text: '{args.input_text}'")
        # Otherwise, read from standard input
        else:
            print("Enter your research topic or text (Ctrl+D or Ctrl+Z on a new line to finish):")
            input_lines = []
            try:
                while True:
                    line = input()
                    input_lines.append(line)
            except EOFError:
                pass  # User finished input
            
            input_text = "\n".join(input_lines)
            input_content = f"# {input_text}\n\n"  # Format as markdown with title
        
        # Create a temporary markdown file name if output file not specified
        if not args.output_file:
            # Convert first few words to filename
            first_words = "_".join(input_content.split()[:5]).lower()
            # Clean the filename
            clean_name = "".join(c if c.isalnum() or c == "_" else "_" for c in first_words)
            output_path = Path(f"{clean_name[:50]}.md")
        else:
            output_path = Path(args.output_file)
        
    else:
        # Using input file
        input_path = Path(args.input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Read input file
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                input_content = f.read()
        except Exception as e:
            raise IOError(f"Error reading input file: {e}")
        
        # Determine output path
        output_path = Path(args.output_file) if args.output_file else input_path
    
    # Determine version history path
    if args.no_version_history:
        version_history_path = None
    else:
        if args.version_history_file:
            version_history_path = Path(args.version_history_file)
        else:
            # Create version history file in same directory as output
            output_dir = output_path.parent
            output_stem = output_path.stem
            version_history_path = output_dir / f"{output_stem}_version_history.md"
    
    return input_content, output_path, version_history_path


def handle_research_command(args: argparse.Namespace) -> int:
    """Handle the research command.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Exit code (0 for success)
    """
    # Load environment variables
    load_dotenv()
    
    try:
        # Get input content and paths
        input_content, output_path, version_history_path = get_input_content_and_paths(args)
    except (FileNotFoundError, IOError) as e:
        logger.error(str(e))
        return 1
    
    # Load configuration
    config_manager = ConfigManager(args.config_path)
    try:
        config = config_manager.load_config()
    except FileNotFoundError:
        logger.error(f"Configuration file not found. Run 'iterative-research config --init' to create one.")
        return 1
    
    # Load environment variables into config
    env_config = config_manager.load_env_config()
    if "perplexity_api_key" in env_config:
        config.api.perplexity_api_key = env_config["perplexity_api_key"]
    if "claude_api_key" in env_config:
        config.api.claude_api_key = env_config["claude_api_key"]
    if "perplexity_model" in env_config:
        config.research.perplexity_model = env_config["perplexity_model"]
    if "claude_model" in env_config:
        config.research.claude_model = env_config["claude_model"]
    if "prompts_directory" in env_config:
        config.prompts.prompts_directory = env_config["prompts_directory"]
    if "use_custom_prompts" in env_config:
        config.prompts.use_custom_prompts = env_config["use_custom_prompts"]
    
    # Override config with command line arguments
    if args.max_iterations is not None:
        config.research.max_iterations = args.max_iterations
    if args.confidence_threshold is not None:
        config.research.confidence_threshold = args.confidence_threshold
    if args.max_cost is not None:
        config.cost_limits.max_cost_per_call = args.max_cost
    if args.temperature is not None:
        config.research.temperature = args.temperature
    if args.verbose:
        config.research.verbose_output = True
    if args.no_version_history:
        config.research.track_version_history = False
    if args.perplexity_model:
        config.research.perplexity_model = args.perplexity_model
    if args.claude_model:
        config.research.claude_model = args.claude_model
    
    # New prompt workflow options
    if args.use_custom_prompts:
        config.prompts.use_custom_prompts = True
    if args.no_custom_prompts:
        config.prompts.use_custom_prompts = False
    if args.prompts_directory:
        config.prompts.prompts_directory = args.prompts_directory
    
    # Controller options
    if args.use_controller:
        config.research.use_controller_termination = True
    if args.no_controller:
        config.research.use_controller_termination = False
    if args.min_new_info_rate is not None:
        config.research.min_new_info_rate = args.min_new_info_rate
    
    # Batch queries options
    if args.batch_queries:
        config.research.batch_queries = True
    if args.no_batch_queries:
        config.research.batch_queries = False
    if args.max_batch_size is not None:
        config.research.max_batch_size = args.max_batch_size
    
    # Check for API keys
    if not config.api.perplexity_api_key or not config.api.claude_api_key:
        logger.error("API keys are missing. Please update configuration with valid API keys.")
        return 1
    
    # Run research tool
    logger.info(f"Starting research process")
    logger.info(f"Output will be written to: {output_path}")
    logger.info(f"Max iterations: {config.research.max_iterations}")
    logger.info(f"Confidence threshold: {config.research.confidence_threshold}")
    logger.info(f"Max cost: ${config.cost_limits.max_cost_per_call:.2f}")
    logger.info(f"Using custom prompts: {config.prompts.use_custom_prompts}")
    logger.info(f"Using controller termination: {config.research.use_controller_termination}")
    logger.info(f"Using batch queries: {config.research.batch_queries}")
    
    try:
        # Create research tool
        research_tool = IterativeResearchTool(config=config)
        
        # Run research cycle
        final_document, version_history = research_tool.run_full_research_cycle(input_content)
        
        # Write output file
        output_markdown = final_document.to_markdown()
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_markdown)
            logger.info(f"Enhanced document written to {output_path}")
        except Exception as e:
            logger.error(f"Error writing output file: {e}")
            return 1
        
        # Write version history if enabled
        if version_history_path and version_history:
            try:
                with open(version_history_path, 'w', encoding='utf-8') as f:
                    f.write(version_history)
                logger.info(f"Version history written to {version_history_path}")
            except Exception as e:
                logger.error(f"Error writing version history file: {e}")
                
        return 0
        
    except CostLimitExceededError as e:
        logger.error(f"Research stopped: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error running research: {e}")
        return 1


def handle_strategic_planner_command(args: argparse.Namespace) -> int:
    """Handle the strategic-planner command.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Load configuration
    config_path = args.config_path
    config_manager = ConfigManager(config_path)
    config = config_manager.load_config()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    
    # Get Claude API key
    claude_api_key = os.getenv("CLAUDE_API_KEY") or config.claude_api_key
    if not claude_api_key:
        logger.error("Claude API key not found. Please set it in the configuration or environment.")
        return 1
    
    # Get Claude model
    claude_model = args.claude_model or os.getenv("CLAUDE_MODEL") or config.claude_model
    if not claude_model:
        claude_model = "claude-3-7-sonnet-20250219"  # Default model
    
    # Get prompt directory
    prompt_dir = args.prompts_directory or os.getenv("PROMPTS_DIRECTORY") or config.prompts_directory
    
    # Get visualization and feedback options
    visualize = not args.no_visualize
    collect_feedback = not args.no_feedback
    feedback_file = args.feedback_file
    
    # Get query
    query = args.query
    if args.input_text is True:
        # Read from console
        print("Enter your research query (Ctrl+D or Ctrl+Z on a new line to finish):")
        query = sys.stdin.read().strip()
    elif args.input_text:
        # Use provided text
        query = args.input_text
    
    if not query:
        logger.error("No query provided. Please provide a query.")
        return 1
    
    try:
        # Create and run the strategic planner
        planner = StrategicPlanner(
            claude_api_key=claude_api_key, 
            claude_model=claude_model,
            prompt_dir=prompt_dir,
            visualize=visualize,
            collect_feedback=collect_feedback,
            feedback_file=feedback_file
        )
        result = planner.run(query)
        
        # Output the result
        if args.output_file:
            output_path = Path(args.output_file)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result)
            logger.info(f"Strategic plan written to {output_path}")
        else:
            print("\n" + result)
        
        return 0
    
    except Exception as e:
        logger.error(f"Error running strategic planner: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def handle_version_command(args: argparse.Namespace) -> int:
    """Handle the version command.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Exit code (0 for success)
    """
    from iterative_research_tool import __version__
    print(f"Iterative Research Tool v{__version__}")
    return 0


def main() -> int:
    """Main entry point for the CLI.
    
    Returns:
        Exit code
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Enable verbose logging if requested
    if hasattr(args, 'verbose') and args.verbose:
        logging.getLogger('iterative_research_tool').setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info("Verbose logging enabled")
    
    # Handle subcommands
    try:
        if args.command == "config":
            return handle_config_command(args)
        elif args.command == "research":
            return handle_research_command(args)
        elif args.command == "strategic-planner":
            return handle_strategic_planner_command(args)
        elif args.command == "version":
            return handle_version_command(args)
        else:
            logging.error(f"Unknown command: {args.command}")
            return 1
    except Exception as e:
        logging.error(f"Error running {args.command}: {e}")
        import traceback
        logging.debug(f"Traceback: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 