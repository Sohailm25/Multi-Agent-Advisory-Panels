#!/bin/bash
# Update CLI script to install the package with the new command

echo "Reinstalling the package to update the CLI commands..."

# Install the package in development mode
pip install -e .

echo "Installation complete!"
echo "You can now use the 'panelsui' command directly in your terminal."
echo ""
echo "Usage examples:"
echo "  panelsui                 - Run the interactive CLI"
echo "  iterative-research       - Run the regular CLI"
echo "  panels                   - Run the panel-based approach" 