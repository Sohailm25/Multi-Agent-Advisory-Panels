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
    from perplexity import Perplexity
except ImportError:
    Perplexity = None

logger = logging.getLogger(__name__)

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
        if Anthropic is None:
            raise ImportError("Anthropic package is not installed. Install it with 'pip install anthropic'")
            
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
        if openai is None:
            raise ImportError("OpenAI package is not installed. Install it with 'pip install openai'")
            
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
        if Perplexity is None:
            raise ImportError("Perplexity package is not installed. Install it with 'pip install perplexity-python'")
            
        self.api_key = api_key or os.environ.get("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("Perplexity API key is required")
            
        self.client = Perplexity(api_key=self.api_key)
    
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
            response = self.client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
                stream=stream
            )
            return response
        except Exception as e:
            logger.error(f"Error calling Perplexity API: {str(e)}")
            raise
    
    def get_available_models(self) -> List[str]:
        """
        Get a list of available Perplexity models.
        
        Returns:
            List of available Perplexity model names
        """
        # Hardcoded list of common Perplexity models
        return [
            "sonar-medium-online",
            "sonar-small-online",
            "mixtral-8x7b-instruct",
            "llama-3-70b-instruct",
        ]

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