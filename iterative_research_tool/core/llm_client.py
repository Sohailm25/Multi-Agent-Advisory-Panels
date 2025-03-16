"""LLM client module for multi-provider support."""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Iterator

# Import LLM provider libraries
try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    import openai
except ImportError:
    openai = None

try:
    from perplexipy import PerplexityClient
except ImportError:
    PerplexityClient = None

logger = logging.getLogger(__name__)

def check_module_availability(module_name: str, provider_name: str) -> None:
    """
    Checks if a required module is available and provides helpful installation instructions if not.
    
    Args:
        module_name: The name of the module to check
        provider_name: The name of the LLM provider
        
    Raises:
        ImportError: If the module is not installed, with a helpful error message
    """
    module_map = {
        "anthropic": Anthropic,
        "openai": openai,
        "perplexity": PerplexityClient
    }
    
    install_commands = {
        "anthropic": "pip install anthropic",
        "openai": "pip install openai",
        "perplexity": "pip install PerplexiPy"
    }
    
    if module_map.get(module_name) is None:
        error_message = (
            f"{provider_name} package is not installed. You can install it with:\n\n"
            f"    {install_commands.get(module_name, f'pip install {module_name}')}\n\n"
            f"Or install all LLM provider dependencies at once with:\n\n"
            f"    pip install -e .[all]\n\n"
            f"You can also run the command with the --install-deps flag to automatically install the required dependencies."
        )
        raise ImportError(error_message)

class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def create_message(self, 
                      model: str, 
                      messages: List[Dict[str, str]], 
                      max_tokens: int = 4000,
                      temperature: float = 0.7,
                      stream: bool = False) -> Any:
        """
        Create a message using the LLM provider.
        
        Args:
            model: The model to use
            messages: The messages to send to the model
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream the response
            
        Returns:
            The model's response
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Get a list of available models from the provider.
        
        Returns:
            List of available model names
        """
        pass

class AnthropicClient(LLMClient):
    """Anthropic Claude client implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Anthropic client.
        
        Args:
            api_key: Anthropic API key
        """
        # Check if the Anthropic package is installed
        check_module_availability("anthropic", "Anthropic")
            
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
            
        self.client = Anthropic(api_key=self.api_key)
    
    def create_message(self, 
                      model: str, 
                      messages: List[Dict[str, str]], 
                      max_tokens: int = 4000,
                      temperature: float = 0.7,
                      stream: bool = False) -> Any:
        """
        Create a message using Anthropic's Claude.
        
        Args:
            model: The Claude model to use
            messages: The messages to send to Claude
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream the response
            
        Returns:
            Claude's response
        """
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
                stream=stream
            )
            return response
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {str(e)}")
            raise
    
    def get_available_models(self) -> List[str]:
        """
        Get a list of available Claude models.
        
        Returns:
            List of available Claude model names
        """
        # Hardcoded list of common Claude models
        return [
            "claude-3-7-sonnet-20250219",
            "claude-3-5-sonnet-20240620",
            "claude-3-opus-20240229",
            "claude-3-haiku-20240307",
        ]

class OpenAIClient(LLMClient):
    """OpenAI client implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key: OpenAI API key
        """
        # Check if the OpenAI package is installed
        check_module_availability("openai", "OpenAI")
            
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
            
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def create_message(self, 
                      model: str, 
                      messages: List[Dict[str, str]], 
                      max_tokens: int = 4000,
                      temperature: float = 0.7,
                      stream: bool = False) -> Any:
        """
        Create a message using OpenAI's models.
        
        Args:
            model: The OpenAI model to use
            messages: The messages to send to the model
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream the response
            
        Returns:
            OpenAI's response
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
                stream=stream
            )
            return response
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise
    
    def get_available_models(self) -> List[str]:
        """
        Get a list of available OpenAI models.
        
        Returns:
            List of available OpenAI model names
        """
        # Hardcoded list of common OpenAI models
        return [
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
        ]

class PerplexityClient(LLMClient):
    """Perplexity client implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Perplexity client.
        
        Args:
            api_key: Perplexity API key
        """
        # Check if the Perplexity package is installed
        check_module_availability("perplexity", "Perplexity")
            
        self.api_key = api_key or os.environ.get("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("Perplexity API key is required")
            
        self.client = PerplexityClient(api_key=self.api_key)
    
    def create_message(self, 
                      model: str, 
                      messages: List[Dict[str, str]], 
                      max_tokens: int = 4000,
                      temperature: float = 0.7,
                      stream: bool = False) -> Any:
        """
        Create a message using Perplexity's models.
        
        Args:
            model: The Perplexity model to use
            messages: The messages to send to the model
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream the response
            
        Returns:
            Perplexity's response
        """
        try:
            # Convert messages to a single prompt for Perplexity
            prompt = self._messages_to_prompt(messages)
            
            if stream:
                # Use streamable query method for streaming responses
                return self.client.queryStreamable(
                    prompt,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            else:
                # Use regular query method for non-streaming responses
                return self.client.query(
                    prompt,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
        except Exception as e:
            logger.error(f"Error calling Perplexity API: {str(e)}")
            raise
    
    def get_available_models(self) -> List[str]:
        """
        Get a list of available models from Perplexity.
        
        Returns:
            List of available model names
        """
        # Return the available models for Perplexity
        # As of current version, these are the supported models
        return [
            "sonar-small-online",
            "sonar-medium-online",
            "sonar-large-online",
            "mixtral-8x7b-instruct",
            "llama-3-8b-instruct",
            "llama-3-70b-instruct"
        ]
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        Convert a list of messages to a single prompt string compatible with Perplexity.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            
        Returns:
            A formatted prompt string
        """
        # Concatenate all messages into a single prompt
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "").lower()
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
            else:
                # Handle other roles or fallback
                prompt_parts.append(f"{role.capitalize()}: {content}")
                
        return "\n\n".join(prompt_parts)

class LLMClientFactory:
    """Factory for creating LLM clients."""
    
    @staticmethod
    def create_client(provider: str, api_key: Optional[str] = None) -> LLMClient:
        """
        Create an LLM client for the specified provider.
        
        Args:
            provider: The LLM provider to use (anthropic, openai, or perplexity)
            api_key: Optional API key to use
            
        Returns:
            An LLM client instance
            
        Raises:
            ValueError: If the provider is not supported
        """
        provider = provider.lower()
        
        if provider == "anthropic":
            return AnthropicClient(api_key)
        elif provider == "openai":
            return OpenAIClient(api_key)
        elif provider == "perplexity":
            return PerplexityClient(api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}. Supported providers: anthropic, openai, perplexity")
    
    @staticmethod
    def get_default_model(provider: str) -> str:
        """
        Get the default model for the specified provider.
        
        Args:
            provider: The LLM provider
            
        Returns:
            Default model name
            
        Raises:
            ValueError: If the provider is not supported
        """
        provider = provider.lower()
        
        if provider == "anthropic":
            return "claude-3-7-sonnet-20250219"
        elif provider == "openai":
            return "gpt-4o"
        elif provider == "perplexity":
            return "sonar-medium-online"
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}. Supported providers: anthropic, openai, perplexity") 