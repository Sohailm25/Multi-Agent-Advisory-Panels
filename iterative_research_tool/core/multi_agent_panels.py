"""Multi-Agent Advisory Panels implementation using LangGraph."""

import logging
from typing import Dict, Any, List, Optional, Callable, TypedDict, Annotated, Tuple, Union
from pydantic import BaseModel, Field

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

# Anthropic imports
from anthropic import Anthropic

# Local imports
from iterative_research_tool.core.user_memory import UserMemory
from iterative_research_tool.core.visualization import TerminalVisualizer

logger = logging.getLogger(__name__)

# Define the state schema for multi-agent panels
class PanelState(TypedDict):
    """State for the multi-agent panel graph."""
    query: str
    user_context: Optional[str]
    panel_type: str
    agent_outputs: Dict[str, str]
    current_agent: Optional[str]
    next_agent: Optional[str]
    final_output: Optional[str]
    error: Optional[str]

class MultiAgentPanel:
    """Base class for multi-agent advisory panels using LangGraph."""
    
    def __init__(
        self, 
        claude_client: Anthropic,
        claude_model: str = "claude-3-7-sonnet-20250219",
        prompt_dir: Optional[str] = None,
        visualize: bool = True,
        user_memory: Optional[UserMemory] = None
    ):
        """Initialize the multi-agent panel.
        
        Args:
            claude_client: Anthropic client for Claude API
            claude_model: Claude model to use
            prompt_dir: Directory containing prompt templates
            visualize: Whether to visualize the panel execution
            user_memory: User memory instance for context
        """
        self.claude_client = claude_client
        self.claude_model = claude_model
        self.prompt_dir = prompt_dir
        self.visualize = visualize
        self.user_memory = user_memory
        
        if self.visualize:
            self.visualizer = TerminalVisualizer()
        
        # Initialize the graph
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph for the panel.
        
        This method should be implemented by subclasses.
        
        Returns:
            The constructed StateGraph
        """
        raise NotImplementedError("Subclasses must implement _build_graph")
    
    def _call_claude(self, prompt: str, max_tokens: int = 4000) -> str:
        """Call Claude API with the given prompt.
        
        Args:
            prompt: The prompt to send to Claude
            max_tokens: Maximum tokens to generate
            
        Returns:
            Claude's response
        """
        try:
            response = self.claude_client.messages.create(
                model=self.claude_model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            return f"Error: {str(e)}"
    
    def run(self, query: str, user_context: Optional[str] = None) -> str:
        """Run the panel with the given query.
        
        Args:
            query: The user's query
            user_context: Optional user context
            
        Returns:
            The panel's final output
        """
        # Initialize the state
        initial_state = {
            "query": query,
            "user_context": user_context or "",
            "panel_type": self.__class__.__name__,
            "agent_outputs": {},
            "current_agent": None,
            "next_agent": None,
            "final_output": None,
            "error": None
        }
        
        # Run the graph
        for state in self.graph.stream(initial_state):
            if self.visualize and state.get("current_agent"):
                self.visualizer.update_agent_status(state["current_agent"], "processing")
            
            if state.get("error"):
                if self.visualize:
                    self.visualizer.show_error(state["error"])
                logger.error(f"Error in panel execution: {state['error']}")
                
        # Get the final state
        final_state = state
        
        if self.visualize:
            self.visualizer.show_final_output(final_state.get("final_output", "No output generated"))
            
        return final_state.get("final_output", "No output generated")

class CognitiveDiversityPanel(MultiAgentPanel):
    """Cognitive Diversity Panel implementation."""
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph for the Cognitive Diversity Panel.
        
        Returns:
            The constructed StateGraph
        """
        # Create the graph
        graph = StateGraph(PanelState)
        
        # Define nodes
        def cognitive_router(state: PanelState) -> PanelState:
            """Route the query to the appropriate cognitive models."""
            from prompts.multi_agent_panels.cognitive_diversity_panel import COGNITIVE_ROUTER_PROMPT
            
            prompt = COGNITIVE_ROUTER_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"]
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["cognitive_router"] = response
            state["current_agent"] = "cognitive_router"
            state["next_agent"] = "first_principles_agent"
            
            return state
        
        def first_principles_agent(state: PanelState) -> PanelState:
            """Apply first principles thinking to the query."""
            from prompts.multi_agent_panels.cognitive_diversity_panel import FIRST_PRINCIPLES_AGENT_PROMPT
            
            prompt = FIRST_PRINCIPLES_AGENT_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"]
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["first_principles_agent"] = response
            state["current_agent"] = "first_principles_agent"
            state["next_agent"] = "inversion_thinker_agent"
            
            return state
        
        def inversion_thinker_agent(state: PanelState) -> PanelState:
            """Apply inversion thinking to the query."""
            from prompts.multi_agent_panels.cognitive_diversity_panel import INVERSION_THINKER_AGENT_PROMPT
            
            prompt = INVERSION_THINKER_AGENT_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"]
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["inversion_thinker_agent"] = response
            state["current_agent"] = "inversion_thinker_agent"
            state["next_agent"] = "systems_dynamics_agent"
            
            return state
        
        def systems_dynamics_agent(state: PanelState) -> PanelState:
            """Apply systems thinking to the query."""
            from prompts.multi_agent_panels.cognitive_diversity_panel import SYSTEMS_DYNAMICS_AGENT_PROMPT
            
            prompt = SYSTEMS_DYNAMICS_AGENT_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"]
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["systems_dynamics_agent"] = response
            state["current_agent"] = "systems_dynamics_agent"
            state["next_agent"] = "opportunity_cost_agent"
            
            return state
        
        def opportunity_cost_agent(state: PanelState) -> PanelState:
            """Apply opportunity cost thinking to the query."""
            from prompts.multi_agent_panels.cognitive_diversity_panel import OPPORTUNITY_COST_AGENT_PROMPT
            
            prompt = OPPORTUNITY_COST_AGENT_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"]
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["opportunity_cost_agent"] = response
            state["current_agent"] = "opportunity_cost_agent"
            state["next_agent"] = "decision_journal_agent"
            
            return state
        
        def decision_journal_agent(state: PanelState) -> PanelState:
            """Apply decision journal thinking to the query."""
            from prompts.multi_agent_panels.cognitive_diversity_panel import DECISION_JOURNAL_AGENT_PROMPT
            
            prompt = DECISION_JOURNAL_AGENT_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"]
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["decision_journal_agent"] = response
            state["current_agent"] = "decision_journal_agent"
            state["next_agent"] = "synthesis_node"
            
            return state
        
        def synthesis_node(state: PanelState) -> PanelState:
            """Synthesize the outputs of all cognitive models."""
            from prompts.multi_agent_panels.cognitive_diversity_panel import SYNTHESIS_NODE_PROMPT
            
            prompt = SYNTHESIS_NODE_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"],
                first_principles_output=state["agent_outputs"].get("first_principles_agent", ""),
                inversion_output=state["agent_outputs"].get("inversion_thinker_agent", ""),
                systems_dynamics_output=state["agent_outputs"].get("systems_dynamics_agent", ""),
                opportunity_cost_output=state["agent_outputs"].get("opportunity_cost_agent", ""),
                decision_journal_output=state["agent_outputs"].get("decision_journal_agent", "")
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["synthesis_node"] = response
            state["current_agent"] = "synthesis_node"
            state["final_output"] = response
            
            return state
        
        # Add nodes to the graph
        graph.add_node("cognitive_router", cognitive_router)
        graph.add_node("first_principles_agent", first_principles_agent)
        graph.add_node("inversion_thinker_agent", inversion_thinker_agent)
        graph.add_node("systems_dynamics_agent", systems_dynamics_agent)
        graph.add_node("opportunity_cost_agent", opportunity_cost_agent)
        graph.add_node("decision_journal_agent", decision_journal_agent)
        graph.add_node("synthesis_node", synthesis_node)
        
        # Define edges
        graph.add_edge("cognitive_router", "first_principles_agent")
        graph.add_edge("first_principles_agent", "inversion_thinker_agent")
        graph.add_edge("inversion_thinker_agent", "systems_dynamics_agent")
        graph.add_edge("systems_dynamics_agent", "opportunity_cost_agent")
        graph.add_edge("opportunity_cost_agent", "decision_journal_agent")
        graph.add_edge("decision_journal_agent", "synthesis_node")
        graph.add_edge("synthesis_node", END)
        
        # Set the entry point
        graph.set_entry_point("cognitive_router")
        
        return graph

