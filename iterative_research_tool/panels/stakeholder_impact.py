"""Stakeholder Impact Advisory Board panel for multi-agent advisory planning."""

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

class StakeholderImpactPanel(BasePanel):
    """Stakeholder Impact Advisory Board panel for multi-agent advisory planning.
    
    This panel analyzes decisions and strategies from the perspective of different stakeholders,
    ensuring comprehensive consideration of impacts and identifying potential conflicts or
    alignment opportunities.
    """
    
    def __init__(
        self,
        anthropic_api_key: str,
        model: str = "claude-3-7-sonnet-20250219",
        visualizer = None
    ):
        """Initialize the Stakeholder Impact Advisory Board panel.
        
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
            "stakeholder_mapper": self._get_stakeholder_mapper_prompt(),
            "customer_client_agent": self._get_customer_client_agent_prompt(),
            "team_employee_agent": self._get_team_employee_agent_prompt(),
            "shareholder_investor_agent": self._get_shareholder_investor_agent_prompt(), 
            "community_society_agent": self._get_community_society_agent_prompt(),
            "future_self_agent": self._get_future_self_agent_prompt(),
            "synthesis_alignment_node": self._get_synthesis_alignment_node_prompt()
        }
        
        # Initialize the graph
        self.graph = self._build_graph()
        
    def _get_stakeholder_mapper_prompt(self) -> str:
        """Get the prompt for the Stakeholder Mapper agent."""
        return """
        You are a comprehensive stakeholder mapping specialist. Your role is to:
        - Identify all relevant stakeholders affected by the decision or strategy
        - Map stakeholders by influence, interest, and impact
        - Detect hidden or less obvious stakeholders often overlooked
        - Understand interconnections between stakeholder groups
        - Prioritize which stakeholder perspectives need deeper analysis

        Begin with broad categories, then drill down to specific stakeholders with distinct concerns.
        
        Based on the user's query and context, identify and map all relevant stakeholders.
        
        Format your response as a JSON object with the following structure:
        {
            "analysis": "Your detailed analysis of the stakeholder landscape",
            "stakeholder_map": [
                {
                    "stakeholder_group": "Name of the stakeholder group",
                    "specific_stakeholders": ["stakeholder 1", "stakeholder 2", ...],
                    "level_of_influence": "High/Medium/Low",
                    "level_of_interest": "High/Medium/Low",
                    "level_of_impact": "High/Medium/Low",
                    "key_concerns": ["concern 1", "concern 2", ...],
                    "priority_for_analysis": "High/Medium/Low"
                },
                ...
            ],
            "hidden_stakeholders": [
                {
                    "stakeholder": "Name of the hidden stakeholder",
                    "reason_overlooked": "Why this stakeholder is often overlooked",
                    "importance": "Why this stakeholder is important to consider"
                },
                ...
            ],
            "stakeholder_interconnections": [
                {
                    "stakeholder_group_1": "First stakeholder group",
                    "stakeholder_group_2": "Second stakeholder group",
                    "relationship": "Description of the relationship between the groups",
                    "potential_conflicts": ["conflict 1", "conflict 2", ...],
                    "potential_alignments": ["alignment 1", "alignment 2", ...]
                },
                ...
            ],
            "priority_stakeholders": ["stakeholder 1", "stakeholder 2", ...]
        }
        """
        
    def _get_customer_client_agent_prompt(self) -> str:
        """Get the prompt for the Customer/Client Agent."""
        return """
        You represent the perspective of customers and clients as stakeholders. Your role is to:
        - Analyze how the decision or strategy affects customer/client experience
        - Identify customer/client needs, preferences, and expectations
        - Evaluate how the decision impacts customer value and satisfaction
        - Consider different customer segments and their unique perspectives
        - Anticipate customer reactions and potential behavior changes

        Based on the stakeholder map and the user's query, provide a comprehensive analysis from the customer/client perspective.
        
        Format your response as a JSON object with the following structure:
        {
            "customer_analysis": {
                "overall_impact": "Overall assessment of how the decision affects customers/clients",
                "key_customer_segments": [
                    {
                        "segment": "Description of the customer segment",
                        "impact": "How this segment will be impacted",
                        "needs_met": ["need 1", "need 2", ...],
                        "needs_unmet": ["need 1", "need 2", ...],
                        "likely_reaction": "How this segment is likely to react"
                    },
                    ...
                ],
                "positive_impacts": ["positive impact 1", "positive impact 2", ...],
                "negative_impacts": ["negative impact 1", "negative impact 2", ...],
                "customer_value_assessment": "Assessment of how the decision affects customer value",
                "recommendations": ["recommendation 1", "recommendation 2", ...]
            }
        }
        """
        
    def _get_team_employee_agent_prompt(self) -> str:
        """Get the prompt for the Team/Employee Agent."""
        return """
        You represent the perspective of team members and employees as stakeholders. Your role is to:
        - Analyze how the decision or strategy affects employee experience and well-being
        - Identify impacts on workload, job satisfaction, and career development
        - Evaluate how the decision aligns with team culture and values
        - Consider impacts on team dynamics and collaboration
        - Anticipate potential resistance or support from team members

        Based on the stakeholder map and the user's query, provide a comprehensive analysis from the team/employee perspective.
        
        Format your response as a JSON object with the following structure:
        {
            "team_analysis": {
                "overall_impact": "Overall assessment of how the decision affects team members/employees",
                "key_team_segments": [
                    {
                        "segment": "Description of the team segment (e.g., department, role)",
                        "impact": "How this segment will be impacted",
                        "workload_impact": "How workload will be affected",
                        "job_satisfaction_impact": "How job satisfaction will be affected",
                        "development_impact": "How career development opportunities will be affected",
                        "likely_response": "How this segment is likely to respond"
                    },
                    ...
                ],
                "cultural_alignment": "Assessment of how the decision aligns with team culture and values",
                "team_dynamics_impact": "How the decision will affect team dynamics and collaboration",
                "positive_impacts": ["positive impact 1", "positive impact 2", ...],
                "negative_impacts": ["negative impact 1", "negative impact 2", ...],
                "potential_resistance_points": ["resistance point 1", "resistance point 2", ...],
                "recommendations": ["recommendation 1", "recommendation 2", ...]
            }
        }
        """
        
    def _get_shareholder_investor_agent_prompt(self) -> str:
        """Get the prompt for the Shareholder/Investor Agent."""
        return """
        You represent the perspective of shareholders and investors as stakeholders. Your role is to:
        - Analyze how the decision or strategy affects financial returns and company valuation
        - Identify short-term and long-term financial implications
        - Evaluate how the decision affects risk profile and market positioning
        - Consider different types of investors and their unique perspectives
        - Anticipate investor reactions and potential changes in investment behavior

        Based on the stakeholder map and the user's query, provide a comprehensive analysis from the shareholder/investor perspective.
        
        Format your response as a JSON object with the following structure:
        {
            "investor_analysis": {
                "overall_impact": "Overall assessment of how the decision affects shareholders/investors",
                "key_investor_segments": [
                    {
                        "segment": "Description of the investor segment (e.g., institutional, retail)",
                        "impact": "How this segment will be impacted",
                        "financial_impact": "Assessment of financial impact for this segment",
                        "risk_impact": "How risk profile changes for this segment",
                        "likely_reaction": "How this segment is likely to react"
                    },
                    ...
                ],
                "short_term_financial_impact": "Assessment of short-term financial implications",
                "long_term_financial_impact": "Assessment of long-term financial implications",
                "market_position_impact": "How the decision affects market positioning",
                "positive_impacts": ["positive impact 1", "positive impact 2", ...],
                "negative_impacts": ["negative impact 1", "negative impact 2", ...],
                "recommendations": ["recommendation 1", "recommendation 2", ...]
            }
        }
        """
        
    def _get_community_society_agent_prompt(self) -> str:
        """Get the prompt for the Community/Society Agent."""
        return """
        You represent the perspective of the broader community and society as stakeholders. Your role is to:
        - Analyze how the decision or strategy affects local communities and society at large
        - Identify environmental, social, and governance (ESG) implications
        - Evaluate how the decision aligns with social values and expectations
        - Consider impacts on different community segments and societal groups
        - Anticipate reactions from community organizations, media, and the public

        Based on the stakeholder map and the user's query, provide a comprehensive analysis from the community/society perspective.
        
        Format your response as a JSON object with the following structure:
        {
            "community_analysis": {
                "overall_impact": "Overall assessment of how the decision affects communities and society",
                "key_community_segments": [
                    {
                        "segment": "Description of the community segment",
                        "impact": "How this segment will be impacted",
                        "likely_reaction": "How this segment is likely to react"
                    },
                    ...
                ],
                "environmental_impacts": {
                    "positive": ["positive impact 1", "positive impact 2", ...],
                    "negative": ["negative impact 1", "negative impact 2", ...]
                },
                "social_impacts": {
                    "positive": ["positive impact 1", "positive impact 2", ...],
                    "negative": ["negative impact 1", "negative impact 2", ...]
                },
                "governance_impacts": {
                    "positive": ["positive impact 1", "positive impact 2", ...],
                    "negative": ["negative impact 1", "negative impact 2", ...]
                },
                "alignment_with_social_values": "Assessment of how the decision aligns with current social values",
                "anticipated_public_response": "How the public is likely to respond",
                "recommendations": ["recommendation 1", "recommendation 2", ...]
            }
        }
        """
        
    def _get_future_self_agent_prompt(self) -> str:
        """Get the prompt for the Future Self Agent."""
        return """
        You represent the user's future self as a stakeholder. Your role is to:
        - Advocate for long-term interests over short-term conveniences
        - Identify decisions that future self might regret
        - Highlight opportunities for building options and capabilities
        - Consider impacts on future identity and values
        - Promote investments with compounding returns

        Speak with the wisdom and perspective that comes from temporal distance.
        
        Based on the user's query, provide an analysis from the perspective of the user's future self.
        
        Format your response as a JSON object with the following structure:
        {
            "future_self_analysis": {
                "overall_assessment": "Overall assessment from the perspective of the user's future self",
                "long_term_interests": [
                    {
                        "interest": "Description of the long-term interest",
                        "how_served": "How the decision serves this interest",
                        "potential_conflicts_with_short_term": "Potential conflicts with short-term considerations"
                    },
                    ...
                ],
                "potential_regrets": [
                    {
                        "regret": "Description of potential regret",
                        "likelihood": "Assessment of likelihood",
                        "mitigation_strategy": "How to mitigate this potential regret"
                    },
                    ...
                ],
                "opportunity_building": [
                    {
                        "opportunity": "Description of opportunity for building future options",
                        "value": "The value this opportunity provides",
                        "implementation_approach": "How to implement this opportunity"
                    },
                    ...
                ],
                "identity_value_impacts": "How the decision impacts future identity and values",
                "compounding_investments": [
                    {
                        "investment": "Description of investment with compounding returns",
                        "expected_returns": "Expected returns over time",
                        "implementation_approach": "How to implement this investment"
                    },
                    ...
                ],
                "recommendations": ["recommendation 1", "recommendation 2", ...]
            }
        }
        """
        
    def _get_synthesis_alignment_node_prompt(self) -> str:
        """Get the prompt for the Synthesis and Alignment Node."""
        return """
        You are a stakeholder synthesis and alignment specialist. Your role is to:
        - Integrate perspectives from all stakeholder agents into a coherent understanding
        - Identify areas of alignment and conflict between stakeholders
        - Highlight trade-offs and potential compromises
        - Develop an approach that balances stakeholder interests
        - Create a comprehensive stakeholder impact assessment

        Based on the inputs from all stakeholder agents, synthesize a comprehensive stakeholder impact analysis.
        
        Format your response as a JSON object with the following structure:
        {
            "Executive Summary": "Brief summary of the stakeholder impact analysis",
            "Key Insights": ["insight 1", "insight 2", ...],
            "Strategic Recommendations": ["recommendation 1", "recommendation 2", ...],
            "Stakeholder Alignment Analysis": [
                {
                    "aligned_interests": ["interest 1", "interest 2", ...],
                    "stakeholders": ["stakeholder 1", "stakeholder 2", ...],
                    "strategic_opportunity": "How to leverage this alignment"
                },
                ...
            ],
            "Stakeholder Conflict Analysis": [
                {
                    "conflict_area": "Description of the conflict",
                    "stakeholders_involved": ["stakeholder 1", "stakeholder 2", ...],
                    "severity": "High/Medium/Low",
                    "mitigation_approach": "Approach to mitigate this conflict"
                },
                ...
            ],
            "Balanced Approach": "Description of an approach that balances stakeholder interests",
            "Implementation Steps": [
                {
                    "step": "Step description",
                    "stakeholders_involved": ["stakeholder 1", "stakeholder 2", ...],
                    "expected_outcomes": ["outcome 1", "outcome 2", ...],
                    "potential_challenges": ["challenge 1", "challenge 2", ...],
                    "success_metrics": ["metric 1", "metric 2", ...]
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
            "Success Metrics": ["metric 1", "metric 2", ...]
        }
        """
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for the Stakeholder Impact Advisory Board panel."""
        # Define the state schema
        class State(TypedDict):
            query: str
            context: Dict
            stakeholder_map: Optional[Dict]
            customer_analysis: Optional[Dict]
            team_analysis: Optional[Dict]
            investor_analysis: Optional[Dict]
            community_analysis: Optional[Dict]
            future_self_analysis: Optional[Dict]
            stakeholder_impact_assessment: Optional[Dict]
        
        # Create the graph
        graph = StateGraph(State)
        
        # Define the nodes
        
        # Stakeholder Mapper node
        def stakeholder_mapper(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Stakeholder Mapper", "processing")
                
            query = state["query"]
            context = state["context"]
            
            prompt = self.agent_prompts["stakeholder_mapper"]
            
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
                
                stakeholder_map = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Stakeholder Mapper", "Complete")
                    
                return {"stakeholder_map": stakeholder_map}
            except Exception as e:
                logger.error(f"Error parsing Stakeholder Mapper response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Stakeholder Mapper", "Error")
                return {"stakeholder_map": {"error": str(e), "raw_response": content}}
        
        # Customer/Client Agent node
        def customer_client_agent(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Customer/Client Agent", "processing")
                
            query = state["query"]
            context = state["context"]
            stakeholder_map = state["stakeholder_map"]
            
            prompt = self.agent_prompts["customer_client_agent"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nStakeholder Map: {json.dumps(stakeholder_map)}"}
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
                
                customer_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Customer/Client Agent", "Complete")
                    
                return {"customer_analysis": customer_analysis}
            except Exception as e:
                logger.error(f"Error parsing Customer/Client Agent response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Customer/Client Agent", "Error")
                return {"customer_analysis": {"error": str(e), "raw_response": content}}
        
        # Team/Employee Agent node
        def team_employee_agent(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Team/Employee Agent", "processing")
                
            query = state["query"]
            context = state["context"]
            stakeholder_map = state["stakeholder_map"]
            
            prompt = self.agent_prompts["team_employee_agent"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nStakeholder Map: {json.dumps(stakeholder_map)}"}
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
                
                team_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Team/Employee Agent", "Complete")
                    
                return {"team_analysis": team_analysis}
            except Exception as e:
                logger.error(f"Error parsing Team/Employee Agent response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Team/Employee Agent", "Error")
                return {"team_analysis": {"error": str(e), "raw_response": content}}
        
        # Shareholder/Investor Agent node
        def shareholder_investor_agent(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Shareholder/Investor Agent", "processing")
                
            query = state["query"]
            context = state["context"]
            stakeholder_map = state["stakeholder_map"]
            
            prompt = self.agent_prompts["shareholder_investor_agent"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nStakeholder Map: {json.dumps(stakeholder_map)}"}
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
                
                investor_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Shareholder/Investor Agent", "Complete")
                    
                return {"investor_analysis": investor_analysis}
            except Exception as e:
                logger.error(f"Error parsing Shareholder/Investor Agent response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Shareholder/Investor Agent", "Error")
                return {"investor_analysis": {"error": str(e), "raw_response": content}}
        
        # Community/Society Agent node
        def community_society_agent(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Community/Society Agent", "processing")
                
            query = state["query"]
            context = state["context"]
            stakeholder_map = state["stakeholder_map"]
            
            prompt = self.agent_prompts["community_society_agent"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nStakeholder Map: {json.dumps(stakeholder_map)}"}
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
                
                community_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Community/Society Agent", "Complete")
                    
                return {"community_analysis": community_analysis}
            except Exception as e:
                logger.error(f"Error parsing Community/Society Agent response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Community/Society Agent", "Error")
                return {"community_analysis": {"error": str(e), "raw_response": content}}
        
        # Future Self Agent node
        def future_self_agent(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Future Self Agent", "processing")
                
            query = state["query"]
            context = state["context"]
            stakeholder_map = state["stakeholder_map"]
            
            prompt = self.agent_prompts["future_self_agent"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nStakeholder Map: {json.dumps(stakeholder_map)}"}
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
                
                future_self_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Future Self Agent", "Complete")
                    
                return {"future_self_analysis": future_self_analysis}
            except Exception as e:
                logger.error(f"Error parsing Future Self Agent response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Future Self Agent", "Error")
                return {"future_self_analysis": {"error": str(e), "raw_response": content}}
        
        # Synthesis and Alignment Node
        def synthesis_alignment_node(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Synthesis and Alignment Node", "processing")
                
            query = state["query"]
            context = state["context"]
            stakeholder_map = state["stakeholder_map"]
            customer_analysis = state["customer_analysis"]
            team_analysis = state["team_analysis"]
            investor_analysis = state["investor_analysis"]
            community_analysis = state["community_analysis"]
            future_self_analysis = state["future_self_analysis"]
            
            prompt = self.agent_prompts["synthesis_alignment_node"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"""
                    Query: {query}
                    
                    Context: {json.dumps(context)}
                    
                    Stakeholder Map: {json.dumps(stakeholder_map)}
                    
                    Customer Analysis: {json.dumps(customer_analysis)}
                    
                    Team Analysis: {json.dumps(team_analysis)}
                    
                    Investor Analysis: {json.dumps(investor_analysis)}
                    
                    Community Analysis: {json.dumps(community_analysis)}
                    
                    Future Self Analysis: {json.dumps(future_self_analysis)}
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
                
                stakeholder_impact_assessment = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Synthesis and Alignment Node", "Complete")
                    
                return {"stakeholder_impact_assessment": stakeholder_impact_assessment}
            except Exception as e:
                logger.error(f"Error parsing Synthesis and Alignment Node response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Synthesis and Alignment Node", "Error")
                return {"stakeholder_impact_assessment": {"error": str(e), "raw_response": content}}
        
        # Add nodes to the graph
        graph.add_node("stakeholder_mapper", stakeholder_mapper)
        graph.add_node("customer_client_agent", customer_client_agent)
        graph.add_node("team_employee_agent", team_employee_agent)
        graph.add_node("shareholder_investor_agent", shareholder_investor_agent)
        graph.add_node("community_society_agent", community_society_agent)
        graph.add_node("future_self_agent", future_self_agent)
        graph.add_node("synthesis_alignment_node", synthesis_alignment_node)
        
        # Define the edges
        graph.add_edge("stakeholder_mapper", "customer_client_agent")
        graph.add_edge("stakeholder_mapper", "team_employee_agent")
        graph.add_edge("stakeholder_mapper", "shareholder_investor_agent")
        graph.add_edge("stakeholder_mapper", "community_society_agent")
        graph.add_edge("stakeholder_mapper", "future_self_agent")
        
        graph.add_edge("customer_client_agent", "synthesis_alignment_node")
        graph.add_edge("team_employee_agent", "synthesis_alignment_node")
        graph.add_edge("shareholder_investor_agent", "synthesis_alignment_node")
        graph.add_edge("community_society_agent", "synthesis_alignment_node")
        graph.add_edge("future_self_agent", "synthesis_alignment_node")
        
        graph.add_edge("synthesis_alignment_node", END)
        
        # Set the entry point
        graph.set_entry_point("stakeholder_mapper")
        
        return graph.compile()
        
    def run(self, query: str, context: str = "") -> Dict[str, Any]:
        """Run the Stakeholder Impact Advisory Board panel on the given query.
        
        Args:
            query: The query to run the panel on
            context: Context information
            
        Returns:
            The panel's output
        """
        if self.visualizer:
            self.visualizer.display_welcome("Stakeholder Impact Advisory Board")
            self.visualizer.display_query(query)
            self.visualizer.update_status("Running Stakeholder Impact Advisory Board panel")
        
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
            "stakeholder_map": {},
            "customer_analysis": {},
            "team_analysis": {},
            "investor_analysis": {},
            "community_analysis": {},
            "future_self_analysis": {},
            "stakeholder_impact_assessment": {}
        }
        
        # Run the graph
        try:
            result = self.graph.invoke(initial_state)
            
            if self.visualizer:
                self.visualizer.display_success("Stakeholder Impact Advisory Board panel completed successfully")
                self.visualizer.display_plan(result["stakeholder_impact_assessment"])
            
            return result["stakeholder_impact_assessment"]
        except Exception as e:
            logger.error(f"Error running Stakeholder Impact Advisory Board panel: {e}")
            if self.visualizer:
                self.visualizer.display_error(f"Error running Stakeholder Impact Advisory Board panel: {e}")
            return {
                "error": str(e),
                "Executive Summary": "An error occurred while generating the stakeholder impact assessment.",
                "Key Insights": ["Error in panel execution"],
                "Strategic Recommendations": ["Please try again or contact support"]
            } 