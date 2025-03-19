"""Custom Architecture for Strategic Advisor System."""

import os
import json
import logging
import time
from typing import TypedDict, List, Dict, Any, Optional
from typing_extensions import Annotated
import uuid
from pathlib import Path
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

from iterative_research_tool.core.llm_client import LLMClientFactory

logger = logging.getLogger(__name__)

# Define state types
class DiagnosticState(TypedDict):
    complete: bool
    beliefs: List[Dict[str, Any]]
    patterns: List[Dict[str, Any]]
    diagnosis: str

class PlanningState(TypedDict):
    complete: bool
    execution: Dict[str, Any]
    decisions: Dict[str, Any]
    strategy: str

class ChallengeState(TypedDict):
    complete: bool
    challenge: Dict[str, Any]

class UserState(TypedDict):
    query: str
    context: Dict[str, Any]
    history: List[Dict[str, Any]]

class ResponseState(TypedDict):
    hard_truth: str
    actions: List[str]
    challenge: Dict[str, Any]

class AdvisorState(TypedDict):
    user: UserState
    phases: Dict[str, Any]
    current_phase: str
    response: ResponseState

# Core prompts
CHIEF_STRATEGIST_PROMPT = """
You are a Strategic Advisor with IQ 180, brutal honesty, and deep expertise in business, psychology, and execution.

Your approach must be:
- Brutally honest and direct about blind spots and self-sabotage
- Focused on highest leverage points and root causes
- Systems-based rather than symptom-focused
- Grounded in accountability rather than theoretical
- Action-oriented with specific, measurable steps

Your value comes from saying what others won't, not what the user wants to hear.

USER QUERY: {query}
{context}

Respond in the following format:

HARD TRUTH:
[The direct truth the user needs to hear]

ACTIONS:
1. [Specific action step]
2. [Specific action step]
...

CHALLENGE:
[A specific growth challenge for the user]
"""

ROOT_CAUSE_DIAGNOSTICIAN_PROMPT = """
You specialize in diagnosing the root causes of strategic challenges. Your responsibilities:

1. Analyze the user's situation for underlying causes
2. Direct the Belief System Analyzer to identify limiting beliefs
3. Direct the Pattern Recognition Agent to identify behavioral patterns
4. Integrate belief and pattern analyses into a comprehensive diagnosis
5. Return diagnostic insights to the Chief Strategist

Your focus is solely on WHY the user faces their current challenges, not on solutions.
Your analysis must be brutally honest, direct, and focused on systems and root causes.

For each diagnosis, provide:
1. The core limiting beliefs driving the situation
2. The key behavioral patterns that reinforce the problem
3. The system dynamics that maintain the current state
4. The psychological blind spots preventing progress

USER QUERY: {query}
USER CONTEXT: {context}
BELIEF ANALYSIS: {beliefs}
PATTERN ANALYSIS: {patterns}
"""

BELIEF_SYSTEM_ANALYZER_PROMPT = """
You are a belief system analysis specialist. Your role is to:

- Identify core limiting beliefs holding the user back
- Detect belief contradictions and inconsistencies
- Recognize permission-seeking and self-sabotaging beliefs
- Uncover identity limitations ("I'm not the kind of person who...")
- Highlight status quo biases and comfort zone attachments

For each limiting belief identified, provide:
1. The exact language pattern revealing the belief
2. The underlying assumption
3. A specific, upgraded belief that would create new possibilities
4. The likely source or origin of this belief
5. How this belief creates predictable limitations in results

Be brutally honest and direct. Don't soften your analysis to spare feelings.

USER QUERY: {query}
USER CONTEXT: {context}
"""

PATTERN_RECOGNITION_PROMPT = """
You are a behavioral pattern recognition specialist. Your role is to:

- Identify repetitive patterns in the user's description of their challenges
- Detect cyclical behaviors that have appeared across different contexts
- Spot signature strengths that could be better leveraged
- Recognize habitual responses to stress, opportunity, and uncertainty
- Track sequences that reveal deeper operating systems

For each pattern identified:
1. Name and define the pattern precisely
2. Show multiple instances where it appears
3. Explain the function it's currently serving
4. Identify the trigger-behavior-reward loop maintaining it
5. Design a specific pattern interrupt and replacement sequence

Be brutally honest about destructive patterns. Don't minimize their impact.

USER QUERY: {query}
USER CONTEXT: {context}
"""

