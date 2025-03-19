"""Cognitive Diversity Panel for multi-perspective analysis."""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Local imports
from iterative_research_tool.panels import BasePanel
from iterative_research_tool.core.visualization import Visualizer
from iterative_research_tool.core.llm_client import LLMClientFactory

logger = logging.getLogger(__name__)

# Define the cognitive diversity agents
COGNITIVE_AGENTS = {
    "systems_thinker": {
        "name": "Systems Thinker",
        "description": "Analyzes complex systems, feedback loops, and emergent properties",
        "prompt": """You are a Systems Thinker who excels at analyzing complex systems, feedback loops, and emergent properties. 
        Your approach involves mapping interconnections, identifying leverage points, and understanding how changes propagate through systems.
        
        Analyze the following query from a systems thinking perspective:
        
        {query}
        
        User Context:
        {context}
        
        Provide your analysis in the following format:
        1. Systems Map: Identify the key components and their relationships
        2. Feedback Loops: Identify reinforcing and balancing feedback loops
        3. Leverage Points: Identify high-impact intervention points
        4. Emergent Properties: Identify potential emergent behaviors
        5. Recommendations: Provide systems-based recommendations
        
        Format your response as JSON with these sections as keys."""
    },
    "first_principles_thinker": {
        "name": "First Principles Thinker",
        "description": "Breaks down problems to fundamental truths and builds up from there",
        "prompt": """You are a First Principles Thinker who excels at breaking down problems to their fundamental truths and building up from there.
        Your approach involves questioning assumptions, identifying core elements, and reasoning from the ground up.
        
        Analyze the following query from a first principles perspective:
        
        {query}
        
        User Context:
        {context}
        
        Provide your analysis in the following format:
        1. Core Truths: Identify the fundamental truths relevant to this problem
        2. Assumptions: Identify and question common assumptions
        3. First Principles Analysis: Analyze the problem from first principles
        4. Derived Insights: Share insights derived from first principles
        5. Recommendations: Provide recommendations based on first principles
        
        Format your response as JSON with these sections as keys."""
    },
    "creative_thinker": {
        "name": "Creative Thinker",
        "description": "Generates novel ideas and approaches through divergent thinking",
        "prompt": """You are a Creative Thinker who excels at generating novel ideas and approaches through divergent thinking.
        Your approach involves making unexpected connections, challenging conventions, and exploring possibilities.
        
        Analyze the following query from a creative thinking perspective:
        
        {query}
        
        User Context:
        {context}
        
        Provide your analysis in the following format:
        1. Reframing: Reframe the problem in multiple ways
        2. Novel Connections: Identify unexpected connections or analogies
        3. Divergent Possibilities: Generate diverse potential approaches
        4. Conventional Wisdom Challenges: Challenge standard approaches
        5. Recommendations: Provide creative recommendations
        
        Format your response as JSON with these sections as keys."""
    },
    "pragmatic_thinker": {
        "name": "Pragmatic Thinker",
        "description": "Focuses on practical implementation and real-world constraints",
        "prompt": """You are a Pragmatic Thinker who excels at focusing on practical implementation and real-world constraints.
        Your approach involves considering resources, feasibility, and concrete steps.
        
        Analyze the following query from a pragmatic perspective:
        
        {query}
        
        User Context:
        {context}
        
        Provide your analysis in the following format:
        1. Resource Assessment: Identify required resources and constraints
        2. Feasibility Analysis: Analyze the practicality of potential approaches
        3. Implementation Challenges: Identify potential obstacles
        4. Practical Steps: Outline concrete implementation steps
        5. Recommendations: Provide pragmatic recommendations
        
        Format your response as JSON with these sections as keys."""
    }
}

