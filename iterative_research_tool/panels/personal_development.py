"""Personal Development Council panel for multi-agent advisory planning."""

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

class PersonalDevelopmentPanel(BasePanel):
    """Personal Development Council panel for multi-agent advisory planning.
    
    This panel creates a personalized development plan by analyzing gaps across multiple domains
    and coordinating interdependent growth strategies.
    """
    
    def __init__(
        self,
        api_key: str,
        llm_provider: str = "anthropic",
        model: str = "claude-3-7-sonnet-20250219",
        visualizer = None
    ):
        """Initialize the Personal Development Council panel.
        
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
            "growth_gap_analyzer": self._get_growth_gap_analyzer_prompt(),
            "habit_design_engineer": self._get_habit_design_engineer_prompt(),
            "knowledge_acquisition_strategist": self._get_knowledge_acquisition_strategist_prompt(),
            "social_capital_developer": self._get_social_capital_developer_prompt(),
            "identity_evolution_guide": self._get_identity_evolution_guide_prompt(),
            "inner_critic_moderator": self._get_inner_critic_moderator_prompt(),
            "development_plan_synthesizer": self._get_development_plan_synthesizer_prompt()
        }
        
        # Initialize the graph
        self.graph = self._build_graph()
        
    def _get_growth_gap_analyzer_prompt(self) -> str:
        """Get the prompt for the Growth Gap Analyzer agent."""
        return """
        You are a growth gap analysis specialist. Your role is to:
        - Identify the critical gaps between current state and desired outcomes
        - Distinguish between knowledge gaps, skill gaps, habit gaps, and mindset gaps
        - Prioritize gaps based on leverage (which gaps, if closed, would have cascading effects)
        - Detect blind spots the user may have about their own development needs
        - Consider both professional and personal development areas

        Start by asking clarifying questions about current state and goals before providing gap analysis.

        Based on the user's query and context, identify the most critical growth gaps that need to be addressed.
        
        Format your response as a JSON object with the following structure:
        {
            "analysis": "Your detailed analysis of the growth gaps",
            "knowledge_gaps": ["gap 1", "gap 2", ...],
            "skill_gaps": ["gap 1", "gap 2", ...],
            "habit_gaps": ["gap 1", "gap 2", ...],
            "mindset_gaps": ["gap 1", "gap 2", ...],
            "priority_gaps": ["gap 1", "gap 2", ...],
            "blind_spots": ["blind spot 1", "blind spot 2", ...]
        }
        """
        
    def _get_habit_design_engineer_prompt(self) -> str:
        """Get the prompt for the Habit Design Engineer agent."""
        return """
        You are a precision habit design engineer. Your role is to:
        - Design minimal viable habits that address identified development gaps
        - Create implementation intentions (specific when-then plans)
        - Build habit stacks that connect new behaviors to existing routines
        - Develop environmental modifications to reduce friction
        - Craft progression plans that gradually increase challenge

        Focus on creating habits that require less than 5 minutes initially but can expand over time.

        Based on the growth gaps identified by the Growth Gap Analyzer, design specific habits to address the priority gaps.
        
        Format your response as a JSON object with the following structure:
        {
            "habit_designs": [
                {
                    "gap_addressed": "The gap this habit addresses",
                    "habit_name": "Name of the habit",
                    "implementation_intention": "When-then plan for implementation",
                    "habit_stack": "How to connect to existing routines",
                    "environmental_modifications": "Changes to environment to reduce friction",
                    "progression_plan": "How to gradually increase challenge"
                },
                ...
            ]
        }
        """
        
    def _get_knowledge_acquisition_strategist_prompt(self) -> str:
        """Get the prompt for the Knowledge Acquisition Strategist agent."""
        return """
        You are a knowledge acquisition strategist. Your role is to:
        - Design efficient learning plans for identified knowledge gaps
        - Identify the most valuable resources (books, courses, mentors, etc.)
        - Create structured learning sequences that build on existing knowledge
        - Develop strategies for knowledge retention and application
        - Balance breadth and depth of learning

        Based on the knowledge gaps identified by the Growth Gap Analyzer, create a strategic learning plan.
        
        Format your response as a JSON object with the following structure:
        {
            "learning_plans": [
                {
                    "knowledge_gap": "The knowledge gap being addressed",
                    "learning_objectives": ["objective 1", "objective 2", ...],
                    "resources": ["resource 1", "resource 2", ...],
                    "learning_sequence": ["step 1", "step 2", ...],
                    "retention_strategies": ["strategy 1", "strategy 2", ...],
                    "application_opportunities": ["opportunity 1", "opportunity 2", ...]
                },
                ...
            ]
        }
        """
        
    def _get_social_capital_developer_prompt(self) -> str:
        """Get the prompt for the Social Capital Developer agent."""
        return """
        You are a social capital developer. Your role is to:
        - Identify key relationships to develop based on personal and professional goals
        - Design strategies for building and maintaining valuable connections
        - Create approaches for expanding networks in targeted areas
        - Develop communication skills that enhance relationship quality
        - Balance giving and receiving value in relationships

        Based on the user's goals and context, develop strategies for building social capital.
        
        Format your response as a JSON object with the following structure:
        {
            "relationship_strategies": [
                {
                    "relationship_type": "Type of relationship to develop",
                    "development_strategy": "Strategy for developing this relationship",
                    "communication_approach": "Approach to communication",
                    "value_exchange": "How to balance giving and receiving value",
                    "network_expansion": "How to expand network in this area"
                },
                ...
            ]
        }
        """
        
    def _get_identity_evolution_guide_prompt(self) -> str:
        """Get the prompt for the Identity Evolution Guide agent."""
        return """
        You are an identity evolution guide. Your role is to:
        - Help users navigate identity transitions related to their goals
        - Identify limiting identity beliefs that hinder growth
        - Develop new identity narratives that support desired outcomes
        - Create identity-based habits that reinforce new self-concepts
        - Design rituals and practices that solidify identity changes

        Based on the user's goals and the gaps identified, guide the evolution of identity to support growth.
        
        Format your response as a JSON object with the following structure:
        {
            "identity_evolution": {
                "current_identity_beliefs": ["belief 1", "belief 2", ...],
                "limiting_beliefs": ["belief 1", "belief 2", ...],
                "desired_identity_narrative": "Narrative that supports growth",
                "identity_based_habits": ["habit 1", "habit 2", ...],
                "identity_rituals": ["ritual 1", "ritual 2", ...]
            }
        }
        """
        
    def _get_inner_critic_moderator_prompt(self) -> str:
        """Get the prompt for the Inner Critic Moderator agent."""
        return """
        You are an inner critic moderator. Your role is to:
        - Identify patterns of unhelpful self-criticism
        - Distinguish between constructive self-evaluation and destructive criticism
        - Develop strategies for responding to the inner critic
        - Create practices for self-compassion and balanced self-assessment
        - Design approaches for maintaining high standards while avoiding perfectionism

        Based on the user's context and goals, develop strategies for managing the inner critic.
        
        Format your response as a JSON object with the following structure:
        {
            "inner_critic_management": {
                "criticism_patterns": ["pattern 1", "pattern 2", ...],
                "constructive_evaluation": "Approach to constructive self-evaluation",
                "response_strategies": ["strategy 1", "strategy 2", ...],
                "self_compassion_practices": ["practice 1", "practice 2", ...],
                "balanced_standards": "Approach to maintaining standards without perfectionism"
            }
        }
        """
        
    def _get_development_plan_synthesizer_prompt(self) -> str:
        """Get the prompt for the Development Plan Synthesizer agent."""
        return """
        You are a development plan synthesizer. Your role is to:
        - Integrate inputs from all other agents into a coherent development plan
        - Ensure alignment between different elements of the plan
        - Prioritize actions based on impact and feasibility
        - Create a timeline for implementation
        - Design a system for tracking progress and making adjustments

        Based on the inputs from all other agents, synthesize a comprehensive personal development plan.
        
        Format your response as a JSON object with the following structure:
        {
            "Executive Summary": "Brief summary of the development plan",
            "Key Insights": ["insight 1", "insight 2", ...],
            "Strategic Recommendations": ["recommendation 1", "recommendation 2", ...],
            "Implementation Steps": [
                {
                    "step": "Step description",
                    "timeline": "Timeline for implementation",
                    "resources_needed": "Resources needed",
                    "success_metrics": "How to measure success"
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
            "Success Metrics": ["metric 1", "metric 2", ...],
            "Progress Tracking System": "System for tracking progress"
        }
        """
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for the Personal Development Council panel."""
        # Define the state schema
        class State(TypedDict):
            query: str
            context: Dict
            growth_gap_analysis: Optional[Dict]
            habit_designs: Optional[Dict]
            learning_plans: Optional[Dict]
            relationship_strategies: Optional[Dict]
            identity_evolution: Optional[Dict]
            inner_critic_management: Optional[Dict]
            development_plan: Optional[Dict]
        
        # Create the graph
        graph = StateGraph(State)
        
        # Define the nodes
        
        # Growth Gap Analyzer node
        def growth_gap_analyzer(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Growth Gap Analyzer", "processing")
                
            query = state["query"]
            context = state["context"]
            
            prompt = self.agent_prompts["growth_gap_analyzer"]
            
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
                
                analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Growth Gap Analyzer", "Complete")
                    
                return {"growth_gap_analysis": analysis}
            except Exception as e:
                logger.error(f"Error parsing Growth Gap Analyzer response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Growth Gap Analyzer", "Error")
                return {"growth_gap_analysis": {"error": str(e), "raw_response": content}}
        
        # Habit Design Engineer node
        def habit_design_engineer(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Habit Design Engineer", "processing")
                
            query = state["query"]
            context = state["context"]
            growth_gap_analysis = state["growth_gap_analysis"]
            
            prompt = self.agent_prompts["habit_design_engineer"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nGrowth Gap Analysis: {json.dumps(growth_gap_analysis)}"}
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
                
                habit_designs = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Habit Design Engineer", "Complete")
                    
                return {"habit_designs": habit_designs}
            except Exception as e:
                logger.error(f"Error parsing Habit Design Engineer response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Habit Design Engineer", "Error")
                return {"habit_designs": {"error": str(e), "raw_response": content}}
        
        # Knowledge Acquisition Strategist node
        def knowledge_acquisition_strategist(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Knowledge Acquisition Strategist", "processing")
                
            query = state["query"]
            context = state["context"]
            growth_gap_analysis = state["growth_gap_analysis"]
            
            prompt = self.agent_prompts["knowledge_acquisition_strategist"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nGrowth Gap Analysis: {json.dumps(growth_gap_analysis)}"}
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
                
                learning_plans = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Knowledge Acquisition Strategist", "Complete")
                    
                return {"learning_plans": learning_plans}
            except Exception as e:
                logger.error(f"Error parsing Knowledge Acquisition Strategist response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Knowledge Acquisition Strategist", "Error")
                return {"learning_plans": {"error": str(e), "raw_response": content}}
        
        # Social Capital Developer node
        def social_capital_developer(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Social Capital Developer", "processing")
                
            query = state["query"]
            context = state["context"]
            growth_gap_analysis = state["growth_gap_analysis"]
            
            prompt = self.agent_prompts["social_capital_developer"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nGrowth Gap Analysis: {json.dumps(growth_gap_analysis)}"}
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
                
                relationship_strategies = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Social Capital Developer", "Complete")
                    
                return {"relationship_strategies": relationship_strategies}
            except Exception as e:
                logger.error(f"Error parsing Social Capital Developer response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Social Capital Developer", "Error")
                return {"relationship_strategies": {"error": str(e), "raw_response": content}}
        
        # Identity Evolution Guide node
        def identity_evolution_guide(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Identity Evolution Guide", "processing")
                
            query = state["query"]
            context = state["context"]
            growth_gap_analysis = state["growth_gap_analysis"]
            
            prompt = self.agent_prompts["identity_evolution_guide"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nGrowth Gap Analysis: {json.dumps(growth_gap_analysis)}"}
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
                
                identity_evolution = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Identity Evolution Guide", "Complete")
                    
                return {"identity_evolution": identity_evolution}
            except Exception as e:
                logger.error(f"Error parsing Identity Evolution Guide response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Identity Evolution Guide", "Error")
                return {"identity_evolution": {"error": str(e), "raw_response": content}}
        
        # Inner Critic Moderator node
        def inner_critic_moderator(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Inner Critic Moderator", "processing")
                
            query = state["query"]
            context = state["context"]
            growth_gap_analysis = state["growth_gap_analysis"]
            
            prompt = self.agent_prompts["inner_critic_moderator"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nGrowth Gap Analysis: {json.dumps(growth_gap_analysis)}"}
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
                
                inner_critic_management = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Inner Critic Moderator", "Complete")
                    
                return {"inner_critic_management": inner_critic_management}
            except Exception as e:
                logger.error(f"Error parsing Inner Critic Moderator response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Inner Critic Moderator", "Error")
                return {"inner_critic_management": {"error": str(e), "raw_response": content}}
        
        # Development Plan Synthesizer node
        def development_plan_synthesizer(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Development Plan Synthesizer", "processing")
                
            query = state["query"]
            context = state["context"]
            growth_gap_analysis = state["growth_gap_analysis"]
            habit_designs = state["habit_designs"]
            learning_plans = state["learning_plans"]
            relationship_strategies = state["relationship_strategies"]
            identity_evolution = state["identity_evolution"]
            inner_critic_management = state["inner_critic_management"]
            
            prompt = self.agent_prompts["development_plan_synthesizer"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"""
                    Query: {query}
                    
                    Context: {json.dumps(context)}
                    
                    Growth Gap Analysis: {json.dumps(growth_gap_analysis)}
                    
                    Habit Designs: {json.dumps(habit_designs)}
                    
                    Learning Plans: {json.dumps(learning_plans)}
                    
                    Relationship Strategies: {json.dumps(relationship_strategies)}
                    
                    Identity Evolution: {json.dumps(identity_evolution)}
                    
                    Inner Critic Management: {json.dumps(inner_critic_management)}
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
                
                development_plan = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Development Plan Synthesizer", "Complete")
                    
                return {"development_plan": development_plan}
            except Exception as e:
                logger.error(f"Error parsing Development Plan Synthesizer response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Development Plan Synthesizer", "Error")
                return {"development_plan": {"error": str(e), "raw_response": content}}
        
        # Add nodes to the graph
        graph.add_node("growth_gap_analyzer", growth_gap_analyzer)
        graph.add_node("habit_design_engineer", habit_design_engineer)
        graph.add_node("knowledge_acquisition_strategist", knowledge_acquisition_strategist)
        graph.add_node("social_capital_developer", social_capital_developer)
        graph.add_node("identity_evolution_guide", identity_evolution_guide)
        graph.add_node("inner_critic_moderator", inner_critic_moderator)
        graph.add_node("development_plan_synthesizer", development_plan_synthesizer)
        
        # Define the edges
        graph.add_edge("growth_gap_analyzer", "habit_design_engineer")
        graph.add_edge("growth_gap_analyzer", "knowledge_acquisition_strategist")
        graph.add_edge("growth_gap_analyzer", "social_capital_developer")
        graph.add_edge("growth_gap_analyzer", "identity_evolution_guide")
        graph.add_edge("growth_gap_analyzer", "inner_critic_moderator")
        
        graph.add_edge("habit_design_engineer", "development_plan_synthesizer")
        graph.add_edge("knowledge_acquisition_strategist", "development_plan_synthesizer")
        graph.add_edge("social_capital_developer", "development_plan_synthesizer")
        graph.add_edge("identity_evolution_guide", "development_plan_synthesizer")
        graph.add_edge("inner_critic_moderator", "development_plan_synthesizer")
        
        graph.add_edge("development_plan_synthesizer", END)
        
        # Set the entry point
        graph.set_entry_point("growth_gap_analyzer")
        
        # Return the compiled graph
        return graph.compile()
        
    def run(self, query: str, context: str = "") -> Dict[str, Any]:
        """Run the Personal Development Council panel on the given query.
        
        Args:
            query: The query to run the panel on
            context: Context information
            
        Returns:
            The panel's output
        """
        if self.visualizer:
            self.visualizer.display_welcome("Personal Development Council")
            self.visualizer.display_query(query)
            self.visualizer.update_status("Running Personal Development Council panel")
        
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
            "growth_gap_analysis": {},
            "habit_designs": {},
            "learning_plans": {},
            "relationship_strategies": {},
            "identity_evolution": {},
            "inner_critic_management": {},
            "development_plan": {}
        }
        
        # Run the graph
        try:
            result = self.graph.invoke(initial_state)
            
            if self.visualizer:
                self.visualizer.display_success("Personal Development Council panel completed successfully")
                self.visualizer.display_plan(result["development_plan"])
            
            return result["development_plan"]
        except Exception as e:
            logger.error(f"Error running Personal Development Council panel: {e}")
            if self.visualizer:
                self.visualizer.display_error(f"Error running Personal Development Council panel: {e}")
            return {
                "error": str(e),
                "Executive Summary": "An error occurred while generating the personal development plan.",
                "Key Insights": ["Error in panel execution"],
                "Strategic Recommendations": ["Please try again or contact support"]
            } 