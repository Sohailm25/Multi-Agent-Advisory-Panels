#!/usr/bin/env python3
"""Comprehensive test script for the multi-agent advisory planner."""

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
from iterative_research_tool.panels.cognitive_diversity import CognitiveDiversityPanel
from iterative_research_tool.panels.decision_intelligence import DecisionIntelligencePanel
from iterative_research_tool.panels.future_scenarios import FutureScenariosPanel

# Test queries for each panel type
TEST_QUERIES = {
    "cognitive-diversity": "What strategic approach should I take for expanding my business internationally?",
    "decision-intelligence": "Should I invest in new technology or optimize existing processes?",
    "future-scenarios": "How might climate change affect my supply chain over the next decade?"
}

# Alternative queries for testing time travel
ALTERNATIVE_QUERIES = {
    "cognitive-diversity": "What strategic approach should I take for expanding my business internationally with limited resources?",
    "decision-intelligence": "Should I invest in new technology or optimize existing processes given budget constraints?",
    "future-scenarios": "How might climate change and geopolitical tensions affect my supply chain over the next decade?"
}

def setup_test_environment():
    """Set up the test environment."""
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it in your .env file or environment")
        return None
    
    # Create test output directory
    test_output_dir = Path("test_output")
    test_output_dir.mkdir(exist_ok=True)
    
    return {
        "api_key": anthropic_api_key,
        "output_dir": str(test_output_dir)
    }

