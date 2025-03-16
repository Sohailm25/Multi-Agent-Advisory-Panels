"""Future Scenarios Panel for exploring potential futures and their implications."""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

# Anthropic imports
from anthropic import Anthropic

# Local imports
from iterative_research_tool.panels import BasePanel
from iterative_research_tool.core.visualization import Visualizer

logger = logging.getLogger(__name__)

# Define the future scenarios agents
SCENARIO_AGENTS = {
    "trend_analyst": {
        "name": "Trend Analyst",
        "description": "Identifies key trends and driving forces",
        "prompt": """You are a Trend Analyst who excels at identifying key trends and driving forces that shape the future.
        Your approach involves scanning across STEEP domains (Social, Technological, Economic, Environmental, Political) to identify important shifts.
        
        Analyze the following query from a trend analysis perspective:
        
        {query}
        
        User Context:
        {context}
        
        Provide your analysis in the following format:
        1. Social Trends: Identify key social and demographic trends
        2. Technological Trends: Identify key technological developments
        3. Economic Trends: Identify key economic and business trends
        4. Environmental Trends: Identify key environmental and resource trends
        5. Political Trends: Identify key political and regulatory trends
        6. Cross-Cutting Forces: Identify trends that cut across multiple domains
        
        Format your response as JSON with these sections as keys."""
    },
    "uncertainty_mapper": {
        "name": "Uncertainty Mapper",
        "description": "Maps critical uncertainties and their potential outcomes",
        "prompt": """You are an Uncertainty Mapper who excels at identifying critical uncertainties and their potential outcomes.
        Your approach involves distinguishing between predetermined elements and true uncertainties, and exploring the range of possible outcomes.
        
        Analyze the following query from an uncertainty mapping perspective:
        
        {query}
        
        User Context:
        {context}
        
        Provide your analysis in the following format:
        1. Predetermined Elements: Identify factors that are relatively certain
        2. Critical Uncertainties: Identify the most important uncertainties
        3. Uncertainty Ranges: For each critical uncertainty, describe the range of possible outcomes
        4. Uncertainty Interactions: Describe how different uncertainties might interact
        5. Signposts: Identify early indicators that would signal which way uncertainties are resolving
        
        Format your response as JSON with these sections as keys."""
    },
    "scenario_builder": {
        "name": "Scenario Builder",
        "description": "Constructs coherent, plausible future scenarios",
        "prompt": """You are a Scenario Builder who excels at constructing coherent, plausible future scenarios.
        Your approach involves combining trends and uncertainties into integrated narratives that explore different possible futures.
        
        Analyze the following query from a scenario building perspective:
        
        {query}
        
        User Context:
        {context}
        
        Provide your analysis in the following format:
        1. Scenario Framework: Describe the key dimensions that differentiate your scenarios
        2. Scenario 1 - [Name]: Describe a coherent future scenario
        3. Scenario 2 - [Name]: Describe a different coherent future scenario
        4. Scenario 3 - [Name]: Describe a third coherent future scenario
        5. Scenario 4 - [Name]: Describe a fourth coherent future scenario
        6. Common Elements: Identify elements common to all scenarios
        
        Format your response as JSON with these sections as keys."""
    },
    "implication_analyst": {
        "name": "Implication Analyst",
        "description": "Analyzes the implications of different scenarios",
        "prompt": """You are an Implication Analyst who excels at analyzing the implications of different scenarios.
        Your approach involves exploring how different futures would affect stakeholders, strategies, and decisions.
        
        Analyze the following query from an implications perspective:
        
        {query}
        
        User Context:
        {context}
        
        Provide your analysis in the following format:
        1. Stakeholder Implications: How different scenarios would affect key stakeholders
        2. Strategic Implications: How different scenarios would affect strategies and plans
        3. Decision Implications: How different scenarios should influence current decisions
        4. Risk Implications: Key risks that emerge in different scenarios
        5. Opportunity Implications: Key opportunities that emerge in different scenarios
        
        Format your response as JSON with these sections as keys."""
    },
    "robust_strategist": {
        "name": "Robust Strategist",
        "description": "Develops strategies that work across multiple futures",
        "prompt": """You are a Robust Strategist who excels at developing strategies that work across multiple possible futures.
        Your approach involves identifying robust actions, adaptive strategies, and options that preserve future flexibility.
        
        Analyze the following query from a robust strategy perspective:
        
        {query}
        
        User Context:
        {context}
        
        Provide your analysis in the following format:
        1. Robust Actions: Identify actions that make sense across all scenarios
        2. Scenario-Specific Strategies: Identify strategies tailored to specific scenarios
        3. Adaptive Strategies: Identify strategies that can adapt as the future unfolds
        4. Real Options: Identify investments that preserve future flexibility
        5. Hedging Strategies: Identify ways to mitigate risks across scenarios
        
        Format your response as JSON with these sections as keys."""
    }
}

