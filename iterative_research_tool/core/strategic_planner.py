"""Strategic Planner module using LangGraph for orchestration."""

import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel, Field

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint import MemorySaver
from langgraph.graph.graph import CompiledGraph

# Anthropic imports
from anthropic import Anthropic

# Visualization imports
from iterative_research_tool.core.visualization import TerminalVisualizer, FeedbackCollector

logger = logging.getLogger(__name__)

# Define the state schema
class PlannerState(BaseModel):
    """State for the strategic planner graph."""
    query: str = Field(description="The user's query or question")
    plan: Optional[str] = Field(default=None, description="The generated strategic plan")
    thoughts: List[str] = Field(default_factory=list, description="Thinking process")
    response: Optional[str] = Field(default=None, description="Final response to the user")
    error: Optional[str] = Field(default=None, description="Error message if any")
    feedback: Optional[Dict[str, Any]] = Field(default=None, description="User feedback on the plan")

class StrategicPlanner:
    """Strategic Planner using LangGraph for orchestration."""
    
    def __init__(
        self, 
        claude_api_key: str, 
        claude_model: str = "claude-3-7-sonnet-20250219", 
        prompt_dir: Optional[str] = None,
        visualize: bool = True,
        collect_feedback: bool = True,
        feedback_file: Optional[str] = None
    ):
        """Initialize the strategic planner.
        
        Args:
            claude_api_key: API key for Claude
            claude_model: Claude model to use
            prompt_dir: Directory containing prompt templates
            visualize: Whether to visualize the execution in the terminal
            collect_feedback: Whether to collect feedback on the generated plan
            feedback_file: Path to the feedback file
        """
        self.claude_client = Anthropic(api_key=claude_api_key)
        self.claude_model = claude_model
        
        # Load the strategic planner prompt
        self.prompt_template = self._load_prompt_template(prompt_dir)
        
        # Set up visualization and feedback
        self.visualize = visualize
        self.collect_feedback = collect_feedback
        self.visualizer = TerminalVisualizer() if visualize else None
        self.feedback_collector = FeedbackCollector(
            save_feedback=collect_feedback,
            feedback_file=feedback_file
        ) if collect_feedback else None
        
        # Build the graph
        self.graph = self._build_graph()
        
    def _load_prompt_template(self, prompt_dir: Optional[str] = None) -> str:
        """Load the strategic planner prompt template.
        
        Args:
            prompt_dir: Directory containing prompt templates
            
        Returns:
            The prompt template as a string
        """
        # Default prompt directories to check
        prompt_dirs = [
            prompt_dir,
            os.getenv("PROMPTS_DIRECTORY"),
            "prompts",
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "prompts"),
        ]
        
        # Filter out None values
        prompt_dirs = [d for d in prompt_dirs if d]
        
        # Try to find the prompt file in the directories
        prompt_filename = "strategic_planner.md"
        for directory in prompt_dirs:
            if not directory:
                continue
                
            prompt_path = Path(directory) / prompt_filename
            if prompt_path.exists():
                logger.info(f"Loading prompt template from {prompt_path}")
                with open(prompt_path, "r", encoding="utf-8") as f:
                    return f.read() + "\n\nResearch Query: {query}\n\n"
        
        # If prompt file not found, use the default prompt
        logger.warning(f"Prompt file {prompt_filename} not found in any of the prompt directories. Using default prompt.")
        return """
You are a Strategic Research Planner, an expert at breaking down complex research questions into clear, actionable plans.

Your task is to analyze the given research query and develop a comprehensive strategic plan that:
1. Identifies the core components and sub-questions within the main research query
2. Outlines a logical sequence of investigation steps
3. Highlights potential challenges and how to address them
4. Suggests specific resources, methodologies, or frameworks to apply
5. Provides clear success criteria for each stage of the research

Think step-by-step and be thorough in your analysis. Your plan should be detailed enough that someone could follow it to conduct high-quality research on the topic.

Research Query: {query}

Strategic Research Plan:
"""
        
    def _build_graph(self) -> CompiledGraph:
        """Build the LangGraph for strategic planning."""
        # Create the graph with the state schema
        graph = StateGraph(PlannerState)
        
        # Add nodes
        graph.add_node("generate_thoughts", self._generate_thoughts)
        graph.add_node("create_plan", self._create_plan)
        graph.add_node("format_response", self._format_response)
        graph.add_node("collect_feedback", self._collect_feedback)
        
        # Add edges
        graph.add_edge("generate_thoughts", "create_plan")
        graph.add_edge("create_plan", "format_response")
        graph.add_edge("format_response", "collect_feedback")
        graph.add_edge("collect_feedback", END)
        
        # Set the entry point
        graph.set_entry_point("generate_thoughts")
        
        # Add event callbacks for visualization
        if self.visualize:
            graph.add_listener(self._node_started)
            graph.add_listener(self._node_ended)
        
        # Compile the graph
        return graph.compile()
    
    def _node_started(self, event_data: Dict[str, Any]):
        """Handle node started event for visualization.
        
        Args:
            event_data: Event data from LangGraph
        """
        if event_data["event_type"] == "node_start" and self.visualizer:
            node_name = event_data["node_name"]
            self.visualizer.update_node(node_name)
    
    def _node_ended(self, event_data: Dict[str, Any]):
        """Handle node ended event for visualization.
        
        Args:
            event_data: Event data from LangGraph
        """
        if event_data["event_type"] == "node_end" and self.visualizer:
            node_name = event_data["node_name"]
            self.visualizer.show_node_complete(node_name)
    
    def _generate_thoughts(self, state: PlannerState) -> PlannerState:
        """Generate initial thoughts about the query."""
        logger.info(f"Generating thoughts for query: {state.query}")
        
        try:
            # Generate thoughts using Claude
            message = self.claude_client.messages.create(
                model=self.claude_model,
                max_tokens=1000,
                temperature=0.7,
                system="You are a strategic research planner. Think step by step about the query to understand its components and requirements.",
                messages=[
                    {"role": "user", "content": f"I need to research: {state.query}\n\nWhat are the key components, challenges, and approaches I should consider? Think step by step."}
                ]
            )
            
            thoughts = message.content[0].text
            state.thoughts.append(thoughts)
            
            # Show thoughts in the visualizer
            if self.visualize:
                self.visualizer.show_thought(thoughts)
                
            return state
            
        except Exception as e:
            logger.error(f"Error generating thoughts: {str(e)}")
            state.error = f"Error generating thoughts: {str(e)}"
            return state
    
    def _create_plan(self, state: PlannerState) -> PlannerState:
        """Create a strategic plan based on the thoughts."""
        logger.info("Creating strategic plan")
        
        if state.error:
            return state
            
        try:
            # Generate the plan using Claude with the strategic planner prompt
            message = self.claude_client.messages.create(
                model=self.claude_model,
                max_tokens=2000,
                temperature=0.5,
                system="You are a strategic research planner. Create a detailed, structured research plan.",
                messages=[
                    {"role": "user", "content": self.prompt_template.format(query=state.query)}
                ]
            )
            
            state.plan = message.content[0].text
            
            # Show plan in the visualizer
            if self.visualize:
                self.visualizer.show_plan(state.plan)
                
            return state
            
        except Exception as e:
            logger.error(f"Error creating plan: {str(e)}")
            state.error = f"Error creating plan: {str(e)}"
            return state
    
    def _format_response(self, state: PlannerState) -> PlannerState:
        """Format the final response to the user."""
        logger.info("Formatting response")
        
        if state.error:
            state.response = f"Error: {state.error}"
            return state
            
        # Format the response with the plan
        state.response = state.plan
        return state
    
    def _collect_feedback(self, state: PlannerState) -> PlannerState:
        """Collect feedback on the generated plan."""
        logger.info("Collecting feedback")
        
        if state.error or not self.collect_feedback:
            return state
            
        try:
            # Collect feedback using the feedback collector
            feedback = self.feedback_collector.collect_feedback(
                query=state.query,
                plan=state.plan
            )
            
            # Store feedback in the state
            state.feedback = feedback
            
            return state
            
        except Exception as e:
            logger.error(f"Error collecting feedback: {str(e)}")
            # Don't set state.error here as we don't want to fail the whole process
            # just because feedback collection failed
            return state
    
    def run(self, query: str) -> str:
        """Run the strategic planner on the given query.
        
        Args:
            query: The research query to plan for
            
        Returns:
            The strategic plan as a string
        """
        logger.info(f"Running strategic planner for query: {query}")
        
        # Start visualization
        if self.visualize:
            self.visualizer.start_visualization("Strategic Planner")
        
        # Initialize the state
        initial_state = PlannerState(query=query)
        
        # Create a memory saver for checkpointing
        memory_saver = MemorySaver()
        
        # Run the graph
        result = self.graph.invoke(
            initial_state,
            {"configurable": {"checkpoint_saver": memory_saver}}
        )
        
        # End visualization
        if self.visualize:
            self.visualizer.end_visualization()
        
        # Return the response or error message
        if result.error:
            return f"Error: {result.error}"
        return result.response 