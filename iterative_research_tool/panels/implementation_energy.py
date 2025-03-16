"""Implementation Energy Panel for multi-agent advisory planning."""

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

class State(TypedDict):
    """State schema for the Implementation Energy Panel."""
    query: str
    context: Optional[dict]
    implementation_energy_assessment: Optional[dict]
    cognitive_load_analysis: Optional[dict]
    motivation_sustainability_analysis: Optional[dict]
    organizational_resistance_evaluation: Optional[dict]
    habit_formation_plan: Optional[dict]
    energy_optimized_implementation_plan: Optional[dict]

class ImplementationEnergyPanel(BasePanel):
    """Implementation Energy Panel for multi-agent advisory planning.
    
    This panel optimizes strategies for sustainable implementation energy, 
    ensuring plans are realistic, manageable, and designed to maintain 
    momentum throughout the execution phase.
    """
    
    def __init__(
        self,
        api_key: str,
        llm_provider: str = "anthropic",
        model: str = "claude-3-7-sonnet-20250219",
        visualizer = None
    ):
        """Initialize the Implementation Energy Panel.
        
        Args:
            api_key: API key for the LLM provider
            llm_provider: LLM provider to use (default: anthropic)
            model: Model to use for planning
            visualizer: Visualizer instance for displaying progress
        """
        # For backward compatibility, we'll use api_key as anthropic_api_key
        self.anthropic_api_key = api_key
        self.llm_provider = llm_provider
        self.model = model
        self.visualizer = visualizer
        
        # Initialize Anthropic client
        self.client = Anthropic(api_key=self.anthropic_api_key)
        
        # Define agent prompts
        self.agent_prompts = {
            "implementation_energy_assessor": self._get_implementation_energy_assessor_prompt(),
            "cognitive_load_analyzer": self._get_cognitive_load_analyzer_prompt(),
            "motivation_sustainability_analyst": self._get_motivation_sustainability_analyst_prompt(),
            "organizational_resistance_evaluator": self._get_organizational_resistance_evaluator_prompt(),
            "habit_formation_specialist": self._get_habit_formation_specialist_prompt(),
            "energy_optimization_synthesizer": self._get_energy_optimization_synthesizer_prompt()
        }
        
        # Initialize the graph
        self.graph = self._build_graph()
        
    def _get_implementation_energy_assessor_prompt(self) -> str:
        """Get the prompt for the Implementation Energy Assessor agent."""
        return """
        You are an implementation energy assessor who evaluates the sustainability of execution plans. Your role is to:
        - Assess the overall energy requirements of the proposed strategy or plan
        - Identify energy hotspots and potential bottlenecks in implementation
        - Evaluate the pacing and sequencing of activities for sustainable execution
        - Analyze the distribution of effort across different stages
        - Consider the match between strategy complexity and available implementation resources

        Based on the user's query and context, assess the implementation energy requirements.
        
        Format your response as a JSON object with the following structure:
        {
            "implementation_energy_assessment": {
                "summary": "Brief summary of your implementation energy assessment",
                "overall_energy_requirement": "High/Medium/Low assessment with explanation",
                "energy_bottlenecks": [
                    {
                        "bottleneck": "Description of the energy bottleneck",
                        "impact": "High/Medium/Low impact assessment",
                        "stage": "Stage of implementation where this occurs",
                        "mitigation_possibilities": ["possibility 1", "possibility 2", ...]
                    },
                    ...
                ],
                "pacing_analysis": {
                    "fast_start_elements": ["element 1", "element 2", ...],
                    "steady_pace_elements": ["element 1", "element 2", ...],
                    "high_energy_requirements": ["requirement 1", "requirement 2", ...],
                    "recovery_periods": ["period 1", "period 2", ...],
                    "overall_pacing_assessment": "Assessment of the overall pacing sustainability"
                },
                "effort_distribution": {
                    "front_loaded_percentage": "Percentage estimate with explanation",
                    "middle_stage_percentage": "Percentage estimate with explanation",
                    "final_stage_percentage": "Percentage estimate with explanation",
                    "distribution_assessment": "Assessment of whether this distribution is optimal"
                },
                "complexity_resource_match": {
                    "strategy_complexity": "High/Medium/Low with explanation",
                    "available_resources": "Assessment based on context",
                    "gap_analysis": "Analysis of any gaps between complexity and resources",
                    "match_assessment": "Overall assessment of the match"
                },
                "energy_saving_opportunities": ["opportunity 1", "opportunity 2", ...]
            }
        }
        """
        
    def _get_cognitive_load_analyzer_prompt(self) -> str:
        """Get the prompt for the Cognitive Load Analyzer agent."""
        return """
        You are a cognitive load analyzer who assesses mental effort requirements. Your role is to:
        - Evaluate the cognitive demands of different aspects of the strategy
        - Identify potential cognitive overload points in implementation
        - Analyze decision fatigue risks and mental model complexity
        - Assess attention management requirements
        - Recommend cognitive load optimization approaches

        Based on the implementation energy assessment, analyze the cognitive load aspects.
        
        Format your response as a JSON object with the following structure:
        {
            "cognitive_load_analysis": {
                "summary": "Brief summary of your cognitive load analysis",
                "key_cognitive_demands": [
                    {
                        "demand": "Description of the cognitive demand",
                        "load_level": "High/Medium/Low",
                        "affected_stakeholders": ["stakeholder 1", "stakeholder 2", ...],
                        "optimization_approaches": ["approach 1", "approach 2", ...]
                    },
                    ...
                ],
                "cognitive_overload_risks": [
                    {
                        "risk": "Description of the cognitive overload risk",
                        "trigger_conditions": ["condition 1", "condition 2", ...],
                        "warning_signs": ["sign 1", "sign 2", ...],
                        "mitigation_strategies": ["strategy 1", "strategy 2", ...]
                    },
                    ...
                ],
                "decision_fatigue_analysis": {
                    "high_fatigue_points": ["point 1", "point 2", ...],
                    "decision_complexity_assessment": "Assessment of decision complexity",
                    "decision_frequency_issues": ["issue 1", "issue 2", ...],
                    "decision_structuring_recommendations": ["recommendation 1", "recommendation 2", ...]
                },
                "mental_model_complexity": {
                    "key_mental_models_required": ["model 1", "model 2", ...],
                    "learning_curve_assessment": "Assessment of the learning curve",
                    "complexity_reduction_opportunities": ["opportunity 1", "opportunity 2", ...],
                    "knowledge_management_recommendations": ["recommendation 1", "recommendation 2", ...]
                },
                "attention_management": {
                    "attention_hotspots": ["hotspot 1", "hotspot 2", ...],
                    "context_switching_frequency": "Assessment with explanation",
                    "focus_enablers": ["enabler 1", "enabler 2", ...],
                    "distraction_risks": ["risk 1", "risk 2", ...],
                    "attention_optimization_approaches": ["approach 1", "approach 2", ...]
                },
                "overall_cognitive_optimization_plan": "Overall plan for optimizing cognitive load"
            }
        }
        """
        
    def _get_motivation_sustainability_analyst_prompt(self) -> str:
        """Get the prompt for the Motivation Sustainability Analyst agent."""
        return """
        You are a motivation sustainability analyst who evaluates engagement durability. Your role is to:
        - Analyze the motivation sustainability of the strategy throughout implementation
        - Identify motivation depletion risks and momentum loss points
        - Evaluate the incentive alignment and motivation architecture
        - Assess progress visibility and feedback loop effectiveness
        - Recommend motivation reinforcement mechanisms

        Based on the implementation energy assessment, analyze motivation sustainability.
        
        Format your response as a JSON object with the following structure:
        {
            "motivation_sustainability_analysis": {
                "summary": "Brief summary of your motivation sustainability analysis",
                "motivation_curve": {
                    "initial_motivation_assessment": "Assessment of initial motivation with explanation",
                    "middle_stage_motivation_risks": ["risk 1", "risk 2", ...],
                    "long_term_motivation_factors": ["factor 1", "factor 2", ...],
                    "critical_motivation_inflection_points": [
                        {
                            "point": "Description of the inflection point",
                            "timing": "When this occurs in the implementation process",
                            "causes": ["cause 1", "cause 2", ...],
                            "intervention_opportunities": ["opportunity 1", "opportunity 2", ...]
                        },
                        ...
                    ],
                    "curve_assessment": "Overall assessment of the motivation curve"
                },
                "motivation_depletion_risks": [
                    {
                        "risk": "Description of the motivation depletion risk",
                        "trigger_conditions": ["condition 1", "condition 2", ...],
                        "warning_signs": ["sign 1", "sign 2", ...],
                        "prevention_strategies": ["strategy 1", "strategy 2", ...]
                    },
                    ...
                ],
                "incentive_alignment": {
                    "aligned_incentives": ["incentive 1", "incentive 2", ...],
                    "misaligned_incentives": ["incentive 1", "incentive 2", ...],
                    "intrinsic_motivation_factors": ["factor 1", "factor 2", ...],
                    "extrinsic_motivation_factors": ["factor 1", "factor 2", ...],
                    "incentive_restructuring_opportunities": ["opportunity 1", "opportunity 2", ...]
                },
                "progress_visibility": {
                    "key_milestones": ["milestone 1", "milestone 2", ...],
                    "progress_measurement_mechanisms": ["mechanism 1", "mechanism 2", ...],
                    "visibility_gaps": ["gap 1", "gap 2", ...],
                    "visibility_enhancement_recommendations": ["recommendation 1", "recommendation 2", ...]
                },
                "feedback_loops": {
                    "existing_feedback_mechanisms": ["mechanism 1", "mechanism 2", ...],
                    "feedback_frequency_assessment": "Assessment with explanation",
                    "feedback_quality_issues": ["issue 1", "issue 2", ...],
                    "feedback_optimization_recommendations": ["recommendation 1", "recommendation 2", ...]
                },
                "motivation_reinforcement_plan": "Overall plan for reinforcing motivation throughout implementation"
            }
        }
        """
        
    def _get_organizational_resistance_evaluator_prompt(self) -> str:
        """Get the prompt for the Organizational Resistance Evaluator agent."""
        return """
        You are an organizational resistance evaluator who assesses implementation friction. Your role is to:
        - Identify potential organizational resistance points to the strategy
        - Evaluate cultural alignment and resistance patterns
        - Analyze stakeholder concerns and opposition sources
        - Assess power dynamics and political factors affecting implementation
        - Recommend resistance management approaches

        Based on the implementation energy assessment, evaluate organizational resistance.
        
        Format your response as a JSON object with the following structure:
        {
            "organizational_resistance_evaluation": {
                "summary": "Brief summary of your organizational resistance evaluation",
                "resistance_hotspots": [
                    {
                        "hotspot": "Description of the resistance hotspot",
                        "stakeholders_involved": ["stakeholder 1", "stakeholder 2", ...],
                        "resistance_intensity": "High/Medium/Low",
                        "underlying_causes": ["cause 1", "cause 2", ...],
                        "management_approaches": ["approach 1", "approach 2", ...]
                    },
                    ...
                ],
                "cultural_alignment": {
                    "aligned_cultural_elements": ["element 1", "element 2", ...],
                    "misaligned_cultural_elements": ["element 1", "element 2", ...],
                    "cultural_evolution_requirements": ["requirement 1", "requirement 2", ...],
                    "cultural_leverage_opportunities": ["opportunity 1", "opportunity 2", ...]
                },
                "stakeholder_concerns": [
                    {
                        "stakeholder": "Stakeholder group",
                        "primary_concerns": ["concern 1", "concern 2", ...],
                        "hidden_agendas": ["agenda 1", "agenda 2", ...],
                        "addressing_strategies": ["strategy 1", "strategy 2", ...]
                    },
                    ...
                ],
                "power_dynamics": {
                    "supportive_power_centers": ["center 1", "center 2", ...],
                    "opposing_power_centers": ["center 1", "center 2", ...],
                    "neutral_power_centers": ["center 1", "center 2", ...],
                    "political_navigation_strategy": "Strategy for navigating power dynamics"
                },
                "institutional_inertia_factors": ["factor 1", "factor 2", ...],
                "organizational_immunities_to_change": ["immunity 1", "immunity 2", ...],
                "resistance_management_plan": "Overall plan for managing organizational resistance"
            }
        }
        """
        
    def _get_habit_formation_specialist_prompt(self) -> str:
        """Get the prompt for the Habit Formation Specialist agent."""
        return """
        You are a habit formation specialist who designs sustainable behavior change. Your role is to:
        - Identify key habits needed for successful strategy implementation
        - Design habit formation loops and behavior change frameworks
        - Evaluate habit stacking opportunities and trigger-routine-reward cycles
        - Assess environmental design factors that support desired behaviors
        - Create a habit-centered implementation plan

        Based on all previous analyses, design habit formation approaches.
        
        Format your response as a JSON object with the following structure:
        {
            "habit_formation_plan": {
                "summary": "Brief summary of your habit formation plan",
                "key_implementation_habits": [
                    {
                        "habit": "Description of the habit",
                        "current_status": "Non-existent/Weak/Developing/Strong",
                        "importance": "High/Medium/Low",
                        "formation_difficulty": "High/Medium/Low",
                        "design_approach": "Approach to forming this habit"
                    },
                    ...
                ],
                "habit_loops": [
                    {
                        "trigger": "The trigger for the habit",
                        "routine": "The routine to be performed",
                        "reward": "The reward that reinforces the habit",
                        "implementation_approach": "How to implement this loop",
                        "monitoring_mechanism": "How to monitor this habit loop"
                    },
                    ...
                ],
                "habit_stacking_opportunities": [
                    {
                        "existing_habit": "The existing habit to stack upon",
                        "new_habit": "The new habit to stack",
                        "connection_mechanism": "How these habits connect",
                        "implementation_approach": "How to implement this stacking"
                    },
                    ...
                ],
                "environmental_design": {
                    "physical_environment_modifications": ["modification 1", "modification 2", ...],
                    "digital_environment_modifications": ["modification 1", "modification 2", ...],
                    "social_environment_modifications": ["modification 1", "modification 2", ...],
                    "choice_architecture_approaches": ["approach 1", "approach 2", ...]
                },
                "habit_formation_metrics": [
                    {
                        "habit": "The habit being measured",
                        "lead_indicator": "Early indicator of habit formation",
                        "lag_indicator": "Later indicator of habit entrenchment",
                        "measurement_approach": "How to measure this habit"
                    },
                    ...
                ],
                "habit_formation_timeline": "Timeline for forming the key implementation habits",
                "sustainability_mechanisms": ["mechanism 1", "mechanism 2", ...],
                "overall_habit_strategy": "Overall strategy for using habits to enable implementation"
            }
        }
        """
        
    def _get_energy_optimization_synthesizer_prompt(self) -> str:
        """Get the prompt for the Energy Optimization Synthesizer agent."""
        return """
        You are an energy optimization synthesizer who creates sustainable implementation plans. Your role is to:
        - Synthesize all previous analyses into a cohesive implementation energy strategy
        - Redesign the approach to optimize for sustainable implementation energy
        - Create an integrated plan that addresses cognitive, motivational, and organizational factors
        - Develop an energy management framework for the implementation process
        - Provide a comprehensive set of recommendations for energy-efficient execution

        Based on all previous analyses, synthesize an energy-optimized implementation plan.
        
        Format your response as a JSON object with the following structure:
        {
            "Executive Summary": "Brief executive summary of the energy-optimized implementation plan",
            "Key Insights": ["insight 1", "insight 2", ...],
            "Energy-Optimized Strategy": {
                "core_approach": "Description of the core approach",
                "energy_efficiency_principles": ["principle 1", "principle 2", ...],
                "key_modifications": [
                    {
                        "original_element": "Original element of the strategy",
                        "energy_optimized_version": "Energy-optimized version",
                        "rationale": "Rationale for this modification",
                        "expected_impact": "Expected impact on implementation energy"
                    },
                    ...
                ],
                "pacing_framework": {
                    "phase_design": [
                        {
                            "phase": "Phase name",
                            "duration": "Expected duration",
                            "energy_profile": "Energy profile for this phase",
                            "key_activities": ["activity 1", "activity 2", ...],
                            "energy_management_approach": "Approach to managing energy in this phase"
                        },
                        ...
                    ],
                    "momentum_maintenance_mechanisms": ["mechanism 1", "mechanism 2", ...],
                    "recovery_periods": ["period 1", "period 2", ...],
                    "adaptation_triggers": ["trigger 1", "trigger 2", ...]
                }
            },
            "Cognitive Optimization Plan": [
                {
                    "cognitive_element": "Element being optimized",
                    "optimization_approach": "Approach to optimization",
                    "implementation_steps": ["step 1", "step 2", ...],
                    "expected_benefits": ["benefit 1", "benefit 2", ...]
                },
                ...
            ],
            "Motivation Architecture": [
                {
                    "motivation_element": "Element being architected",
                    "design_approach": "Approach to designing this element",
                    "implementation_steps": ["step 1", "step 2", ...],
                    "sustainability_mechanisms": ["mechanism 1", "mechanism 2", ...]
                },
                ...
            ],
            "Organizational Alignment Plan": [
                {
                    "alignment_element": "Element being aligned",
                    "alignment_approach": "Approach to alignment",
                    "implementation_steps": ["step 1", "step 2", ...],
                    "resistance_management": "Approach to managing resistance"
                },
                ...
            ],
            "Habit-Centered Implementation": [
                {
                    "core_habit": "Core habit for implementation",
                    "development_approach": "Approach to developing this habit",
                    "supporting_mechanisms": ["mechanism 1", "mechanism 2", ...],
                    "measurement_approach": "Approach to measuring habit formation"
                },
                ...
            ],
            "Implementation Energy Metrics": ["metric 1", "metric 2", ...],
            "Energy Risk Management": {
                "energy_depletion_risks": ["risk 1", "risk 2", ...],
                "early_warning_indicators": ["indicator 1", "indicator 2", ...],
                "contingency_approaches": ["approach 1", "approach 2", ...],
                "energy_reserve_strategies": ["strategy 1", "strategy 2", ...]
            }
        }
        """
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for the Implementation Energy Panel."""
        # Create the graph using the State TypedDict
        graph = StateGraph(State)
        
        # Define the nodes
        
        # Implementation Energy Assessor node
        def implementation_energy_assessor(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Implementation Energy Assessor", "processing")
                
            query = state["query"]
            context = state["context"]
            
            prompt = self.agent_prompts["implementation_energy_assessor"]
            
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
                
                implementation_energy_assessment = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Implementation Energy Assessor", "Complete")
                    
                return {"implementation_energy_assessment": implementation_energy_assessment}
            except Exception as e:
                logger.error(f"Error parsing Implementation Energy Assessor response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Implementation Energy Assessor", "Error")
                return {"implementation_energy_assessment": {"error": str(e), "raw_response": content}}
        
        # Cognitive Load Analyzer node
        def cognitive_load_analyzer(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Cognitive Load Analyzer", "processing")
                
            query = state["query"]
            context = state["context"]
            implementation_energy_assessment = state["implementation_energy_assessment"]
            
            prompt = self.agent_prompts["cognitive_load_analyzer"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nImplementation Energy Assessment: {json.dumps(implementation_energy_assessment)}"}
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
                
                cognitive_load_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Cognitive Load Analyzer", "Complete")
                    
                return {"cognitive_load_analysis": cognitive_load_analysis}
            except Exception as e:
                logger.error(f"Error parsing Cognitive Load Analyzer response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Cognitive Load Analyzer", "Error")
                return {"cognitive_load_analysis": {"error": str(e), "raw_response": content}}
        
        # Motivation Sustainability Analyst node
        def motivation_sustainability_analyst(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Motivation Sustainability Analyst", "processing")
                
            query = state["query"]
            context = state["context"]
            implementation_energy_assessment = state["implementation_energy_assessment"]
            
            prompt = self.agent_prompts["motivation_sustainability_analyst"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nImplementation Energy Assessment: {json.dumps(implementation_energy_assessment)}"}
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
                
                motivation_sustainability_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Motivation Sustainability Analyst", "Complete")
                    
                return {"motivation_sustainability_analysis": motivation_sustainability_analysis}
            except Exception as e:
                logger.error(f"Error parsing Motivation Sustainability Analyst response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Motivation Sustainability Analyst", "Error")
                return {"motivation_sustainability_analysis": {"error": str(e), "raw_response": content}}
        
        # Organizational Resistance Evaluator node
        def organizational_resistance_evaluator(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Organizational Resistance Evaluator", "processing")
                
            query = state["query"]
            context = state["context"]
            implementation_energy_assessment = state["implementation_energy_assessment"]
            
            prompt = self.agent_prompts["organizational_resistance_evaluator"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nImplementation Energy Assessment: {json.dumps(implementation_energy_assessment)}"}
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
                
                organizational_resistance_evaluation = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Organizational Resistance Evaluator", "Complete")
                    
                return {"organizational_resistance_evaluation": organizational_resistance_evaluation}
            except Exception as e:
                logger.error(f"Error parsing Organizational Resistance Evaluator response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Organizational Resistance Evaluator", "Error")
                return {"organizational_resistance_evaluation": {"error": str(e), "raw_response": content}}
        
        # Habit Formation Specialist node
        def habit_formation_specialist(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Habit Formation Specialist", "processing")
                
            query = state["query"]
            context = state["context"]
            implementation_energy_assessment = state["implementation_energy_assessment"]
            cognitive_load_analysis = state["cognitive_load_analysis"]
            motivation_sustainability_analysis = state["motivation_sustainability_analysis"]
            organizational_resistance_evaluation = state["organizational_resistance_evaluation"]
            
            prompt = self.agent_prompts["habit_formation_specialist"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"""
                    Query: {query}
                    
                    Context: {json.dumps(context)}
                    
                    Implementation Energy Assessment: {json.dumps(implementation_energy_assessment)}
                    
                    Cognitive Load Analysis: {json.dumps(cognitive_load_analysis)}
                    
                    Motivation Sustainability Analysis: {json.dumps(motivation_sustainability_analysis)}
                    
                    Organizational Resistance Evaluation: {json.dumps(organizational_resistance_evaluation)}
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
                
                habit_formation_plan = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Habit Formation Specialist", "Complete")
                    
                return {"habit_formation_plan": habit_formation_plan}
            except Exception as e:
                logger.error(f"Error parsing Habit Formation Specialist response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Habit Formation Specialist", "Error")
                return {"habit_formation_plan": {"error": str(e), "raw_response": content}}
        
        # Energy Optimization Synthesizer node
        def energy_optimization_synthesizer(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Energy Optimization Synthesizer", "processing")
                
            query = state["query"]
            context = state["context"]
            implementation_energy_assessment = state["implementation_energy_assessment"]
            cognitive_load_analysis = state["cognitive_load_analysis"]
            motivation_sustainability_analysis = state["motivation_sustainability_analysis"]
            organizational_resistance_evaluation = state["organizational_resistance_evaluation"]
            habit_formation_plan = state["habit_formation_plan"]
            
            prompt = self.agent_prompts["energy_optimization_synthesizer"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"""
                    Query: {query}
                    
                    Context: {json.dumps(context)}
                    
                    Implementation Energy Assessment: {json.dumps(implementation_energy_assessment)}
                    
                    Cognitive Load Analysis: {json.dumps(cognitive_load_analysis)}
                    
                    Motivation Sustainability Analysis: {json.dumps(motivation_sustainability_analysis)}
                    
                    Organizational Resistance Evaluation: {json.dumps(organizational_resistance_evaluation)}
                    
                    Habit Formation Plan: {json.dumps(habit_formation_plan)}
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
                
                energy_optimized_implementation_plan = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Energy Optimization Synthesizer", "Complete")
                    
                return {"energy_optimized_implementation_plan": energy_optimized_implementation_plan}
            except Exception as e:
                logger.error(f"Error parsing Energy Optimization Synthesizer response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Energy Optimization Synthesizer", "Error")
                return {"energy_optimized_implementation_plan": {"error": str(e), "raw_response": content}}
        
        # Add nodes to the graph
        graph.add_node("implementation_energy_assessor", implementation_energy_assessor)
        graph.add_node("cognitive_load_analyzer", cognitive_load_analyzer)
        graph.add_node("motivation_sustainability_analyst", motivation_sustainability_analyst)
        graph.add_node("organizational_resistance_evaluator", organizational_resistance_evaluator)
        graph.add_node("habit_formation_specialist", habit_formation_specialist)
        graph.add_node("energy_optimization_synthesizer", energy_optimization_synthesizer)
        
        # Define the edges
        graph.add_edge("implementation_energy_assessor", "cognitive_load_analyzer")
        graph.add_edge("implementation_energy_assessor", "motivation_sustainability_analyst")
        graph.add_edge("implementation_energy_assessor", "organizational_resistance_evaluator")
        graph.add_edge("cognitive_load_analyzer", "habit_formation_specialist")
        graph.add_edge("motivation_sustainability_analyst", "habit_formation_specialist")
        graph.add_edge("organizational_resistance_evaluator", "habit_formation_specialist")
        graph.add_edge("habit_formation_specialist", "energy_optimization_synthesizer")
        graph.add_edge("energy_optimization_synthesizer", END)
        
        # Set the entry point
        graph.set_entry_point("implementation_energy_assessor")
        
        # Return the compiled graph
        return graph.compile()
        
    def run(self, query: str, context: str = "") -> Dict[str, Any]:
        """Run the Implementation Energy Panel on the given query.
        
        Args:
            query: The query to run the panel on
            context: Context information
            
        Returns:
            The panel's output
        """
        if self.visualizer:
            self.visualizer.display_welcome("Implementation Energy Panel")
            self.visualizer.display_query(query)
            self.visualizer.update_status("Running Implementation Energy Panel")
        
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
            "implementation_energy_assessment": {},
            "cognitive_load_analysis": {},
            "motivation_sustainability_analysis": {},
            "organizational_resistance_evaluation": {},
            "habit_formation_plan": {},
            "energy_optimized_implementation_plan": {}
        }
        
        # Run the graph
        try:
            result = self.graph.invoke(initial_state)
            
            if self.visualizer:
                self.visualizer.display_success("Implementation Energy Panel completed successfully")
                self.visualizer.display_plan(result["energy_optimized_implementation_plan"])
            
            return result["energy_optimized_implementation_plan"]
        except Exception as e:
            logger.error(f"Error running Implementation Energy Panel: {e}")
            if self.visualizer:
                self.visualizer.display_error(f"Error running Implementation Energy Panel: {e}")
            return {
                "error": str(e),
                "Executive Summary": "An error occurred while running the Implementation Energy Panel.",
                "Key Insights": ["Error in panel execution"],
                "Energy-Optimized Strategy": {"core_approach": "Please try again or contact support"}
            } 