class DecisionIntelligencePanel(MultiAgentPanel):
    """Decision Intelligence Panel implementation."""
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph for the Decision Intelligence Panel.
        
        Returns:
            The constructed StateGraph
        """
        # Create the graph
        graph = StateGraph(PanelState)
        
        # Define nodes
        def decision_classifier(state: PanelState) -> PanelState:
            """Classify the decision type and complexity."""
            from prompts.multi_agent_panels.decision_intelligence_panel import DECISION_CLASSIFIER_PROMPT
            
            prompt = DECISION_CLASSIFIER_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"]
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["decision_classifier"] = response
            state["current_agent"] = "decision_classifier"
            state["next_agent"] = "options_generator"
            
            return state
        
        def options_generator(state: PanelState) -> PanelState:
            """Generate options for the decision."""
            from prompts.multi_agent_panels.decision_intelligence_panel import OPTIONS_GENERATOR_PROMPT
            
            prompt = OPTIONS_GENERATOR_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"],
                decision_classification=state["agent_outputs"].get("decision_classifier", "")
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["options_generator"] = response
            state["current_agent"] = "options_generator"
            state["next_agent"] = "criteria_definer"
            
            return state
        
        def criteria_definer(state: PanelState) -> PanelState:
            """Define criteria for evaluating options."""
            from prompts.multi_agent_panels.decision_intelligence_panel import CRITERIA_DEFINER_PROMPT
            
            prompt = CRITERIA_DEFINER_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"],
                decision_classification=state["agent_outputs"].get("decision_classifier", ""),
                options=state["agent_outputs"].get("options_generator", "")
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["criteria_definer"] = response
            state["current_agent"] = "criteria_definer"
            state["next_agent"] = "probability_assessor"
            
            return state
        
        def probability_assessor(state: PanelState) -> PanelState:
            """Assess probabilities for different outcomes."""
            from prompts.multi_agent_panels.decision_intelligence_panel import PROBABILITY_ASSESSOR_PROMPT
            
            prompt = PROBABILITY_ASSESSOR_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"],
                decision_classification=state["agent_outputs"].get("decision_classifier", ""),
                options=state["agent_outputs"].get("options_generator", ""),
                criteria=state["agent_outputs"].get("criteria_definer", "")
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["probability_assessor"] = response
            state["current_agent"] = "probability_assessor"
            state["next_agent"] = "consequence_mapper"
            
            return state
        
        def consequence_mapper(state: PanelState) -> PanelState:
            """Map consequences of different options."""
            from prompts.multi_agent_panels.decision_intelligence_panel import CONSEQUENCE_MAPPER_PROMPT
            
            prompt = CONSEQUENCE_MAPPER_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"],
                decision_classification=state["agent_outputs"].get("decision_classifier", ""),
                options=state["agent_outputs"].get("options_generator", ""),
                criteria=state["agent_outputs"].get("criteria_definer", ""),
                probability_assessment=state["agent_outputs"].get("probability_assessor", "")
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["consequence_mapper"] = response
            state["current_agent"] = "consequence_mapper"
            state["next_agent"] = "decision_evaluation"
            
            return state
        
        def decision_evaluation(state: PanelState) -> PanelState:
            """Evaluate options based on criteria, probabilities, and consequences."""
            from prompts.multi_agent_panels.decision_intelligence_panel import DECISION_EVALUATION_PROMPT
            
            prompt = DECISION_EVALUATION_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"],
                decision_classification=state["agent_outputs"].get("decision_classifier", ""),
                options=state["agent_outputs"].get("options_generator", ""),
                criteria=state["agent_outputs"].get("criteria_definer", ""),
                probability_assessment=state["agent_outputs"].get("probability_assessor", ""),
                consequence_mapping=state["agent_outputs"].get("consequence_mapper", "")
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["decision_evaluation"] = response
            state["current_agent"] = "decision_evaluation"
            state["next_agent"] = "final_recommendation"
            
            return state
        
        def final_recommendation(state: PanelState) -> PanelState:
            """Provide final recommendation based on all analyses."""
            from prompts.multi_agent_panels.decision_intelligence_panel import FINAL_RECOMMENDATION_PROMPT
            
            prompt = FINAL_RECOMMENDATION_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"],
                decision_classification=state["agent_outputs"].get("decision_classifier", ""),
                options=state["agent_outputs"].get("options_generator", ""),
                criteria=state["agent_outputs"].get("criteria_definer", ""),
                probability_assessment=state["agent_outputs"].get("probability_assessor", ""),
                consequence_mapping=state["agent_outputs"].get("consequence_mapper", ""),
                decision_evaluation=state["agent_outputs"].get("decision_evaluation", "")
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["final_recommendation"] = response
            state["current_agent"] = "final_recommendation"
            state["final_output"] = response
            
            return state
        
        # Add nodes to the graph
        graph.add_node("decision_classifier", decision_classifier)
        graph.add_node("options_generator", options_generator)
        graph.add_node("criteria_definer", criteria_definer)
        graph.add_node("probability_assessor", probability_assessor)
        graph.add_node("consequence_mapper", consequence_mapper)
        graph.add_node("decision_evaluation", decision_evaluation)
        graph.add_node("final_recommendation", final_recommendation)
        
        # Define edges
        graph.add_edge("decision_classifier", "options_generator")
        graph.add_edge("options_generator", "criteria_definer")
        graph.add_edge("criteria_definer", "probability_assessor")
        graph.add_edge("probability_assessor", "consequence_mapper")
        graph.add_edge("consequence_mapper", "decision_evaluation")
        graph.add_edge("decision_evaluation", "final_recommendation")
        graph.add_edge("final_recommendation", END)
        
        # Set the entry point
        graph.set_entry_point("decision_classifier")
        
        return graph

class FutureScenarioPanel(MultiAgentPanel):
    """Future Scenario Planning Panel implementation."""
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph for the Future Scenario Planning Panel.
        
        Returns:
            The constructed StateGraph
        """
        # Create the graph
        graph = StateGraph(PanelState)
        
        # Define nodes
        def trend_analyzer(state: PanelState) -> PanelState:
            """Analyze relevant trends."""
            from prompts.multi_agent_panels.future_scenario_panel import TREND_ANALYZER_PROMPT
            
            prompt = TREND_ANALYZER_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"]
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["trend_analyzer"] = response
            state["current_agent"] = "trend_analyzer"
            state["next_agent"] = "scenario_generator"
            
            return state
        
        def scenario_generator(state: PanelState) -> PanelState:
            """Generate future scenarios based on trends."""
            from prompts.multi_agent_panels.future_scenario_panel import SCENARIO_GENERATOR_PROMPT
            
            prompt = SCENARIO_GENERATOR_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"],
                trend_analysis=state["agent_outputs"].get("trend_analyzer", "")
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["scenario_generator"] = response
            state["current_agent"] = "scenario_generator"
            state["next_agent"] = "opportunity_explorer"
            
            return state
        
        def opportunity_explorer(state: PanelState) -> PanelState:
            """Explore opportunities in each scenario."""
            from prompts.multi_agent_panels.future_scenario_panel import OPPORTUNITY_EXPLORER_PROMPT
            
            prompt = OPPORTUNITY_EXPLORER_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"],
                trend_analysis=state["agent_outputs"].get("trend_analyzer", ""),
                scenarios=state["agent_outputs"].get("scenario_generator", "")
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["opportunity_explorer"] = response
            state["current_agent"] = "opportunity_explorer"
            state["next_agent"] = "threat_analyzer"
            
            return state
        
        def threat_analyzer(state: PanelState) -> PanelState:
            """Analyze threats in each scenario."""
            from prompts.multi_agent_panels.future_scenario_panel import THREAT_ANALYZER_PROMPT
            
            prompt = THREAT_ANALYZER_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"],
                trend_analysis=state["agent_outputs"].get("trend_analyzer", ""),
                scenarios=state["agent_outputs"].get("scenario_generator", ""),
                opportunities=state["agent_outputs"].get("opportunity_explorer", "")
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["threat_analyzer"] = response
            state["current_agent"] = "threat_analyzer"
            state["next_agent"] = "robust_strategy_developer"
            
            return state
        
        def robust_strategy_developer(state: PanelState) -> PanelState:
            """Develop robust strategies across scenarios."""
            from prompts.multi_agent_panels.future_scenario_panel import ROBUST_STRATEGY_DEVELOPER_PROMPT
            
            prompt = ROBUST_STRATEGY_DEVELOPER_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"],
                trend_analysis=state["agent_outputs"].get("trend_analyzer", ""),
                scenarios=state["agent_outputs"].get("scenario_generator", ""),
                opportunities=state["agent_outputs"].get("opportunity_explorer", ""),
                threats=state["agent_outputs"].get("threat_analyzer", "")
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["robust_strategy_developer"] = response
            state["current_agent"] = "robust_strategy_developer"
            state["next_agent"] = "scenario_synthesis"
            
            return state
        
        def scenario_synthesis(state: PanelState) -> PanelState:
            """Synthesize insights from all scenarios."""
            from prompts.multi_agent_panels.future_scenario_panel import SCENARIO_SYNTHESIS_PROMPT
            
            prompt = SCENARIO_SYNTHESIS_PROMPT.format(
                query=state["query"],
                user_context=state["user_context"],
                trend_analysis=state["agent_outputs"].get("trend_analyzer", ""),
                scenarios=state["agent_outputs"].get("scenario_generator", ""),
                opportunities=state["agent_outputs"].get("opportunity_explorer", ""),
                threats=state["agent_outputs"].get("threat_analyzer", ""),
                robust_strategies=state["agent_outputs"].get("robust_strategy_developer", "")
            )
            
            response = self._call_claude(prompt)
            
            # Update state
            state["agent_outputs"]["scenario_synthesis"] = response
            state["current_agent"] = "scenario_synthesis"
            state["final_output"] = response
            
            return state
        
        # Add nodes to the graph
        graph.add_node("trend_analyzer", trend_analyzer)
        graph.add_node("scenario_generator", scenario_generator)
        graph.add_node("opportunity_explorer", opportunity_explorer)
        graph.add_node("threat_analyzer", threat_analyzer)
        graph.add_node("robust_strategy_developer", robust_strategy_developer)
        graph.add_node("scenario_synthesis", scenario_synthesis)
        
        # Define edges
        graph.add_edge("trend_analyzer", "scenario_generator")
        graph.add_edge("scenario_generator", "opportunity_explorer")
        graph.add_edge("opportunity_explorer", "threat_analyzer")
        graph.add_edge("threat_analyzer", "robust_strategy_developer")
        graph.add_edge("robust_strategy_developer", "scenario_synthesis")
        graph.add_edge("scenario_synthesis", END)
        
        # Set the entry point
        graph.set_entry_point("trend_analyzer")
        
        return graph

