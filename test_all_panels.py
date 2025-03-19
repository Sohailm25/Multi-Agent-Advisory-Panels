#!/usr/bin/env python

import subprocess
import sys
import time
import os
import importlib.util

def test_panel_info():
    print("\n===== Testing panel-info for all panels =====\n")
    panels = [
        "cognitive-diversity",
        "constraint-analysis",
        "contrarian-challenge",
        "decision-intelligence",
        "future-scenarios",
        "implementation-energy",
        "personal-development",
        "product-development",
        "stakeholder-impact",
        "temporal-perspective"
    ]

    for panel in panels:
        cmd = f"python -m iterative_research_tool.cli --panel-info {panel}"
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"Exit code: {result.returncode}")
        
        if result.returncode == 0:
            print(f"SUCCESS for {panel}")
        else:
            print(f"ERROR for {panel}: {result.stderr}")
        print("-" * 50)

def test_strategic_commands():
    print("\n===== Testing strat-custom and strat-swarm commands =====\n")
    
    # Test query
    test_query = "How to improve team productivity"
    api_key = "test_key"  # Using a placeholder API key
    
    # Test strat-custom
    cmd = f'python -m iterative_research_tool.cli strat-custom "{test_query}" --api-key {api_key}'
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"Exit code: {result.returncode}")
    
    if result.returncode == 0:
        print(f"SUCCESS for strat-custom")
    else:
        print(f"ERROR for strat-custom: {result.stderr}")
    print("-" * 50)
    
    # Test strat-swarm
    cmd = f'python -m iterative_research_tool.cli strat-swarm "{test_query}" --api-key {api_key}'
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"Exit code: {result.returncode}")
    
    if result.returncode == 0:
        print(f"SUCCESS for strat-swarm")
    else:
        print(f"ERROR for strat-swarm: {result.stderr}")
    print("-" * 50)

def test_panel_command_formats():
    print("\n===== Testing different panel command formats =====\n")
    
    test_query = "How to improve team productivity"
    panel = "cognitive-diversity"
    api_key = "test_key"
    
    # Format 1: Query at the end
    cmd1 = f'python -m iterative_research_tool.cli --panel {panel} --api-key {api_key} "{test_query}"'
    print(f"Testing format 1: {cmd1}")
    result1 = subprocess.run(cmd1, shell=True, capture_output=True, text=True)
    print(f"Exit code: {result1.returncode}")
    if result1.stderr:
        print(f"STDERR: {result1.stderr}")
    print("-" * 50)
    
    # Format 2: Query at the beginning
    cmd2 = f'python -m iterative_research_tool.cli "{test_query}" --panel {panel} --api-key {api_key}'
    print(f"Testing format 2: {cmd2}")
    result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True)
    print(f"Exit code: {result2.returncode}")
    if result2.stderr:
        print(f"STDERR: {result2.stderr}")
    print("-" * 50)
    
    # Format 3: Query as parameter
    cmd3 = f'python -m iterative_research_tool.cli --panel {panel} --api-key {api_key} --query "{test_query}"'
    print(f"Testing format 3: {cmd3}")
    result3 = subprocess.run(cmd3, shell=True, capture_output=True, text=True)
    print(f"Exit code: {result3.returncode}")
    if result3.stderr:
        print(f"STDERR: {result3.stderr}")
    print("-" * 50)

def test_direct_function_call():
    print("\n===== Testing direct function call to run_with_panel =====\n")
    
    try:
        # Import the run_with_panel function from the CLI module
        spec = importlib.util.find_spec("iterative_research_tool.cli")
        if spec is None:
            print("Could not find CLI module. Make sure the package is installed.")
            return
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check if run_with_panel function exists in the module
        if not hasattr(module, 'run_with_panel'):
            print("run_with_panel function not found in CLI module.")
            return
        
        # Test parameters
        test_query = "How to improve team productivity"
        test_panel = "cognitive-diversity"
        test_provider = "anthropic"  # Using anthropic as default provider
        test_api_key = "test_key"  # Using a placeholder API key
        
        print(f"Calling run_with_panel directly with:")
        print(f"  - query: {test_query}")
        print(f"  - panel: {test_panel}")
        print(f"  - provider: {test_provider}")
        
        # Call the function directly
        result = module.run_with_panel(
            query=test_query,
            panel_type=test_panel,
            llm_provider=test_provider,
            api_key=test_api_key,
            verbose=True
        )
        
        print(f"Function returned: {result}")
        
        if result == 0:
            print(f"SUCCESS for direct function call with {test_panel}")
        else:
            print(f"ERROR for direct function call with {test_panel}")
        
    except Exception as e:
        print(f"Error during direct function call: {e}")
    
    print("-" * 50)

def analyze_cli_file():
    print("\n===== Analyzing cli.py for panel command structure =====\n")
    
    try:
        # Look for run_with_panel function
        result = subprocess.run("grep -n 'def run_with_panel' iterative_research_tool/cli.py", 
                               shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Found run_with_panel function: {result.stdout.strip()}")
            
            # Get the function signature
            line_number = result.stdout.split(":")[0]
            cmd = f"sed -n '{line_number},{int(line_number) + 10}p' iterative_research_tool/cli.py"
            signature = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            print("Function signature:")
            print(signature.stdout)
        else:
            print("Could not find run_with_panel function definition.")
    except Exception as e:
        print(f"Error analyzing CLI file: {e}")

if __name__ == "__main__":
    test_panel_info()
    test_strategic_commands()
    test_panel_command_formats()
    test_direct_function_call()
    analyze_cli_file()
    
    print("\nAll tests completed.")
