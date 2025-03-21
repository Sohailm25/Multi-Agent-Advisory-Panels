"""LLM Component for modular use in iterative research tool components."""

import os
import logging
from typing import Optional, Dict, Any, List

from iterative_research_tool.core.llm_client import LLMClientFactory

logger = logging.getLogger(__name__)

class LLMComponent:
    """A component that provides a unified interface for LLM calls.
    
    This class wraps various LLM provider clients to provide a consistent interface
    for generating text from prompts, regardless of the underlying provider.
    """
    
    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.2
    ):
        """Initialize the LLM component.
        
        Args:
            provider: The LLM provider to use (openai or anthropic)
            api_key: API key for the provider
            model: The model to use
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Create the LLM client
        llm_client_factory = LLMClientFactory()
        self.llm_client = llm_client_factory.create_client(
            provider=self.provider,
            api_key=self.api_key
        )
        
        # Set the model
        if model:
            self.model = model
        else:
            self.model = LLMClientFactory.get_default_model(self.provider)
        
        logger.info(f"Initialized LLM Component with provider: {self.provider} and model: {self.model}")
    
    def generate(self, prompt: str) -> str:
        """Generate text from a prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The generated text
        """
        try:
            # Log the prompt
            logger.debug(f"Generating text for prompt (first 100 chars): {prompt[:100]}...")
            
            # Format messages differently based on the provider
            if self.provider == "anthropic":
                # Anthropic requires a top-level system parameter as a string
                system_message = "You are a strategic advisor providing insightful and actionable guidance."
                user_messages = [{"role": "user", "content": prompt}]
                
                response = self.llm_client.create_message(
                    model=self.model,
                    messages=user_messages,
                    max_tokens=self.max_tokens, 
                    temperature=self.temperature,
                    system=system_message  # Pass system message as a string for Anthropic
                )
                
                # Extract content from Anthropic response
                if hasattr(response, 'content') and len(response.content) > 0:
                    response_text = response.content[0].text
                else:
                    response_text = str(response)
            else:
                # Default format for OpenAI and others
                messages = [
                    {"role": "system", "content": "You are a strategic advisor providing insightful and actionable guidance."},
                    {"role": "user", "content": prompt}
                ]
                
                response = self.llm_client.create_message(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens, 
                    temperature=self.temperature
                )
                
                # Extract content from OpenAI response
                if hasattr(response, 'choices') and len(response.choices) > 0:
                    response_text = response.choices[0].message.content
                else:
                    response_text = str(response)
            
            # Log the response
            logger.debug(f"Generated text (first 100 chars): {response_text[:100]}...")
            
            return response_text
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error generating text: {error_msg}")
            
            # Check for API key related errors
            if "401" in error_msg or "invalid_api_key" in error_msg or "Incorrect API key" in error_msg:
                return "ERROR: The API key provided is invalid or unauthorized."
            
            # Check for rate limit errors
            elif "quota" in error_msg or "capacity" in error_msg or "rate limit" in error_msg:
                return "ERROR: API rate limit exceeded. Please try again later."
            
            # Generic error
            else:
                return f"ERROR: {error_msg}" 