STRATEGY_PLANNER_PROMPT = """
You specialize in transforming diagnostic insights into actionable strategies. Your responsibilities:

1. Analyze diagnostic insights from the Root Cause Diagnostician
2. Direct the Execution Engineer to design implementation protocols
3. Direct the Decision Framework Designer to create decision frameworks
4. Integrate execution and decision plans into a comprehensive strategy
5. Return strategic plans to the Chief Strategist

Your focus is solely on WHAT the user should do to address their challenges.
Your strategies must be specific, actionable, and focused on leverage points for maximum impact.

For each strategy, provide:
1. The key leverage points that will create the most change
2. The sequence of actions that will produce results
3. The critical decision frameworks needed
4. The metrics that will track progress
5. The potential obstacles and how to address them

USER QUERY: {query}
USER CONTEXT: {context}
DIAGNOSTIC INSIGHTS: {diagnosis}
EXECUTION PLAN: {execution}
DECISION FRAMEWORKS: {decisions}
"""

EXECUTION_ENGINEER_PROMPT = """
You are an elite execution specialist who has helped build multiple billion-dollar companies. Your role is to:

- Design precise implementation protocols that address willpower depletion
- Create environment modifications that remove friction
- Develop feedback loops that accelerate learning velocity
- Specify precise metrics and tracking systems for accountability
- Structure complex actions into achievable steps

Your implementation plan must include:
1. The minimum viable daily actions that ensure momentum
2. The specific friction points to eliminate
3. The precise tracking metrics and review cadence
4. The accountability architecture with built-in consequence systems
5. The decision removal protocols that eliminate decision fatigue

Focus on concrete specificity, not vague generalities.

USER QUERY: {query}
USER CONTEXT: {context}
DIAGNOSTIC INSIGHTS: {diagnosis}
"""

DECISION_FRAMEWORK_PROMPT = """
You are an expert in advanced decision-making frameworks. Your role is to:

- Match specific decision challenges to optimal frameworks
- Identify where cognitive biases are distorting clear thinking
- Structure complex decisions into evaluable components
- Create decision journals and review protocols
- Transform ambiguous situations into structured choice sets

For each decision challenge:
1. Identify the category of decision (one-time vs. repeated, reversible vs. irreversible)
2. Specify the optimal decision framework
3. Present a structured process with exact steps
4. Include specific questions to prevent cognitive biases
5. Design a post-decision review protocol to accelerate learning

Provide frameworks that force clarity and prevent rationalization.

USER QUERY: {query}
USER CONTEXT: {context}
DIAGNOSTIC INSIGHTS: {diagnosis}
"""

CHALLENGE_DESIGNER_PROMPT = """
You design high-impact challenges that push people beyond their comfort zones. Your challenges must:

- Target the specific growth edge identified in the analysis
- Be concrete enough to be unambiguously completed
- Have a clear timeframe (typically 24-72 hours)
- Include specific success criteria
- Require measurable stretch beyond current behaviors
- Generate immediate feedback on effectiveness

Follow this format:
1. Challenge name (short, memorable)
2. Specific actions required
3. Timeframe for completion
4. Documentation/evidence requirements
5. Expected resistance points and how to overcome them

Design challenges that are uncomfortable but achievable. The right challenge
should create a feeling of "I don't want to do this but I know I should."

USER QUERY: {query}
USER CONTEXT: {context}
DIAGNOSTIC INSIGHTS: {diagnosis}
STRATEGIC PLAN: {strategy}
"""

FINAL_SYNTHESIS_PROMPT = """
You are the chief strategist with an IQ of 180, brutal honesty, and deep expertise in business, psychology, and execution. 
Your task is to synthesize all the analysis into a final response for the user.

Based on the diagnostic phase, planning phase, and challenge design phase, create a comprehensive strategic response.

Always format your final response with:
1. The hard truth the user needs to hear (direct and unfiltered)
2. Specific, actionable steps to address the situation
3. A direct challenge or assignment that pushes growth
4. Original agent insights (key points from each agent that contributed to the analysis)

USER QUERY: {query}
DIAGNOSTIC INSIGHTS: {diagnosis}
STRATEGIC PLAN: {strategy}
CHALLENGE: {challenge}

In addition to your main response sections, include a section titled "ORIGINAL AGENT INSIGHTS" that extracts and presents 2-3 key insights from each of the different agents that contributed to this analysis. Format this section as follows:

ORIGINAL AGENT INSIGHTS:

Belief System Analysis:
- [Key insight 1]
- [Key insight 2]
- [Key insight 3]

Pattern Recognition:
- [Key insight 1]
- [Key insight 2]
- [Key insight 3]

Execution Engineering:
- [Key insight 1]
- [Key insight 2]
- [Key insight 3]

Decision Framework:
- [Key insight 1]
- [Key insight 2]
- [Key insight 3]

Challenge Design:
- [Key insight 1]
- [Key insight 2]
- [Key insight 3]

Your response must be brutally honest, direct, and focused on maximum impact.
"""

