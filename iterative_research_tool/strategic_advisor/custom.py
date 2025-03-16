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

USER QUERY: {query}
DIAGNOSTIC INSIGHTS: {diagnosis}
STRATEGIC PLAN: {strategy}
CHALLENGE: {challenge}

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
        verbose: bool = False
    ):
        """Initialize the Strategic Advisor with custom architecture.
        
        Args:
            llm_provider: The LLM provider to use
            api_key: The API key for the LLM provider
            model: The model to use
            output_dir: Directory to save outputs to
            verbose: Whether to enable verbose output
        """
        self.llm_provider = llm_provider.lower()
        self.api_key = api_key
        self.verbose = verbose
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Set the model
        if model:
            self.model = model
        else:
            self.model = LLMClientFactory.get_default_model(self.llm_provider)
            
        self.logger.info(f"Strategic Advisor (Custom) using LLM provider: {self.llm_provider} with model: {self.model}")
        
        # Set up the LLM client
        self.llm_client = LLMClientFactory.create_client(self.llm_provider, self.api_key)
        
        # Set up the output directory
        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = os.path.expanduser("~/strategic_advisor_output")
            
        # Create the output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Build the LangGraph state machine
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine for the custom architecture."""
        # Define node functions
        def chief_strategist(state: AdvisorState) -> Dict[str, Any]:
            """Chief Strategist node that coordinates the entire process."""
            if state["current_phase"] == "init":
                # Initial analysis - determine if we need to start with diagnostic phase
                return {"current_phase": "diagnostic"}
            
            elif state["current_phase"] == "complete":
                # All phases complete, generate final response
                prompt = FINAL_SYNTHESIS_PROMPT.format(
                    query=state["user"]["query"],
                    diagnosis=state["phases"]["diagnostic"]["diagnosis"],
                    strategy=state["phases"]["planning"]["strategy"],
                    challenge=json.dumps(state["phases"]["challenge"]["challenge"])
                )
                
                response = self._call_llm(prompt)
                
                # Extract the components (hard truth, actions, challenge)
                response_parts = response.split("\n\n")
                hard_truth = ""
                actions = []
                challenge = {}
                
                for part in response_parts:
                    if "THE HARD TRUTH" in part.upper() or "HARD TRUTH" in part.upper():
                        hard_truth = part.split(":", 1)[1].strip() if ":" in part else part
                    elif "ACTIONABLE STEPS" in part.upper() or "ACTIONS" in part.upper():
                        action_text = part.split(":", 1)[1].strip() if ":" in part else part
                        actions = [a.strip() for a in action_text.split("\n") if a.strip()]
                    elif "CHALLENGE" in part.upper() or "ASSIGNMENT" in part.upper():
                        challenge_text = part.split(":", 1)[1].strip() if ":" in part else part
                        challenge = {
                            "name": "Strategic Challenge",
                            "description": challenge_text,
                            "timeframe": "24-72 hours"
                        }
                
                return {
                    "response": {
                        "hard_truth": hard_truth,
                        "actions": actions,
                        "challenge": challenge
                    }
                }
            
            return {}
        
        def root_cause_diagnostician(state: AdvisorState) -> Dict[str, Any]:
            """Root Cause Diagnostician node that coordinates the diagnostic phase."""
            # If beliefs and patterns not analyzed yet, direct to analyzers
            if not state["phases"]["diagnostic"].get("beliefs"):
                return {"current_phase": "belief_analysis"}
            
            if not state["phases"]["diagnostic"].get("patterns"):
                return {"current_phase": "pattern_analysis"}
            
            # Synthesize diagnosis
            prompt = ROOT_CAUSE_DIAGNOSTICIAN_PROMPT.format(
                query=state["user"]["query"],
                context=json.dumps(state["user"].get("context", {})),
                beliefs=json.dumps(state["phases"]["diagnostic"]["beliefs"]),
                patterns=json.dumps(state["phases"]["diagnostic"]["patterns"])
            )
            
            diagnosis = self._call_llm(prompt)
            
            return {
                "phases": {
                    **state["phases"],
                    "diagnostic": {
                        **state["phases"]["diagnostic"],
                        "complete": True,
                        "diagnosis": diagnosis
                    }
                },
                "current_phase": "planning"
            }
        
        def belief_system_analyzer(state: AdvisorState) -> Dict[str, Any]:
            """Belief System Analyzer node that identifies limiting beliefs."""
            prompt = BELIEF_SYSTEM_ANALYZER_PROMPT.format(
                query=state["user"]["query"],
                context=json.dumps(state["user"].get("context", {}))
            )
            
            analysis = self._call_llm(prompt)
            
            # Parse belief analysis into structured format
            belief_lines = analysis.split("\n")
            beliefs = []
            current_belief = {}
            
            for line in belief_lines:
                line = line.strip()
                if line and line[0].isdigit() and ":" in line:
                    if current_belief and "belief" in current_belief:
                        beliefs.append(current_belief)
                        current_belief = {}
                    
                    belief_text = line.split(":", 1)[1].strip()
                    current_belief["belief"] = belief_text
                
                elif line.startswith("Upgraded belief:") or line.startswith("Upgraded Belief:"):
                    current_belief["upgrade"] = line.split(":", 1)[1].strip()
            
            # Add the last belief if exists
            if current_belief and "belief" in current_belief:
                beliefs.append(current_belief)
            
            # If no structured beliefs were extracted, create a simple one from the analysis
            if not beliefs:
                beliefs = [{"belief": "Extracted from analysis", "content": analysis}]
            
            return {
                "phases": {
                    **state["phases"],
                    "diagnostic": {
                        **state["phases"]["diagnostic"],
                        "beliefs": beliefs
                    }
                },
                "current_phase": "diagnostic"  # Return to diagnostician
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
                "init": "root_cause_diagnostician",
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
    
    def generate_advice(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate strategic advice for the given query using the custom architecture.
        
        Args:
            query: The user's query
            context: Optional context information
            
        Returns:
            The strategic advice with hard truth, actions, and challenge
        """
        session_id = str(uuid.uuid4())
        start_time = time.time()
        
        self.logger.info(f"Generating strategic advice for query: {query}")
        self.logger.info(f"Session ID: {session_id}")
        
        try:
            # Format the chief strategist prompt
            prompt = CHIEF_STRATEGIST_PROMPT.format(
                query=query,
                context=json.dumps(context) if context else ""
            )
            
            # Call the LLM
            response_text = self._call_llm(prompt)
            
            # Parse the response
            response = self._parse_chief_strategist_response(response_text)
            
            # Add metadata
            response["session_id"] = session_id
            response["execution_time"] = time.time() - start_time
            
            # Save the response
            self._save_response(response, session_id)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating advice: {e}")
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
        
        # Split into sections
        sections = response_text.split("\n\n")
        current_section = None
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            if "HARD TRUTH:" in section:
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
            "challenge": challenge
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