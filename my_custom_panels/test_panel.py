"""Custom Panel Template for Multi-Agent Advisory Planner

This template provides a starting point for creating your own custom advisory panel.
Follow the structure and implement your own agent prompts and workflow logic.
"""

import logging
from typing import Dict, List, Any, Optional
import json

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Anthropic imports
from anthropic import Anthropic

# Local imports
from iterative_research_tool.panels import BasePanel

logger = logging.getLogger(__name__)

class CustomPanel(BasePanel):
    """Custom Panel for multi-agent advisory planning.
    
    This is a template for creating your own custom panel. 
    Replace this docstring with a meaningful description of your panel.
    
    Your panel should have a clear purpose and approach to providing strategic advice.
    """
    
    def __init__(
        self,
        anthropic_api_key: str,
        model: str = "claude-3-7-sonnet-20250219",
        visualizer = None
    ):
        """Initialize the Custom Panel.
        
        Args:
            anthropic_api_key: API key for Anthropic
            model: Model to use for planning
            visualizer: Visualizer instance for displaying progress
        """
        self.anthropic_api_key = anthropic_api_key
        self.model = model
        self.client = Anthropic(api_key=anthropic_api_key)
        self.visualizer = visualizer
        
        # Define agent prompts
        self.agent_prompts = {
            "agent1": self._get_agent1_prompt(),
            "agent2": self._get_agent2_prompt(),
            "agent3": self._get_agent3_prompt(),
            "synthesizer": self._get_synthesizer_prompt()
        }
        
        # Initialize the graph
        self.graph = self._build_graph()
        
    def _get_agent1_prompt(self) -> str:
        """Get the prompt for Agent 1.
        
        Replace with your own prompt that defines this agent's role, tasks, and output format.
        """
        return """
        You are Agent 1 who analyzes [specific aspect of the problem].
        
        Your role is to:
        - [Task 1]
        - [Task 2]
        - [Task 3]
        
        Format your response as a JSON object with the following structure:
        {
            "agent1_analysis": {
                "summary": "Brief summary of your analysis",
                "key_points": ["point 1", "point 2", ...],
                "detailed_analysis": {
                    "aspect1": "Analysis of aspect 1",
                    "aspect2": "Analysis of aspect 2",
                    ...
                },
                "recommendations": ["recommendation 1", "recommendation 2", ...]
            }
        }
        """
        
    def _get_agent2_prompt(self) -> str:
        """Get the prompt for Agent 2.
        
        Replace with your own prompt that defines this agent's role, tasks, and output format.
        """
        return """
        You are Agent 2 who analyzes [another specific aspect of the problem].
        
        Your role is to:
        - [Task 1]
        - [Task 2]
        - [Task 3]
        
        Format your response as a JSON object with the following structure:
        {
            "agent2_analysis": {
                "summary": "Brief summary of your analysis",
                "key_points": ["point 1", "point 2", ...],
                "detailed_analysis": {
                    "aspect1": "Analysis of aspect 1",
                    "aspect2": "Analysis of aspect 2",
                    ...
                },
                "recommendations": ["recommendation 1", "recommendation 2", ...]
            }
        }
        """
        
    def _get_agent3_prompt(self) -> str:
        """Get the prompt for Agent 3.
        
        Replace with your own prompt that defines this agent's role, tasks, and output format.
        """
        return """
        You are Agent 3 who analyzes [another specific aspect of the problem].
        
        Your role is to:
        - [Task 1]
        - [Task 2]
        - [Task 3]
        
        Format your response as a JSON object with the following structure:
        {
            "agent3_analysis": {
                "summary": "Brief summary of your analysis",
                "key_points": ["point 1", "point 2", ...],
                "detailed_analysis": {
                    "aspect1": "Analysis of aspect 1",
                    "aspect2": "Analysis of aspect 2",
                    ...
                },
                "recommendations": ["recommendation 1", "recommendation 2", ...]
            }
        }
        """
        
    def _get_synthesizer_prompt(self) -> str:
        """Get the prompt for the Synthesizer agent.
        
        The synthesizer agent should combine the analyses from all other agents
        into a cohesive strategic plan or recommendation.
        """
        return """
        You are a synthesizer who combines insights from various specialized agents to create a comprehensive plan.
        
        Your role is to:
        - Integrate insights from all agents into a cohesive whole
        - Resolve any contradictions or tensions between different analyses
        - Prioritize recommendations based on their strategic importance
        - Create an actionable, comprehensive plan
        
        Format your response as a JSON object with the following structure:
        {
            "Executive Summary": "Brief executive summary of the strategic plan",
            "Key Insights": ["insight 1", "insight 2", ...],
            "Strategic Recommendations": [
                {
                    "recommendation": "Description of the recommendation",
                    "rationale": "Rationale for this recommendation",
                    "implementation_steps": ["step 1", "step 2", ...],
                    "expected_impact": "Expected impact of this recommendation",
                    "priority": "High/Medium/Low"
                },
                ...
            ],
            "Implementation Timeline": {
                "short_term": ["action 1", "action 2", ...],
                "medium_term": ["action 1", "action 2", ...],
                "long_term": ["action 1", "action 2", ...]
            },
            "Success Metrics": ["metric 1", "metric 2", ...],
            "Potential Challenges": [
                {
                    "challenge": "Description of the challenge",
                    "mitigation_approach": "Approach to mitigate this challenge"
                },
                ...
            ]
        }
        """
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for the Custom Panel.
        
        This method defines the workflow of how agents interact with each other.
        Customize the graph structure based on your panel's requirements.
        """
        # Define the state schema
        state_schema = {
            "query": str,
            "context": dict,
            "agent1_analysis": dict,
            "agent2_analysis": dict,
            "agent3_analysis": dict,
            "strategic_plan": dict
        }
        
        # Create the graph
        graph = StateGraph(state_schema=state_schema)
        
        # Define the nodes
        
        # Agent 1 node
        def agent1_function(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Agent 1", "processing")
                
            query = state["query"]
            context = state["context"]
            
            prompt = self.agent_prompts["agent1"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}"}
                ]
            )
            
            try:
                content = response.content[0].text
                # Extract JSON from the response
                import re
                json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
                
                agent1_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Agent 1", "Complete")
                    
                return {"agent1_analysis": agent1_analysis}
            except Exception as e:
                logger.error(f"Error parsing Agent 1 response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Agent 1", "Error")
                return {"agent1_analysis": {"error": str(e), "raw_response": content}}
        
        # Agent 2 node
        def agent2_function(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Agent 2", "processing")
                
            query = state["query"]
            context = state["context"]
            agent1_analysis = state["agent1_analysis"]
            
            prompt = self.agent_prompts["agent2"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nAgent 1 Analysis: {json.dumps(agent1_analysis)}"}
                ]
            )
            
            try:
                content = response.content[0].text
                # Extract JSON from the response
                import re
                json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
                
                agent2_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Agent 2", "Complete")
                    
                return {"agent2_analysis": agent2_analysis}
            except Exception as e:
                logger.error(f"Error parsing Agent 2 response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Agent 2", "Error")
                return {"agent2_analysis": {"error": str(e), "raw_response": content}}
        
        # Agent 3 node
        def agent3_function(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Agent 3", "processing")
                
            query = state["query"]
            context = state["context"]
            agent1_analysis = state["agent1_analysis"]
            agent2_analysis = state["agent2_analysis"]
            
            prompt = self.agent_prompts["agent3"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"""
                    Query: {query}
                    
                    Context: {json.dumps(context)}
                    
                    Agent 1 Analysis: {json.dumps(agent1_analysis)}
                    
                    Agent 2 Analysis: {json.dumps(agent2_analysis)}
                    """}
                ]
            )
            
            try:
                content = response.content[0].text
                # Extract JSON from the response
                import re
                json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
                
                agent3_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Agent 3", "Complete")
                    
                return {"agent3_analysis": agent3_analysis}
            except Exception as e:
                logger.error(f"Error parsing Agent 3 response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Agent 3", "Error")
                return {"agent3_analysis": {"error": str(e), "raw_response": content}}
        
        # Synthesizer node
        def synthesizer_function(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Synthesizer", "processing")
                
            query = state["query"]
            context = state["context"]
            agent1_analysis = state["agent1_analysis"]
            agent2_analysis = state["agent2_analysis"]
            agent3_analysis = state["agent3_analysis"]
            
            prompt = self.agent_prompts["synthesizer"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"""
                    Query: {query}
                    
                    Context: {json.dumps(context)}
                    
                    Agent 1 Analysis: {json.dumps(agent1_analysis)}
                    
                    Agent 2 Analysis: {json.dumps(agent2_analysis)}
                    
                    Agent 3 Analysis: {json.dumps(agent3_analysis)}
                    """}
                ]
            )
            
            try:
                content = response.content[0].text
                # Extract JSON from the response
                import re
                json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
                
                strategic_plan = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Synthesizer", "Complete")
                    
                return {"strategic_plan": strategic_plan}
            except Exception as e:
                logger.error(f"Error parsing Synthesizer response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Synthesizer", "Error")
                return {"strategic_plan": {"error": str(e), "raw_response": content}}
        
        # Add nodes to the graph
        graph.add_node("agent1", agent1_function)
        graph.add_node("agent2", agent2_function)
        graph.add_node("agent3", agent3_function)
        graph.add_node("synthesizer", synthesizer_function)
        
        # Define the edges
        graph.add_edge("agent1", "agent2")
        graph.add_edge("agent2", "agent3")
        graph.add_edge("agent3", "synthesizer")
        graph.add_edge("synthesizer", END)
        
        # Set the entry point
        graph.set_entry_point("agent1")
        
        return graph
        
    def run(self, query: str, context: str = "") -> Dict[str, Any]:
        """Run the Custom Panel on the given query.
        
        Args:
            query: The query to run the panel on
            context: Context information
            
        Returns:
            The panel's output
        """
        if self.visualizer:
            self.visualizer.display_welcome("Custom Panel")
            self.visualizer.display_query(query)
            self.visualizer.update_status("Running Custom Panel")
        
        # Parse context if it's a string
        if isinstance(context, str):
            try:
                context_dict = json.loads(context)
            except:
                context_dict = {"raw_context": context}
        else:
            context_dict = context
        
        # Initialize the state
        initial_state = {
            "query": query,
            "context": context_dict,
            "agent1_analysis": {},
            "agent2_analysis": {},
            "agent3_analysis": {},
            "strategic_plan": {}
        }
        
        # Run the graph
        try:
            result = self.graph.invoke(initial_state)
            
            if self.visualizer:
                self.visualizer.display_success("Custom Panel completed successfully")
                self.visualizer.display_plan(result["strategic_plan"])
            
            return result["strategic_plan"]
        except Exception as e:
            logger.error(f"Error running Custom Panel: {e}")
            if self.visualizer:
                self.visualizer.display_error(f"Error running Custom Panel: {e}")
            return {
                "error": str(e),
                "Executive Summary": "An error occurred while running the Custom Panel.",
                "Key Insights": ["Error in panel execution"],
                "Strategic Recommendations": [{"recommendation": "Please try again or contact support"}]
            } 