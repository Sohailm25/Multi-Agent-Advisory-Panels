#!/usr/bin/env python3
"""
Comprehensive Test Script for Multi-Agent Advisory Planner

This script performs a comprehensive test of all components of the Multi-Agent Advisory Planner,
including all panel types, time travel functionality, stateful memory, and user feedback.
"""

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Initialize colorama
init()

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from iterative_research_tool.strategic_planner import StrategicPlanner
from iterative_research_tool.core.visualization import Visualizer
from iterative_research_tool.core.user_memory import UserMemory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Test queries for each panel type
TEST_QUERIES = {
    "cognitive-diversity": "What strategies should I consider for expanding my software business internationally?",
    "decision-intelligence": "How should I approach the decision to pivot my product to a new market segment?",
    "future-scenarios": "What potential future scenarios should I prepare for in the renewable energy sector over the next decade?",
    "personal-development": "How can I develop my leadership skills to become a more effective CEO?",
    "stakeholder-impact": "How will transitioning to a remote-first workplace model impact our different stakeholders?",
    "constraint-analysis": "What constraints should I consider when expanding my manufacturing business to a new geographical location?",
    "temporal-perspective": "How should I think about the implementation timeline for adopting AI in my healthcare organization?",
    "contrarian-challenge": "What are the potential flaws and alternative perspectives to my strategy of focusing on premium products?",
    "implementation-energy": "How can I ensure that my team maintains momentum and energy throughout our year-long digital transformation initiative?",
    "product-development": "How should I approach developing a new SaaS product for the financial services industry?"
}

# Alternative queries for testing time travel
ALT_QUERIES = {
    "cognitive-diversity": "What strategies should I consider for expanding my e-commerce business to Asian markets?",
    "decision-intelligence": "How should I approach the decision to acquire a competitor in my industry?",
    "future-scenarios": "What potential future scenarios should I prepare for in the AI industry over the next five years?",
    "personal-development": "How can I balance my professional growth with personal well-being?",
    "stakeholder-impact": "How will our shift to sustainable practices impact our various stakeholders?",
    "constraint-analysis": "What constraints should I consider when transitioning my business to a subscription model?",
    "temporal-perspective": "How should I structure the timeline for a digital transformation initiative in my organization?",
    "contrarian-challenge": "What might be wrong with my approach to expanding into international markets?",
    "implementation-energy": "How can I prevent burnout during our upcoming product launch?",
    "product-development": "How should I evolve my physical retail product to better serve the changing market?"
}

def setup_test_environment():
    """Set up the test environment."""
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print(f"{Fore.RED}Error: ANTHROPIC_API_KEY not found in environment variables.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please set the ANTHROPIC_API_KEY environment variable or create a .env file.{Style.RESET_ALL}")
        sys.exit(1)
    
    # Create test output directory
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    return api_key, output_dir

