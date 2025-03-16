"""Decision Intelligence Panel for structured decision-making."""

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

# Define the decision intelligence agents
DECISION_AGENTS = {
    "problem_framer": {
        "name": "Problem Framer",
        "description": "Clarifies the decision context and frames the problem",
        "prompt": """You are a Problem Framer who excels at clarifying decision contexts and framing problems effectively.
        Your approach involves identifying the core decision, stakeholders, constraints, and success criteria.
        
        Analyze the following query from a problem framing perspective:
        
        {query}
        
        User Context:
        {context}
        
        Provide your analysis in the following format:
        1. Decision Statement: Clearly articulate the decision that needs to be made
        2. Stakeholder Analysis: Identify key stakeholders and their interests
        3. Constraints & Boundaries: Identify key constraints and boundaries
        4. Success Criteria: Define what success looks like
        5. Key Questions: List critical questions that need to be answered
        
        Format your response as JSON with these sections as keys."""
    },
    "options_generator": {
        "name": "Options Generator",
        "description": "Generates a diverse set of decision options",
        "prompt": """You are an Options Generator who excels at creating a diverse set of decision options.
        Your approach involves divergent thinking, considering multiple pathways, and exploring the solution space broadly.
        
        Analyze the following query from an options generation perspective:
        
        {query}
        
        User Context:
        {context}
        
        Provide your analysis in the following format:
        1. Conventional Options: List standard or obvious options
        2. Creative Options: List novel or unexpected options
        3. Hybrid Options: List options that combine elements of different approaches
        4. Counterintuitive Options: List options that seem counterintuitive but might work
        5. Option Dimensions: Identify key dimensions along which options vary
        
        Format your response as JSON with these sections as keys."""
    },
    "evidence_analyst": {
        "name": "Evidence Analyst",
        "description": "Evaluates available evidence and identifies information gaps",
        "prompt": """You are an Evidence Analyst who excels at evaluating available evidence and identifying information gaps.
        Your approach involves assessing data quality, identifying biases, and determining what additional information is needed.
        
        Analyze the following query from an evidence analysis perspective:
        
        {query}
        
        User Context:
        {context}
        
        Provide your analysis in the following format:
        1. Available Evidence: Summarize what evidence appears to be available
        2. Evidence Quality: Assess the quality and reliability of available evidence
        3. Information Gaps: Identify critical missing information
        4. Potential Biases: Highlight potential biases in the available information
        5. Evidence Collection Plan: Suggest how to gather additional evidence
        
        Format your response as JSON with these sections as keys."""
    },
    "consequence_forecaster": {
        "name": "Consequence Forecaster",
        "description": "Projects potential outcomes and second-order effects",
        "prompt": """You are a Consequence Forecaster who excels at projecting potential outcomes and second-order effects.
        Your approach involves scenario planning, considering unintended consequences, and thinking through causal chains.
        
        Analyze the following query from a consequence forecasting perspective:
        
        {query}
        
        User Context:
        {context}
        
        Provide your analysis in the following format:
        1. Direct Outcomes: Identify likely direct outcomes of different approaches
        2. Second-Order Effects: Identify potential second-order effects
        3. Unintended Consequences: Highlight possible unintended consequences
        4. Time Horizons: Consider effects across different time horizons
        5. Key Uncertainties: Identify critical uncertainties in forecasting consequences
        
        Format your response as JSON with these sections as keys."""
    },
    "decision_evaluator": {
        "name": "Decision Evaluator",
        "description": "Evaluates options against multiple criteria and values",
        "prompt": """You are a Decision Evaluator who excels at evaluating options against multiple criteria and values.
        Your approach involves multi-criteria analysis, value trade-offs, and sensitivity analysis.
        
        Analyze the following query from a decision evaluation perspective:
        
        {query}
        
        User Context:
        {context}
        
        Provide your analysis in the following format:
        1. Evaluation Criteria: Identify key criteria for evaluating options
        2. Option Assessment: Assess how well different approaches meet the criteria
        3. Value Trade-offs: Identify key trade-offs between competing values
        4. Sensitivity Analysis: Assess how sensitive the evaluation is to different assumptions
        5. Recommended Option(s): Provide recommendations based on the evaluation
        
        Format your response as JSON with these sections as keys."""
    }
}

class DecisionIntelligencePanel(BasePanel):
    """Panel that brings together decision intelligence agents for structured decision-making."""
    
    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        model: str = "claude-3-7-sonnet-20250219",
        visualizer: Optional[Visualizer] = None
    ):
        """Initialize the decision intelligence panel.
        
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
        self.agents = DECISION_AGENTS
    
    def run(self, query: str, context: str) -> Dict[str, Any]:
        """Run the decision intelligence panel on the given query.
        
        Args:
            query: The query to analyze
            context: User context information
            
        Returns:
            The panel's output
        """
        self.visualizer.display_message("Running Decision Intelligence Panel...")
        
        # Run the agents in sequence
        agent_results = self._run_agents_sequential(query, context)
        
        # Synthesize the results
        synthesis = self._synthesize_results(query, agent_results)
        
        # Prepare the final output
        output = {
            "panel_type": "decision_intelligence",
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
            "problem_framer",
            "options_generator",
            "evidence_analyst",
            "consequence_forecaster",
            "decision_evaluator"
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
            Synthesized decision recommendation
        """
        self.visualizer.update_status("Synthesizing decision recommendation...")
        
        # Create a prompt for synthesis
        prompt = f"""
        You are a Decision Intelligence Advisor who excels at synthesizing structured decision analyses into clear recommendations.
        
        Original Query: {query}
        
        You have received analyses from the following decision intelligence agents:
        {', '.join([f"{agent_info['name']}" for agent_id, agent_info in self.agents.items()])}
        
        Here are their analyses:
        {json.dumps(agent_results, indent=2)}
        
        Please synthesize these analyses into a comprehensive decision recommendation with the following sections:
        1. Decision Summary: Summarize the decision context and key considerations
        2. Recommended Option(s): Clearly state the recommended option(s)
        3. Rationale: Explain the rationale for the recommendation
        4. Implementation Considerations: Highlight key considerations for implementation
        5. Monitoring & Adaptation: Suggest how to monitor outcomes and adapt as needed
        
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