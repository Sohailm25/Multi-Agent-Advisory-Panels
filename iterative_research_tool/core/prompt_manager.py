"""Module for managing prompt templates."""

import os
import logging
import json
from pathlib import Path
from typing import Dict, Optional, Union

logger = logging.getLogger(__name__)

class PromptManager:
    """Manager for handling prompt templates."""
    
    def __init__(self, prompts_dir: Optional[Union[str, Path]] = None):
        """Initialize the prompt manager.
        
        Args:
            prompts_dir: Directory containing prompt template files. 
                         If None, uses default locations.
        """
        self.prompts_dir = None
        self.prompt_cache = {}
        
        # Try to find prompts directory
        if prompts_dir:
            self.prompts_dir = Path(prompts_dir)
        else:
            # Try different locations in order of preference
            possible_locations = [
                # Current working directory
                Path.cwd() / "prompts",
                # Package directory
                Path(__file__).parent.parent / "prompts",
                # User home directory
                Path.home() / ".iterative_research_tool" / "prompts",
            ]
            
            for location in possible_locations:
                if location.exists() and location.is_dir():
                    self.prompts_dir = location
                    break
        
        if not self.prompts_dir or not self.prompts_dir.exists():
            logger.warning(f"No prompts directory found. Using default prompts.")
        else:
            logger.info(f"Using prompts from: {self.prompts_dir}")
    
    def get_prompt(self, prompt_name: str) -> str:
        """Get a prompt template by name.
        
        Args:
            prompt_name: Name of the prompt template (without extension)
            
        Returns:
            Prompt template text
        """
        # Check cache first
        if prompt_name in self.prompt_cache:
            return self.prompt_cache[prompt_name]
        
        # Try to load from file
        if self.prompts_dir:
            prompt_path = self.prompts_dir / f"{prompt_name}.md"
            if prompt_path.exists():
                try:
                    with open(prompt_path, 'r', encoding='utf-8') as f:
                        prompt_text = f.read()
                    
                    # Cache for future use
                    self.prompt_cache[prompt_name] = prompt_text
                    return prompt_text
                except Exception as e:
                    logger.error(f"Error loading prompt {prompt_name}: {e}")
        
        # If we get here, we couldn't load the prompt, so use default
        return self._get_default_prompt(prompt_name)
    
    def _get_default_prompt(self, prompt_name: str) -> str:
        """Get default prompt templates.
        
        Args:
            prompt_name: Name of the prompt template
            
        Returns:
            Default prompt template text
        """
        # Simplified default prompts
        defaults = {
            "cli_input_prompt": """SYSTEM PROMPT:
You are an expert research query formulator. Transform the user input into optimal queries for research.

USER INPUT:
{user_cli_input}""",
            
            "perplexity_to_claude_prompt": """SYSTEM PROMPT:
You are a research enhancement specialist. Transform this raw research into a more comprehensive document.

OUTPUT FORMAT:
1. Enhanced Document
2. Further Research Directions as JSON within triple backticks""",
            
            "claude_to_perplexity_deeper_prompt": """SYSTEM PROMPT:
You are a research query expansion specialist. Transform research questions into optimal queries.""",
            
            "loop_controller_prompt": """SYSTEM PROMPT:
You are the controller for an iterative research process. Assess progress and determine when to continue or conclude."""
        }
        
        if prompt_name in defaults:
            logger.info(f"Using default prompt for {prompt_name}")
            return defaults[prompt_name]
        else:
            logger.error(f"No default prompt found for {prompt_name}")
            return f"ERROR: No prompt template found for {prompt_name}"
    
    def format_prompt(self, prompt_name: str, **kwargs) -> str:
        """Format a prompt template with the provided arguments.
        
        Args:
            prompt_name: Name of the prompt template
            **kwargs: Arguments to format the template with
            
        Returns:
            Formatted prompt text
        """
        prompt_template = self.get_prompt(prompt_name)
        
        # Log the template and parameters for debugging
        logger.debug(f"Formatting prompt '{prompt_name}' with parameters: {list(kwargs.keys())}")
        
        # Check for common parameters that might be missing and provide defaults
        if prompt_name == "perplexity_to_claude_prompt":
            if "document_content" not in kwargs:
                logger.info(f"Adding default document_content parameter to {prompt_name}")
                kwargs["document_content"] = "No research content available yet."
            
            # The research_questions parameter is not actually used in the template,
            # so we don't need to add it as a default
        
        if prompt_name == "claude_to_perplexity_deeper_prompt" and "research_questions" not in kwargs:
            logger.info(f"Adding default research_questions parameter to {prompt_name}")
            default_questions = {
                "research_questions": [
                    {
                        "question": "What is the most current information about this topic?",
                        "importance": "Provides baseline knowledge",
                        "expected_insights": "Basic understanding of the subject"
                    }
                ]
            }
            kwargs["research_questions"] = json.dumps(default_questions, indent=2)
        
        # Debugging output to verify actual template content
        template_preview = prompt_template[:500] + "..." if len(prompt_template) > 500 else prompt_template
        logger.debug(f"Template content: {template_preview}")
        
        try:
            return prompt_template.format(**kwargs)
        except KeyError as e:
            param_name = str(e).strip("'")
            logger.error(f"Missing required parameter for prompt {prompt_name}: {param_name}")
            
            # Special case for perplexity_to_claude_prompt template
            if prompt_name == "perplexity_to_claude_prompt" and param_name == "\n     \"research_questions\"":
                logger.info(f"Ignoring research_questions parameter for {prompt_name} as it's not actually used")
                # Remove the parameter from the error and try again with just document_content
                return prompt_template.format(document_content=kwargs.get("document_content", "No content provided"))
            
            # Check if the parameter is in the template but not in kwargs
            if "{" + param_name + "}" in prompt_template:
                logger.info(f"Adding default value for missing parameter '{param_name}'")
                kwargs[param_name] = f"[Default value for {param_name}]"
                try:
                    return prompt_template.format(**kwargs)
                except Exception as ex:
                    logger.error(f"Failed to format prompt {prompt_name} even with default values: {ex}")
            else:
                logger.error(f"Parameter '{param_name}' not found in template but reported missing. Template issue?")
            
            return prompt_template 