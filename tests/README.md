# Tests Directory

This directory contains test files for the Iterative Research Tool.

## Test Files

- `test_all_panels.py`: Tests all available panels in the system.
- `test_claude_client.py`: Tests the Claude client implementation.
- `test_planner.py`: Tests the strategic planner functionality.
- `test_single_panel.py`: Tests a single panel implementation.
- `direct_cache_test.py`: Tests the direct caching functionality for LLM responses.

## Running Tests

To run a specific test, use:

```bash
python3 -m tests.test_name
```

For example:

```bash
python3 -m tests.test_planner
```

## Adding New Tests

When adding new tests, please follow these guidelines:

1. Name test files with the prefix `test_`.
2. Use descriptive names for test functions.
3. Include docstrings explaining what each test does.
4. Add the new test to this README file. 