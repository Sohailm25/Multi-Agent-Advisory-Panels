#!/usr/bin/env python3
"""Test script for LLM caching in Strategic Advisor Swarm."""

import os
import json
import time
import argparse
from dotenv import load_dotenv

from iterative_research_tool.strategic_advisor import StrategicAdvisorSwarm

def main():
    """Run the caching test."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test LLM caching for Strategic Advisor Swarm")
    parser.add_argument("--model", help="LLM model to use")
    parser.add_argument("--provider", default="anthropic", choices=["anthropic", "openai", "perplexity"], 
                        help="LLM provider to use")
    parser.add_argument("--api-key", help="API key for the LLM provider")
    parser.add_argument("--iterations", type=int, default=3, help="Number of iterations for testing")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching for comparison")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    # Set up the API key
    api_key = args.api_key or os.environ.get(f"{args.provider.upper()}_API_KEY")
    if not api_key:
        print(f"Error: No API key found for {args.provider}.")
        print(f"Please set {args.provider.upper()}_API_KEY environment variable or use --api-key.")
        return 1
    
    # Create an instance of Strategic Advisor with caching enabled
    advisor_with_cache = StrategicAdvisorSwarm(
        llm_provider=args.provider,
        api_key=api_key,
        model=args.model,
        verbose=args.verbose,
        use_cache=True
    )
    
    # Test prompt
    test_prompt = """
    Analyze the following business scenario and provide strategic advice:
    
    A medium-sized software company is experiencing high employee turnover, especially among senior developers.
    The company has competitive salaries but struggles with maintaining a positive work culture.
    What strategic changes should the company implement to improve retention?
    """
    
    print("\n===== TESTING WITH CACHING ENABLED =====")
    with_cache_results = advisor_with_cache.test_cache(test_prompt, args.iterations)
    print(f"Total time: {with_cache_results['total_time']:.2f} seconds")
    print(f"First call time: {with_cache_results['first_call_time']:.2f} seconds")
    print(f"Average cached call time: {with_cache_results['avg_cached_call_time']:.2f} seconds")
    print(f"Cache hit rate: {with_cache_results['cache_stats']['hit_rate']:.2f}")
    
    # If requested, test without caching for comparison
    if args.no_cache:
        # Create an instance with caching disabled
        advisor_without_cache = StrategicAdvisorSwarm(
            llm_provider=args.provider,
            api_key=api_key,
            model=args.model,
            verbose=args.verbose,
            use_cache=False
        )
        
        print("\n===== TESTING WITH CACHING DISABLED =====")
        # For the no-cache test, we'll use the built-in test method but force use_cache=False
        advisor_without_cache.use_cache = False
        start_time = time.time()
        results_without_cache = []
        
        for i in range(args.iterations):
            iteration_start = time.time()
            response = advisor_without_cache._call_llm(test_prompt)
            iteration_time = time.time() - iteration_start
            results_without_cache.append({
                "iteration": i + 1,
                "time": iteration_time,
                "response_length": len(response)
            })
        
        total_time_without_cache = time.time() - start_time
        avg_time_without_cache = total_time_without_cache / args.iterations
        
        print(f"Total time: {total_time_without_cache:.2f} seconds")
        print(f"Average call time: {avg_time_without_cache:.2f} seconds")
        
        # Compare the results
        print("\n===== COMPARISON =====")
        speedup = avg_time_without_cache / with_cache_results['avg_time_per_call']
        print(f"Speedup with caching: {speedup:.2f}x")
        
        # Calculate time saved
        time_saved = total_time_without_cache - with_cache_results['total_time']
        print(f"Time saved: {time_saved:.2f} seconds")
    
    # Save detailed results to a file
    results_file = "cache_test_results.json"
    with open(results_file, "w") as f:
        json.dump(with_cache_results, f, indent=2)
    
    print(f"\nDetailed results saved to {results_file}")
    return 0

if __name__ == "__main__":
    exit(main()) 