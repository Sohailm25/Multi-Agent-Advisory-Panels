"""Strategic planner module for multi-agent advisory planning."""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import uuid

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Local imports
from iterative_research_tool.core.visualization import Visualizer
from iterative_research_tool.core.user_memory import UserMemory
from iterative_research_tool.core.panel_factory import panel_factory
from iterative_research_tool.panels.time_travel import TimeTravel
from iterative_research_tool.core.llm_client import LLMClientFactory

logger = logging.getLogger(__name__)

class StrategicPlanner:
    """Strategic planner that coordinates multi-agent advisory panels."""
    
    def __init__(
        self,
        llm_provider: str = "anthropic",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        memory_file: Optional[str] = None,
        output_dir: Optional[str] = None,
        panel_type: str = "cognitive-diversity",
        custom_panel_paths: Optional[List[str]] = None,
        verbose: bool = False
    ):
        """Initialize the strategic planner.
        
        Args:
            llm_provider: The LLM provider to use (anthropic, openai, or perplexity)
            api_key: API key for the LLM provider
            model: Model to use for planning (if None, uses the default model for the provider)
            memory_file: Path to the memory file
            output_dir: Directory to save outputs
            panel_type: Type of panel to use
            custom_panel_paths: Optional list of paths to custom panel implementations
            verbose: Whether to print verbose output
        """
        self.llm_provider = llm_provider.lower()
        self.api_key = api_key or os.environ.get(f"{self.llm_provider.upper()}_API_KEY")
        
        # Set up the LLM client
        try:
            self.llm_client = LLMClientFactory.create_client(self.llm_provider, self.api_key)
            logger.info(f"Using LLM provider: {self.llm_provider}")
        except Exception as e:
            logger.error(f"Error creating LLM client: {str(e)}")
            raise
        
        # Set the model or use the default for the provider
        self.model = model or LLMClientFactory.get_default_model(self.llm_provider)
        logger.info(f"Using model: {self.model}")
        
        self.verbose = verbose
        
        # Set up output directory
        self.output_dir = output_dir or os.path.expanduser("~/iterative_research_tool_output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize user memory
        self.user_memory = UserMemory(
            memory_file=memory_file,
            llm_provider=self.llm_provider,
            api_key=self.api_key,
            model=self.model
        )
        
        # Initialize visualizer
        self.visualizer = Visualizer()
        
        # Initialize time travel capability
        self.time_travel = TimeTravel()
        
        # Initialize panel factory and discover panels
        panel_factory.discover_panels(custom_panel_paths)
        
        # Set up the panel based on the panel type
        self.panel_type = panel_type
        self.panel = self._initialize_panel(panel_type)
        
        # Initialize state for the current session
        self.session_id = str(uuid.uuid4())
        self.current_state = {
            "session_id": self.session_id,
            "query": "",
            "context": {},
            "panel_outputs": {},
            "final_plan": None,
            "feedback": None,
            "history": [],
            "timestamps": {
                "start": time.time(),
                "end": None
            }
        }
    
    def _initialize_panel(self, panel_type: str) -> Any:
        """Initialize the appropriate panel based on the panel type.
        
        Args:
            panel_type: The type of panel to use
            
        Returns:
            The initialized panel
            
        Raises:
            ValueError: If the panel type is not found
        """
        try:
            logger.info(f"Initializing panel: {panel_type}")
            return panel_factory.create_panel(
                panel_type,
                llm_provider=self.llm_provider,
                api_key=self.api_key,
                model=self.model,
                visualizer=self.visualizer
            )
        except ValueError as e:
            logger.error(f"Error initializing panel: {str(e)}")
            raise
    
    def get_available_panels(self) -> List[str]:
        """Get a list of available panel types.
        
        Returns:
            List of available panel types
        """
        return panel_factory.list_available_panels()
    
    def get_panel_info(self, panel_type: str) -> Dict[str, Any]:
        """Get information about a panel type.
        
        Args:
            panel_type: The panel type to get information for
            
        Returns:
            Dictionary with panel information
        """
        return panel_factory.get_panel_info(panel_type)
    
    def generate_strategic_plan(self, query: str) -> Dict[str, Any]:
        """Generate a strategic plan for the given query.
        
        Args:
            query: The query to plan for
            
        Returns:
            The strategic plan
        """
        # Initialize session
        session_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Initialize state
        self.current_state = {
            "query": query,
            "session_id": session_id,
            "start_time": start_time,
            "panel_type": self.panel_type,
            "panel_output": {},
            "final_plan": {},
            "feedback": {},
            "timestamps": {
                "start": start_time
            },
            "queries": []  # Add an empty queries list for user memory
        }
        
        # Save initial state
        self.time_travel.save_state(self.current_state.copy(), "initial")
        
        # Get user context from memory
        context = self.user_memory.get_context(query)
        self.current_state["context"] = context
        
        # Display information
        if self.verbose:
            self.visualizer.display_message(f"Starting strategic planning session ({self.session_id})")
            self.visualizer.display_message(f"Query: {query}")
            self.visualizer.display_message(f"Panel: {self.panel_type}")
            self.visualizer.display_message(f"Model: {self.model}")
            if context:
                self.visualizer.display_message("User Context:")
                for key, value in context.items():
                    self.visualizer.display_message(f"  {key}: {value}")
        
        try:
            # Run the panel to generate the plan
            self.visualizer.display_message(f"Executing strategic planning session with {self.panel_type.title()} Panel...")
            
            # Run the panel
            panel_output = self.panel.run(query, context)
            self.current_state["panel_outputs"] = panel_output
            
            # Generate the final plan by summarizing the panel output
            final_plan = self._generate_final_plan(query, panel_output)
            self.current_state["final_plan"] = final_plan
            
            # Save the state for this session
            self.current_state["timestamps"]["end"] = time.time()
            self._save_session_output()
            
            return final_plan
            
        except Exception as e:
            logger.error(f"Error in strategic planning session: {str(e)}")
            self.visualizer.display_message(f"Error: {str(e)}")
            raise
    
    def _generate_final_plan(self, query: str, panel_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a final plan by summarizing the panel output.
        
        Args:
            query: The original query
            panel_output: The output from the panel
            
        Returns:
            The final strategic plan
        """
        self.visualizer.display_message("Generating final strategic plan...")
        
        # Create a prompt to generate the final plan
        prompt = f"""You are a strategic planning expert. Given the following query and panel output, create a comprehensive strategic plan.

Query: {query}

Panel Output:
{json.dumps(panel_output, indent=2)}

Your task is to synthesize this information into a clear, actionable strategic plan with the following sections:
1. Executive Summary
2. Key Insights
3. Strategic Recommendations
4. Implementation Steps
5. Potential Challenges and Mitigations
6. Success Metrics

Format your response as JSON with these sections as keys.
"""
        
        try:
            # Call the LLM to generate the final plan
            response = self.llm_client.create_message(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000
            )
            
            # Extract the JSON from the response
            if hasattr(response, 'content') and isinstance(response.content, list):
                response_text = response.content[0].text
            else:
                response_text = response.choices[0].message.content
            
            # Find JSON in the response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                final_plan = json.loads(json_str)
                
                # Add metadata
                final_plan["query"] = query
                final_plan["timestamp"] = time.time()
                final_plan["model"] = self.model
                
                return final_plan
            else:
                logger.warning("Could not find JSON in final plan response")
                return {
                    "error": "Could not generate final plan",
                    "query": query,
                    "timestamp": time.time(),
                    "model": self.model
                }
                
        except Exception as e:
            logger.error(f"Error generating final plan: {str(e)}")
            return {
                "error": f"Error generating final plan: {str(e)}",
                "query": query,
                "timestamp": time.time(),
                "model": self.model
            }
    
    def _save_session_output(self) -> None:
        """Save the current session output to a file."""
        try:
            output_file = os.path.join(self.output_dir, f"session_{self.session_id}_{int(time.time())}.json")
            with open(output_file, 'w') as f:
                json.dump(self.current_state, f, indent=2)
            
            logger.info(f"Saved session output to {output_file}")
            self.visualizer.display_message(f"Session output saved to: {output_file}")
            
            # Update user memory with the session information
            self.user_memory.update_memory(
                query=self.current_state["query"],
                context=self.current_state["context"],
                output=self.current_state
            )
            
        except Exception as e:
            logger.error(f"Error saving session output: {str(e)}")
    
    def collect_feedback(self, rating: int, comments: str) -> Dict[str, Any]:
        """
        Collect feedback on the generated plan.
        
        Args:
            rating: Rating from 1-5
            comments: Feedback comments
            
        Returns:
            The feedback data
        """
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
            
        feedback = {
            "rating": rating,
            "comments": comments,
            "timestamp": time.time()
        }
        
        self.current_state["feedback"] = feedback
        self._save_session_output()
        
        return feedback
    
    def time_travel_to(self, checkpoint: str) -> Dict[str, Any]:
        """Travel back in time to a specific checkpoint.
        
        Args:
            checkpoint: The checkpoint to travel to
            
        Returns:
            The state at the checkpoint
        """
        state = self.time_travel.load_state(checkpoint)
        if state:
            self.current_state = state
            self.visualizer.display_message(f"Traveled back to checkpoint: {checkpoint}")
            
            # If we're at the final checkpoint, display the plan
            if checkpoint == "final" and self.current_state.get("final_plan"):
                self.visualizer.display_plan(self.current_state["final_plan"])
            
            return state
        else:
            self.visualizer.display_error(f"Checkpoint {checkpoint} not found")
            return self.current_state
    
    def get_available_checkpoints(self) -> List[str]:
        """Get the available time travel checkpoints.
        
        Returns:
            List of available checkpoints
        """
        return self.time_travel.get_checkpoints()
    
    def explore_alternative(self, query: str) -> Dict[str, Any]:
        """Explore an alternative approach to the current plan.
        
        Args:
            query: The modified query to explore
            
        Returns:
            The alternative plan
        """
        # Save the current state
        original_state = self.current_state.copy()
        
        # Generate a new plan with the modified query
        alternative_plan = self.generate_strategic_plan(query)
        
        # Save the alternative state
        self.time_travel.save_state(self.current_state.copy(), "alternative")
        
        # Restore the original state
        self.current_state = original_state
        
        # Return the alternative plan
        return alternative_plan 