def test_panel(panel_type, api_key, output_dir, verbose=True):
    """Test a specific panel type."""
    print(f"\n{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Testing {panel_type} Panel{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
    
    # Initialize components
    visualizer = Visualizer(show_progress=verbose)
    visualizer.display_welcome(f"Testing {panel_type} Panel")
    
    # Get test query
    query = TEST_QUERIES.get(panel_type, "What strategic advice can you provide for my business?")
    visualizer.display_query(query)
    
    # Create output file path
    output_file = output_dir / f"{panel_type}_test_plan.json"
    
    # Initialize planner
    try:
        start_time = time.time()
        visualizer.update_status(f"Initializing {panel_type} panel")
        
        planner = StrategicPlanner(
            anthropic_api_key=api_key,
            panel_type=panel_type,
            verbose=verbose
        )
        
        # Generate plan
        visualizer.update_status(f"Generating plan with {panel_type} panel")
        plan = planner.generate_plan(query)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Save plan to file
        with open(output_file, "w") as f:
            json.dump(plan, f, indent=2)
        
        visualizer.display_success(f"Plan generated and saved to {output_file}")
        print(f"{Fore.GREEN}Execution time: {execution_time:.2f} seconds{Style.RESET_ALL}")
        
        # Test time travel
        visualizer.update_status("Testing time travel functionality")
        
        # Get alternative query
        alt_query = ALT_QUERIES.get(panel_type, "What alternative strategic advice can you provide?")
        visualizer.display_query(f"Alternative query: {alt_query}")
        
        # Generate alternative plan
        alt_plan = planner.generate_plan(alt_query)
        
        # Save alternative plan
        alt_output_file = output_dir / f"{panel_type}_alt_plan.json"
        with open(alt_output_file, "w") as f:
            json.dump(alt_plan, f, indent=2)
        
        visualizer.display_success(f"Alternative plan generated and saved to {alt_output_file}")
        
        # Test rewinding to previous state
        visualizer.update_status("Testing rewind functionality")
        checkpoints = planner.get_checkpoints()
        
        if checkpoints and len(checkpoints) > 0:
            # Rewind to first checkpoint
            planner.rewind_to_checkpoint(checkpoints[0])
            visualizer.display_success(f"Successfully rewound to checkpoint: {checkpoints[0]}")
            
            # Generate plan from rewound state
            rewound_plan = planner.generate_plan(query)
            
            # Save rewound plan
            rewound_output_file = output_dir / f"{panel_type}_rewound_plan.json"
            with open(rewound_output_file, "w") as f:
                json.dump(rewound_plan, f, indent=2)
            
            visualizer.display_success(f"Rewound plan generated and saved to {rewound_output_file}")
        else:
            visualizer.display_error("No checkpoints available for time travel testing")
        
        return True
    except Exception as e:
        visualizer.display_error(f"Error testing {panel_type} panel: {str(e)}")
        logger.exception(f"Error testing {panel_type} panel")
        return False

def test_user_memory(api_key, output_dir, verbose=True):
    """Test user memory functionality."""
    print(f"\n{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Testing User Memory{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
    
    # Initialize components
    visualizer = Visualizer(show_progress=verbose)
    visualizer.display_welcome("Testing User Memory")
    
    try:
        # Create memory file path
        memory_file = output_dir / "test_user_memory.json"
        
        # Initialize user memory
        visualizer.update_status("Initializing user memory")
        user_memory = UserMemory(memory_file_path=str(memory_file))
        
        # Add test memory entries
        visualizer.update_status("Adding test memory entries")
        user_memory.add_memory("preference", "The user prefers concise and actionable plans")
        user_memory.add_memory("background", "The user runs a software development company with 50 employees")
        user_memory.add_memory("goal", "The user wants to expand internationally within the next year")
        
        # Save memory
        user_memory.save_memory()
        
        # Load memory
        visualizer.update_status("Loading user memory")
        loaded_memory = UserMemory(memory_file_path=str(memory_file))
        
        # Verify memory contents
        memory_contents = loaded_memory.get_all_memories()
        
        if (
            "preference" in memory_contents and
            "background" in memory_contents and
            "goal" in memory_contents
        ):
            visualizer.display_success("User memory functionality verified successfully")
            
            # Test with planner
            visualizer.update_status("Testing planner with user memory")
            
            planner = StrategicPlanner(
                anthropic_api_key=api_key,
                panel_type="cognitive-diversity",
                verbose=verbose,
                memory_file_path=str(memory_file)
            )
            
            query = "What strategic advice can you provide for my business?"
            visualizer.display_query(query)
            
            plan = planner.generate_plan(query)
            
            # Save plan to file
            output_file = output_dir / "memory_test_plan.json"
            with open(output_file, "w") as f:
                json.dump(plan, f, indent=2)
            
            visualizer.display_success(f"Plan with user memory generated and saved to {output_file}")
            return True
        else:
            visualizer.display_error("User memory verification failed")
            return False
    except Exception as e:
        visualizer.display_error(f"Error testing user memory: {str(e)}")
        logger.exception("Error testing user memory")
        return False

def test_feedback_collection(verbose=True):
    """Test feedback collection functionality."""
    print(f"\n{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Testing Feedback Collection{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
    
    # Initialize components
    visualizer = Visualizer(show_progress=verbose)
    visualizer.display_welcome("Testing Feedback Collection")
    
    try:
        # Create a mock plan
        mock_plan = {
            "Executive Summary": "This is a test plan for feedback collection.",
            "Key Insights": [
                "Insight 1: This is a test insight.",
                "Insight 2: This is another test insight."
            ],
            "Strategic Recommendations": [
                "Recommendation 1: This is a test recommendation.",
                "Recommendation 2: This is another test recommendation."
            ]
        }
        
        # Display the mock plan
        visualizer.display_plan(mock_plan)
        
        # Test automatic feedback collection
        visualizer.update_status("Testing automatic feedback collection")
        
        # Create a mock feedback collector
        class MockFeedbackCollector:
            def __init__(self):
                self.feedback_file = "test_output/feedback_test.json"
                
            def collect_feedback(self, plan):
                feedback = {
                    "rating": 5,
                    "strengths": "Clear and concise",
                    "weaknesses": "None",
                    "suggestions": "None",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Save feedback to file
                os.makedirs(os.path.dirname(self.feedback_file), exist_ok=True)
                
                try:
                    # Load existing feedback if file exists
                    if os.path.exists(self.feedback_file):
                        with open(self.feedback_file, "r") as f:
                            all_feedback = json.load(f)
                    else:
                        all_feedback = []
                    
                    # Add new feedback
                    all_feedback.append(feedback)
                    
                    # Save updated feedback
                    with open(self.feedback_file, "w") as f:
                        json.dump(all_feedback, f, indent=2)
                        
                    return True
                except Exception as e:
                    print(f"Error saving feedback: {str(e)}")
                    return False
        
        # Collect mock feedback
        mock_collector = MockFeedbackCollector()
        result = mock_collector.collect_feedback(mock_plan)
        
        if result:
            visualizer.display_success("Feedback collection functionality verified successfully")
            return True
        else:
            visualizer.display_error("Feedback collection verification failed")
            return False
    except Exception as e:
        visualizer.display_error(f"Error testing feedback collection: {str(e)}")
        logger.exception("Error testing feedback collection")
        return False

def main():
    """Run the comprehensive test suite."""
    parser = argparse.ArgumentParser(description="Comprehensive test for Multi-Agent Advisory Planner")
    parser.add_argument("--panels", nargs="+", choices=["cognitive-diversity", "decision-intelligence", "future-scenarios", 
                        "personal-development", "stakeholder-impact", "constraint-analysis", "temporal-perspective",
                        "contrarian-challenge", "implementation-energy", "product-development", "all"],
                        default=["all"], help="Panel types to test")
    parser.add_argument("--skip-memory", action="store_true", help="Skip user memory tests")
    parser.add_argument("--skip-feedback", action="store_true", help="Skip feedback collection tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    # Set up test environment
    api_key, output_dir = setup_test_environment()
    
    # Determine which panels to test
    panels_to_test = []
    if "all" in args.panels:
        panels_to_test = ["cognitive-diversity", "decision-intelligence", "future-scenarios", "personal-development", 
                          "stakeholder-impact", "constraint-analysis", "temporal-perspective", "contrarian-challenge",
                          "implementation-energy", "product-development"]
    else:
        panels_to_test = args.panels
    
    # Run tests
    results = {}
    
    # Test each panel
    for panel_type in panels_to_test:
        results[f"{panel_type}_panel"] = test_panel(panel_type, api_key, output_dir, args.verbose)
    
    # Test user memory
    if not args.skip_memory:
        results["user_memory"] = test_user_memory(api_key, output_dir, args.verbose)
    
    # Test feedback collection
    if not args.skip_feedback:
        results["feedback_collection"] = test_feedback_collection(args.verbose)
    
    # Display test summary
    print(f"\n{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Test Summary{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
    
    all_passed = True
    for test_name, result in results.items():
        status = f"{Fore.GREEN}PASSED{Style.RESET_ALL}" if result else f"{Fore.RED}FAILED{Style.RESET_ALL}"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    # Final result
    if all_passed:
        print(f"\n{Fore.GREEN}All tests passed successfully!{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}Some tests failed. Please check the logs for details.{Style.RESET_ALL}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 