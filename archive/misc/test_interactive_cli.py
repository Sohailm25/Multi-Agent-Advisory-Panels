#!/usr/bin/env python
"""Test script for the interactive CLI.

This script runs the interactive CLI to test its functionality.
"""

import sys
from iterative_research_tool.core.interactive_cli import run_interactive_cli

if __name__ == "__main__":
    print("Starting interactive CLI test")
    try:
        selections = run_interactive_cli()
        print("\nSelections made:")
        for key, value in selections.items():
            if key == "api_key" and value:
                print(f"  {key}: [API KEY HIDDEN]")
            else:
                print(f"  {key}: {value}")
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError running interactive CLI: {e}")
        sys.exit(1) 