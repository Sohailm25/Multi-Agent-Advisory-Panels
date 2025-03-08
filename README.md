# Iterative Research Document Generator

A command-line tool that creates exhaustive, textbook-quality research documents through iterative AI enhancement. This tool leverages both Perplexity and Claude APIs to progressively improve document quality while minimizing hallucinations.

## Use Cases

- **Academic Research**: Generate comprehensive literature reviews and research summaries with proper citations
- **Content Creation**: Create in-depth articles, blog posts, or educational materials on complex topics
- **Knowledge Management**: Transform rough notes or outlines into structured, comprehensive documents
- **Educational Resources**: Generate teaching materials, study guides, or textbook-like content
- **Competitive Intelligence**: Research industry trends, competitor strategies, or market analyses
- **Technical Documentation**: Create detailed documentation for products, services, or technologies

## Features

- **Document Enhancement**: Start with a basic markdown document and enhance it iteratively
- **Fact-Grounded Research**: Uses Perplexity API to ground research in reliable sources
- **Intelligent Restructuring**: Uses Claude to reorganize and improve document flow
- **Citation Tracking**: All facts are tracked with their sources and reliability
- **Confidence Scoring**: Each section receives a confidence score based on its citations
- **Version History**: Maintains a history of document revisions
- **Cost Control**: Monitor and limit API costs
- **Custom Prompts**: Use specialized prompts for enhanced research workflow
- **Intelligent Loop Control**: Automatically determine when to stop research based on diminishing returns
- **Deeper Research**: Generate follow-up questions for more comprehensive coverage

## Prerequisites

- Python 3.9 or higher
- Perplexity API key ([Get one here](https://docs.perplexity.ai/))
- Claude API key from Anthropic ([Get one here](https://console.anthropic.com/))

## Installation

```bash
# Clone the repository
git clone https://github.com/example/iterative_research_tool.git
cd iterative_research_tool

# Install the package (with prompt setup)
bash install.sh

# Or install with a virtual environment
bash install.sh --venv
```

## Required Configuration

Before using the tool, you **must** set up your API keys. You have two options:

### Option 1: Environment Variables (.env file)

Create a `.env` file in the project root with the following content:

```
PERPLEXITY_API_KEY=your-perplexity-key
CLAUDE_API_KEY=your-claude-key
PERPLEXITY_MODEL=sonar
CLAUDE_MODEL=claude-3-7-sonnet-20250219
PROMPTS_DIRECTORY=prompts
```

### Option 2: Configuration File

Initialize a configuration file:

```bash
# Initialize configuration
iterative-research config --init --perplexity-api-key YOUR_PERPLEXITY_KEY --claude-api-key YOUR_CLAUDE_KEY
```

This will create a configuration file at `~/.config/iterative_research_tool/config.json`. You can also specify a custom path:

```bash
iterative-research config --init --path ./config.json
```

## Usage

### Basic Usage

```bash
# Enhance a document (edit in place)
iterative-research research input.md

# Specify an output file
iterative-research research input.md --output-file enhanced.md

# Limit cost
iterative-research research input.md --max-cost 2.5

# Set other parameters
iterative-research research input.md --max-iterations 5 --confidence-threshold 0.7

# Input research topic directly from console
iterative-research research --input-text

# Or using the shorthand
iterative-research research -x

# Provide text directly as a command-line argument
iterative-research research --input-text "Your research topic here"

# Or with the shorthand
iterative-research research -x "The intersection of Islam and meditation techniques"
```

### Advanced Usage with Custom Prompts

```bash
# Use the enhanced prompt-based workflow
iterative-research research input.md --use-custom-prompts

# Customize the prompt directory
iterative-research research input.md --use-custom-prompts --prompts-directory ./my-prompts

# Control batch query behavior
iterative-research research input.md --use-custom-prompts --no-batch-queries

# Adjust loop controller settings
iterative-research research input.md --use-custom-prompts --min-new-info-rate 15.0
```

### Version History

By default, the tool creates a version history file alongside the output file. You can disable this:

```bash
iterative-research research input.md --no-version-history
```

Or specify a custom version history file:

```bash
iterative-research research input.md --version-history-file history.md
```

## Advanced Configuration

Edit the configuration file manually to fine-tune settings:

- **API Keys**: Update your API keys
- **Cost Limits**: Control maximum spending
- **Research Settings**: Adjust iterations, thresholds, and models
- **Output Settings**: Configure verbosity and version tracking

## How It Works

1. **Document Initialization**: Parses the input document structure
2. **Research Phase**: Uses Perplexity to find factual information
3. **Enhancement Phase**: Uses Claude to improve structure and clarity
4. **Verification**: Cross-checks claims and calculates confidence scores
5. **Iteration**: Repeats the process until quality thresholds are met
6. **Output**: Produces enhanced document and version history

## Key Files to Modify

If you want to customize or extend the tool's functionality, these are the key files to edit:

- **`.env`**: Environment variables including API keys and model names
- **`iterative_research_tool/core/perplexity_client.py`**: Modify how the tool interacts with Perplexity API
- **`iterative_research_tool/core/claude_client.py`**: Customize Claude API interactions
- **`prompts/`**: Customize the prompt templates to adjust research behavior
- **`iterative_research_tool/core/research.py`**: Main research logic and workflow
- **`iterative_research_tool/cli/args.py`**: Command-line interface parameters

## Common Errors and Solutions (FAQ)

### API Key Issues

**Error**: `Error: Anthropic API key not found`

**Solution**: Ensure you've correctly set up your API keys in either the `.env` file or configuration file. Double-check for typos in the key or variable names.

### Model Specification

**Error**: `Error: Unknown model 'sonar-model-xyz'` 

**Solution**: The model name is incorrect. Update your `.env` file to use one of the supported models:
- For Perplexity: Use "sonar" or "llama-3-sonar-large-32k-online"
- For Claude: Use "claude-3-7-sonnet-20250219" or another supported model version

### Cost Limits

**Error**: `CostLimitExceededError: Estimated cost $5.75 exceeds the maximum allowed cost $5.00`

**Solution**: The operation would exceed your specified cost limit. Either:
1. Increase the cost limit with `--max-cost 6.0` 
2. Reduce the scope of your research by limiting iterations with `--max-iterations 2`

### Topic Drift

**Issue**: Claude generates content on an unrelated topic

**Solution**: This can happen due to system prompt interference. Ensure your `.env` file correctly specifies the model and check that the system prompts in the `prompts/` directory are properly formatted.

### Installation Problems

**Error**: `ModuleNotFoundError: No module named 'anthropic'`

**Solution**: Reinstall the package with all dependencies:
```bash
pip uninstall -y iterative_research_tool
pip install -e .
```

### Permission Errors

**Error**: `PermissionError: [Errno 13] Permission denied: '/path/to/output.md'`

**Solution**: Ensure you have write permissions to the directory where you're saving the output file.

## Contributing

Contributions are welcome! Feel free to submit pull requests for new features, improvements, or bug fixes.

## License

MIT License 