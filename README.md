# Multi-Agent Advisory Planner

A powerful CLI tool leveraging multiple specialized agent panels to provide strategic planning and decision-making support.

## Overview

The Multi-Agent Advisory Planner is a comprehensive system that combines specialized advisory panels, each composed of multiple AI agents with distinct roles. These panels work together to provide strategic advice, plan complex initiatives, analyze decisions, and explore future scenarios.

Key features:
- Multiple specialized advisory panels
- Support for multiple LLM providers (Anthropic, OpenAI, Perplexity)
- Time travel functionality to explore alternative scenarios
- Customizable panel creation
- Stateful memory across sessions
- Rich visualizations in the terminal
- Comprehensive feedback collection

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/research_cli_tool.git
cd research_cli_tool
```

2. Install dependencies:
```bash
pip install -e .
```

## Project Structure

The project is organized into the following directories:

- `iterative_research_tool/`: Main package directory
  - `core/`: Core functionality and utilities
  - `panels/`: Panel implementations for different advisory contexts
  - `strategic_advisor/`: Strategic advisor implementations (custom and swarm architectures)
  - `prompts/`: Prompt templates used by the system
- `tests/`: Test files for the project
- `docs/`: Documentation files
- `archive/`: Archived files that are no longer actively used
- `my_custom_panels/`: Example directory for custom panel implementations

3. Set up your API keys:
```bash
# For Anthropic (default)
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env

# For OpenAI (optional)
echo "OPENAI_API_KEY=your_api_key_here" >> .env

# For Perplexity (optional)
echo "PERPLEXITY_API_KEY=your_api_key_here" >> .env
```

## Usage

### Basic Usage

Run the CLI with a query:
```bash
python -m iterative_research_tool.cli "What strategic approach should I take for expanding my business internationally?"
```

### Selecting an LLM Provider

Choose a specific LLM provider:
```bash
python -m iterative_research_tool.cli --llm-provider openai "What strategic approach should I take for expanding my business internationally?"
```

Available LLM providers:
- `anthropic` (default): Uses Anthropic's Claude models
- `openai`: Uses OpenAI's GPT models
- `perplexity`: Uses Perplexity's models

You can also specify a model:
```bash
python -m iterative_research_tool.cli --llm-provider openai --model gpt-4o "What strategic approach should I take for expanding my business internationally?"
```

If you need to install dependencies for a specific provider:
```bash
python -m iterative_research_tool.cli --llm-provider openai --install-deps
```

### Selecting a Panel

Choose a specific advisory panel:
```bash
python -m iterative_research_tool.cli --panel cognitive-diversity "What strategic approach should I take for expanding my business internationally?"
```

Available panels:
- `cognitive-diversity`: Provides diverse perspectives from different cognitive styles
- `decision-intelligence`: Analyzes decisions from multiple angles
- `future-scenarios`: Explores potential future scenarios and implications
- `personal-development`: Provides guidance for personal and professional growth
- `stakeholder-impact`: Analyzes impacts on different stakeholders
- `constraint-analysis`: Identifies constraints and turns them into opportunities
- `temporal-perspective`: Analyzes problems across different time horizons
- `contrarian-challenge`: Tests strategies by challenging assumptions
- `implementation-energy`: Optimizes strategies for sustainable implementation
- `product-development`: Provides product strategy advice

### Listing Available Panels

List all available panels:
```bash
python -m iterative_research_tool.cli --list-panels
```

### Getting Panel Information

Get detailed information about a specific panel:
```bash
python -m iterative_research_tool.cli --panel-info cognitive-diversity
```

### Time Travel

Explore alternative scenarios:
```bash
python -m iterative_research_tool.cli --alternative "What if I focused on the Asian market instead?" 
```

Show available checkpoints:
```bash
python -m iterative_research_tool.cli --show-checkpoints
```

Travel to a specific checkpoint:
```bash
python -m iterative_research_tool.cli --time-travel initial
```

### Saving Output

Save the plan to a file:
```bash
python -m iterative_research_tool.cli --output-file my_plan.json "What strategic approach should I take for expanding my business internationally?"
```

## LLM Provider Configuration

The tool supports multiple LLM providers, each with their own API keys and models:

### Anthropic (Default)
- Environment variable: `ANTHROPIC_API_KEY`
- Default model: `claude-3-7-sonnet-20250219`
- Installation: `pip install anthropic`

### OpenAI
- Environment variable: `OPENAI_API_KEY`
- Default model: `gpt-4o`
- Installation: `pip install openai`

### Perplexity
- Environment variable: `PERPLEXITY_API_KEY`
- Default model: `sonar-medium-online`
- Installation: `pip install perplexity-python`

You can specify the provider and model at runtime:
```bash
python -m iterative_research_tool.cli --llm-provider openai --model gpt-4 "Your query here"
```

Or use the `--api-key` flag to override the environment variable:
```bash
python -m iterative_research_tool.cli --llm-provider perplexity --api-key your_api_key_here "Your query here"
```

## Panel Factory Pattern

The system uses a Panel Factory Pattern to dynamically discover and instantiate panels. This allows for easy extension with custom panels. The key benefits include:

- Automatic discovery of all available panels
- Dynamic instantiation without hardcoded dependencies
- Support for custom panels in external directories
- Consistent interface across all panels

## Creating Custom Panels

You can extend the system by creating your own custom panels tailored to your specific needs. We provide a comprehensive guide and template for creating custom panels:

- [Custom Panel Creation Guide](README_CUSTOM_PANELS.md)
- [Custom Panel Template](custom_panel_template.py)

To use a custom panel:

1. Create your panel following the guide
2. Place it in a directory
3. Run the CLI with your custom panel:

```bash
python -m iterative_research_tool.cli --custom-panel-path my_custom_panels/ --panel my-custom-panel "Your query here"
```

## Architecture

The Multi-Agent Advisory Planner is built with a modular architecture:

- `strategic_planner.py`: Coordinates the overall planning process
- `panels/`: Contains the specialized advisory panels
- `core/`: Contains core functionality and utilities
- `cli.py`: Provides the command-line interface
- `core/llm_client.py`: Provides a unified interface for different LLM providers

## Contributing

Contributions are welcome! Please check the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 