"""Product Development Panel for multi-agent advisory planning."""

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

class ProductDevelopmentPanel(BasePanel):
    """Product Development Panel for multi-agent advisory planning.
    
    This panel provides comprehensive product strategy advice, including
    market analysis, customer insights, product positioning, development
    roadmapping, and go-to-market strategies.
    """
    
    def __init__(
        self,
        anthropic_api_key: str,
        model: str = "claude-3-7-sonnet-20250219",
        visualizer = None
    ):
        """Initialize the Product Development Panel.
        
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
            "market_opportunity_analyzer": self._get_market_opportunity_analyzer_prompt(),
            "customer_insight_specialist": self._get_customer_insight_specialist_prompt(),
            "product_positioning_strategist": self._get_product_positioning_strategist_prompt(),
            "technical_feasibility_evaluator": self._get_technical_feasibility_evaluator_prompt(),
            "competitive_landscape_mapper": self._get_competitive_landscape_mapper_prompt(),
            "product_roadmap_developer": self._get_product_roadmap_developer_prompt(),
            "go_to_market_strategist": self._get_go_to_market_strategist_prompt(),
            "product_strategy_synthesizer": self._get_product_strategy_synthesizer_prompt()
        }
        
        # Initialize the graph
        self.graph = self._build_graph()
        
    def _get_market_opportunity_analyzer_prompt(self) -> str:
        """Get the prompt for the Market Opportunity Analyzer agent."""
        return """
        You are a market opportunity analyzer who identifies and evaluates market opportunities. Your role is to:
        - Analyze market size, growth, and trends relevant to the product concept
        - Identify market segments and their relative attractiveness
        - Evaluate market timing and window of opportunity
        - Analyze key market drivers and potential market barriers
        - Provide an overall assessment of market opportunity

        Based on the user's query about product development, analyze the market opportunity.
        
        Format your response as a JSON object with the following structure:
        {
            "market_analysis": {
                "summary": "Brief summary of your market opportunity analysis",
                "market_size_and_growth": {
                    "current_market_size": "Assessment of current market size with data where available",
                    "growth_forecast": "Forecast for market growth with timeframe",
                    "market_maturity": "Assessment of where the market is in its lifecycle",
                    "growth_drivers": ["driver 1", "driver 2", ...],
                    "market_size_assessment": "Overall assessment of market size opportunity"
                },
                "market_segmentation": [
                    {
                        "segment": "Name of the market segment",
                        "size": "Estimated size of this segment",
                        "growth": "Growth rate of this segment",
                        "needs": ["need 1", "need 2", ...],
                        "attractiveness": "High/Medium/Low with explanation",
                        "fit_with_concept": "Assessment of fit with the product concept"
                    },
                    ...
                ],
                "market_timing": {
                    "window_of_opportunity": "Assessment of the window of opportunity",
                    "timing_factors": ["factor 1", "factor 2", ...],
                    "urgency_assessment": "Assessment of urgency to enter the market",
                    "timing_risks": ["risk 1", "risk 2", ...]
                },
                "market_drivers": [
                    {
                        "driver": "Name of the market driver",
                        "impact": "High/Medium/Low",
                        "direction": "Positive/Negative",
                        "explanation": "Explanation of how this driver affects the market"
                    },
                    ...
                ],
                "market_barriers": [
                    {
                        "barrier": "Name of the market barrier",
                        "impact": "High/Medium/Low",
                        "mitigation_possibilities": ["possibility 1", "possibility 2", ...],
                        "explanation": "Explanation of how this barrier affects market entry"
                    },
                    ...
                ],
                "opportunity_assessment": {
                    "overall_attractiveness": "High/Medium/Low with explanation",
                    "key_opportunities": ["opportunity 1", "opportunity 2", ...],
                    "key_risks": ["risk 1", "risk 2", ...],
                    "recommended_focus_areas": ["area 1", "area 2", ...]
                }
            }
        }
        """
        
    def _get_customer_insight_specialist_prompt(self) -> str:
        """Get the prompt for the Customer Insight Specialist agent."""
        return """
        You are a customer insight specialist who deeply understands customer needs and behaviors. Your role is to:
        - Identify key customer personas and their characteristics
        - Analyze customer needs, pain points, and jobs-to-be-done
        - Evaluate the customer journey and key touchpoints
        - Assess customer willingness to pay and pricing psychology
        - Recommend customer-centric product features and approaches

        Based on the market analysis, provide customer insights for the product concept.
        
        Format your response as a JSON object with the following structure:
        {
            "customer_insights": {
                "summary": "Brief summary of your customer insights",
                "customer_personas": [
                    {
                        "persona": "Name of the customer persona",
                        "description": "Brief description of this persona",
                        "demographics": "Key demographics of this persona",
                        "psychographics": "Key psychographics of this persona",
                        "goals": ["goal 1", "goal 2", ...],
                        "pain_points": ["pain point 1", "pain point 2", ...],
                        "decision_criteria": ["criterion 1", "criterion 2", ...],
                        "influence_level": "Assessment of this persona's influence in purchase decisions"
                    },
                    ...
                ],
                "jobs_to_be_done": [
                    {
                        "job": "Description of the job-to-be-done",
                        "context": "Context in which this job arises",
                        "importance": "High/Medium/Low",
                        "current_solutions": ["solution 1", "solution 2", ...],
                        "satisfaction_with_current": "Assessment of current satisfaction",
                        "improvement_opportunities": ["opportunity 1", "opportunity 2", ...]
                    },
                    ...
                ],
                "customer_journey": {
                    "awareness_stage": {
                        "touchpoints": ["touchpoint 1", "touchpoint 2", ...],
                        "customer_needs": ["need 1", "need 2", ...],
                        "key_challenges": ["challenge 1", "challenge 2", ...],
                        "optimization_opportunities": ["opportunity 1", "opportunity 2", ...]
                    },
                    "consideration_stage": {
                        "touchpoints": ["touchpoint 1", "touchpoint 2", ...],
                        "customer_needs": ["need 1", "need 2", ...],
                        "key_challenges": ["challenge 1", "challenge 2", ...],
                        "optimization_opportunities": ["opportunity 1", "opportunity 2", ...]
                    },
                    "purchase_stage": {
                        "touchpoints": ["touchpoint 1", "touchpoint 2", ...],
                        "customer_needs": ["need 1", "need 2", ...],
                        "key_challenges": ["challenge 1", "challenge 2", ...],
                        "optimization_opportunities": ["opportunity 1", "opportunity 2", ...]
                    },
                    "post_purchase_stage": {
                        "touchpoints": ["touchpoint 1", "touchpoint 2", ...],
                        "customer_needs": ["need 1", "need 2", ...],
                        "key_challenges": ["challenge 1", "challenge 2", ...],
                        "optimization_opportunities": ["opportunity 1", "opportunity 2", ...]
                    }
                },
                "willingness_to_pay": {
                    "price_sensitivity": "Assessment of price sensitivity",
                    "value_perception_factors": ["factor 1", "factor 2", ...],
                    "pricing_model_recommendations": ["recommendation 1", "recommendation 2", ...],
                    "price_range_assessment": "Assessment of viable price range"
                },
                "customer_centric_recommendations": {
                    "must_have_features": ["feature 1", "feature 2", ...],
                    "key_differentiators": ["differentiator 1", "differentiator 2", ...],
                    "experience_design_principles": ["principle 1", "principle 2", ...],
                    "customer_engagement_approaches": ["approach 1", "approach 2", ...]
                }
            }
        }
        """
        
    def _get_product_positioning_strategist_prompt(self) -> str:
        """Get the prompt for the Product Positioning Strategist agent."""
        return """
        You are a product positioning strategist who defines how products should be positioned in the market. Your role is to:
        - Develop a compelling value proposition for the product
        - Define key differentiating factors and competitive advantages
        - Create messaging frameworks and positioning statements
        - Align positioning with target customer segments
        - Ensure positioning supports the product's strategic objectives

        Based on the market analysis and customer insights, develop product positioning.
        
        Format your response as a JSON object with the following structure:
        {
            "product_positioning": {
                "summary": "Brief summary of your product positioning",
                "value_proposition": {
                    "core_value_proposition": "The main value proposition for the product",
                    "supporting_elements": ["element 1", "element 2", ...],
                    "value_proposition_by_segment": [
                        {
                            "segment": "Target segment",
                            "value_proposition": "Value proposition for this segment",
                            "rationale": "Rationale for this value proposition"
                        },
                        ...
                    ],
                    "evidence_points": ["evidence 1", "evidence 2", ...]
                },
                "differentiation": {
                    "key_differentiators": [
                        {
                            "differentiator": "Description of the differentiator",
                            "importance_to_customers": "High/Medium/Low",
                            "sustainability": "Assessment of how sustainable this differentiator is",
                            "communication_approach": "How to communicate this differentiator"
                        },
                        ...
                    ],
                    "competitive_advantages": [
                        {
                            "advantage": "Description of the competitive advantage",
                            "source": "Source of this competitive advantage",
                            "defensibility": "Assessment of how defensible this advantage is",
                            "leverage_approach": "How to leverage this advantage"
                        },
                        ...
                    ],
                    "differentiation_strategy": "Overall strategy for differentiation",
                    "white_space_opportunities": ["opportunity 1", "opportunity 2", ...]
                },
                "messaging_framework": {
                    "positioning_statement": "Formal positioning statement for the product",
                    "tagline_options": ["tagline 1", "tagline 2", ...],
                    "key_messages": [
                        {
                            "audience": "Target audience for this message",
                            "message": "The key message for this audience",
                            "supporting_points": ["point 1", "point 2", ...],
                            "communication_channels": ["channel 1", "channel 2", ...]
                        },
                        ...
                    ],
                    "brand_personality": ["personality trait 1", "personality trait 2", ...],
                    "tone_and_voice": "Recommendations for tone and voice"
                },
                "segment_alignment": [
                    {
                        "segment": "Target segment",
                        "positioning_approach": "Positioning approach for this segment",
                        "key_messages": ["message 1", "message 2", ...],
                        "objection_handling": ["objection handling 1", "objection handling 2", ...]
                    },
                    ...
                ],
                "strategic_alignment": {
                    "alignment_with_objectives": "Assessment of alignment with strategic objectives",
                    "market_perception_goals": ["goal 1", "goal 2", ...],
                    "positioning_evolution": "How positioning should evolve over time",
                    "success_metrics": ["metric 1", "metric 2", ...]
                }
            }
        }
        """
        
    def _get_technical_feasibility_evaluator_prompt(self) -> str:
        """Get the prompt for the Technical Feasibility Evaluator agent."""
        return """
        You are a technical feasibility evaluator who assesses the technical viability of product concepts. Your role is to:
        - Evaluate core technical requirements and technological dependencies
        - Assess development complexity and resource requirements
        - Identify technical risks and potential mitigation approaches
        - Recommend development approaches and technology stack options
        - Provide a timeline assessment for development phases

        Based on the product concept, evaluate technical feasibility.
        
        Format your response as a JSON object with the following structure:
        {
            "technical_feasibility_assessment": {
                "summary": "Brief summary of your technical feasibility assessment",
                "core_technical_requirements": [
                    {
                        "requirement": "Description of the technical requirement",
                        "complexity": "High/Medium/Low",
                        "criticality": "High/Medium/Low",
                        "feasibility": "Assessment of feasibility"
                    },
                    ...
                ],
                "technology_dependencies": [
                    {
                        "dependency": "Description of the technology dependency",
                        "maturity": "Assessment of technology maturity",
                        "availability": "Assessment of availability",
                        "alternatives": ["alternative 1", "alternative 2", ...],
                        "risk_level": "High/Medium/Low"
                    },
                    ...
                ],
                "development_assessment": {
                    "overall_complexity": "Assessment of overall development complexity",
                    "resource_requirements": {
                        "skills_needed": ["skill 1", "skill 2", ...],
                        "team_size_estimate": "Estimated team size required",
                        "specialized_expertise": ["expertise 1", "expertise 2", ...],
                        "infrastructure_needs": ["need 1", "need 2", ...]
                    },
                    "build_vs_buy_considerations": [
                        {
                            "component": "Component being considered",
                            "build_considerations": ["consideration 1", "consideration 2", ...],
                            "buy_considerations": ["consideration 1", "consideration 2", ...],
                            "recommendation": "Build/Buy/Hybrid with rationale"
                        },
                        ...
                    ],
                    "development_approach": "Recommended development approach (e.g., agile, waterfall)"
                },
                "technical_risks": [
                    {
                        "risk": "Description of the technical risk",
                        "probability": "High/Medium/Low",
                        "impact": "High/Medium/Low",
                        "mitigation_strategy": "Strategy to mitigate this risk",
                        "contingency_plan": "Plan if the risk materializes"
                    },
                    ...
                ],
                "technology_stack_recommendations": {
                    "frontend": ["technology 1", "technology 2", ...],
                    "backend": ["technology 1", "technology 2", ...],
                    "database": ["technology 1", "technology 2", ...],
                    "infrastructure": ["technology 1", "technology 2", ...],
                    "third_party_services": ["service 1", "service 2", ...],
                    "rationale": "Rationale for these technology choices"
                },
                "timeline_assessment": {
                    "mvp_timeline": "Estimated timeline for MVP development",
                    "full_product_timeline": "Estimated timeline for full product development",
                    "key_milestones": [
                        {
                            "milestone": "Description of the milestone",
                            "timeline": "Estimated timeline for this milestone",
                            "dependencies": ["dependency 1", "dependency 2", ...],
                            "risk_factors": ["risk factor 1", "risk factor 2", ...]
                        },
                        ...
                    ],
                    "scaling_considerations": ["consideration 1", "consideration 2", ...]
                },
                "overall_feasibility": "Overall assessment of technical feasibility"
            }
        }
        """
        
    def _get_competitive_landscape_mapper_prompt(self) -> str:
        """Get the prompt for the Competitive Landscape Mapper agent."""
        return """
        You are a competitive landscape mapper who analyzes the competitive environment for the product. Your role is to:
        - Identify key competitors and their market positions
        - Analyze competitive strategies and market dynamics
        - Assess the competitive landscape and potential threats
        - Recommend strategies for gaining market share

        Based on the market analysis, analyze the competitive landscape for the product.
        
        Format your response as a JSON object with the following structure:
        {
            "competitive_landscape": {
                "summary": "Brief summary of your competitive landscape analysis",
                "key_competitors": [
                    {
                        "competitor": "Name of the competitor",
                        "market_position": "Current market position of the competitor",
                        "competitive_strategy": "Key competitive strategy of the competitor",
                        "market_share": "Market share of the competitor",
                        "threat_level": "High/Medium/Low"
                    },
                    ...
                ],
                "market_dynamics": {
                    "growth_rate": "Overall growth rate of the market",
                    "market_concentration": "Assessment of market concentration",
                    "entry_barriers": "Assessment of entry barriers",
                    "exit_barriers": "Assessment of exit barriers"
                },
                "competitive_threats": [
                    {
                        "threat": "Description of the competitive threat",
                        "probability": "High/Medium/Low",
                        "impact": "High/Medium/Low",
                        "mitigation_strategy": "Strategy to mitigate this threat"
                    },
                    ...
                ],
                "market_share_strategy": "Recommended strategy for gaining market share"
            }
        }
        """
        
    def _get_product_roadmap_developer_prompt(self) -> str:
        """Get the prompt for the Product Roadmap Developer agent."""
        return """
        You are a product roadmap developer who plans and develops product roadmaps. Your role is to:
        - Define product roadmap stages and milestones
        - Identify key product features and functionalities
        - Schedule development phases and timelines
        - Allocate resources and team members
        - Ensure roadmap alignment with strategic objectives

        Based on the market analysis, customer insights, and product positioning, develop a product roadmap.
        
        Format your response as a JSON object with the following structure:
        {
            "product_roadmap": {
                "summary": "Brief summary of your product roadmap",
                "stages": [
                    {
                        "stage": "Name of the product stage",
                        "description": "Brief description of this stage",
                        "milestones": [
                            {
                                "milestone": "Description of the milestone",
                                "timeline": "Estimated timeline for this milestone",
                                "dependencies": ["dependency 1", "dependency 2", ...],
                                "risk_factors": ["risk factor 1", "risk factor 2", ...]
                            },
                            ...
                        ],
                        "key_features": ["feature 1", "feature 2", ...],
                        "resource_allocation": {
                            "skills_needed": ["skill 1", "skill 2", ...],
                            "team_size_estimate": "Estimated team size required",
                            "specialized_expertise": ["expertise 1", "expertise 2", ...],
                            "infrastructure_needs": ["need 1", "need 2", ...]
                        },
                        "strategic_alignment": {
                            "alignment_with_objectives": "Assessment of alignment with strategic objectives",
                            "market_perception_goals": ["goal 1", "goal 2", ...]
                        }
                    },
                    ...
                ],
                "strategic_alignment": {
                    "alignment_with_objectives": "Assessment of alignment with strategic objectives",
                    "market_perception_goals": ["goal 1", "goal 2", ...]
                }
            }
        }
        """
        
    def _get_go_to_market_strategist_prompt(self) -> str:
        """Get the prompt for the Go-to-Market Strategist agent."""
        return """
        You are a go-to-market strategist who plans and executes go-to-market strategies. Your role is to:
        - Develop a comprehensive go-to-market strategy
        - Identify key channels and distribution methods
        - Allocate resources and team members
        - Monitor and adjust strategy execution

        Based on the market analysis, product positioning, and product roadmap, develop a go-to-market strategy.
        
        Format your response as a JSON object with the following structure:
        {
            "go_to_market_strategy": {
                "summary": "Brief summary of your go-to-market strategy",
                "strategy_components": [
                    {
                        "component": "Name of the go-to-market component",
                        "description": "Brief description of this component",
                        "strategy_approach": "Strategy approach for this component",
                        "resource_allocation": {
                            "skills_needed": ["skill 1", "skill 2", ...],
                            "team_size_estimate": "Estimated team size required",
                            "specialized_expertise": ["expertise 1", "expertise 2", ...],
                            "infrastructure_needs": ["need 1", "need 2", ...]
                        },
                        "strategic_alignment": {
                            "alignment_with_objectives": "Assessment of alignment with strategic objectives",
                            "market_perception_goals": ["goal 1", "goal 2", ...]
                        }
                    },
                    ...
                ],
                "strategic_alignment": {
                    "alignment_with_objectives": "Assessment of alignment with strategic objectives",
                    "market_perception_goals": ["goal 1", "goal 2", ...]
                }
            }
        }
        """
        
    def _get_product_strategy_synthesizer_prompt(self) -> str:
        """Get the prompt for the Product Strategy Synthesizer agent."""
        return """
        You are a product strategy synthesizer who combines insights from various agents to develop a comprehensive product strategy. Your role is to:
        - Integrate insights from market opportunity analyzer, customer insight specialist, product positioning strategist, technical feasibility evaluator, competitive landscape mapper, product roadmap developer, go-to-market strategist, and product strategy synthesizer
        - Develop a comprehensive product strategy that aligns with strategic objectives
        - Ensure strategy consistency across all product components

        Based on the insights from all agents, synthesize a comprehensive product strategy.
        
        Format your response as a JSON object with the following structure:
        {
            "Executive Summary": "Brief executive summary of the product strategy",
            "Key Insights": ["insight 1", "insight 2", ...],
            "Market Strategy": {
                "target_markets": ["market 1", "market 2", ...],
                "market_entry_approach": "Approach to entering the market",
                "market_expansion_strategy": "Strategy for market expansion",
                "market_differentiation": "How the product will differentiate in the market"
            },
            "Product Strategy": {
                "core_product_definition": "Definition of the core product",
                "key_features_and_benefits": [
                    {
                        "feature": "Description of the feature",
                        "benefit": "Benefit this feature provides",
                        "target_segment": "Segment this benefits",
                        "priority": "High/Medium/Low"
                    },
                    ...
                ],
                "product_roadmap_summary": "Summary of the product roadmap",
                "technical_approach": "High-level technical approach"
            },
            "Customer Strategy": {
                "target_customer_segments": ["segment 1", "segment 2", ...],
                "value_proposition_summary": "Summary of the value proposition",
                "customer_acquisition_approach": "Approach to customer acquisition",
                "customer_retention_strategy": "Strategy for customer retention"
            },
            "Competitive Strategy": {
                "competitive_positioning": "How the product is positioned against competitors",
                "competitive_advantages": ["advantage 1", "advantage 2", ...],
                "response_to_competitive_threats": "How to respond to competitive threats",
                "market_share_strategy": "Strategy for gaining market share"
            },
            "Go-to-Market Strategy": {
                "launch_approach": "Approach to product launch",
                "channel_strategy": "Strategy for distribution channels",
                "pricing_strategy": "Strategy for product pricing",
                "marketing_and_communications": "Marketing and communications approach"
            },
            "Implementation Plan": {
                "key_milestones": [
                    {
                        "milestone": "Description of the milestone",
                        "timeline": "Estimated timeline",
                        "key_dependencies": ["dependency 1", "dependency 2", ...],
                        "success_criteria": ["criterion 1", "criterion 2", ...]
                    },
                    ...
                ],
                "resource_requirements": {
                    "team_composition": ["role 1", "role 2", ...],
                    "budget_considerations": "High-level budget considerations",
                    "key_partnerships": ["partnership 1", "partnership 2", ...],
                    "infrastructure_needs": ["need 1", "need 2", ...]
                },
                "risk_management": [
                    {
                        "risk": "Description of the risk",
                        "probability": "High/Medium/Low",
                        "impact": "High/Medium/Low",
                        "mitigation_strategy": "Strategy to mitigate this risk"
                    },
                    ...
                ]
            },
            "Success Metrics": [
                {
                    "metric": "Description of the metric",
                    "target": "Target value",
                    "measurement_approach": "How to measure this metric",
                    "timeframe": "Timeframe for measurement"
                },
                ...
            ],
            "Strategic Alignment": "How the product strategy aligns with broader organizational goals"
        }
        """
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for the Product Development Panel."""
        # Define the state schema
        from typing import TypedDict, Optional as Opt
        
        class State(TypedDict):
            query: str
            context: str
            market_opportunity: Opt[dict]
            customer_insights: Opt[dict]
            product_positioning: Opt[dict]
            technical_feasibility: Opt[dict]
            product_roadmap: Opt[dict]
            go_to_market: Opt[dict]
            product_strategy: Opt[dict]
            competitive_landscape: Opt[dict]
        
        # Create the graph
        graph = StateGraph(State)
        
        # Define the nodes
        
        # Market Opportunity Analyzer node
        def market_opportunity_analyzer(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Market Opportunity Analyzer", "processing")
                
            query = state["query"]
            context = state["context"]
            
            prompt = self.agent_prompts["market_opportunity_analyzer"]
            
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
                
                market_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Market Opportunity Analyzer", "Complete")
                    
                return {"market_opportunity": market_analysis}
            except Exception as e:
                logger.error(f"Error parsing Market Opportunity Analyzer response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Market Opportunity Analyzer", "Error")
                return {"market_opportunity": {"error": str(e), "raw_response": content}}
        
        # Customer Insight Specialist node
        def customer_insight_specialist(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Customer Insight Specialist", "processing")
                
            query = state["query"]
            context = state["context"]
            market_analysis = state["market_opportunity"]
            
            prompt = self.agent_prompts["customer_insight_specialist"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nMarket Analysis: {json.dumps(market_analysis)}"}
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
                
                customer_insights = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Customer Insight Specialist", "Complete")
                    
                return {"customer_insights": customer_insights}
            except Exception as e:
                logger.error(f"Error parsing Customer Insight Specialist response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Customer Insight Specialist", "Error")
                return {"customer_insights": {"error": str(e), "raw_response": content}}
        
        # Product Positioning Strategist node
        def product_positioning_strategist(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Product Positioning Strategist", "processing")
                
            query = state["query"]
            context = state["context"]
            market_analysis = state["market_opportunity"]
            customer_insights = state["customer_insights"]
            
            prompt = self.agent_prompts["product_positioning_strategist"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"""
                    Query: {query}
                    
                    Context: {json.dumps(context)}
                    
                    Market Analysis: {json.dumps(market_analysis)}
                    
                    Customer Insights: {json.dumps(customer_insights)}
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
                
                product_positioning = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Product Positioning Strategist", "Complete")
                    
                return {"product_positioning": product_positioning}
            except Exception as e:
                logger.error(f"Error parsing Product Positioning Strategist response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Product Positioning Strategist", "Error")
                return {"product_positioning": {"error": str(e), "raw_response": content}}
        
        # Technical Feasibility Evaluator node
        def technical_feasibility_evaluator(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Technical Feasibility Evaluator", "processing")
                
            query = state["query"]
            context = state["context"]
            market_analysis = state["market_opportunity"]
            customer_insights = state["customer_insights"]
            product_positioning = state["product_positioning"]
            
            prompt = self.agent_prompts["technical_feasibility_evaluator"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"""
                    Query: {query}
                    
                    Context: {json.dumps(context)}
                    
                    Market Analysis: {json.dumps(market_analysis)}
                    
                    Customer Insights: {json.dumps(customer_insights)}
                    
                    Product Positioning: {json.dumps(product_positioning)}
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
                
                technical_feasibility = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Technical Feasibility Evaluator", "Complete")
                    
                return {"technical_feasibility": technical_feasibility}
            except Exception as e:
                logger.error(f"Error parsing Technical Feasibility Evaluator response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Technical Feasibility Evaluator", "Error")
                return {"technical_feasibility": {"error": str(e), "raw_response": content}}
        
        # Competitive Landscape Mapper node
        def competitive_landscape_mapper(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Competitive Landscape Mapper", "processing")
                
            query = state["query"]
            context = state["context"]
            market_analysis = state["market_opportunity"]
            product_positioning = state["product_positioning"]
            
            prompt = self.agent_prompts["competitive_landscape_mapper"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"""
                    Query: {query}
                    
                    Context: {json.dumps(context)}
                    
                    Market Analysis: {json.dumps(market_analysis)}
                    
                    Product Positioning: {json.dumps(product_positioning)}
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
                
                competitive_landscape = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Competitive Landscape Mapper", "Complete")
                    
                return {"competitive_landscape": competitive_landscape}
            except Exception as e:
                logger.error(f"Error parsing Competitive Landscape Mapper response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Competitive Landscape Mapper", "Error")
                return {"competitive_landscape": {"error": str(e), "raw_response": content}}
        
        # Product Roadmap Developer node
        def product_roadmap_developer(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Product Roadmap Developer", "processing")
                
            query = state["query"]
            context = state["context"]
            market_analysis = state["market_opportunity"]
            customer_insights = state["customer_insights"]
            product_positioning = state["product_positioning"]
            technical_feasibility = state["technical_feasibility"]
            competitive_landscape = state["competitive_landscape"]
            
            prompt = self.agent_prompts["product_roadmap_developer"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"""
                    Query: {query}
                    
                    Context: {json.dumps(context)}
                    
                    Market Analysis: {json.dumps(market_analysis)}
                    
                    Customer Insights: {json.dumps(customer_insights)}
                    
                    Product Positioning: {json.dumps(product_positioning)}
                    
                    Technical Feasibility: {json.dumps(technical_feasibility)}
                    
                    Competitive Landscape: {json.dumps(competitive_landscape)}
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
                
                product_roadmap = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Product Roadmap Developer", "Complete")
                    
                return {"product_roadmap": product_roadmap}
            except Exception as e:
                logger.error(f"Error parsing Product Roadmap Developer response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Product Roadmap Developer", "Error")
                return {"product_roadmap": {"error": str(e), "raw_response": content}}
        
        # Go-to-Market Strategist node
        def go_to_market_strategist(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Go-to-Market Strategist", "processing")
                
            query = state["query"]
            context = state["context"]
            market_analysis = state["market_opportunity"]
            customer_insights = state["customer_insights"]
            product_positioning = state["product_positioning"]
            competitive_landscape = state["competitive_landscape"]
            product_roadmap = state["product_roadmap"]
            
            prompt = self.agent_prompts["go_to_market_strategist"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"""
                    Query: {query}
                    
                    Context: {json.dumps(context)}
                    
                    Market Analysis: {json.dumps(market_analysis)}
                    
                    Customer Insights: {json.dumps(customer_insights)}
                    
                    Product Positioning: {json.dumps(product_positioning)}
                    
                    Competitive Landscape: {json.dumps(competitive_landscape)}
                    
                    Product Roadmap: {json.dumps(product_roadmap)}
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
                
                go_to_market = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Go-to-Market Strategist", "Complete")
                    
                return {"go_to_market": go_to_market}
            except Exception as e:
                logger.error(f"Error parsing Go-to-Market Strategist response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Go-to-Market Strategist", "Error")
                return {"go_to_market": {"error": str(e), "raw_response": content}}
        
        # Product Strategy Synthesizer node
        def product_strategy_synthesizer(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Product Strategy Synthesizer", "processing")
                
            query = state["query"]
            context = state["context"]
            market_analysis = state["market_opportunity"]
            customer_insights = state["customer_insights"]
            product_positioning = state["product_positioning"]
            technical_feasibility = state["technical_feasibility"]
            competitive_landscape = state["competitive_landscape"]
            product_roadmap = state["product_roadmap"]
            go_to_market = state["go_to_market"]
            
            prompt = self.agent_prompts["product_strategy_synthesizer"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"""
                    Query: {query}
                    
                    Context: {json.dumps(context)}
                    
                    Market Analysis: {json.dumps(market_analysis)}
                    
                    Customer Insights: {json.dumps(customer_insights)}
                    
                    Product Positioning: {json.dumps(product_positioning)}
                    
                    Technical Feasibility: {json.dumps(technical_feasibility)}
                    
                    Competitive Landscape: {json.dumps(competitive_landscape)}
                    
                    Product Roadmap: {json.dumps(product_roadmap)}
                    
                    Go-to-Market Strategy: {json.dumps(go_to_market)}
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
                
                product_strategy = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Product Strategy Synthesizer", "Complete")
                    
                return {"product_strategy": product_strategy}
            except Exception as e:
                logger.error(f"Error parsing Product Strategy Synthesizer response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Product Strategy Synthesizer", "Error")
                return {"product_strategy": {"error": str(e), "raw_response": content}}
        
        # Add nodes to the graph
        graph.add_node("market_opportunity_analyzer", market_opportunity_analyzer)
        graph.add_node("customer_insight_specialist", customer_insight_specialist)
        graph.add_node("product_positioning_strategist", product_positioning_strategist)
        graph.add_node("technical_feasibility_evaluator", technical_feasibility_evaluator)
        graph.add_node("competitive_landscape_mapper", competitive_landscape_mapper)
        graph.add_node("product_roadmap_developer", product_roadmap_developer)
        graph.add_node("go_to_market_strategist", go_to_market_strategist)
        graph.add_node("product_strategy_synthesizer", product_strategy_synthesizer)
        
        # Define the edges
        graph.add_edge("market_opportunity_analyzer", "customer_insight_specialist")
        graph.add_edge("market_opportunity_analyzer", "competitive_landscape_mapper")
        graph.add_edge("customer_insight_specialist", "product_positioning_strategist")
        graph.add_edge("product_positioning_strategist", "technical_feasibility_evaluator")
        graph.add_edge("competitive_landscape_mapper", "product_roadmap_developer")
        graph.add_edge("technical_feasibility_evaluator", "product_roadmap_developer")
        graph.add_edge("product_roadmap_developer", "go_to_market_strategist")
        graph.add_edge("go_to_market_strategist", "product_strategy_synthesizer")
        graph.add_edge("product_strategy_synthesizer", END)
        
        # Set the entry point
        graph.set_entry_point("market_opportunity_analyzer")
        
        # Return the compiled graph
        return graph.compile()
        
    def run(self, query: str, context: str = "") -> Dict[str, Any]:
        """Run the Product Development Panel on the given query.
        
        Args:
            query: The query to run the panel on
            context: Context information
            
        Returns:
            The panel's output
        """
        if self.visualizer:
            self.visualizer.display_welcome("Product Development Panel")
            self.visualizer.display_query(query)
            self.visualizer.update_status("Running Product Development Panel")
        
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
            "market_opportunity": {},
            "customer_insights": {},
            "product_positioning": {},
            "technical_feasibility": {},
            "product_roadmap": {},
            "go_to_market": {},
            "product_strategy": {},
            "competitive_landscape": {}
        }
        
        # Run the graph
        try:
            result = self.graph.invoke(initial_state)
            
            if self.visualizer:
                self.visualizer.display_success("Product Development Panel completed successfully")
                self.visualizer.display_plan(result["product_strategy"])
            
            return result["product_strategy"]
        except Exception as e:
            logger.error(f"Error running Product Development Panel: {e}")
            if self.visualizer:
                self.visualizer.display_error(f"Error running Product Development Panel: {e}")
            return {
                "error": str(e),
                "Executive Summary": "An error occurred while running the Product Development Panel.",
                "Key Insights": ["Error in panel execution"],
                "Product Strategy": {"core_product_definition": "Please try again or contact support"}
            } 