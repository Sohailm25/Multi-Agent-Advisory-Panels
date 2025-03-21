"""Interactive CLI module for the Iterative Research Tool.

This module provides an interactive command-line interface with arrow key
selection for various options like strategy, panels, and LLM providers.
"""

import os
import sys
import questionary
from typing import Optional, List, Dict, Any, Tuple
from colorama import Fore, Style

from iterative_research_tool.core.config import ConfigManager
from iterative_research_tool.core.panel_factory import panel_factory
from iterative_research_tool.core.visualization import Visualizer

# Constants for styling
QUESTIONARY_STYLE = questionary.Style([
    ("selected", "fg:green bold"),
    ("pointer", "fg:green bold"),
    ("highlighted", "fg:green"),
    ("answer", "fg:green bold"),
    ("checkbox-selected", "fg:green"),
])

# Strategy options
STRATEGY_CHOICES = [
    # Temporarily removed panel-based approach for initial GitHub deployment
    # questionary.Choice("Panel-based approach (custom panels)", "panels"),
    questionary.Choice("Strategic Advisor (Custom Architecture)", "strat-custom"),
    questionary.Choice("Strategic Advisor (Swarm Architecture)", "strat-swarm"),
]

# LLM provider options
LLM_PROVIDER_CHOICES = [
    questionary.Choice("Anthropic (Claude models)", "anthropic"),
    questionary.Choice("OpenAI (GPT models)", "openai"),
    questionary.Choice("Perplexity", "perplexity"),
]

# Model mapping by provider
MODEL_CHOICES_BY_PROVIDER = {
    "anthropic": [
        questionary.Choice("Claude 3.7 Sonnet", "claude-3-7-sonnet-20250219"),
        questionary.Choice("Claude 3.5 Sonnet", "claude-3-5-sonnet-20240620"),
        questionary.Choice("Claude 3 Opus", "claude-3-opus-20240229"),
        questionary.Choice("Claude 3 Haiku", "claude-3-haiku-20240307"),
    ],
    "openai": [
        questionary.Choice("GPT-4o", "gpt-4o"),
        questionary.Choice("GPT-4", "gpt-4"),
        questionary.Choice("GPT-3.5 Turbo", "gpt-3.5-turbo"),
    ],
    "perplexity": [
        questionary.Choice("Sonar Small", "sonar-small-online"),
        questionary.Choice("Sonar Medium", "sonar-medium-online"),
        questionary.Choice("Sonar Large", "sonar-large-online"),
    ],
}