class FutureScenariosPanel(BasePanel):
    """Panel that explores potential futures and their implications."""
    
    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        model: str = "claude-3-7-sonnet-20250219",
        visualizer: Optional[Visualizer] = None
    ):
        """Initialize the future scenarios panel.
        
        Args:
            anthropic_api_key: API key for Anthropic
            model: Model to use for the panel
            visualizer: Visualizer for displaying output
        """
        self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.anthropic_api_key:
            raise ValueError("Anthropic API key is required")
            
        self.model = model
        self.client = Anthropic(api_key=self.anthropic_api_key)
        self.visualizer = visualizer or Visualizer()
        
        # Initialize the agents
        self.agents = SCENARIO_AGENTS
    
    def run(self, query: str, context: str) -> Dict[str, Any]:
        """Run the future scenarios panel on the given query.
        
        Args:
            query: The query to analyze
            context: User context information
            
        Returns:
            The panel's output
        """
        self.visualizer.display_message("Running Future Scenarios Panel...")
        
        # Run the agents in sequence
        agent_results = self._run_agents_sequential(query, context)
        
        # Synthesize the results
        synthesis = self._synthesize_results(query, agent_results)
        
        # Prepare the final output
        output = {
            "panel_type": "future_scenarios",
            "query": query,
            "agent_results": agent_results,
            "synthesis": synthesis,
            "timestamp": time.time()
        }
        
        return output
    
    def _run_agents_sequential(self, query: str, context: str) -> Dict[str, Any]:
        """Run agents in a sequential order, with each agent building on previous results.
        
        Args:
            query: The query to analyze
            context: User context information
            
        Returns:
            Dictionary of agent results
        """
        results = {}
        accumulated_context = context
        
        # Define the sequence of agents
        agent_sequence = [
            "trend_analyst",
            "uncertainty_mapper",
            "scenario_builder",
            "implication_analyst",
            "robust_strategist"
        ]
        
        # Run each agent in sequence
        for agent_id in agent_sequence:
            agent_info = self.agents[agent_id]
            
            self.visualizer.update_agent_status(
                agent_name=agent_info["name"],
                status="Running"
            )
            
            # Update the context with previous results
            if results:
                accumulated_context = f"{context}\n\nPrevious Analysis:\n{json.dumps(results, indent=2)}"
            
            try:
                # Run the agent
                result = self._run_agent(agent_id, agent_info, query, accumulated_context)
                results[agent_id] = result
                
                self.visualizer.update_agent_status(
                    agent_name=agent_info["name"],
                    status="Complete"
                )
            except Exception as e:
                logger.error(f"Error running agent {agent_id}: {e}")
                results[agent_id] = {"error": str(e)}
                
                self.visualizer.update_agent_status(
                    agent_name=agent_info["name"],
                    status="Error"
                )
        
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
        # Format the prompt
        prompt = agent_info["prompt"].format(query=query, context=context)
        
        # Call Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = response.content[0].text
        
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
                    "error": "Could not parse JSON response",
                    "raw_response": response_text
                }
        except json.JSONDecodeError:
            logger.warning(f"Error parsing JSON from {agent_info['name']}'s response")
            return {
                "agent_id": agent_id,
                "agent_name": agent_info["name"],
                "agent_description": agent_info["description"],
                "error": "Could not parse JSON response",
                "raw_response": response_text
            }
    
    def _synthesize_results(self, query: str, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize the results from all agents.
        
        Args:
            query: The original query
            agent_results: Results from all agents
            
        Returns:
            Synthesized future-ready strategy
        """
        self.visualizer.update_status("Synthesizing future-ready strategy...")
        
        # Create a prompt for synthesis
        prompt = f"""
        You are a Future-Ready Strategist who excels at synthesizing scenario analyses into actionable, future-proof strategies.
        
        Original Query: {query}
        
        You have received analyses from the following scenario planning agents:
        {', '.join([f"{agent_info['name']}" for agent_id, agent_info in self.agents.items()])}
        
        Here are their analyses:
        {json.dumps(agent_results, indent=2)}
        
        Please synthesize these analyses into a comprehensive future-ready strategy with the following sections:
        1. Future Landscape: Summarize the key trends and scenarios that shape the future landscape
        2. Strategic Imperatives: Identify the most important strategic imperatives given the future landscape
        3. Core Strategy: Outline a core strategy that is robust across multiple futures
        4. Adaptive Elements: Identify elements of the strategy that should adapt to different futures
        5. Near-Term Actions: Recommend specific near-term actions to implement the strategy
        
        Format your response as JSON with these sections as keys.
        """
        
        # Call Claude for synthesis
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        synthesis_text = response.content[0].text
        
        # Extract the JSON from the response
        try:
            # Find JSON in the response
            json_start = synthesis_text.find("{")
            json_end = synthesis_text.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = synthesis_text[json_start:json_end]
                synthesis = json.loads(json_str)
                return synthesis
            else:
                logger.warning("Could not find JSON in synthesis response")
                return {
                    "error": "Could not parse JSON synthesis",
                    "raw_synthesis": synthesis_text
                }
        except json.JSONDecodeError:
            logger.warning("Error parsing JSON from synthesis response")
            return {
                "error": "Could not parse JSON synthesis",
                "raw_synthesis": synthesis_text
            } 