#!/bin/bash

# Iterative Research Tool Installation Script

echo "Installing Iterative Research Tool..."

# Create a virtual environment (optional)
if [ "$1" = "--venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    echo "Virtual environment created and activated."
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install the package in development mode
echo "Installing package..."
pip install -e .

# Create config directory
mkdir -p ~/.config/iterative_research_tool

# Create prompts directory and copy prompt files
echo "Setting up prompt files..."
mkdir -p ~/.config/iterative_research_tool/prompts
if [ -d "prompts" ]; then
    cp prompts/*.md ~/.config/iterative_research_tool/prompts/ 2>/dev/null || echo "No prompt files found to copy"
    echo "Prompt files copied to ~/.config/iterative_research_tool/prompts/"
else
    echo "No prompts directory found. Custom prompts will not be available."
fi

echo "Installation complete!"
echo "To get started, run: iterative-research config --init --perplexity-api-key YOUR_KEY --claude-api-key YOUR_KEY"
echo "Then enhance a document with: iterative-research research example.md"
echo "To use custom prompts: iterative-research research example.md --use-custom-prompts" 