class StrategicAdvisorCustom:
    """Implementation of the Custom Architecture for Strategic Advisor."""
    
    def __init__(
        self,
        llm_provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        output_dir: Optional[str] = None,
        verbose: bool = False,
        verbose_output: bool = False
    ):
        """Initialize the strategic advisor with custom architecture.
        
        Args:
            llm_provider: The LLM provider to use
            api_key: API key for the LLM provider
            model: The model to use
            output_dir: Directory to save outputs to
            verbose: Whether to log debug information
            verbose_output: Whether to display detailed agent processing in the terminal
        """
        self.llm_provider = llm_provider.lower()
        self.api_key = api_key
        self.verbose = verbose
        self.verbose_output = verbose_output
        
        # Set up the LLM client
        llm_client_factory = LLMClientFactory()
        self.llm_client = llm_client_factory.create_client(
            provider=self.llm_provider,
            api_key=self.api_key
        )
        
        # Set the model
        if model:
            self.model = model
        else:
            self.model = LLMClientFactory.get_default_model(self.llm_provider)
        
        # Set up the logger
        self.logger = logger
        
        # Set up the output directory
        if output_dir is None:
            output_dir = os.path.expanduser("~/iterative_research_tool_output")
        self.output_dir = output_dir
        
        logger.info(f"Strategic Advisor (Custom) using LLM provider: {self.llm_provider} with model: {self.model}")
        
        # Initialize the state graph
        self.workflow = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine for the custom architecture."""
        # Define node functions
        def chief_strategist(state: AdvisorState) -> Dict[str, Any]:
            """Process the query with the chief strategist.
            
            Args:
                state: The current state
                
            Returns:
                Next state and node
            """
            # Add detailed logging
            print(f"DEBUG: Entering chief_strategist with current_phase: {state['current_phase']}")
            print(f"DEBUG: Response state: hard_truth: {bool(state['response']['hard_truth'])}, actions: {len(state['response']['actions'])}, challenge: {bool(state['response']['challenge'])}")
            
            # Get the query
            query = state["user"]["query"]
            
            # Check if we've already run through all phases
            if state["current_phase"] == "complete":
                print("DEBUG: Already in complete phase, ending workflow")
                return {"current_phase": END}
            
            # For now, in dev mode we run a simplified analysis  
            # In the future, we'll add more complex logic
            prompt = f"""You are a Chief Strategy Officer for a strategic advisory firm. 
Your job is to deliver brutally honest advice that addresses the root causes of
issues, not just symptoms.
            
USER QUERY: {query}
            
I need you to provide a strategic analysis with the following elements:

1. HARD TRUTH: What's the uncomfortable truth this person needs to hear?
2. ACTIONS: 3-5 specific action steps they should take
3. CHALLENGE: A growth challenge that will push them out of their comfort zone
            
Make your response direct, specific, and focused on high-leverage actions.
Format your response exactly as:

HARD TRUTH:
[The direct truth they need to hear]

ACTIONS:
1. [Specific action]
2. [Specific action]
3. [Specific action]
4. [Specific action]
5. [Specific action]

