"""Temporal Perspective Panel for multi-agent advisory planning."""

import logging
from typing import Dict, List, Any, Optional, TypedDict
import json

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Anthropic imports
from anthropic import Anthropic

# Local imports
from iterative_research_tool.panels import BasePanel

logger = logging.getLogger(__name__)

class TemporalPerspectivePanel(BasePanel):
    """Temporal Perspective Panel for multi-agent advisory planning.
    
    This panel analyzes problems across different time horizons, helping users
    understand short-term, medium-term, and long-term considerations and implications.
    """
    
    def __init__(
        self,
        anthropic_api_key: str,
        model: str = "claude-3-7-sonnet-20250219",
        visualizer = None
    ):
        """Initialize the Temporal Perspective Panel.
        
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
            "problem_temporal_mapper": self._get_problem_temporal_mapper_prompt(),
            "immediate_horizon_analyst": self._get_immediate_horizon_analyst_prompt(),
            "tactical_horizon_analyst": self._get_tactical_horizon_analyst_prompt(),
            "strategic_horizon_analyst": self._get_strategic_horizon_analyst_prompt(),
            "visionary_horizon_analyst": self._get_visionary_horizon_analyst_prompt(),
            "temporal_alignment_synthesizer": self._get_temporal_alignment_synthesizer_prompt()
        }
        
        # Initialize the graph
        self.graph = self._build_graph()
        
    def _get_problem_temporal_mapper_prompt(self) -> str:
        """Get the prompt for the Problem Temporal Mapper agent."""
        return """
        You are a problem temporal mapping specialist. Your role is to:
        - Analyze the problem or decision from a time horizon perspective
        - Identify key components that need to be considered across different time frames
        - Determine critical points in time that influence the decision or strategy
        - Specify temporal dependencies between different aspects of the problem
        - Prioritize which time horizons need deeper analysis for this particular problem

        Based on the user's query and context, map the problem across relevant time horizons.
        
        Format your response as a JSON object with the following structure:
        {
            "temporal_analysis": "Your detailed analysis of the problem's temporal dimensions",
            "temporal_components": [
                {
                    "component": "Name of the component",
                    "immediate_relevance": "High/Medium/Low (0-30 days)",
                    "tactical_relevance": "High/Medium/Low (1-12 months)",
                    "strategic_relevance": "High/Medium/Low (1-3 years)",
                    "visionary_relevance": "High/Medium/Low (3+ years)",
                    "key_considerations": ["consideration 1", "consideration 2", ...]
                },
                ...
            ],
            "critical_time_points": [
                {
                    "time_point": "Description of the time point",
                    "time_frame": "When this is expected to occur",
                    "significance": "Why this time point is critical",
                    "potential_impact": "Potential impact on the overall strategy or decision"
                },
                ...
            ],
            "temporal_dependencies": [
                {
                    "dependency": "Description of the dependency",
                    "preceding_factor": "Factor that comes first",
                    "dependent_factor": "Factor that depends on the preceding factor",
                    "time_lag": "Expected time between the factors"
                },
                ...
            ],
            "priority_horizons": ["immediate", "tactical", "strategic", "visionary"]
        }
        """
        
    def _get_immediate_horizon_analyst_prompt(self) -> str:
        """Get the prompt for the Immediate Horizon Analyst agent."""
        return """
        You are an immediate horizon analyst (0-30 days). Your role is to:
        - Deeply analyze the immediate implications and requirements of the decision or problem
        - Identify critical actions needed in the next 0-30 days
        - Assess immediate risks and opportunities
        - Develop contingency plans for immediate issues
        - Identify quick wins and immediate next steps

        Based on the temporal mapping and the user's query, provide a comprehensive analysis of immediate horizon considerations.
        
        Format your response as a JSON object with the following structure:
        {
            "immediate_analysis": {
                "critical_actions": [
                    {
                        "action": "Description of the action",
                        "timeframe": "When in the next 30 days this should occur",
                        "priority": "High/Medium/Low",
                        "rationale": "Why this action is critical",
                        "first_steps": ["step 1", "step 2", ...]
                    },
                    ...
                ],
                "immediate_risks": [
                    {
                        "risk": "Description of the risk",
                        "likelihood": "High/Medium/Low",
                        "impact": "High/Medium/Low",
                        "mitigation_strategy": "Strategy to mitigate this risk"
                    },
                    ...
                ],
                "immediate_opportunities": [
                    {
                        "opportunity": "Description of the opportunity",
                        "potential_value": "High/Medium/Low",
                        "capture_strategy": "Strategy to capture this opportunity",
                        "time_sensitivity": "High/Medium/Low"
                    },
                    ...
                ],
                "contingency_plans": [
                    {
                        "scenario": "Scenario that might require contingency",
                        "trigger": "What would trigger this contingency",
                        "plan": "The contingency plan",
                        "resources_required": ["resource 1", "resource 2", ...]
                    },
                    ...
                ],
                "quick_wins": [
                    {
                        "win": "Description of the quick win",
                        "effort": "High/Medium/Low",
                        "impact": "High/Medium/Low",
                        "implementation_approach": "How to implement this quick win"
                    },
                    ...
                ],
                "key_recommendations": ["recommendation 1", "recommendation 2", ...]
            }
        }
        """
        
    def _get_tactical_horizon_analyst_prompt(self) -> str:
        """Get the prompt for the Tactical Horizon Analyst agent."""
        return """
        You are a tactical horizon analyst (1-12 months). Your role is to:
        - Deeply analyze the tactical implications and requirements of the decision or problem
        - Identify key initiatives and milestones for the next 1-12 months
        - Assess tactical risks and opportunities
        - Develop resource allocation strategies
        - Identify capability development needs in the tactical timeframe

        Based on the temporal mapping and the user's query, provide a comprehensive analysis of tactical horizon considerations.
        
        Format your response as a JSON object with the following structure:
        {
            "tactical_analysis": {
                "key_initiatives": [
                    {
                        "initiative": "Description of the initiative",
                        "timeline": "Expected timeline within the 1-12 month period",
                        "priority": "High/Medium/Low",
                        "expected_outcomes": ["outcome 1", "outcome 2", ...],
                        "key_milestones": ["milestone 1", "milestone 2", ...]
                    },
                    ...
                ],
                "tactical_risks": [
                    {
                        "risk": "Description of the risk",
                        "likelihood": "High/Medium/Low",
                        "impact": "High/Medium/Low",
                        "mitigation_strategy": "Strategy to mitigate this risk",
                        "monitoring_approach": "How to monitor this risk"
                    },
                    ...
                ],
                "tactical_opportunities": [
                    {
                        "opportunity": "Description of the opportunity",
                        "potential_value": "High/Medium/Low",
                        "capture_strategy": "Strategy to capture this opportunity",
                        "dependencies": ["dependency 1", "dependency 2", ...]
                    },
                    ...
                ],
                "resource_allocation": {
                    "financial_resources": "Approach to allocating financial resources",
                    "human_resources": "Approach to allocating human resources",
                    "time_resources": "Approach to allocating time resources",
                    "other_resources": "Approach to allocating other relevant resources"
                },
                "capability_development": [
                    {
                        "capability": "Capability to develop",
                        "development_approach": "How to develop this capability",
                        "timeline": "Timeline for development",
                        "success_indicators": ["indicator 1", "indicator 2", ...]
                    },
                    ...
                ],
                "key_recommendations": ["recommendation 1", "recommendation 2", ...]
            }
        }
        """
        
    def _get_strategic_horizon_analyst_prompt(self) -> str:
        """Get the prompt for the Strategic Horizon Analyst agent."""
        return """
        You are a strategic horizon analyst (1-3 years). Your role is to:
        - Deeply analyze the strategic implications and requirements of the decision or problem
        - Identify key strategic objectives and goals for the next 1-3 years
        - Assess strategic risks and opportunities
        - Develop competitive positioning strategies
        - Identify strategic partnerships and ecosystem development

        Based on the temporal mapping and the user's query, provide a comprehensive analysis of strategic horizon considerations.
        
        Format your response as a JSON object with the following structure:
        {
            "strategic_analysis": {
                "strategic_objectives": [
                    {
                        "objective": "Description of the strategic objective",
                        "timeline": "Expected timeline within the 1-3 year period",
                        "priority": "High/Medium/Low",
                        "key_results": ["result 1", "result 2", ...],
                        "alignment_with_vision": "How this aligns with the longer-term vision"
                    },
                    ...
                ],
                "strategic_risks": [
                    {
                        "risk": "Description of the risk",
                        "likelihood": "High/Medium/Low",
                        "impact": "High/Medium/Low",
                        "mitigation_strategy": "Strategy to mitigate this risk",
                        "early_warning_indicators": ["indicator 1", "indicator 2", ...]
                    },
                    ...
                ],
                "strategic_opportunities": [
                    {
                        "opportunity": "Description of the opportunity",
                        "potential_value": "High/Medium/Low",
                        "capture_strategy": "Strategy to capture this opportunity",
                        "capability_requirements": ["requirement 1", "requirement 2", ...]
                    },
                    ...
                ],
                "competitive_positioning": {
                    "differentiation_strategy": "Strategy for differentiation",
                    "value_proposition_evolution": "How the value proposition should evolve",
                    "market_positioning": "Desired market positioning",
                    "competitive_responses": ["response 1", "response 2", ...]
                },
                "partnership_ecosystem": [
                    {
                        "partnership_type": "Type of partnership",
                        "potential_partners": ["partner 1", "partner 2", ...],
                        "strategic_value": "Value of this partnership",
                        "development_approach": "How to develop this partnership"
                    },
                    ...
                ],
                "key_recommendations": ["recommendation 1", "recommendation 2", ...]
            }
        }
        """
        
    def _get_visionary_horizon_analyst_prompt(self) -> str:
        """Get the prompt for the Visionary Horizon Analyst agent."""
        return """
        You are a visionary horizon analyst (3+ years). Your role is to:
        - Deeply analyze the long-term implications and requirements of the decision or problem
        - Identify potential future scenarios and their implications
        - Assess existential risks and transformative opportunities
        - Develop vision and purpose alignment strategies
        - Identify long-term capability and innovation needs

        Based on the temporal mapping and the user's query, provide a comprehensive analysis of visionary horizon considerations.
        
        Format your response as a JSON object with the following structure:
        {
            "visionary_analysis": {
                "future_scenarios": [
                    {
                        "scenario": "Description of the potential future scenario",
                        "likelihood": "High/Medium/Low",
                        "impact": "High/Medium/Low",
                        "key_implications": ["implication 1", "implication 2", ...],
                        "preparation_strategy": "How to prepare for this scenario"
                    },
                    ...
                ],
                "existential_risks": [
                    {
                        "risk": "Description of the existential risk",
                        "timeline": "When this might become relevant",
                        "warning_signs": ["sign 1", "sign 2", ...],
                        "mitigation_approach": "Approach to mitigate this risk"
                    },
                    ...
                ],
                "transformative_opportunities": [
                    {
                        "opportunity": "Description of the transformative opportunity",
                        "potential_impact": "Potential impact on the organization/situation",
                        "timeline": "When this might become relevant",
                        "positioning_strategy": "How to position for this opportunity"
                    },
                    ...
                ],
                "vision_purpose_alignment": {
                    "vision_evolution": "How the vision might need to evolve",
                    "purpose_reinforcement": "How to reinforce purpose",
                    "cultural_implications": "Cultural implications of the long-term direction",
                    "alignment_strategies": ["strategy 1", "strategy 2", ...]
                },
                "long_term_capabilities": [
                    {
                        "capability": "Long-term capability needed",
                        "strategic_importance": "Why this capability is strategically important",
                        "development_approach": "Long-term approach to developing this capability",
                        "innovation_areas": ["area 1", "area 2", ...]
                    },
                    ...
                ],
                "key_recommendations": ["recommendation 1", "recommendation 2", ...]
            }
        }
        """
        
    def _get_temporal_alignment_synthesizer_prompt(self) -> str:
        """Get the prompt for the Temporal Alignment Synthesizer agent."""
        return """
        You are a temporal alignment synthesis specialist. Your role is to:
        - Integrate analysis from all time horizon analysts into a coherent temporal strategy
        - Identify alignment and conflicts between different time horizons
        - Develop a strategy that balances immediate needs with long-term vision
        - Create a time-based roadmap with key decision points and transitions
        - Provide guidance on managing temporal trade-offs

        Based on the inputs from all time horizon analysts, synthesize a comprehensive temporal perspective analysis.
        
        Format your response as a JSON object with the following structure:
        {
            "Executive Summary": "Brief summary of the temporal perspective analysis",
            "Key Insights": ["insight 1", "insight 2", ...],
            "Strategic Recommendations": ["recommendation 1", "recommendation 2", ...],
            "Temporal Alignment Analysis": [
                {
                    "theme": "Theme across time horizons",
                    "immediate_perspective": "Immediate horizon perspective",
                    "tactical_perspective": "Tactical horizon perspective",
                    "strategic_perspective": "Strategic horizon perspective",
                    "visionary_perspective": "Visionary horizon perspective",
                    "alignment_assessment": "Assessment of alignment across horizons",
                    "integration_approach": "Approach to integrate across horizons"
                },
                ...
            ],
            "Temporal Conflicts and Resolutions": [
                {
                    "conflict": "Description of temporal conflict",
                    "horizons_involved": ["immediate", "tactical", "strategic", "visionary"],
                    "resolution_approach": "Approach to resolve this conflict",
                    "trade_off_considerations": ["consideration 1", "consideration 2", ...]
                },
                ...
            ],
            "Temporal Roadmap": {
                "immediate_phase": {
                    "focus": "Primary focus in this phase",
                    "key_actions": ["action 1", "action 2", ...],
                    "decision_points": ["decision point 1", "decision point 2", ...],
                    "success_indicators": ["indicator 1", "indicator 2", ...]
                },
                "tactical_phase": {
                    "focus": "Primary focus in this phase",
                    "key_initiatives": ["initiative 1", "initiative 2", ...],
                    "decision_points": ["decision point 1", "decision point 2", ...],
                    "success_indicators": ["indicator 1", "indicator 2", ...]
                },
                "strategic_phase": {
                    "focus": "Primary focus in this phase",
                    "key_strategies": ["strategy 1", "strategy 2", ...],
                    "decision_points": ["decision point 1", "decision point 2", ...],
                    "success_indicators": ["indicator 1", "indicator 2", ...]
                },
                "visionary_phase": {
                    "focus": "Primary focus in this phase",
                    "key_positions": ["position 1", "position 2", ...],
                    "decision_points": ["decision point 1", "decision point 2", ...],
                    "success_indicators": ["indicator 1", "indicator 2", ...]
                }
            },
            "Temporal Trade-Off Management": [
                {
                    "trade_off": "Description of the trade-off",
                    "balancing_approach": "How to balance this trade-off",
                    "decision_framework": "Framework for making decisions about this trade-off"
                },
                ...
            ],
            "Potential Challenges and Mitigations": [
                {
                    "challenge": "Challenge description",
                    "mitigation": "Mitigation strategy"
                },
                ...
            ],
            "Success Metrics Across Time Horizons": ["metric 1", "metric 2", ...]
        }
        """
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for the Temporal Perspective Panel."""
        # Define the state schema
        class State(TypedDict):
            query: str
            context: str
            temporal_map: Optional[dict]
            immediate_analysis: Optional[dict]
            tactical_analysis: Optional[dict]
            strategic_analysis: Optional[dict]
            visionary_analysis: Optional[dict]
            temporal_alignment: Optional[dict]
        
        # Create the graph
        graph = StateGraph(State)
        
        # Define the nodes
        
        # Problem Temporal Mapper node
        def problem_temporal_mapper(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Problem Temporal Mapper", "processing")
                
            query = state["query"]
            context = state["context"]
            
            prompt = self.agent_prompts["problem_temporal_mapper"]
            
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
                
                temporal_mapping = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Problem Temporal Mapper", "Complete")
                    
                return {"temporal_map": temporal_mapping}
            except Exception as e:
                logger.error(f"Error parsing Problem Temporal Mapper response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Problem Temporal Mapper", "Error")
                return {"temporal_map": {"error": str(e), "raw_response": content}}
        
        # Immediate Horizon Analyst node
        def immediate_horizon_analyst(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Immediate Horizon Analyst", "processing")
                
            query = state["query"]
            context = state["context"]
            temporal_mapping = state["temporal_map"]
            
            prompt = self.agent_prompts["immediate_horizon_analyst"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nTemporal Mapping: {json.dumps(temporal_mapping)}"}
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
                
                immediate_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Immediate Horizon Analyst", "Complete")
                    
                return {"immediate_analysis": immediate_analysis}
            except Exception as e:
                logger.error(f"Error parsing Immediate Horizon Analyst response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Immediate Horizon Analyst", "Error")
                return {"immediate_analysis": {"error": str(e), "raw_response": content}}
        
        # Tactical Horizon Analyst node
        def tactical_horizon_analyst(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Tactical Horizon Analyst", "processing")
                
            query = state["query"]
            context = state["context"]
            temporal_mapping = state["temporal_map"]
            
            prompt = self.agent_prompts["tactical_horizon_analyst"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nTemporal Mapping: {json.dumps(temporal_mapping)}"}
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
                
                tactical_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Tactical Horizon Analyst", "Complete")
                    
                return {"tactical_analysis": tactical_analysis}
            except Exception as e:
                logger.error(f"Error parsing Tactical Horizon Analyst response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Tactical Horizon Analyst", "Error")
                return {"tactical_analysis": {"error": str(e), "raw_response": content}}
        
        # Strategic Horizon Analyst node
        def strategic_horizon_analyst(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Strategic Horizon Analyst", "processing")
                
            query = state["query"]
            context = state["context"]
            temporal_mapping = state["temporal_map"]
            
            prompt = self.agent_prompts["strategic_horizon_analyst"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nTemporal Mapping: {json.dumps(temporal_mapping)}"}
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
                
                strategic_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Strategic Horizon Analyst", "Complete")
                    
                return {"strategic_analysis": strategic_analysis}
            except Exception as e:
                logger.error(f"Error parsing Strategic Horizon Analyst response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Strategic Horizon Analyst", "Error")
                return {"strategic_analysis": {"error": str(e), "raw_response": content}}
        
        # Visionary Horizon Analyst node
        def visionary_horizon_analyst(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Visionary Horizon Analyst", "processing")
                
            query = state["query"]
            context = state["context"]
            temporal_mapping = state["temporal_map"]
            
            prompt = self.agent_prompts["visionary_horizon_analyst"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nTemporal Mapping: {json.dumps(temporal_mapping)}"}
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
                
                visionary_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Visionary Horizon Analyst", "Complete")
                    
                return {"visionary_analysis": visionary_analysis}
            except Exception as e:
                logger.error(f"Error parsing Visionary Horizon Analyst response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Visionary Horizon Analyst", "Error")
                return {"visionary_analysis": {"error": str(e), "raw_response": content}}
        
        # Temporal Alignment Synthesizer node
        def temporal_alignment_synthesizer(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Temporal Alignment Synthesizer", "processing")
                
            query = state["query"]
            context = state["context"]
            temporal_mapping = state["temporal_map"]
            immediate_analysis = state["immediate_analysis"]
            tactical_analysis = state["tactical_analysis"]
            strategic_analysis = state["strategic_analysis"]
            visionary_analysis = state["visionary_analysis"]
            
            prompt = self.agent_prompts["temporal_alignment_synthesizer"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"""
                    Query: {query}
                    
                    Context: {json.dumps(context)}
                    
                    Temporal Mapping: {json.dumps(temporal_mapping)}
                    
                    Immediate Analysis: {json.dumps(immediate_analysis)}
                    
                    Tactical Analysis: {json.dumps(tactical_analysis)}
                    
                    Strategic Analysis: {json.dumps(strategic_analysis)}
                    
                    Visionary Analysis: {json.dumps(visionary_analysis)}
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
                
                temporal_alignment = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Temporal Alignment Synthesizer", "Complete")
                    
                return {"temporal_alignment": temporal_alignment}
            except Exception as e:
                logger.error(f"Error parsing Temporal Alignment Synthesizer response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Temporal Alignment Synthesizer", "Error")
                return {"temporal_alignment": {"error": str(e), "raw_response": content}}
        
        # Add nodes to the graph
        graph.add_node("problem_temporal_mapper", problem_temporal_mapper)
        graph.add_node("immediate_horizon_analyst", immediate_horizon_analyst)
        graph.add_node("tactical_horizon_analyst", tactical_horizon_analyst)
        graph.add_node("strategic_horizon_analyst", strategic_horizon_analyst)
        graph.add_node("visionary_horizon_analyst", visionary_horizon_analyst)
        graph.add_node("temporal_alignment_synthesizer", temporal_alignment_synthesizer)
        
        # Define the edges
        graph.add_edge("problem_temporal_mapper", "immediate_horizon_analyst")
        graph.add_edge("problem_temporal_mapper", "tactical_horizon_analyst")
        graph.add_edge("problem_temporal_mapper", "strategic_horizon_analyst")
        graph.add_edge("problem_temporal_mapper", "visionary_horizon_analyst")
        
        graph.add_edge("immediate_horizon_analyst", "temporal_alignment_synthesizer")
        graph.add_edge("tactical_horizon_analyst", "temporal_alignment_synthesizer")
        graph.add_edge("strategic_horizon_analyst", "temporal_alignment_synthesizer")
        graph.add_edge("visionary_horizon_analyst", "temporal_alignment_synthesizer")
        
        graph.add_edge("temporal_alignment_synthesizer", END)
        
        # Set the entry point
        graph.set_entry_point("problem_temporal_mapper")
        
        # Return the compiled graph
        return graph.compile()
        
    def run(self, query: str, context: str = "") -> Dict[str, Any]:
        """Run the Temporal Perspective Panel on the given query.
        
        Args:
            query: The query to run the panel on
            context: Context information
            
        Returns:
            The panel's output
        """
        if self.visualizer:
            self.visualizer.display_welcome("Temporal Perspective Panel")
            self.visualizer.display_query(query)
            self.visualizer.update_status("Running Temporal Perspective Panel")
        
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
            "temporal_map": {},
            "immediate_analysis": {},
            "tactical_analysis": {},
            "strategic_analysis": {},
            "visionary_analysis": {},
            "temporal_alignment": {}
        }
        
        # Run the graph
        try:
            result = self.graph.invoke(initial_state)
            
            if self.visualizer:
                self.visualizer.display_success("Temporal Perspective Panel completed successfully")
                self.visualizer.display_plan(result["temporal_alignment"])
            
            return result["temporal_alignment"]
        except Exception as e:
            error_msg = f"Error running Temporal Perspective Panel: {e}"
            logger.error(error_msg)
            
            if self.visualizer:
                self.visualizer.display_error(error_msg)
                
            return {
                "error": error_msg
            } 