class CognitiveDiversityPanel(BasePanel):
    """Panel that brings together diverse cognitive styles for comprehensive analysis."""
    
    def __init__(
        self,
        llm_provider: str = "anthropic",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        visualizer: Optional[Visualizer] = None
    ):
        """Initialize the cognitive diversity panel.
        
        Args:
            llm_provider: The LLM provider to use (anthropic, openai, or perplexity)
            api_key: API key for the LLM provider
            model: Model to use for the panel (if None, uses the default model for the provider)
            visualizer: Visualizer for displaying output
        """
        self.llm_provider = llm_provider.lower()
        self.api_key = api_key or os.environ.get(f"{self.llm_provider.upper()}_API_KEY")
        
        # Set up the LLM client
        try:
            self.llm_client = LLMClientFactory.create_client(self.llm_provider, self.api_key)
            # Set the model or use the default for the provider
            self.model = model or LLMClientFactory.get_default_model(self.llm_provider)
            logger.info(f"CognitiveDiversityPanel using LLM provider: {self.llm_provider} with model: {self.model}")
        except Exception as e:
            logger.error(f"Error creating LLM client: {str(e)}")
            raise
            
        self.visualizer = visualizer or Visualizer()
        
        # Initialize the agents
        self.agents = COGNITIVE_AGENTS
    
    def run(self, query: str, context: str) -> Dict[str, Any]:
        """Run the cognitive diversity panel on the given query.
        
        Args:
            query: The query to analyze
            context: User context information
            
        Returns:
            The panel's output
        """
        self.visualizer.display_message("Running Cognitive Diversity Panel...")
        
        # Run each agent in parallel
        agent_results = self._run_agents_parallel(query, context)
        
        # Synthesize the results
        synthesis = self._synthesize_results(query, agent_results)
        
        # Prepare the final output
        output = {
            "query": query,
            "agent_results": agent_results,
            "synthesis": synthesis,
            "timestamp": time.time()
        }
        
        return output
    
    def _run_agents_parallel(self, query: str, context: str) -> Dict[str, Any]:
        """Run all agents in parallel.
        
        Args:
            query: The query to analyze
            context: User context information
            
        Returns:
            Results from all agents
        """
        results = {}
        
        # Create a thread pool
        with ThreadPoolExecutor(max_workers=len(self.agents)) as executor:
            # Submit tasks for each agent
            future_to_agent = {
                executor.submit(self._run_agent, agent_id, agent_info, query, context): agent_id
                for agent_id, agent_info in self.agents.items()
            }
            
            # Process results as they complete
            for future in future_to_agent:
                agent_id = future_to_agent[future]
                try:
                    result = future.result()
                    results[agent_id] = result
                except Exception as e:
                    logger.error(f"Error running agent {agent_id}: {str(e)}")
                    results[agent_id] = {
                        "agent_id": agent_id,
                        "agent_name": self.agents[agent_id]["name"],
                        "agent_description": self.agents[agent_id]["description"],
                        "error": str(e)
                    }
        
        return results
    
    def _run_agent(self, agent_id: str, agent_info: Dict[str, str], query: str, context: str) -> Dict[str, Any]:
        """Run a single agent.
        
        Args:
            agent_id: ID of the agent
            agent_info: Information about the agent
            query: The query to analyze
            context: User context information
            
        Returns:
            The agent's analysis
        """
        self.visualizer.update_agent_status(
            agent_name=agent_info["name"],
            status="Running"
        )
        
        # Format the prompt
        prompt = agent_info["prompt"].format(query=query, context=context)
        
        # Call the LLM
        response = self.llm_client.create_message(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000
        )
        
        # Extract the response text based on the provider
        if hasattr(response, 'content') and isinstance(response.content, list):
            response_text = response.content[0].text
        else:
            response_text = response.choices[0].message.content
        
        # Extract the JSON from the response
        try:
            # Find JSON in the response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                analysis = json.loads(json_str)
                
                # Add metadata
                analysis["agent_id"] = agent_id
                analysis["agent_name"] = agent_info["name"]
                analysis["agent_description"] = agent_info["description"]
                
                return analysis
            else:
                logger.warning(f"Could not find JSON in {agent_info['name']}'s response")
                return {
                    "agent_id": agent_id,
                    "agent_name": agent_info["name"],
                    "agent_description": agent_info["description"],
                    "error": "Could not find JSON in response",
                    "raw_response": response_text
                }
        except json.JSONDecodeError as e:
            logger.warning(f"Error parsing JSON from {agent_info['name']}'s response: {str(e)}")
            return {
                "agent_id": agent_id,
                "agent_name": agent_info["name"],
                "agent_description": agent_info["description"],
                "error": f"Error parsing JSON: {str(e)}",
                "raw_response": response_text
            }
        finally:
            self.visualizer.update_agent_status(
                agent_name=agent_info["name"],
                status="Complete"
            )
    
    def _synthesize_results(self, query: str, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize the results from all agents.
        
        Args:
            query: The original query
            agent_results: Results from all agents
            
        Returns:
            Synthesized insights
        """
        self.visualizer.display_message("Synthesizing insights from all cognitive perspectives...")
        
        # Create a prompt for synthesis
        prompt = f"""You are a meta-cognitive analyst tasked with synthesizing insights from multiple cognitive perspectives.

Original Query: {query}

The following analyses were provided by different cognitive specialists:

{json.dumps(agent_results, indent=2)}

Please synthesize these diverse perspectives into a cohesive analysis with the following sections:
1. Key Insights: The most important insights across all perspectives
2. Complementary Viewpoints: How the different perspectives complement each other
3. Tensions and Trade-offs: Areas where perspectives may conflict
4. Integrated Recommendations: Recommendations that incorporate multiple perspectives
5. Meta-analysis: Reflection on the value of cognitive diversity for this query
6. Original Agent Insights: Key insights from each individual agent, preserving their unique cognitive style and perspective

Format your response as JSON with these sections as keys.

For the "Original Agent Insights" section, extract 3-5 of the most important and unique insights from each agent, organizing them by agent name. This should allow the user to see both your integrated analysis and the original thinking from each cognitive perspective.

Example format for the "Original Agent Insights" section:
"Original Agent Insights": {
    "Agent Name 1": ["key insight 1", "key insight 2", "key insight 3"],
    "Agent Name 2": ["key insight 1", "key insight 2", "key insight 3"],
    ...
}
"""
        
        try:
            # Call the LLM for synthesis
            response = self.llm_client.create_message(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000
            )
            
            # Extract the response text based on the provider
            if hasattr(response, 'content') and isinstance(response.content, list):
                response_text = response.content[0].text
            else:
                response_text = response.choices[0].message.content
            
            # Extract the JSON from the response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                synthesis = json.loads(json_str)
                return synthesis
            else:
                logger.warning("Could not find JSON in synthesis response")
                return {
                    "error": "Could not find JSON in synthesis response",
                    "raw_response": response_text
                }
        except Exception as e:
            logger.error(f"Error synthesizing results: {str(e)}")
            return {
                "error": f"Error synthesizing results: {str(e)}"
            } 