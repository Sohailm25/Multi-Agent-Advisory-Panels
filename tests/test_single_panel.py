#!/usr/bin/env python3
"""Focused test script for testing a single panel with detailed output."""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Initialize colorama
init()

from iterative_research_tool.strategic_planner import StrategicPlanner
from iterative_research_tool.core.visualization import Visualizer

def main():
    """Run a focused test on a single panel."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test a single panel with detailed output")
    parser.add_argument("--panel", "-p", 
                      choices=["cognitive-diversity", "decision-intelligence", "future-scenarios", "personal-development",
                              "stakeholder-impact", "constraint-analysis", "temporal-perspective",
                              "contrarian-challenge", "implementation-energy", "product-development"],
                      default="cognitive-diversity",
                      help="Panel type to test")
    parser.add_argument("--query", "-q", 
                      help="Custom query to test with")
    parser.add_argument("--output", "-o",
                      help="Output file for the plan (JSON)")
    parser.add_argument("--verbose", "-v", action="store_true",
                      help="Enable verbose output")
    parser.add_argument("--memory-file", "-m",
                      help="Custom memory file path")
    parser.add_argument("--output-dir", "-d",
                      help="Custom output directory")
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        print(f"{Fore.RED}Error: ANTHROPIC_API_KEY environment variable not set{Style.RESET_ALL}")
        print("Please set it in your .env file or environment")
        return 1
    
    # Create output directory if specified
    output_dir = args.output_dir
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Create visualizer
    visualizer = Visualizer()
    
    # Display welcome message
    visualizer.display_welcome(f"Testing {args.panel} Panel")
    
    # Create strategic planner
    try:
        planner = StrategicPlanner(
            anthropic_api_key=anthropic_api_key,
            panel_type=args.panel,
            memory_file=args.memory_file,
            output_dir=output_dir,
            verbose=args.verbose
        )
    except Exception as e:
        visualizer.display_error(f"Error creating strategic planner: {e}")
        return 1
    
    # Get the query
    query = args.query
    if not query:
        # Default queries for each panel type
        default_queries = {
            "cognitive-diversity": "What strategic approach should I take for expanding my business internationally?",
            "decision-intelligence": "Should I invest in new technology or optimize existing processes?",
            "future-scenarios": "How might climate change affect my supply chain over the next decade?",
            "personal-development": "How can I develop my leadership skills to become a more effective CEO?",
            "stakeholder-impact": "How will transitioning to a remote-first workplace model impact our different stakeholders?",
            "constraint-analysis": "What constraints should I consider when expanding my manufacturing business to a new geographical location?",
            "temporal-perspective": "How should I think about the implementation timeline for adopting AI in my healthcare organization?",
            "contrarian-challenge": "What could be wrong with my strategy to focus on expanding our premium product line?",
            "implementation-energy": "How can I ensure my team maintains motivation throughout our year-long product development cycle?",
            "product-development": "How should I approach creating a new software product for the healthcare market?"
        }
        query = default_queries[args.panel]
    
    visualizer.display_message(f"Running with query: {query}")
    
    # Generate plan
    try:
        start_time = time.time()
        plan = planner.plan(query)
        end_time = time.time()
        
        # Display timing information
        duration = end_time - start_time
        visualizer.display_success(f"Plan generated in {duration:.2f} seconds")
        
        # Save the plan to a file if specified
        output_file = args.output
        if output_file:
            with open(output_file, "w") as f:
                json.dump(plan, f, indent=2)
            visualizer.display_message(f"Plan saved to {output_file}")
        
        # Display plan structure
        visualizer.display_message("\nPlan Structure:")
        for key in plan.keys():
            visualizer.display_message(f"- {key}")
        
        # Collect feedback
        if visualizer.prompt_yes_no("Would you like to provide feedback on the plan?"):
            feedback = planner.collect_feedback()
            visualizer.display_message(f"Feedback collected: {json.dumps(feedback, indent=2)}")
        
        # Test time travel
        if visualizer.prompt_yes_no("Would you like to test time travel?"):
            # Get available checkpoints
            checkpoints = planner.get_available_checkpoints()
            visualizer.display_message(f"Available checkpoints: {checkpoints}")
            
            # Prompt for checkpoint
            checkpoint = visualizer.prompt_choice("Select a checkpoint to travel to:", checkpoints)
            if checkpoint:
                state = planner.time_travel_to(checkpoint)
                visualizer.display_success(f"Traveled to checkpoint: {checkpoint}")
        
        # Test alternative exploration
        if visualizer.prompt_yes_no("Would you like to test alternative exploration?"):
            alt_query = visualizer.prompt_input("Enter an alternative query:")
            if alt_query:
                visualizer.display_message(f"Exploring alternative: {alt_query}")
                alt_plan = planner.explore_alternative(alt_query)
                
                # Save the alternative plan to a file
                if output_file:
                    alt_output_file = f"{os.path.splitext(output_file)[0]}_alternative.json"
                    with open(alt_output_file, "w") as f:
                        json.dump(alt_plan, f, indent=2)
                    visualizer.display_message(f"Alternative plan saved to {alt_output_file}")
        
        return 0
    
    except Exception as e:
        visualizer.display_error(f"Error generating plan: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 