# Factory function to create the appropriate panel
def create_panel(
    panel_type: str,
    claude_client: Anthropic,
    claude_model: str = "claude-3-7-sonnet-20250219",
    prompt_dir: Optional[str] = None,
    visualize: bool = True,
    user_memory: Optional[UserMemory] = None
) -> MultiAgentPanel:
    """Create a multi-agent panel of the specified type.
    
    Args:
        panel_type: Type of panel to create
        claude_client: Anthropic client for Claude API
        claude_model: Claude model to use
        prompt_dir: Directory containing prompt templates
        visualize: Whether to visualize the panel execution
        user_memory: User memory instance for context
        
    Returns:
        The created panel
        
    Raises:
        ValueError: If the panel type is not supported
    """
    panel_map = {
        "cognitive-diversity": CognitiveDiversityPanel,
        "decision-intelligence": DecisionIntelligencePanel,
        "future-scenarios": FutureScenarioPanel,
    }
    
    if panel_type not in panel_map:
        raise ValueError(f"Unsupported panel type: {panel_type}. Supported types: {list(panel_map.keys())}")
    
    panel_class = panel_map[panel_type]
    return panel_class(
        claude_client=claude_client,
        claude_model=claude_model,
        prompt_dir=prompt_dir,
        visualize=visualize,
        user_memory=user_memory
    ) 