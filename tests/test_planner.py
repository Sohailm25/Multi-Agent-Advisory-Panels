#!/usr/bin/env python3
"""Test script for the multi-agent advisory planner."""

import os
import sys
import json
from dotenv import load_dotenv

from iterative_research_tool.strategic_planner import StrategicPlanner
from iterative_research_tool.core.visualization import Visualizer

def main():
    """Run a test of the multi-agent advisory planner."""
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it in your .env file or environment")
        return 1
    
    # Create visualizer
    visualizer = Visualizer()
    
    # Create strategic planner with cognitive diversity panel
    planner = StrategicPlanner(
        anthropic_api_key=anthropic_api_key,
        panel_type="cognitive-diversity",
        verbose=True
    )
    
    # Run the planner with a test query
    query = "What strategic approach should I take for expanding my business internationally?"
    
    visualizer.display_message("Running test with query:")
    visualizer.display_query(query)
    
    # Generate plan
    plan = planner.plan(query)
    
    # Save the plan to a file
    with open("test_plan.json", "w") as f:
        json.dump(plan, f, indent=2)
    
    visualizer.display_success("Test completed successfully!")
    visualizer.display_message("Plan saved to test_plan.json")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 