class InteractiveCLI:
    """Interactive command-line interface for the Iterative Research Tool.
    
    This class provides interactive prompts with arrow key selection for
    the various options available in the tool.
    """
    
    def __init__(self):
        """Initialize the interactive CLI."""
        self.visualizer = Visualizer()
        self.config_manager = ConfigManager()
        
        # Make sure panel factory is initialized
        panel_factory.discover_panels(verbose=False)
        
        # Store user selections
        self.selected_strategy = None
        self.selected_panel = None
        self.selected_llm_provider = None
        self.selected_model = None
        self.api_key = None
        self.query = None
        
    def start(self) -> Dict[str, Any]:
        """Start the interactive CLI flow.
        
        Returns:
            Dict containing all the user selections
        """
        try:
            # Display welcome message
            self.visualizer.display_message(f"\n{Style.BRIGHT}Welcome to the Interactive Research Tool!{Style.RESET_ALL}")
            self.visualizer.display_message("Use arrow keys to navigate and Enter to select options.")
            
            # Select strategy
            self._select_strategy()
            
            # Panel selection is temporarily disabled for initial GitHub deployment
            # if self.selected_strategy == "panels":
            #     self._select_panel()
            
            # Get query
            self._get_query()
            
            # Select LLM provider
            self._select_llm_provider()
            
            # Select model
            self._select_model()
            
            # Check API key
            self._check_api_key()
            
            # Show summary of choices
            self._show_summary()
            
            # Return all selections
            return {
                "strategy": self.selected_strategy,
                "panel": self.selected_panel,
                "query": self.query,
                "llm_provider": self.selected_llm_provider,
                "model": self.selected_model,
                "api_key": self.api_key,
            }
            
        except KeyboardInterrupt:
            self.visualizer.display_message("\n\nInterrupt received. Exiting...")
            sys.exit(0)
    
    def _select_strategy(self) -> None:
        """Prompt the user to select a strategy."""
        self.visualizer.display_message("\n")
        strategy = questionary.select(
            "Select your approach:",
            choices=STRATEGY_CHOICES,
            style=QUESTIONARY_STYLE
        ).ask()
        
        if not strategy:
            raise KeyboardInterrupt()
        
        self.selected_strategy = strategy
        self.visualizer.display_success(f"Selected strategy: {Fore.GREEN}{self._get_strategy_display_name(strategy)}{Style.RESET_ALL}")
    
    # Temporarily commented out for initial GitHub deployment
    # def _select_panel(self) -> None:
    #     """Prompt the user to select a panel."""
    #     available_panels = panel_factory.list_available_panels()
    #     
    #     if not available_panels:
    #         self.visualizer.display_error("No panels available. Please check your installation.")
    #         raise KeyboardInterrupt()
    #     
    #     panel_choices = [
    #         questionary.Choice(panel, panel) for panel in available_panels
    #     ]
    #     
    #     self.visualizer.display_message("\n")
    #     panel = questionary.select(
    #         "Select a panel:",
    #         choices=panel_choices,
    #         style=QUESTIONARY_STYLE
    #     ).ask()
    #     
    #     if not panel:
    #         raise KeyboardInterrupt()
    #     
    #     self.selected_panel = panel
    #     self.visualizer.display_success(f"Selected panel: {Fore.GREEN}{panel}{Style.RESET_ALL}")
    
    def _get_query(self) -> None:
        """Get the user's query."""
        self.visualizer.display_message("\n")
        query = questionary.text(
            "Enter your research query:",
            style=QUESTIONARY_STYLE
        ).ask()
        
        if not query:
            self.visualizer.display_error("Query cannot be empty")
            return self._get_query()
        
        self.query = query
        self.visualizer.display_success(f"Query: {Fore.CYAN}{query}{Style.RESET_ALL}")
    
    def _select_llm_provider(self) -> None:
        """Prompt the user to select an LLM provider."""
        self.visualizer.display_message("\n")
        provider = questionary.select(
            "Select your LLM provider:",
            choices=LLM_PROVIDER_CHOICES,
            style=QUESTIONARY_STYLE
        ).ask()
        
        if not provider:
            raise KeyboardInterrupt()
        
        self.selected_llm_provider = provider
        display_name = next((c.title for c in LLM_PROVIDER_CHOICES if c.value == provider), provider)
        self.visualizer.display_success(f"Selected LLM provider: {Fore.GREEN}{display_name}{Style.RESET_ALL}")
    
    def _select_model(self) -> None:
        """Prompt the user to select a model for the chosen provider."""
        provider = self.selected_llm_provider
        
        if provider not in MODEL_CHOICES_BY_PROVIDER:
            self.visualizer.display_error(f"No models defined for provider: {provider}")
            return
        
        self.visualizer.display_message("\n")
        model = questionary.select(
            f"Select a {provider.title()} model:",
            choices=MODEL_CHOICES_BY_PROVIDER[provider],
            style=QUESTIONARY_STYLE
        ).ask()
        
        if not model:
            raise KeyboardInterrupt()
        
        self.selected_model = model
        display_name = next((c.title for c in MODEL_CHOICES_BY_PROVIDER[provider] if c.value == model), model)
        self.visualizer.display_success(f"Selected model: {Fore.GREEN}{display_name}{Style.RESET_ALL}")
    
    def _check_api_key(self) -> None:
        """Check if the API key is available and prompt if needed."""
        env_var = f"{self.selected_llm_provider.upper()}_API_KEY"
        api_key = os.environ.get(env_var)
        
        if api_key:
            self.visualizer.display_success(f"Using API key from environment variable: {env_var}")
            self.api_key = api_key
            return
        
        self.visualizer.display_message("\n")
        self.visualizer.display_message(f"API key for {self.selected_llm_provider.title()} not found in environment variables.")
        
        api_key = questionary.password(
            f"Enter your {self.selected_llm_provider.title()} API key:",
            style=QUESTIONARY_STYLE
        ).ask()
        
        if not api_key:
            self.visualizer.display_error("API key cannot be empty")
            return self._check_api_key()
        
        self.api_key = api_key
        self.visualizer.display_success("API key provided")
    
    def _show_summary(self) -> None:
        """Show a summary of all selections."""
        self.visualizer.display_message("\n")
        self.visualizer.display_message(f"{Style.BRIGHT}Summary of your selections:{Style.RESET_ALL}")
        self.visualizer.display_message(f"Strategy: {Fore.GREEN}{self._get_strategy_display_name(self.selected_strategy)}{Style.RESET_ALL}")
        
        if self.selected_panel:
            self.visualizer.display_message(f"Panel: {Fore.GREEN}{self.selected_panel}{Style.RESET_ALL}")
        
        self.visualizer.display_message(f"LLM Provider: {Fore.GREEN}{self.selected_llm_provider.title()}{Style.RESET_ALL}")
        self.visualizer.display_message(f"Model: {Fore.GREEN}{self.selected_model}{Style.RESET_ALL}")
        self.visualizer.display_message(f"Query: {Fore.CYAN}{self.query}{Style.RESET_ALL}")
        self.visualizer.display_message("\n")
    
    def _get_strategy_display_name(self, strategy_value: str) -> str:
        """Get the display name for a strategy value."""
        for choice in STRATEGY_CHOICES:
            if choice.value == strategy_value:
                return choice.title
        return strategy_value


# Main function to run the interactive CLI
def run_interactive_cli():
    """Run the interactive CLI and return the selections."""
    cli = InteractiveCLI()
    return cli.start()


if __name__ == "__main__":
    # Test the interactive CLI
    selections = run_interactive_cli()
    print("Selected options:", selections) 