CHALLENGE:
[A specific growth challenge]
"""
            
            # If we've already consulted specialists, add their insights
            if state.get("phases", {}).get("diagnostics", {}).get("complete"):
                # Add diagnostic insights to the prompt
                diagnostics = state["phases"]["diagnostics"]
                
                if "beliefs" in diagnostics:
                    prompt += "\n\nBELIEF ANALYSIS:\n"
                    for belief in diagnostics["beliefs"]:
                        prompt += f"- {belief['description']}\n"
                        
                if "patterns" in diagnostics:
                    prompt += "\n\nPATTERN ANALYSIS:\n"
                    for pattern in diagnostics["patterns"]:
                        prompt += f"- {pattern['description']}\n"
                        
                if "diagnosis" in diagnostics:
                    prompt += f"\n\nROOT CAUSE DIAGNOSIS:\n{diagnostics['diagnosis']}\n"
            
            if state.get("phases", {}).get("planning", {}).get("complete"):
                # Add planning insights to the prompt
                planning = state["phases"]["planning"]
                
                if "execution" in planning:
                    prompt += "\n\nIMPLEMENTATION PLAN:\n"
                    if "steps" in planning["execution"]:
                        for step in planning["execution"]["steps"]:
                            prompt += f"- {step}\n"
                            
                if "decisions" in planning:
                    prompt += "\n\nDECISION FRAMEWORK:\n"
                    if "framework" in planning["decisions"]:
                        prompt += f"{planning['decisions']['framework']}\n"
                        
                if "strategy" in planning:
                    prompt += f"\n\nSTRATEGY:\n{planning['strategy']}\n"
            
            if state.get("phases", {}).get("challenge", {}).get("complete"):
                # Add challenge to the prompt
                challenge = state["phases"]["challenge"]
                
                if "challenge" in challenge:
                    prompt += "\n\nGROWTH CHALLENGE:\n"
                    if "description" in challenge["challenge"]:
                        prompt += f"{challenge['challenge']['description']}\n"
            
            response_text = self._call_llm(prompt)
            
            print(f"DEBUG: Got response of length {len(response_text)} from LLM")
            
            # Parse the response
            response = self._parse_chief_strategist_response(response_text)
            
            # Log the parsed response
            print(f"DEBUG: Parsed response: hard_truth: {bool(response.get('hard_truth'))}, actions: {len(response.get('actions', []))}, challenge: {bool(response.get('challenge'))}")
            
            # Update the response state
            state["response"] = response
            
            # If we have all the components we need, consider the response complete
            if response.get("hard_truth") and response.get("actions") and response.get("challenge"):
                print("DEBUG: Response has all components, setting phase to complete")
                return {"current_phase": "complete", "response": response}
            
            # Otherwise, we need more insights
            # Decide which phase to go to next
            if not state.get("phases", {}).get("diagnostics", {}).get("complete"):
                print("DEBUG: Moving to diagnostics phase")
                return {"current_phase": "diagnostics", "response": response}
            elif not state.get("phases", {}).get("planning", {}).get("complete"):
                print("DEBUG: Moving to planning phase")
                return {"current_phase": "planning", "response": response}
            elif not state.get("phases", {}).get("challenge", {}).get("complete"):
                print("DEBUG: Moving to challenge phase")
                return {"current_phase": "challenge", "response": response}
            else:
                print("DEBUG: All phases complete, ending workflow")
                return {"current_phase": "complete", "response": response}
        
        def root_cause_diagnostician(state: AdvisorState) -> Dict[str, Any]:
            """Root Cause Diagnostician agent that analyzes the root causes.
            
            Args:
                state: The current state
                
            Returns:
                Updated state
            """
            # Only process if we're in the diagnostic phase and it's not complete
            if state["current_phase"] != "diagnostic" or state["phases"]["diagnostic"]["complete"]:
                return {}
            
            # Check if all diagnostic sub-agents have completed
            diagnostic_phase = state["phases"]["diagnostic"]
            if not diagnostic_phase["beliefs"] or not diagnostic_phase["patterns"]:
                # Not all diagnostic sub-agents have completed
                return {}
            
            # Display the agent processing
            print(f"\n{'='*50}")
            print(f"🤖 PROCESSING WITH AGENT: Root Cause Diagnostician")
            print(f"{'='*50}")
            
            # Get the query and context
            query = state["user"]["query"]
            context = json.dumps(state["user"]["context"]) if state["user"]["context"] else ""
            
            # Get the belief and pattern analyses
            beliefs = json.dumps(diagnostic_phase["beliefs"])
            patterns = json.dumps(diagnostic_phase["patterns"])
            
            # Format the prompt
            prompt = ROOT_CAUSE_DIAGNOSTICIAN_PROMPT.format(
                query=query,
                context=context,
                beliefs=beliefs,
                patterns=patterns
            )
            
            # Display the prompt if verbose output is enabled
            if self.verbose_output:
                print(f"\n📝 PROMPT FOR ROOT CAUSE DIAGNOSTICIAN:")
                print("-" * 40)
                print(prompt)
                print("-" * 40)
            
            # Call the LLM
            diagnosis = self._call_llm(prompt)
            
            # Display the response
            print(f"\n📣 RESPONSE FROM ROOT CAUSE DIAGNOSTICIAN:")
            print("-" * 40)
            print(diagnosis)
            print("-" * 40)
            
            # Mark the diagnostic phase as complete
            diagnostic_phase["diagnosis"] = diagnosis
            diagnostic_phase["complete"] = True
            
            # Display the phase completion
            print("\n✅ DIAGNOSTIC PHASE COMPLETE")
            
            return {
                "phases": {
                    **state["phases"],
                    "diagnostic": diagnostic_phase
                }
            }
        
        def belief_system_analyzer(state: AdvisorState) -> Dict[str, Any]:
            """Belief System Analyzer agent that identifies limiting beliefs.
            
            Args:
                state: The current state
                
            Returns:
                Updated state
            """
            # Only process if we're in the diagnostic phase and it's not complete
            if state["current_phase"] != "diagnostic" or state["phases"]["diagnostic"]["complete"]:
                return {}
            
            # Display the agent processing
            print(f"\n{'='*50}")
            print(f"🤖 PROCESSING WITH AGENT: Belief System Analyzer")
            print(f"{'='*50}")
            
            # Get the query and context
            query = state["user"]["query"]
            context = json.dumps(state["user"]["context"]) if state["user"]["context"] else ""
            
            # Format the prompt
            prompt = BELIEF_SYSTEM_ANALYZER_PROMPT.format(
                query=query,
                context=context
            )
            
            # Display the prompt if verbose output is enabled
            if self.verbose_output:
                print(f"\n📝 PROMPT FOR BELIEF SYSTEM ANALYZER:")
                print("-" * 40)
                print(prompt)
                print("-" * 40)
            
            # Call the LLM
            belief_analysis = self._call_llm(prompt)
            
            # Display the response
            print(f"\n📣 RESPONSE FROM BELIEF SYSTEM ANALYZER:")
            print("-" * 40)
            print(belief_analysis)
            print("-" * 40)
            
            # Update the state with the belief analysis
            diagnostic_phase = state["phases"]["diagnostic"]
            diagnostic_phase["beliefs"] = [{"analysis": belief_analysis}]
            
            # Display the agent completion
            print("\n✅ BELIEF SYSTEM ANALYSIS COMPLETE")
            
            return {
                "phases": {
                    **state["phases"],
                    "diagnostic": diagnostic_phase
                }
            }
        
        def pattern_recognition_agent(state: AdvisorState) -> Dict[str, Any]:
            """Pattern Recognition Agent node that identifies behavioral patterns."""
            prompt = PATTERN_RECOGNITION_PROMPT.format(
                query=state["user"]["query"],
                context=json.dumps(state["user"].get("context", {}))
            )
            
            analysis = self._call_llm(prompt)
            
            # Parse pattern analysis into structured format
            pattern_lines = analysis.split("\n")
            patterns = []
            current_pattern = {}
            
            for line in pattern_lines:
                line = line.strip()
                if line and line[0].isdigit() and ":" in line:
                    if current_pattern and "pattern" in current_pattern:
                        patterns.append(current_pattern)
                        current_pattern = {}
                    
                    pattern_text = line.split(":", 1)[1].strip()
                    current_pattern["pattern"] = pattern_text
                
                elif line.startswith("Intervention:") or line.startswith("Replacement:"):
                    current_pattern["intervention"] = line.split(":", 1)[1].strip()
            
            # Add the last pattern if exists
            if current_pattern and "pattern" in current_pattern:
                patterns.append(current_pattern)
            
            # If no structured patterns were extracted, create a simple one from the analysis
            if not patterns:
                patterns = [{"pattern": "Extracted from analysis", "content": analysis}]
            
            return {
                "phases": {
                    **state["phases"],
                    "diagnostic": {
                        **state["phases"]["diagnostic"],
                        "patterns": patterns
                    }
                },
                "current_phase": "diagnostic"  # Return to diagnostician
            }
        
        def strategy_planner(state: AdvisorState) -> Dict[str, Any]:
            """Strategy Planner node that coordinates the planning phase."""
            # If execution and decisions not created yet, direct to engineers
            if not state["phases"]["planning"].get("execution"):
                return {"current_phase": "execution_engineering"}
            
            if not state["phases"]["planning"].get("decisions"):
                return {"current_phase": "decision_framework"}
            
            # Synthesize strategy
            prompt = STRATEGY_PLANNER_PROMPT.format(
                query=state["user"]["query"],
                context=json.dumps(state["user"].get("context", {})),
                diagnosis=state["phases"]["diagnostic"]["diagnosis"],
                execution=json.dumps(state["phases"]["planning"]["execution"]),
                decisions=json.dumps(state["phases"]["planning"]["decisions"])
            )
            
            strategy = self._call_llm(prompt)
            
            return {
                "phases": {
                    **state["phases"],
                    "planning": {
                        **state["phases"]["planning"],
                        "complete": True,
                        "strategy": strategy
                    }
                },
                "current_phase": "challenge"
            }
        
        def execution_engineer(state: AdvisorState) -> Dict[str, Any]:
            """Execution Engineer node that creates implementation protocols."""
            prompt = EXECUTION_ENGINEER_PROMPT.format(
                query=state["user"]["query"],
                context=json.dumps(state["user"].get("context", {})),
                diagnosis=state["phases"]["diagnostic"]["diagnosis"]
            )
            
            analysis = self._call_llm(prompt)
            
            # Parse execution plan into structured format
            execution_plan = {
                "daily_actions": [],
                "friction_points": [],
                "metrics": [],
                "accountability": {},
                "full_analysis": analysis
            }
            
            # Extract structured components if possible
            sections = analysis.split("\n\n")
            current_section = ""
            
            for section in sections:
                if "DAILY ACTIONS" in section.upper() or "MINIMUM VIABLE" in section.upper():
                    current_section = "daily_actions"
                    actions = [line.strip() for line in section.split("\n") if line.strip() and not line.upper().startswith("DAILY")]
                    execution_plan["daily_actions"] = actions
                
                elif "FRICTION" in section.upper():
                    current_section = "friction_points"
                    points = [line.strip() for line in section.split("\n") if line.strip() and not line.upper().startswith("FRICTION")]
                    execution_plan["friction_points"] = points
                
                elif "METRICS" in section.upper() or "TRACKING" in section.upper():
                    current_section = "metrics"
                    metrics = [line.strip() for line in section.split("\n") if line.strip() and not line.upper().startswith("METRICS")]
                    execution_plan["metrics"] = metrics
            
            return {
                "phases": {
                    **state["phases"],
                    "planning": {
                        **state["phases"]["planning"],
                        "execution": execution_plan
                    }
                },
                "current_phase": "planning"  # Return to strategy planner
            }
        
        def decision_framework_designer(state: AdvisorState) -> Dict[str, Any]:
            """Decision Framework Designer node that creates decision models."""
            prompt = DECISION_FRAMEWORK_PROMPT.format(
                query=state["user"]["query"],
                context=json.dumps(state["user"].get("context", {})),
                diagnosis=state["phases"]["diagnostic"]["diagnosis"]
            )
            
            analysis = self._call_llm(prompt)
            
            # Parse decision frameworks into structured format
            decision_plan = {
                "frameworks": [],
                "questions": [],
                "review_protocol": {},
                "full_analysis": analysis
            }
            
            # Extract structured components if possible
            sections = analysis.split("\n\n")
            current_section = ""
            
            for section in sections:
                if "FRAMEWORK" in section.upper() or "DECISION MODEL" in section.upper():
                    current_section = "frameworks"
                    frameworks = [line.strip() for line in section.split("\n") if line.strip() and not line.upper().startswith("FRAMEWORK")]
                    decision_plan["frameworks"] = frameworks
                
                elif "QUESTION" in section.upper() or "BIAS" in section.upper():
                    current_section = "questions"
                    questions = [line.strip() for line in section.split("\n") if line.strip() and not line.upper().startswith("QUESTION")]
                    decision_plan["questions"] = questions
                
                elif "REVIEW" in section.upper() or "PROTOCOL" in section.upper():
                    current_section = "review_protocol"
                    protocol = section.split(":", 1)[1].strip() if ":" in section else section
                    decision_plan["review_protocol"] = {"description": protocol}
            
            return {
                "phases": {
                    **state["phases"],
                    "planning": {
                        **state["phases"]["planning"],
                        "decisions": decision_plan
                    }
                },
                "current_phase": "planning"  # Return to strategy planner
            }
        
        def challenge_designer(state: AdvisorState) -> Dict[str, Any]:
            """Challenge Designer node that creates growth challenges."""
            prompt = CHALLENGE_DESIGNER_PROMPT.format(
                query=state["user"]["query"],
                context=json.dumps(state["user"].get("context", {})),
                diagnosis=state["phases"]["diagnostic"]["diagnosis"],
                strategy=state["phases"]["planning"]["strategy"]
            )
            
            analysis = self._call_llm(prompt)
            
            # Parse challenge into structured format
            challenge = {
                "name": "Strategic Challenge",
                "actions": [],
                "timeframe": "24-72 hours",
                "success_criteria": [],
                "resistance_points": [],
                "full_description": analysis
            }
            
            # Extract structured components if possible
            sections = analysis.split("\n\n")
            
            for i, section in enumerate(sections):
                if i == 0 and ":" in section:  # First section often has the challenge name
                    challenge["name"] = section.split(":", 1)[1].strip()
                
                if "ACTION" in section.upper() or "REQUIRE" in section.upper():
                    actions = [line.strip() for line in section.split("\n") if line.strip() and not line.upper().startswith("ACTION")]
                    challenge["actions"] = actions
                
                elif "TIMEFRAME" in section.upper() or "DEADLINE" in section.upper():
                    timeframe = section.split(":", 1)[1].strip() if ":" in section else section
                    challenge["timeframe"] = timeframe
                
                elif "SUCCESS" in section.upper() or "CRITERIA" in section.upper():
                    criteria = [line.strip() for line in section.split("\n") if line.strip() and not line.upper().startswith("SUCCESS")]
                    challenge["success_criteria"] = criteria
                
                elif "RESISTANCE" in section.upper() or "OBSTACLE" in section.upper():
                    points = [line.strip() for line in section.split("\n") if line.strip() and not line.upper().startswith("RESISTANCE")]
                    challenge["resistance_points"] = points
            
            return {
                "phases": {
                    **state["phases"],
                    "challenge": {
                        "complete": True,
                        "challenge": challenge
                    }
                },
                "current_phase": "complete"  # All phases complete, move to final synthesis
            }
        
        # Create the graph
        workflow = StateGraph(AdvisorState)
        
        # Add nodes
        workflow.add_node("chief_strategist", chief_strategist)
        workflow.add_node("root_cause_diagnostician", root_cause_diagnostician)
        workflow.add_node("belief_system_analyzer", belief_system_analyzer)
        workflow.add_node("pattern_recognition_agent", pattern_recognition_agent)
        workflow.add_node("strategy_planner", strategy_planner)
        workflow.add_node("execution_engineer", execution_engineer)
        workflow.add_node("decision_framework_designer", decision_framework_designer)
        workflow.add_node("challenge_designer", challenge_designer)
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "chief_strategist",
            lambda state: {
                "start": "root_cause_diagnostician",
                "diagnostic": "root_cause_diagnostician",
                "complete": END
            }.get(state["current_phase"], "chief_strategist")
        )
        
        workflow.add_conditional_edges(
            "root_cause_diagnostician",
            lambda state: {
                "belief_analysis": "belief_system_analyzer",
                "pattern_analysis": "pattern_recognition_agent",
                "planning": "strategy_planner"
            }.get(state["current_phase"], "root_cause_diagnostician")
        )
        
        workflow.add_conditional_edges(
            "strategy_planner",
            lambda state: {
                "execution_engineering": "execution_engineer",
                "decision_framework": "decision_framework_designer",
                "challenge": "challenge_designer"
            }.get(state["current_phase"], "strategy_planner")
        )
        
        # Add specific edges
        workflow.add_edge("belief_system_analyzer", "root_cause_diagnostician")
        workflow.add_edge("pattern_recognition_agent", "root_cause_diagnostician")
        workflow.add_edge("execution_engineer", "strategy_planner")
        workflow.add_edge("decision_framework_designer", "strategy_planner")
        workflow.add_edge("challenge_designer", "chief_strategist")
        
        # Set entry point
        workflow.set_entry_point("chief_strategist")
        
        # Compile the graph
        return workflow.compile()
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt and return the response text.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The response text from the LLM
        """
        try:
            # Make the API call
            response = self.llm_client.create_message(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000
            )
            
            # Extract the text based on the provider's response format
            if hasattr(response, 'content') and isinstance(response.content, list):
                result = response.content[0].text
            else:
                result = response.choices[0].message.content
            
            return result
                
        except Exception as e:
            self.logger.error(f"Error calling LLM: {str(e)}")
            raise
    
    def _validate_query(self, query: str) -> bool:
        """Validate the query to ensure it's meaningful and can be processed.
        
        Args:
            query: The query to validate
            
        Returns:
            True if the query is valid, False otherwise
        """
        if not query or not query.strip():
            return False
            
        # Check if query is too short (less than 3 words)
        words = query.split()
        if len(words) < 3:
            return False
            
        # Check if query seems like random characters
        # Count the percentage of non-alphabetic characters
        alpha_count = sum(c.isalpha() or c.isspace() for c in query)
        if alpha_count / len(query) < 0.7:  # Less than 70% alphabetic chars
            return False
            
        # Check if query contains at least one word with more than 3 characters
        if not any(len(word) > 3 for word in words):
            return False
            
        return True
    
    def generate_advice(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate strategic advice for a query.
        
        Args:
            query: The user's query
            context: Optional context
            
        Returns:
            A dictionary containing the strategic advice
        """
        # Initialize session
        session_id = str(uuid.uuid4())
        start_time = time.time()
        
        self.logger.info(f"Generating strategic advice for query: {query}")
        self.logger.info(f"Session ID: {session_id}")
        
        print(f"\n📋 STARTING STRATEGIC ADVISOR (CUSTOM ARCHITECTURE)")
        print(f"Query: {query}")
        print(f"Session ID: {session_id}")
        
        # Validate the query
        if not self._validate_query(query):
            self.logger.warning(f"Invalid query detected: {query}")
            return {
                "hard_truth": "I couldn't understand your query. It appears to be too short, contains mostly random characters, or lacks meaningful content.",
                "actions": [
                    "Please provide a clearer, more detailed query that describes what you're looking for advice about.",
                    "Make sure your query is written in complete sentences and contains specific details about your situation.",
                    "Try to ask a question that relates to a specific challenge, goal, or decision you're facing."
                ],
                "challenge": {
                    "description": "The clearer and more specific you can be with your query, the better advice I can provide.",
                    "question": "What specific situation, challenge, or decision would you like advice about?"
                },
                "session_id": session_id,
                "execution_time": time.time() - start_time
            }
        
        # Create the initial state
        initial_state = {
            "user": {
                "query": query,
                "context": context or {},
                "history": []
            },
            "phases": {},
            "current_phase": "start",
            "response": {
                "hard_truth": "",
                "actions": [],
                "challenge": {}
            }
        }
        
        try:
            # Run the workflow with increased recursion limit
            print("\n🚀 RUNNING CUSTOM AGENT WORKFLOW...")
            end_state = self.workflow.invoke(initial_state, config={"recursion_limit": 50})
            
            # Extract the response
            response = end_state["response"]
            
            # Add metadata
            response["session_id"] = session_id
            response["execution_time"] = time.time() - start_time
            
            # Save the response
            self._save_response(response, session_id)
            
            print(f"\n⏱️ EXECUTION TIME: {response['execution_time']:.2f} seconds")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating advice: {e}")
            print(f"\n❌ ERROR: {str(e)}")
            raise
            
    def _parse_chief_strategist_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the response from the chief strategist.
        
        Args:
            response_text: The raw response text
            
        Returns:
            A structured response dictionary
        """
        # Initialize response components
        hard_truth = ""
        actions = []
        challenge = {}
        final_analysis = ""
        
        # Split into sections
        sections = response_text.split("\n\n")
        current_section = None
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            if "FINAL ANALYSIS:" in section or "ANALYSIS:" in section:
                current_section = "final_analysis"
                final_analysis = section.replace("FINAL ANALYSIS:", "").replace("ANALYSIS:", "").strip()
            elif "HARD TRUTH:" in section:
                current_section = "hard_truth"
                hard_truth = section.replace("HARD TRUTH:", "").strip()
            elif "ACTIONS:" in section:
                current_section = "actions"
                action_lines = [line.strip() for line in section.split("\n")[1:] if line.strip()]
                actions = []
                for line in action_lines:
                    # Remove any leading numbers or bullet points
                    if line[0].isdigit() and ". " in line:
                        actions.append(line.split(". ", 1)[1])
                    elif line.startswith("- "):
                        actions.append(line[2:])
                    else:
                        actions.append(line)
            elif "CHALLENGE:" in section:
                current_section = "challenge"
                challenge_text = section.replace("CHALLENGE:", "").strip()
                challenge = {
                    "name": "Strategic Challenge",
                    "description": challenge_text
                }
            elif current_section == "final_analysis":
                final_analysis += "\n\n" + section
            elif current_section == "hard_truth":
                hard_truth += "\n\n" + section
            elif current_section == "actions":
                action_lines = [line.strip() for line in section.split("\n") if line.strip()]
                for line in action_lines:
                    # Remove any leading numbers or bullet points
                    if line[0].isdigit() and ". " in line:
                        actions.append(line.split(". ", 1)[1])
                    elif line.startswith("- "):
                        actions.append(line[2:])
                    else:
                        actions.append(line)
            elif current_section == "challenge":
                challenge["description"] += "\n\n" + section
        
        # Create the final response
        response = {
            "hard_truth": hard_truth,
            "actions": actions,
            "challenge": challenge,
            "final_analysis": final_analysis
        }
        
        return response
    
    def _save_response(self, response: Dict[str, Any], session_id: str) -> None:
        """Save the response to a file.
        
        Args:
            response: The response to save
            session_id: The session ID
        """
        # Create the output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Generate a filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"strategic_advice_{timestamp}_{session_id[:8]}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        # Save the response
        with open(filepath, "w") as f:
            json.dump(response, f, indent=2)
        
        self.logger.info(f"Response saved to {filepath}") 