"""Client for interacting with the Claude API."""

import logging
import time
from typing import Dict, List, Any, Optional
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import tiktoken

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Client for interacting with the Claude API."""
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "claude-3-opus-20240229",
        temperature: float = 0.2,
        max_retries: int = 3
    ):
        """Initialize Claude client.
        
        Args:
            api_key: Claude API key
            model: Claude model to use
            temperature: Temperature for generation (0.0-1.0)
            max_retries: Maximum number of retries for API calls
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.api_key = api_key  # Store API key directly as an attribute
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.cost_per_1k_input_tokens = 0.003  # Rate for Claude 3.7 Sonnet ($3 per 1M tokens)
        self.cost_per_1k_output_tokens = 0.015  # Rate for Claude 3.7 Sonnet ($15 per 1M tokens)
        self.encoder = tiktoken.get_encoding("cl100k_base")  # Claude uses cl100k
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        return len(self.encoder.encode(text))
    
    def estimate_cost(self, input_text: str, max_tokens_output: int) -> float:
        """Estimate cost of a Claude API call.
        
        Args:
            input_text: Input text to generate from
            max_tokens_output: Maximum tokens to generate
            
        Returns:
            Estimated cost in USD
        """
        input_tokens = self.count_tokens(input_text)
        
        # Claude charges per 1k tokens, rounded up
        input_cost = (input_tokens / 1000) * self.cost_per_1k_input_tokens
        
        # Estimate output cost (assuming max_tokens are used)
        output_cost = (max_tokens_output / 1000) * self.cost_per_1k_output_tokens
        
        return input_cost + output_cost
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type((anthropic.RateLimitError, anthropic.APIConnectionError)),
        reraise=True
    )
    def generate(
        self, 
        system_prompt: str = "", 
        user_prompt: str = "",
        max_tokens: int = 4000,
        temperature: float = 0.2
    ):
        """Generate text with Claude.
        
        Args:
            system_prompt: System instructions for Claude
            user_prompt: User prompt for Claude
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            
        Returns:
            Dictionary with generated text, usage, and other metadata
        """
        # Debug logging
        logger.debug(f"Claude generate called with:")
        logger.debug(f"System prompt length: {len(system_prompt)}")
        logger.debug(f"User prompt preview (first 300 chars): {user_prompt[:300]}...")
        logger.debug(f"Max tokens: {max_tokens}")
        logger.debug(f"Temperature: {temperature}")
        
        try:
            # Estimate cost
            prompt_text = system_prompt + "\n" + user_prompt
            input_tokens = len(prompt_text) // 4  # Rough estimate, 4 chars per token
            output_tokens = max_tokens
            
            # No need to create a new client, use the existing one
            # client = anthropic.Anthropic(
            #    api_key=self.api_key
            # )
            
            logger.debug(f"Calling Claude API with {self.model}")
            
            # Call the API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Calculate costs
            response_tokens = response.usage.output_tokens
            prompt_tokens = response.usage.input_tokens
            
            input_cost = (prompt_tokens / 1000) * self.cost_per_1k_input_tokens
            output_cost = (response_tokens / 1000) * self.cost_per_1k_output_tokens
            total_cost = input_cost + output_cost
            
            self.last_call_cost = total_cost
            
            logger.debug(f"Claude API call: {prompt_tokens} input tokens, {response_tokens} output tokens, ${total_cost:.4f} cost")
            
            # Debug log the response
            logger.debug(f"Claude response preview (first 300 chars): {response.content[0].text[:300]}...")
            
            # Create result object in format consistent with previous API
            result = {
                "text": response.content[0].text,
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": response_tokens,
                    "total_tokens": prompt_tokens + response_tokens
                },
                "cost": total_cost
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            raise

    def generate_content(self, prompt: str, max_tokens: int = 4000, temperature: float = 0.2):
        """Generate content with Claude using a simple prompt.
        
        Args:
            prompt: Full prompt for Claude
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            
        Returns:
            Generated text content
        """
        # Add detailed logging
        logger.debug(f"Claude generate_content called with:")
        logger.debug(f"Prompt length: {len(prompt)}")
        logger.debug(f"Prompt preview (first 500 chars): {prompt[:500]}...")
        logger.debug(f"Prompt last 500 chars: {prompt[-500:] if len(prompt) > 500 else prompt}")
        logger.debug(f"Max tokens: {max_tokens}")
        logger.debug(f"Temperature: {temperature}")
        
        try:
            # Extract system prompt if it exists
            system_prompt = ""
            user_content = prompt
            
            # Check if the prompt contains a SYSTEM PROMPT: section
            if "SYSTEM PROMPT:" in prompt:
                # Split the prompt into system and user parts
                parts = prompt.split("SYSTEM PROMPT:", 1)
                if len(parts) > 1:
                    # The second part contains the system prompt and the rest
                    system_and_rest = parts[1].strip()
                    
                    # Find where the system prompt ends and user content begins
                    # Look for common section dividers like "DOCUMENT CONTENT:"
                    dividers = ["DOCUMENT CONTENT:", "INPUT:", "PROCESS THE INPUT", "PROCESS THE RESEARCH"]
                    
                    user_content_start_idx = float('inf')
                    for divider in dividers:
                        idx = system_and_rest.find(divider)
                        if idx != -1 and idx < user_content_start_idx:
                            user_content_start_idx = idx
                    
                    if user_content_start_idx < float('inf'):
                        system_prompt = system_and_rest[:user_content_start_idx].strip()
                        user_content = system_and_rest[user_content_start_idx:].strip()
                    else:
                        # If no clear divider, use a heuristic - first 500 chars as system prompt
                        logger.warning("No clear divider found between system prompt and user content - using heuristic")
                        system_prompt = system_and_rest[:500].strip()
                        user_content = prompt  # Keep the full prompt as user content as fallback
            
            logger.debug(f"Extracted system prompt (first 200 chars): {system_prompt[:200]}...")
            logger.debug(f"Extracted user content (first 200 chars): {user_content[:200]}...")
            
            # Use existing client instead of creating a new one
            logger.debug(f"Calling Claude API with {self.model}")
            logger.debug(f"Using system prompt: {len(system_prompt) > 0}")
            
            messages = [{"role": "user", "content": user_content}]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,  # Pass system prompt separately
                messages=messages
            )
            
            # Calculate costs
            response_tokens = response.usage.output_tokens
            prompt_tokens = response.usage.input_tokens
            
            input_cost = (prompt_tokens / 1000) * self.cost_per_1k_input_tokens
            output_cost = (response_tokens / 1000) * self.cost_per_1k_output_tokens
            total_cost = input_cost + output_cost
            
            self.last_call_cost = total_cost
            
            logger.debug(f"Claude API call: {prompt_tokens} input tokens, {response_tokens} output tokens, ${total_cost:.4f} cost")
            
            # Log the response for debugging
            logger.debug(f"Claude response preview (first 500 chars): {response.content[0].text[:500]}...")
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            raise 