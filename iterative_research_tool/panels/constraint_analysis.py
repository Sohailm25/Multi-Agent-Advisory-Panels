"""Constraint Analysis Panel for multi-agent advisory planning."""

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

class ConstraintAnalysisPanel(BasePanel):
    """Constraint Analysis Panel for multi-agent advisory planning.
    
    This panel identifies and analyzes different types of constraints affecting strategy implementation,
    converting perceived limitations into creative opportunities.
    """
    
    def __init__(
        self,
        anthropic_api_key: str,
        model: str = "claude-3-7-sonnet-20250219",
        visualizer = None
    ):
        """Initialize the Constraint Analysis Panel.
        
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
            "constraint_identifier": self._get_constraint_identifier_prompt(),
            "resource_constraints_analyst": self._get_resource_constraints_analyst_prompt(),
            "technical_constraints_analyst": self._get_technical_constraints_analyst_prompt(),
            "regulatory_constraints_analyst": self._get_regulatory_constraints_analyst_prompt(),
            "market_constraints_analyst": self._get_market_constraints_analyst_prompt(),
            "internal_constraints_analyst": self._get_internal_constraints_analyst_prompt(),
            "constraint_opportunity_synthesizer": self._get_constraint_opportunity_synthesizer_prompt()
        }
        
        # Initialize the graph
        self.graph = self._build_graph()
        
    def _get_constraint_identifier_prompt(self) -> str:
        """Get the prompt for the Constraint Identifier agent."""
        return """
        You are a comprehensive constraint identification specialist. Your role is to:
        - Identify all potential constraints affecting the strategic initiative or decision
        - Categorize constraints by type (resource, technical, regulatory, market, internal, etc.)
        - Determine severity and impact of different constraints
        - Detect hidden or less obvious constraints often overlooked
        - Prioritize which constraints need deeper analysis

        Based on the user's query and context, identify and categorize all relevant constraints.
        
        Format your response as a JSON object with the following structure:
        {
            "analysis": "Your detailed analysis of the constraint landscape",
            "constraint_categories": [
                {
                    "category": "Category name (e.g., Resource, Technical, Regulatory, etc.)",
                    "specific_constraints": [
                        {
                            "constraint": "Description of the specific constraint",
                            "severity": "High/Medium/Low",
                            "impact": "Description of how this constraint impacts the initiative",
                            "is_firm": "Yes/No/Maybe (whether the constraint is fixed or flexible)",
                            "priority_for_analysis": "High/Medium/Low"
                        },
                        ...
                    ]
                },
                ...
            ],
            "hidden_constraints": [
                {
                    "constraint": "Description of the hidden constraint",
                    "category": "Category it belongs to",
                    "reason_overlooked": "Why this constraint is often overlooked",
                    "potential_impact": "Potential impact if not addressed"
                },
                ...
            ],
            "priority_constraints": ["constraint 1", "constraint 2", ...]
        }
        """
        
    def _get_resource_constraints_analyst_prompt(self) -> str:
        """Get the prompt for the Resource Constraints Analyst agent."""
        return """
        You are a resource constraints analyst. Your role is to:
        - Deeply analyze constraints related to budget, time, people, and materials
        - Identify strategies for optimizing limited resources
        - Find creative approaches to work within resource limitations
        - Suggest resource reallocation opportunities
        - Develop time-phased approaches to manage resource constraints

        Based on the constraint identification and the user's query, provide a comprehensive analysis of resource constraints.
        
        Format your response as a JSON object with the following structure:
        {
            "resource_analysis": {
                "financial_constraints": {
                    "constraints": ["constraint 1", "constraint 2", ...],
                    "optimization_strategies": ["strategy 1", "strategy 2", ...],
                    "creative_approaches": ["approach 1", "approach 2", ...],
                    "reallocation_opportunities": ["opportunity 1", "opportunity 2", ...]
                },
                "time_constraints": {
                    "constraints": ["constraint 1", "constraint 2", ...],
                    "optimization_strategies": ["strategy 1", "strategy 2", ...],
                    "creative_approaches": ["approach 1", "approach 2", ...],
                    "phasing_opportunities": ["opportunity 1", "opportunity 2", ...]
                },
                "human_resource_constraints": {
                    "constraints": ["constraint 1", "constraint 2", ...],
                    "optimization_strategies": ["strategy 1", "strategy 2", ...],
                    "creative_approaches": ["approach 1", "approach 2", ...],
                    "skill_development_opportunities": ["opportunity 1", "opportunity 2", ...]
                },
                "material_constraints": {
                    "constraints": ["constraint 1", "constraint 2", ...],
                    "optimization_strategies": ["strategy 1", "strategy 2", ...],
                    "creative_approaches": ["approach 1", "approach 2", ...],
                    "substitution_opportunities": ["opportunity 1", "opportunity 2", ...]
                },
                "key_recommendations": ["recommendation 1", "recommendation 2", ...]
            }
        }
        """
        
    def _get_technical_constraints_analyst_prompt(self) -> str:
        """Get the prompt for the Technical Constraints Analyst agent."""
        return """
        You are a technical constraints analyst. Your role is to:
        - Deeply analyze constraints related to technology, infrastructure, and capabilities
        - Identify strategies for overcoming technical limitations
        - Suggest technological alternatives or workarounds
        - Evaluate build vs. buy vs. partner options
        - Develop approaches to manage technical debt

        Based on the constraint identification and the user's query, provide a comprehensive analysis of technical constraints.
        
        Format your response as a JSON object with the following structure:
        {
            "technical_analysis": {
                "technology_constraints": {
                    "constraints": ["constraint 1", "constraint 2", ...],
                    "mitigation_strategies": ["strategy 1", "strategy 2", ...],
                    "alternatives": ["alternative 1", "alternative 2", ...],
                    "opportunity_areas": ["opportunity 1", "opportunity 2", ...]
                },
                "infrastructure_constraints": {
                    "constraints": ["constraint 1", "constraint 2", ...],
                    "mitigation_strategies": ["strategy 1", "strategy 2", ...],
                    "alternatives": ["alternative 1", "alternative 2", ...],
                    "opportunity_areas": ["opportunity 1", "opportunity 2", ...]
                },
                "capability_constraints": {
                    "constraints": ["constraint 1", "constraint 2", ...],
                    "mitigation_strategies": ["strategy 1", "strategy 2", ...],
                    "skill_development_approaches": ["approach 1", "approach 2", ...],
                    "opportunity_areas": ["opportunity 1", "opportunity 2", ...]
                },
                "build_buy_partner_analysis": {
                    "build_options": ["option 1", "option 2", ...],
                    "buy_options": ["option 1", "option 2", ...],
                    "partner_options": ["option 1", "option 2", ...],
                    "recommendations": ["recommendation 1", "recommendation 2", ...]
                },
                "technical_debt_management": {
                    "current_debt_areas": ["area 1", "area 2", ...],
                    "management_strategies": ["strategy 1", "strategy 2", ...],
                    "opportunity_areas": ["opportunity 1", "opportunity 2", ...]
                },
                "key_recommendations": ["recommendation 1", "recommendation 2", ...]
            }
        }
        """
        
    def _get_regulatory_constraints_analyst_prompt(self) -> str:
        """Get the prompt for the Regulatory Constraints Analyst agent."""
        return """
        You are a regulatory constraints analyst. Your role is to:
        - Deeply analyze constraints related to laws, regulations, and compliance requirements
        - Identify strategies for navigating regulatory environments
        - Suggest approaches to ensure compliance while achieving objectives
        - Evaluate regulatory risks and mitigation strategies
        - Identify potential advocacy or policy engagement opportunities

        Based on the constraint identification and the user's query, provide a comprehensive analysis of regulatory constraints.
        
        Format your response as a JSON object with the following structure:
        {
            "regulatory_analysis": {
                "legal_constraints": {
                    "constraints": ["constraint 1", "constraint 2", ...],
                    "navigation_strategies": ["strategy 1", "strategy 2", ...],
                    "risk_areas": ["risk 1", "risk 2", ...],
                    "opportunity_areas": ["opportunity 1", "opportunity 2", ...]
                },
                "compliance_constraints": {
                    "constraints": ["constraint 1", "constraint 2", ...],
                    "compliance_strategies": ["strategy 1", "strategy 2", ...],
                    "risk_areas": ["risk 1", "risk 2", ...],
                    "opportunity_areas": ["opportunity 1", "opportunity 2", ...]
                },
                "policy_constraints": {
                    "constraints": ["constraint 1", "constraint 2", ...],
                    "navigation_strategies": ["strategy 1", "strategy 2", ...],
                    "advocacy_opportunities": ["opportunity 1", "opportunity 2", ...],
                    "engagement_strategies": ["strategy 1", "strategy 2", ...]
                },
                "regional_variations": [
                    {
                        "region": "Region name",
                        "specific_constraints": ["constraint 1", "constraint 2", ...],
                        "navigation_strategies": ["strategy 1", "strategy 2", ...]
                    },
                    ...
                ],
                "future_regulatory_trends": {
                    "anticipated_changes": ["change 1", "change 2", ...],
                    "preparation_strategies": ["strategy 1", "strategy 2", ...],
                    "opportunity_areas": ["opportunity 1", "opportunity 2", ...]
                },
                "key_recommendations": ["recommendation 1", "recommendation 2", ...]
            }
        }
        """
        
    def _get_market_constraints_analyst_prompt(self) -> str:
        """Get the prompt for the Market Constraints Analyst agent."""
        return """
        You are a market constraints analyst. Your role is to:
        - Deeply analyze constraints related to market conditions, competition, and customer expectations
        - Identify strategies for navigating market limitations
        - Suggest approaches to differentiate within crowded markets
        - Evaluate competitor responses and counter-strategies
        - Identify opportunities to reframe market constraints

        Based on the constraint identification and the user's query, provide a comprehensive analysis of market constraints.
        
        Format your response as a JSON object with the following structure:
        {
            "market_analysis": {
                "market_condition_constraints": {
                    "constraints": ["constraint 1", "constraint 2", ...],
                    "navigation_strategies": ["strategy 1", "strategy 2", ...],
                    "opportunity_areas": ["opportunity 1", "opportunity 2", ...]
                },
                "competitive_constraints": {
                    "constraints": ["constraint 1", "constraint 2", ...],
                    "differentiation_strategies": ["strategy 1", "strategy 2", ...],
                    "anticipated_responses": ["response 1", "response 2", ...],
                    "counter_strategies": ["strategy 1", "strategy 2", ...]
                },
                "customer_expectation_constraints": {
                    "constraints": ["constraint 1", "constraint 2", ...],
                    "expectation_management_strategies": ["strategy 1", "strategy 2", ...],
                    "experience_enhancement_opportunities": ["opportunity 1", "opportunity 2", ...]
                },
                "pricing_constraints": {
                    "constraints": ["constraint 1", "constraint 2", ...],
                    "pricing_strategies": ["strategy 1", "strategy 2", ...],
                    "value_demonstration_approaches": ["approach 1", "approach 2", ...]
                },
                "distribution_constraints": {
                    "constraints": ["constraint 1", "constraint 2", ...],
                    "channel_strategies": ["strategy 1", "strategy 2", ...],
                    "innovative_approaches": ["approach 1", "approach 2", ...]
                },
                "key_recommendations": ["recommendation 1", "recommendation 2", ...]
            }
        }
        """
        
    def _get_internal_constraints_analyst_prompt(self) -> str:
        """Get the prompt for the Internal Constraints Analyst agent."""
        return """
        You are an internal constraints analyst. Your role is to:
        - Deeply analyze constraints related to organizational culture, processes, and politics
        - Identify strategies for navigating internal resistance and limitations
        - Suggest approaches to build support and momentum
        - Evaluate power dynamics and potential allies/opponents
        - Identify opportunities to transform cultural constraints

        Based on the constraint identification and the user's query, provide a comprehensive analysis of internal constraints.
        
        Format your response as a JSON object with the following structure:
        {
            "internal_analysis": {
                "cultural_constraints": {
                    "constraints": ["constraint 1", "constraint 2", ...],
                    "navigation_strategies": ["strategy 1", "strategy 2", ...],
                    "transformation_opportunities": ["opportunity 1", "opportunity 2", ...]
                },
                "process_constraints": {
                    "constraints": ["constraint 1", "constraint 2", ...],
                    "optimization_strategies": ["strategy 1", "strategy 2", ...],
                    "innovation_opportunities": ["opportunity 1", "opportunity 2", ...]
                },
                "political_constraints": {
                    "constraints": ["constraint 1", "constraint 2", ...],
                    "navigation_strategies": ["strategy 1", "strategy 2", ...],
                    "alliance_building_approaches": ["approach 1", "approach 2", ...]
                },
                "stakeholder_map": [
                    {
                        "stakeholder": "Stakeholder name/role",
                        "likely_position": "Supporter/Opponent/Neutral",
                        "key_concerns": ["concern 1", "concern 2", ...],
                        "engagement_strategy": "How to engage this stakeholder"
                    },
                    ...
                ],
                "organizational_structure_constraints": {
                    "constraints": ["constraint 1", "constraint 2", ...],
                    "navigation_strategies": ["strategy 1", "strategy 2", ...],
                    "restructuring_opportunities": ["opportunity 1", "opportunity 2", ...]
                },
                "key_recommendations": ["recommendation 1", "recommendation 2", ...]
            }
        }
        """
        
    def _get_constraint_opportunity_synthesizer_prompt(self) -> str:
        """Get the prompt for the Constraint-Opportunity Synthesizer agent."""
        return """
        You are a constraint-opportunity synthesis specialist. Your role is to:
        - Integrate analysis from all constraint specialists into a coherent framework
        - Transform constraints into creative opportunities and advantages
        - Identify hidden benefits within apparent limitations
        - Develop a constraint-based innovation strategy
        - Create actionable recommendations that embrace constraints

        Based on the inputs from all constraint analysts, synthesize a comprehensive constraint-opportunity analysis.
        
        Format your response as a JSON object with the following structure:
        {
            "Executive Summary": "Brief summary of the constraint-opportunity analysis",
            "Key Insights": ["insight 1", "insight 2", ...],
            "Strategic Recommendations": ["recommendation 1", "recommendation 2", ...],
            "Constraint-Opportunity Matrix": [
                {
                    "constraint_category": "Category name",
                    "key_constraints": ["constraint 1", "constraint 2", ...],
                    "reframed_as_opportunities": ["opportunity 1", "opportunity 2", ...],
                    "strategic_advantages": ["advantage 1", "advantage 2", ...],
                    "innovation_triggers": ["trigger 1", "trigger 2", ...]
                },
                ...
            ],
            "Implementation Approach": {
                "phasing_strategy": "Description of phased approach to address constraints",
                "quick_wins": ["quick win 1", "quick win 2", ...],
                "medium_term_initiatives": ["initiative 1", "initiative 2", ...],
                "long_term_transformations": ["transformation 1", "transformation 2", ...]
            },
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
        """Build the LangGraph workflow for the Constraint Analysis Panel."""
        # Define the state schema
        class State(TypedDict):
            query: str
            context: str
            constraints: Optional[dict]
            resource_constraints: Optional[dict]
            technical_constraints: Optional[dict]
            regulatory_constraints: Optional[dict]
            market_analysis: Optional[dict]
            internal_analysis: Optional[dict]
            constraint_opportunity_synthesis: Optional[dict]
        
        graph = StateGraph(State)
        
        # Define the nodes
        
        # Constraint Identifier node
        def constraint_identifier(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Constraint Identifier", "processing")
                
            query = state["query"]
            context = state["context"]
            
            prompt = self.agent_prompts["constraint_identifier"]
            
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
                
                constraint_identification = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Constraint Identifier", "Complete")
                    
                return {"constraints": constraint_identification}
            except Exception as e:
                logger.error(f"Error parsing Constraint Identifier response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Constraint Identifier", "Error")
                return {"constraints": {"error": str(e), "raw_response": content}}
        
        # Resource Constraints Analyst node
        def resource_constraints_analyst(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Resource Constraints Analyst", "processing")
                
            query = state["query"]
            context = state["context"]
            constraints = state["constraints"]
            
            prompt = self.agent_prompts["resource_constraints_analyst"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nConstraint Identification: {json.dumps(constraints)}"}
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
                
                resource_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Resource Constraints Analyst", "Complete")
                    
                return {"resource_constraints": resource_analysis}
            except Exception as e:
                logger.error(f"Error parsing Resource Constraints Analyst response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Resource Constraints Analyst", "Error")
                return {"resource_constraints": {"error": str(e), "raw_response": content}}
        
        # Technical Constraints Analyst node
        def technical_constraints_analyst(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Technical Constraints Analyst", "processing")
                
            query = state["query"]
            context = state["context"]
            constraints = state["constraints"]
            
            prompt = self.agent_prompts["technical_constraints_analyst"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nConstraint Identification: {json.dumps(constraints)}"}
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
                
                technical_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Technical Constraints Analyst", "Complete")
                    
                return {"technical_constraints": technical_analysis}
            except Exception as e:
                logger.error(f"Error parsing Technical Constraints Analyst response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Technical Constraints Analyst", "Error")
                return {"technical_constraints": {"error": str(e), "raw_response": content}}
        
        # Regulatory Constraints Analyst node
        def regulatory_constraints_analyst(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Regulatory Constraints Analyst", "processing")
                
            query = state["query"]
            context = state["context"]
            constraints = state["constraints"]
            
            prompt = self.agent_prompts["regulatory_constraints_analyst"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nConstraint Identification: {json.dumps(constraints)}"}
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
                
                regulatory_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Regulatory Constraints Analyst", "Complete")
                    
                return {"regulatory_constraints": regulatory_analysis}
            except Exception as e:
                logger.error(f"Error parsing Regulatory Constraints Analyst response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Regulatory Constraints Analyst", "Error")
                return {"regulatory_constraints": {"error": str(e), "raw_response": content}}
        
        # Market Constraints Analyst node
        def market_constraints_analyst(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Market Constraints Analyst", "processing")
                
            query = state["query"]
            context = state["context"]
            constraints = state["constraints"]
            
            prompt = self.agent_prompts["market_constraints_analyst"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nConstraint Identification: {json.dumps(constraints)}"}
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
                
                market_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Market Constraints Analyst", "Complete")
                    
                return {"market_analysis": market_analysis}
            except Exception as e:
                logger.error(f"Error parsing Market Constraints Analyst response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Market Constraints Analyst", "Error")
                return {"market_analysis": {"error": str(e), "raw_response": content}}
        
        # Internal Constraints Analyst node
        def internal_constraints_analyst(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Internal Constraints Analyst", "processing")
                
            query = state["query"]
            context = state["context"]
            constraints = state["constraints"]
            
            prompt = self.agent_prompts["internal_constraints_analyst"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nConstraint Identification: {json.dumps(constraints)}"}
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
                
                internal_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Internal Constraints Analyst", "Complete")
                    
                return {"internal_analysis": internal_analysis}
            except Exception as e:
                logger.error(f"Error parsing Internal Constraints Analyst response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Internal Constraints Analyst", "Error")
                return {"internal_analysis": {"error": str(e), "raw_response": content}}
        
        # Constraint-Opportunity Synthesizer node
        def constraint_opportunity_synthesizer(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Constraint-Opportunity Synthesizer", "processing")
                
            query = state["query"]
            context = state["context"]
            constraints = state["constraints"]
            resource_constraints = state["resource_constraints"]
            technical_constraints = state["technical_constraints"]
            regulatory_constraints = state["regulatory_constraints"]
            market_analysis = state["market_analysis"]
            internal_analysis = state["internal_analysis"]
            
            prompt = self.agent_prompts["constraint_opportunity_synthesizer"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"""
                    Query: {query}
                    
                    Context: {json.dumps(context)}
                    
                    Constraint Identification: {json.dumps(constraints)}
                    
                    Resource Constraints: {json.dumps(resource_constraints)}
                    
                    Technical Constraints: {json.dumps(technical_constraints)}
                    
                    Regulatory Constraints: {json.dumps(regulatory_constraints)}
                    
                    Market Analysis: {json.dumps(market_analysis)}
                    
                    Internal Analysis: {json.dumps(internal_analysis)}
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
                
                constraint_opportunity_synthesis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Constraint-Opportunity Synthesizer", "Complete")
                    
                return {"constraint_opportunity_synthesis": constraint_opportunity_synthesis}
            except Exception as e:
                logger.error(f"Error parsing Constraint-Opportunity Synthesizer response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Constraint-Opportunity Synthesizer", "Error")
                return {"constraint_opportunity_synthesis": {"error": str(e), "raw_response": content}}
        
        # Add nodes to the graph
        graph.add_node("constraint_identifier", constraint_identifier)
        graph.add_node("resource_constraints_analyst", resource_constraints_analyst)
        graph.add_node("technical_constraints_analyst", technical_constraints_analyst)
        graph.add_node("regulatory_constraints_analyst", regulatory_constraints_analyst)
        graph.add_node("market_constraints_analyst", market_constraints_analyst)
        graph.add_node("internal_constraints_analyst", internal_constraints_analyst)
        graph.add_node("constraint_opportunity_synthesizer", constraint_opportunity_synthesizer)
        
        # Define the edges
        graph.add_edge("constraint_identifier", "resource_constraints_analyst")
        graph.add_edge("constraint_identifier", "technical_constraints_analyst")
        graph.add_edge("constraint_identifier", "regulatory_constraints_analyst")
        graph.add_edge("constraint_identifier", "market_constraints_analyst")
        graph.add_edge("constraint_identifier", "internal_constraints_analyst")
        
        graph.add_edge("resource_constraints_analyst", "constraint_opportunity_synthesizer")
        graph.add_edge("technical_constraints_analyst", "constraint_opportunity_synthesizer")
        graph.add_edge("regulatory_constraints_analyst", "constraint_opportunity_synthesizer")
        graph.add_edge("market_constraints_analyst", "constraint_opportunity_synthesizer")
        graph.add_edge("internal_constraints_analyst", "constraint_opportunity_synthesizer")
        
        graph.add_edge("constraint_opportunity_synthesizer", END)
        
        # Set the entry point
        graph.set_entry_point("constraint_identifier")
        
        # Return the compiled graph
        return graph.compile()
        
    def run(self, query: str, context: str = "") -> Dict[str, Any]:
        """Run the Constraint Analysis Panel on the given query.
        
        Args:
            query: The query to run the panel on
            context: Context information
            
        Returns:
            The panel's output
        """
        if self.visualizer:
            self.visualizer.display_welcome("Constraint Analysis Panel")
            self.visualizer.display_query(query)
            self.visualizer.update_status("Running Constraint Analysis Panel")
        
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
            "constraints": {},
            "resource_constraints": {},
            "technical_constraints": {},
            "regulatory_constraints": {},
            "market_analysis": {},
            "internal_analysis": {},
            "constraint_opportunity_synthesis": {}
        }
        
        # Run the graph
        try:
            result = self.graph.invoke(initial_state)
            
            if self.visualizer:
                self.visualizer.display_success("Constraint Analysis Panel completed successfully")
                self.visualizer.display_plan(result["constraint_opportunity_synthesis"])
            
            return result["constraint_opportunity_synthesis"]
        except Exception as e:
            logger.error(f"Error running Constraint Analysis Panel: {e}")
            if self.visualizer:
                self.visualizer.display_error(f"Error running Constraint Analysis Panel: {e}")
            return {
                "error": str(e),
                "Executive Summary": "An error occurred while generating the constraint-opportunity analysis.",
                "Key Insights": ["Error in panel execution"],
                "Strategic Recommendations": ["Please try again or contact support"]
            } 