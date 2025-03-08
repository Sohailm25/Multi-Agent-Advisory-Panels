#!/usr/bin/env python3
"""Test script for the Claude client."""

import os
import logging
from dotenv import load_dotenv
from iterative_research_tool.core.claude_client import ClaudeClient

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    """Test the Claude client."""
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        logger.error("CLAUDE_API_KEY not found in environment variables")
        return
    
    # Create client
    claude_client = ClaudeClient(
        api_key=api_key,
        model=os.getenv("CLAUDE_MODEL", "claude-3-7-sonnet-20250219"),
        temperature=0.2
    )
    
    # Test generate method
    logger.info("Testing generate method...")
    response = claude_client.generate(
        system_prompt="You are a helpful assistant.",
        user_prompt="What is quantum computing?",
        max_tokens=100
    )
    
    logger.info(f"Response: {response.content[0].text}")
    
    # Test generate_content method
    logger.info("Testing generate_content method...")
    content = claude_client.generate_content(
        prompt="SYSTEM PROMPT: You are a helpful assistant.\n\nDOCUMENT CONTENT: What is quantum computing?",
        max_tokens=100
    )
    
    logger.info(f"Content: {content}")

if __name__ == "__main__":
    main() 