def test_panel(panel_type, env, visualizer, verbose=False):
    """Test a specific panel type.
    
    Args:
        panel_type: Type of panel to test
        env: Test environment
        visualizer: Visualizer instance
        verbose: Whether to print verbose output
        
    Returns:
        True if the test passed, False otherwise
    """
    visualizer.display_message(f"Testing {panel_type} panel...")
    
    try:
        # Create strategic planner
        planner = StrategicPlanner(
            anthropic_api_key=env["api_key"],
            panel_type=panel_type,
            output_dir=env["output_dir"],
            verbose=verbose
        )
        
        # Get the test query
        query = TEST_QUERIES[panel_type]
        
        visualizer.display_message(f"Running with query: {query}")
        
        # Generate plan
        start_time = time.time()
        plan = planner.plan(query)
        end_time = time.time()
        
        # Verify the plan structure
        required_keys = ["Executive Summary", "Key Insights", "Strategic Recommendations", 
                         "Implementation Steps", "Potential Challenges and Mitigations", 
                         "Success Metrics"]
        
        missing_keys = [key for key in required_keys if key not in plan]
        if missing_keys:
            visualizer.display_error(f"Plan is missing required keys: {missing_keys}")
            return False
        
        # Save the plan to a file
        output_file = os.path.join(env["output_dir"], f"{panel_type}_plan.json")
        with open(output_file, "w") as f:
            json.dump(plan, f, indent=2)
        
        visualizer.display_success(f"{panel_type} panel test passed in {end_time - start_time:.2f} seconds")
        visualizer.display_message(f"Plan saved to {output_file}")
        
        # Test time travel
        visualizer.display_message("Testing time travel...")
        
        # Get available checkpoints
        checkpoints = planner.get_available_checkpoints()
        if not checkpoints:
            visualizer.display_error("No checkpoints available")
            return False
        
        visualizer.display_message(f"Available checkpoints: {checkpoints}")
        
        # Travel to initial checkpoint
        if "initial" in checkpoints:
            initial_state = planner.time_travel_to("initial")
            if not initial_state:
                visualizer.display_error("Failed to travel to initial checkpoint")
                return False
            
            visualizer.display_success("Time travel to initial checkpoint successful")
        
        # Test alternative exploration
        visualizer.display_message("Testing alternative exploration...")
        
        alternative_query = ALTERNATIVE_QUERIES[panel_type]
        alternative_plan = planner.explore_alternative(alternative_query)
        
        # Save the alternative plan to a file
        alt_output_file = os.path.join(env["output_dir"], f"{panel_type}_alternative_plan.json")
        with open(alt_output_file, "w") as f:
            json.dump(alternative_plan, f, indent=2)
        
        visualizer.display_success("Alternative exploration test passed")
        visualizer.display_message(f"Alternative plan saved to {alt_output_file}")
        
        return True
    
    except Exception as e:
        visualizer.display_error(f"Error testing {panel_type} panel: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_panel_instantiation(env, visualizer):
    """Test direct instantiation of panel classes.
    
    Args:
        env: Test environment
        visualizer: Visualizer instance
        
    Returns:
        True if the test passed, False otherwise
    """
    visualizer.display_message("Testing direct panel instantiation...")
    
    try:
        # Test CognitiveDiversityPanel
        cognitive_panel = CognitiveDiversityPanel(
            anthropic_api_key=env["api_key"],
            visualizer=visualizer
        )
        
        # Test DecisionIntelligencePanel
        decision_panel = DecisionIntelligencePanel(
            anthropic_api_key=env["api_key"],
            visualizer=visualizer
        )
        
        # Test FutureScenariosPanel
        future_panel = FutureScenariosPanel(
            anthropic_api_key=env["api_key"],
            visualizer=visualizer
        )
        
        # Run a simple query on each panel
        test_query = "How can I improve team collaboration?"
        test_context = "User is a team leader in a software company."
        
        visualizer.display_message("Testing CognitiveDiversityPanel.run()...")
        cognitive_result = cognitive_panel.run(test_query, test_context)
        
        visualizer.display_message("Testing DecisionIntelligencePanel.run()...")
        decision_result = decision_panel.run(test_query, test_context)
        
        visualizer.display_message("Testing FutureScenariosPanel.run()...")
        future_result = future_panel.run(test_query, test_context)
        
        # Save the results to files
        for panel_name, result in [
            ("cognitive_direct", cognitive_result),
            ("decision_direct", decision_result),
            ("future_direct", future_result)
        ]:
            output_file = os.path.join(env["output_dir"], f"{panel_name}_result.json")
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)
            
            visualizer.display_message(f"Result saved to {output_file}")
        
        visualizer.display_success("Direct panel instantiation test passed")
        return True
    
    except Exception as e:
        visualizer.display_error(f"Error testing direct panel instantiation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_memory(env, visualizer):
    """Test user memory functionality.
    
    Args:
        env: Test environment
        visualizer: Visualizer instance
        
    Returns:
        True if the test passed, False otherwise
    """
    visualizer.display_message("Testing user memory...")
    
    try:
        # Create a test memory file
        memory_file = os.path.join(env["output_dir"], "test_memory.json")
        
        # Create strategic planner with memory file
        planner = StrategicPlanner(
            anthropic_api_key=env["api_key"],
            memory_file=memory_file,
            output_dir=env["output_dir"]
        )
        
        # Run a sequence of queries to build up memory
        queries = [
            "What's the best way to learn programming?",
            "How can I improve my public speaking skills?",
            "What strategies can help me manage a remote team effectively?"
        ]
        
        for i, query in enumerate(queries):
            visualizer.display_message(f"Running query {i+1}/{len(queries)}: {query}")
            planner.plan(query)
        
        # Verify that the memory file exists
        if not os.path.exists(memory_file):
            visualizer.display_error(f"Memory file {memory_file} does not exist")
            return False
        
        # Load the memory file and check its structure
        with open(memory_file, "r") as f:
            memory = json.load(f)
        
        required_keys = ["user_profile", "interactions", "last_updated"]
        missing_keys = [key for key in required_keys if key not in memory]
        if missing_keys:
            visualizer.display_error(f"Memory is missing required keys: {missing_keys}")
            return False
        
        # Check that interactions were recorded
        if len(memory["interactions"]) < len(queries):
            visualizer.display_error(f"Expected at least {len(queries)} interactions, but found {len(memory['interactions'])}")
            return False
        
        visualizer.display_success("User memory test passed")
        return True
    
    except Exception as e:
        visualizer.display_error(f"Error testing user memory: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the comprehensive test suite."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test the multi-agent advisory planner")
    parser.add_argument("--panel", choices=["cognitive-diversity", "decision-intelligence", "future-scenarios", "all"],
                      default="all", help="Panel type to test")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    # Set up the test environment
    env = setup_test_environment()
    if not env:
        return 1
    
    # Create visualizer
    visualizer = Visualizer()
    
    visualizer.display_welcome("Multi-Agent Advisory Planner Test Suite")
    
    # Determine which panels to test
    panels_to_test = ["cognitive-diversity", "decision-intelligence", "future-scenarios"] if args.panel == "all" else [args.panel]
    
    # Run the tests
    test_results = {}
    
    # Test direct panel instantiation
    test_results["direct_instantiation"] = test_direct_panel_instantiation(env, visualizer)
    
    # Test user memory
    test_results["user_memory"] = test_user_memory(env, visualizer)
    
    # Test each panel
    for panel_type in panels_to_test:
        test_results[panel_type] = test_panel(panel_type, env, visualizer, args.verbose)
    
    # Display summary
    visualizer.display_message("\nTest Summary:")
    all_passed = True
    for test_name, result in test_results.items():
        status = "PASSED" if result else "FAILED"
        color = Fore.GREEN if result else Fore.RED
        visualizer.display_message(f"{test_name}: {color}{status}{Style.RESET_ALL}")
        if not result:
            all_passed = False
    
    if all_passed:
        visualizer.display_success("All tests passed!")
        return 0
    else:
        visualizer.display_error("Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 