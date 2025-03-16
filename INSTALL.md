# Installation Guide

This guide explains how to install the Multi-Agent Advisory Planner and its dependencies.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Git

## Basic Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/research_cli_tool.git
cd research_cli_tool
```

2. Install dependencies:

You have several installation options depending on your needs:

```bash
# Basic installation (includes only the Anthropic provider by default)
pip install -e .

# Install with all LLM providers (recommended for most users)
pip install -e ".[all]"

# Complete installation with all providers and development tools
pip install -e ".[complete]"

# Installation with just a specific additional provider
pip install -e ".[openai]"     # For OpenAI
pip install -e ".[perplexity]" # For Perplexity
```

> **Important Note:** The quotes around ".[all]" are important in some shells (like zsh) to prevent glob expansion. If you're using zsh (default on macOS), make sure to include the quotes.

3. Set up your API keys:
```bash
# For Anthropic (default)
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env

# For OpenAI (optional)
echo "OPENAI_API_KEY=your_api_key_here" >> .env

# For Perplexity (optional)
echo "PERPLEXITY_API_KEY=your_api_key_here" >> .env
```

## LLM Provider Dependencies

The tool supports multiple LLM providers, each with their own Python package:

| Provider   | Python Package | Installation Command              |
|------------|---------------|----------------------------------|
| Anthropic  | `anthropic`   | `pip install anthropic`          |
| OpenAI     | `openai`      | `pip install openai`             |
| Perplexity | `PerplexiPy`  | `pip install PerplexiPy`         |

When you install with `pip install -e ".[all]"`, all these dependencies are installed automatically.

## Automatic Dependency Installation

If you encounter missing dependencies when running the tool, you can use the `--install-deps` flag to automatically install the required packages:

```bash
# Automatically install dependencies for a specific provider
panels --llm-provider perplexity --install-deps

# Or when using the longer command form
python -m iterative_research_tool.cli --llm-provider perplexity --install-deps
```

## Verifying Installation

After installation, you can verify that everything is working correctly by listing the available panels:

```bash
panels --list-panels
```

This command should list all available panels without requiring an API key.

## Global Command Usage

After installing the package, you can use the global `panels` command from anywhere in your terminal:

```bash
# Use the default panel with Anthropic provider
panels "What strategic approach should I take for expanding my business internationally?"

# Use a specific panel
panels --panel cognitive-diversity "What strategic approach should I take?"

# Use a specific LLM provider
panels --llm-provider openai "How should I approach this problem?"
```

The `panels` command works exactly the same as the longer `python -m iterative_research_tool.cli` command, with all the same options and parameters.

## Troubleshooting

If you encounter any installation issues:

1. **Missing dependencies**: Use the `--install-deps` flag as described above.

2. **Shell glob expansion errors**: Make sure to use quotes around the extras when installing, e.g., `pip install -e ".[all]"`.

3. **Import errors**: Ensure you have installed the appropriate provider packages.

4. **API key errors**: Verify that you've set up your API keys correctly in the `.env` file. 