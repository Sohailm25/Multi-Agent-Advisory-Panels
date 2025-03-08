"""Configuration management for the Iterative Research Tool."""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


class APIConfig(BaseModel):
    """API configuration settings."""
    perplexity_api_key: str
    claude_api_key: str


class CostLimitConfig(BaseModel):
    """Cost limitation configuration."""
    max_cost_per_call: float = 5.0  # Default max cost in USD
    perplexity_cost_per_1k_tokens: float = 0.001  # $1 per 1M tokens (input and output)
    perplexity_cost_per_search: float = 0.005  # $5 per 1000 searches
    claude_cost_per_1k_input_tokens: float = 0.003  # Rate for Claude 3.7 Sonnet ($3 per 1M tokens)
    claude_cost_per_1k_output_tokens: float = 0.015  # Rate for Claude 3.7 Sonnet ($15 per 1M tokens)


class PromptConfig(BaseModel):
    """Prompt configuration settings."""
    use_custom_prompts: bool = True
    prompts_directory: Optional[str] = None
    cli_input_prompt: str = "cli_input_prompt"
    perplexity_to_claude_prompt: str = "perplexity_to_claude_prompt"
    claude_to_perplexity_deeper_prompt: str = "claude_to_perplexity_deeper_prompt"
    loop_controller_prompt: str = "loop_controller_prompt"


class ResearchConfig(BaseModel):
    """Research process configuration."""
    max_iterations: int = Field(default=3, ge=1, le=10)
    confidence_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    perplexity_model: str = "sonar"
    claude_model: str = "claude-3-7-sonnet-20250219"
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    verbose_output: bool = True
    track_version_history: bool = True
    use_controller_termination: bool = True
    min_new_info_rate: float = Field(default=10.0, ge=0.0, le=100.0)  # Minimum new info percentage to continue
    batch_queries: bool = True  # Whether to run multiple deeper queries in batch
    max_batch_size: int = Field(default=5, ge=1, le=10)  # Maximum number of queries to run in batch


class ToolConfig(BaseModel):
    """Main configuration for the Iterative Research Tool."""
    api: APIConfig
    cost_limits: CostLimitConfig = Field(default_factory=CostLimitConfig)
    research: ResearchConfig = Field(default_factory=ResearchConfig)
    prompts: PromptConfig = Field(default_factory=PromptConfig)


class ConfigManager:
    """Manages configuration loading and saving."""
    
    DEFAULT_CONFIG_PATH = "~/.config/iterative_research_tool/config.json"
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the config manager.
        
        Args:
            config_path: Path to the config file. If None, uses default path.
        """
        self.config_path = Path(config_path or self.DEFAULT_CONFIG_PATH).expanduser()
    
    def ensure_config_dir(self) -> None:
        """Ensure the configuration directory exists."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> ToolConfig:
        """Load configuration from file.
        
        Returns:
            ToolConfig object
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValidationError: If config is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found at {self.config_path}")
        
        try:
            with open(self.config_path, "r") as f:
                config_data = json.load(f)
            
            return ToolConfig.parse_obj(config_data)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file: {self.config_path}")
            raise
        except ValidationError as e:
            logger.error(f"Invalid configuration: {e}")
            raise
    
    def save_config(self, config: ToolConfig) -> None:
        """Save configuration to file.
        
        Args:
            config: Configuration to save
        """
        self.ensure_config_dir()
        
        # Convert to dict and save
        config_dict = config.dict()
        
        with open(self.config_path, "w") as f:
            json.dump(config_dict, f, indent=2)
        
        logger.info(f"Configuration saved to {self.config_path}")
    
    def create_default_config(self, perplexity_api_key: str = "", claude_api_key: str = "") -> ToolConfig:
        """Create a default configuration.
        
        Args:
            perplexity_api_key: Perplexity API key
            claude_api_key: Claude API key
            
        Returns:
            Default configuration
        """
        api_config = APIConfig(
            perplexity_api_key=perplexity_api_key,
            claude_api_key=claude_api_key
        )
        
        return ToolConfig(api=api_config)
    
    def initialize_config(self, perplexity_api_key: str = "", claude_api_key: str = "") -> ToolConfig:
        """Initialize configuration, creating default if it doesn't exist.
        
        Args:
            perplexity_api_key: Perplexity API key
            claude_api_key: Claude API key
            
        Returns:
            Configuration object
        """
        if not self.config_path.exists():
            config = self.create_default_config(
                perplexity_api_key=perplexity_api_key,
                claude_api_key=claude_api_key
            )
            self.save_config(config)
            return config
        
        try:
            return self.load_config()
        except (FileNotFoundError, json.JSONDecodeError, ValidationError):
            # If loading fails, create and save default config
            config = self.create_default_config(
                perplexity_api_key=perplexity_api_key,
                claude_api_key=claude_api_key
            )
            self.save_config(config)
            return config
    
    def load_env_config(self) -> Dict[str, str]:
        """Load configuration from environment variables.
        
        Returns:
            Dictionary of configuration values from environment
        """
        env_config = {}
        
        # API keys
        if os.environ.get("PERPLEXITY_API_KEY"):
            env_config["perplexity_api_key"] = os.environ.get("PERPLEXITY_API_KEY")
        
        if os.environ.get("CLAUDE_API_KEY"):
            env_config["claude_api_key"] = os.environ.get("CLAUDE_API_KEY")
        
        # Model names
        if os.environ.get("PERPLEXITY_MODEL"):
            env_config["perplexity_model"] = os.environ.get("PERPLEXITY_MODEL")
        
        if os.environ.get("CLAUDE_MODEL"):
            env_config["claude_model"] = os.environ.get("CLAUDE_MODEL")
        
        # Prompt settings
        if os.environ.get("PROMPTS_DIRECTORY"):
            env_config["prompts_directory"] = os.environ.get("PROMPTS_DIRECTORY")
        
        if "USE_CUSTOM_PROMPTS" in os.environ:
            env_config["use_custom_prompts"] = os.environ.get("USE_CUSTOM_PROMPTS").lower() in ("true", "1", "yes")
        
        return env_config 