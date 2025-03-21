"""Custom Architecture for Strategic Advisor System."""

import os
import json
import logging
import time
import re
import uuid
import traceback
from typing import TypedDict, List, Dict, Any, Optional, Callable
from typing_extensions import Annotated
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
    current_phase: Annotated[str, "last"]
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

CHALLENGER_PROMPT = """
You specialize in identifying weaknesses and edge cases in strategic plans. Your responsibilities:

1. Stress-test strategies without holding back
2. Identify underlying assumptions that could prove false
3. Find edge cases where the strategy might fail
4. Determine potential improvements to strengthen the plan
5. Deliver honest critique without sugar-coating

Your analysis must be rigorous, direct, and focused on improving the strategy.
Avoid superficial criticism - dig into fundamental vulnerabilities.

For each challenge, provide:
1. The specific weaknesses in the current approach
2. The underlying assumptions that could be disproven
3. Edge cases where the strategy might break down
4. Specific recommendations to strengthen the plan

USER QUERY: {query}
USER CONTEXT: {context}
STRATEGY: {strategy}
EXECUTION PLAN: {execution}
DECISION FRAMEWORKS: {decisions}
"""

HARD_TRUTH_PROMPT = """
You specialize in delivering uncomfortable but necessary truths. Your responsibilities:

1. Cut through denial and self-deception with direct honesty
2. Identify the painful realities the user is avoiding
3. Confront protection mechanisms that prevent growth
4. Deliver truths in a way that leads to action rather than despair
5. Focus on the specific behaviors and beliefs that maintain stuck patterns

Your insights should be brutally honest but not cruel for cruelty's sake.
Every hard truth should lead to a potential breakthrough.

Focus on:
1. Specific self-limiting behaviors the user needs to acknowledge
2. Identity-level shifts required for transformation
3. Comfort zone attachments preventing progress
4. False narratives blocking the path forward
5. Resource investments needed that the user is resisting

USER QUERY: {query}
USER CONTEXT: {context}
DIAGNOSTIC INSIGHTS: {diagnosis}
CHALLENGE RESULTS: {challenge}
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

ACTION_DESIGNER_PROMPT = """
You specialize in creating highly actionable implementation plans. Your responsibilities:

1. Transform insights into concrete action steps
2. Prioritize steps based on impact and feasibility
3. Create accountability systems and tracking mechanisms
4. Design habits that facilitate consistent execution
5. Provide contingency plans for common failure points

Your plans must be specific, measurable, and immediately implementable.
Avoid vague directives - create precise actions with clear success criteria.

For each plan, provide:
1. Immediate first steps (what to do today)
2. Daily/weekly implementation rituals
3. Tracking and accountability systems
4. Environmental modifications to reduce friction
5. Troubleshooting protocols for common obstacles

USER QUERY: {query}
USER CONTEXT: {context}
DIAGNOSTIC INSIGHTS: {diagnosis}
STRATEGIC PLAN: {strategy}
CHALLENGE RESULTS: {challenge}
HARD TRUTHS: {hard_truth}
"""

class StrategicAdvisorCustom:
    """Implementation of the Custom Architecture for Strategic Advisor."""
    
    def __init__(
        self,
        llm_provider: str = "anthropic",
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
        
        # Define emoji indicators for each phase
        self.emojis = {
            "diagnostic": "🔍",
            "belief": "🧠",
            "pattern": "🔄",
            "root_cause": "🌱",
            "planning": "📝",
            "execution": "⚙️",
            "decision": "🔀",
            "challenge": "🏆",
            "hard_truth": "💎",
            "action": "🚀",
            "final": "✨"
        }
        
        # Initialize LLM component to None
        self.llm_component = None
        
        logger.info(f"Strategic Advisor (Custom) using LLM provider: {self.llm_provider} with model: {self.model}")
        
        # Initialize the state graph
        self.workflow = self._build_graph()
    
    def link_llm_component(self, llm_component):
        """Link an LLM component to this advisor.
        
        Args:
            llm_component: An object that has a generate method
        """
        self.llm_component = llm_component
        # print(f"DEBUG: Linked LLM component of type {type(llm_component).__name__}")

    def generate_advice(self, query: str) -> Dict[str, Any]:
        """Generate strategic advice for the given query.
        
        Args:
            query: User query to get advice for
            
        Returns:
            Dictionary containing the generated advice
        """
        # Initialize the state for the workflow
        state = {
            "query": query,
            "current_phase": "start",
            "response": {
                "hard_truth": "",
                "actions": [],
                "challenge": {}
            }
        }
        
        start_time = time.time()
        try:
            # Run the workflow with the initialized state
            final_state = self._execute_workflow(state)
            
            # Check if we got a valid response
            if final_state and isinstance(final_state, dict) and "response" in final_state:
                result = final_state["response"]
                if "error" in result:
                    return {
                        "hard_truth": f"ERROR: {result['error']}",
                        "actions": ["Try again later or check your API key settings"],
                        "challenge": {}
                    }
                return result
            else:
                # Return a default response if something went wrong
                return {
                    "hard_truth": "ERROR: Failed to generate a complete response",
                    "actions": ["Try again with a simpler query", "Check system logs for errors"],
                    "challenge": {}
                }
        except KeyError as e:
            error_message = f"KeyError: {str(e)}"
            # traceback.print_exc()  # Print the traceback for debugging
            return {
                "hard_truth": f"ERROR: {error_message}",
                "actions": ["Try again with a simpler query", "Check system logs for errors"],
                "challenge": {}
            }
        except Exception as e:
            error_message = f"{type(e).__name__}: {str(e)}"
            # Print traceback for debugging if needed
            # traceback.print_exc()
            
            if "API key" in str(e) or "unauthorized" in str(e).lower():
                return {
                    "hard_truth": "ERROR: The API key provided is invalid or unauthorized.",
                    "actions": [
                        "Verify your API key is correctly set in the environment variable",
                        "Make sure your account has sufficient credits",
                        "Try using a different LLM provider"
                    ],
                    "challenge": {}
                }
            
            return {
                "hard_truth": f"ERROR: {error_message}",
                "actions": ["Try again with a simpler query", "Check system logs for errors"],
                "challenge": {}
            }
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            # print(f"DEBUG: Execution time: {execution_time:.2f} seconds")

    def _build_graph(self) -> Callable:
        """Build the graph for the workflow.
        
        Returns:
            Callable: A workflow function
        """
        # Initialize the StateGraph
        workflow = StateGraph(AdvisorState)
        
        # Add nodes for each state
        workflow.add_node("start", self.start)
        workflow.add_node("diagnostic", self.diagnostic)
        workflow.add_node("belief_system_analyzer", self.belief_system_analyzer)
        workflow.add_node("pattern_recognition_agent", self.pattern_recognition_agent)
        workflow.add_node("root_cause_diagnostician", self.root_cause_diagnostician)
        workflow.add_node("strategy_planner", self.strategy_planner)
        workflow.add_node("execution_engineer", self.execution_engineer)
        workflow.add_node("decision_framework_designer", self.decision_framework_designer)
        workflow.add_node("hard_truth_teller", self.hard_truth_teller)
        workflow.add_node("action_designer", self.action_designer)
        workflow.add_node("challenge_designer", self.challenge_designer)
        workflow.add_node("challenger", self.challenger)
        workflow.add_node("final_synthesis", self.final_synthesis)
        workflow.add_node("chief_strategist", self.chief_strategist)
        workflow.add_node("complete", self.complete)
        
        # print("DEBUG: Added all nodes to workflow graph")
        
        # Set the entry point
        workflow.set_entry_point("start")
        
        # Add conditional edges
        workflow.add_edge("start", "chief_strategist")
        
        # Define the routing function for chief_strategist
        def route_from_chief_strategist(state):
            current_phase = state.get("current_phase")
            if current_phase == "diagnostic":
                return "diagnostic"
            elif current_phase == "complete":
                return "complete"
            else:
                return None
        
        workflow.add_conditional_edges(
            "chief_strategist", 
            route_from_chief_strategist
        )
        
        # Diagnostic phase edges
        workflow.add_edge("diagnostic", "belief_system_analyzer")
        workflow.add_edge("belief_system_analyzer", "pattern_recognition_agent")
        workflow.add_edge("pattern_recognition_agent", "root_cause_diagnostician")
        workflow.add_edge("root_cause_diagnostician", "strategy_planner")
        
        # Planning phase edges
        workflow.add_edge("strategy_planner", "execution_engineer")
        workflow.add_edge("execution_engineer", "decision_framework_designer")
        workflow.add_edge("decision_framework_designer", "hard_truth_teller")
        
        # Action and challenge phase edges
        workflow.add_edge("hard_truth_teller", "action_designer")
        workflow.add_edge("action_designer", "challenge_designer")
        workflow.add_edge("challenge_designer", "challenger")
        workflow.add_edge("challenger", "final_synthesis")
        
        # Final synthesis edge
        workflow.add_edge("final_synthesis", "chief_strategist")
        
        # Adding explicit end state handling
        workflow.add_edge("complete", "__end__")
        
        # print("DEBUG: Added all edges to workflow graph")
        
        # Compile the workflow with an increased recursion limit
        return workflow.compile()
    
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
    
    def _save_response_to_file(self, response: Dict[str, Any], file_path: str = None) -> None:
        """Save the response to a specified file path or generate a default path.
        
        Args:
            response: The response to save
            file_path: Optional path to save the file, if None a default path is generated
        """
        # Create the output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # If no file path is provided, generate one
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_id = response.get("session_id", str(uuid.uuid4())[:8])
            filename = f"strategic_advice_{timestamp}_{session_id}.json"
            file_path = os.path.join(self.output_dir, filename)
        
        # Save the response
        with open(file_path, "w") as f:
            json.dump(response, f, indent=2)
        
        self.logger.info(f"Response saved to {file_path}")
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM.
        
        Args:
            prompt: Prompt to send to the LLM
            
        Returns:
            Response from the LLM
        """
        try:
            # Show a progress indicator
            # print("Processing response...")
            
            # Forward the call to the linked LLM component
            if self.llm_component:
                response = self.llm_component.generate(prompt)
                # Clear the progress indicator (add a carriage return)
                print("\r                            \r", end="")
                return response
            else:
                print("ERROR: No LLM component linked")
                return "Error: No LLM component linked"
        except Exception as e:
            # Clear the progress indicator (add a carriage return)
            print("\r                            \r", end="")
            
            error_message = str(e)
            
            # Check for common API key related errors
            if "401" in error_message or "Unauthorized" in error_message or "Invalid API key" in error_message:
                print(f"\n🔑 API KEY ERROR: {error_message}")
                return f"""HARD TRUTH: Your API key is invalid or unauthorized.

ACTIONS:
1. Verify your API key is correct
2. Check if your API key has proper permissions
3. Ensure your billing is up to date
4. Try regenerating a new API key

If using OpenAI, check your API key at https://platform.openai.com/account/api-keys
If using Anthropic, verify your key at https://console.anthropic.com/
"""
            else:
                print(f"\n⚠️ LLM CALL ERROR: {error_message}")
                return f"Error occurred: {error_message}"

    def start(self, state: AdvisorState) -> Dict[str, Any]:
        """Initialize the workflow state.
        
        Args:
            state: The initial state containing user query
            
        Returns:
            Updated state ready to begin workflow
        """
        # print("\n🚀 INITIALIZING STRATEGIC ADVISOR WORKFLOW")
        # print(f"DEBUG: Starting workflow with query: {state['user']['query']}")
        
        # Initialize the workflow state
        return {
            "current_phase": "start",
            "response": {
                "hard_truth": "",
                "actions": [],
                "challenge": {}
            }
        }

    def _parse_chief_strategist_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the response from the chief strategist.
        
        Args:
            response_text: Response from the LLM
            
        Returns:
            Parsed response with hard truth, actions, and challenge
        """
        parsed_response = {}
        
        # Extract the hard truth
        hard_truth_match = re.search(r"HARD TRUTH:(.*?)(?=\n\n|ACTIONS:|$)", response_text, re.DOTALL)
        if hard_truth_match:
            parsed_response["hard_truth"] = hard_truth_match.group(1).strip()
            # print(f"DEBUG: Extracted hard truth of length {len(parsed_response['hard_truth'])}")
        
        # Extract the actions
        actions_match = re.search(r"ACTIONS:(.*?)(?=\n\n|CHALLENGE:|$)", response_text, re.DOTALL)
        if actions_match:
            actions_text = actions_match.group(1).strip()
            # Split by numbered items or bullet points
            actions = re.findall(r"\d+\.\s+(.*?)(?=\n\d+\.|$)", actions_text, re.DOTALL)
            if not actions:
                actions = re.findall(r"[-*]\s+(.*?)(?=\n[-*]|$)", actions_text, re.DOTALL)
            if not actions:
                actions = [line.strip() for line in actions_text.split("\n") if line.strip()]
            
            parsed_response["actions"] = [action.strip() for action in actions if action.strip()]
            # print(f"DEBUG: Extracted {len(parsed_response['actions'])} actions")
        
        # Extract the challenge
        challenge_match = re.search(r"CHALLENGE:(.*?)(?=\n\n|$)", response_text, re.DOTALL)
        if challenge_match:
            challenge_text = challenge_match.group(1).strip()
            # Try to extract a description and timeframe
            timeframe_match = re.search(r"Timeframe:\s*(.*?)(?=\n|$)", challenge_text, re.IGNORECASE)
            if timeframe_match:
                timeframe = timeframe_match.group(1).strip()
                # Remove the timeframe line from the description
                description = re.sub(r"Timeframe:\s*.*?(?=\n|$)", "", challenge_text, flags=re.IGNORECASE).strip()
            else:
                # Default timeframe if not specified
                timeframe = "Next 24-72 hours"
                description = challenge_text
            
            parsed_response["challenge"] = {
                "description": description,
                "timeframe": timeframe
            }
            # print(f"DEBUG: Extracted challenge with description length {len(description)}")
        
        return parsed_response

    def chief_strategist(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the query with the chief strategist.
        
        Args:
            state: The current state
            
        Returns:
            Next state and node
        """
        # Add detailed logging
        # print(f"DEBUG: Entering chief_strategist with current_phase: {state.get('current_phase', 'unknown')}")
        
        # Check if we have the expected state structure
        if not isinstance(state, dict):
            print(f"ERROR: Invalid state type: {type(state)}")
            return {
                "current_phase": "__end__",
                "response": {
                    "hard_truth": "An error occurred: Invalid state type",
                    "actions": ["Try again with a different query"]
                }
            }
            
        # Get the query - handle different state structures
        query = None
        if 'user' in state and isinstance(state['user'], dict) and 'query' in state['user']:
            query = state["user"]["query"]
        elif 'query' in state:
            query = state["query"]
            # Restructure the state to match expected format
            state = {
                "user": {
                    "query": query,
                    "context": {},
                    "history": []
                },
                "phases": {},
                "current_phase": state.get("current_phase", "start"),
                "response": state.get("response", {
                    "hard_truth": "",
                    "actions": [],
                    "challenge": {}
                })
            }
            
        if not query:
            print("ERROR: No query found in state")
            return {
                "current_phase": "__end__",
                "response": {
                    "hard_truth": "An error occurred: No query provided",
                    "actions": ["Provide a query and try again"]
                }
            }
            
        # Check if we've already run through all phases
        if state.get("current_phase") == "complete":
            # print("DEBUG: Already in complete phase, ending workflow")
            return {"current_phase": "__end__"}
        
        # Handle special __end__ state
        if state.get("current_phase") == "__end__":
            # print("DEBUG: Received __end__ state, terminating workflow")
            return None
        
        # If we're in the "start" phase, we should always proceed to diagnostic regardless of response completeness
        if state.get("current_phase") == "start":
            # Format a simplified prompt just to get initial insights
            prompt = f"""You are a Chief Strategy Officer for a strategic advisory firm. 
Your job is to deliver brutally honest advice that addresses the root causes of
issues, not just symptoms.
            
USER QUERY: {query}
            
I need you to provide some initial thoughts on this query that will help guide a comprehensive analysis.
What might be the underlying issues and potential directions for analysis?

Please provide brief preliminary insights that other specialist agents can build upon.
"""
            
            # Call the LLM for initial insights only
            response_text = self._call_llm(prompt)
            # print(f"DEBUG: Got initial insights of length {len(response_text)} from LLM")
            
            # Store these insights but don't parse as a full response
            prelim_response = {
                "preliminary_insights": response_text,
                "hard_truth": "",
                "actions": [],
                "challenge": {}
            }
            
            # Initialize the diagnostic phase
            # print("DEBUG: Moving to diagnostic phase (initial workflow stage)")
            return {
                "current_phase": "diagnostic",  # Using "diagnostic" consistently
                "phases": {
                    **state.get("phases", {}),
                    "diagnostic": {  # Using "diagnostic" consistently 
                        "complete": False,
                        "beliefs": [],
                        "patterns": [],
                        "diagnosis": ""
                    }
                },
                "response": prelim_response,
                "user": {
                    "query": query, 
                    "context": {},
                    "history": []
                }
            }
        
        # For final synthesis after all phases are complete
        if state["current_phase"] == "final_synthesis":
            # print("DEBUG: Performing final synthesis of all agent insights")
            
            # Get the query and context
            query = state["user"]["query"]
            context = json.dumps(state["user"].get("context", {})) if state["user"].get("context") else ""
            
            # Get the diagnostic insights
            diagnostic_phase = state.get("phases", {}).get("diagnostic", {})
            diagnosis = diagnostic_phase.get("diagnosis", "")
            
            # Get the strategy plan
            planning_phase = state.get("phases", {}).get("planning", {})
            strategy = planning_phase.get("strategy", "")
            
            # Get the challenge design
            challenge_phase = state.get("phases", {}).get("challenge", {})
            challenge = challenge_phase.get("challenge", {})
            challenge_text = json.dumps(challenge)
            
            # Get the hard truth insights
            hard_truth_phase = state.get("phases", {}).get("hard_truth", {})
            hard_truth = hard_truth_phase.get("insights", "")
            
            # Get the action plan
            action_phase = state.get("phases", {}).get("action", {})
            action_plan = action_phase.get("plan", {})
            
            # Format action steps
            action_steps = []
            if action_plan and isinstance(action_plan, dict):
                if "immediate_steps" in action_plan:
                    action_steps.extend(action_plan["immediate_steps"])
                if "habits" in action_plan:
                    action_steps.extend(action_plan["habits"])
                if "tracking" in action_plan:
                    action_steps.extend(action_plan["tracking"])
                if "contingencies" in action_plan:
                    action_steps.extend(action_plan["contingencies"])
            
            # Use the comprehensive final synthesis prompt
            prompt = FINAL_SYNTHESIS_PROMPT.format(
                query=query,
                diagnosis=diagnosis or "No diagnostic information available.",
                strategy=strategy or "No strategy information available.",
                challenge=challenge_text or "No challenge information available."
            )
            
            # Display the prompt if verbose output is enabled
            if self.verbose_output:
                print(f"\n📝 PROMPT FOR FINAL SYNTHESIS:")
                print("-" * 40)
                print(prompt)
                print("-" * 40)
            
            # Call the LLM
            try:
                response_text = self._call_llm(prompt)
                # print(f"DEBUG: Got final synthesis response of length {len(response_text)} from LLM")
            except Exception as e:
                # print(f"DEBUG: Error in final synthesis LLM call: {str(e)}")
                # Use existing data as fallback
                response_text = hard_truth
            
            # Parse the response
            parsed_response = self._parse_chief_strategist_response(response_text)
            
            # If we couldn't parse a hard truth from the LLM response, use the one from the hard truth phase
            if not parsed_response.get("hard_truth") and hard_truth:
                hard_truth_match = re.search(r"HARD TRUTH:(.*?)(?=\n\n|ACTIONS:|$)", hard_truth, re.DOTALL)
                if hard_truth_match:
                    parsed_response["hard_truth"] = hard_truth_match.group(1).strip()
            
            # If we couldn't parse actions from the LLM response, use the ones from the action plan
            if not parsed_response.get("actions") and action_steps:
                parsed_response["actions"] = action_steps
            
            # If we couldn't parse a challenge from the LLM response, use the one from the challenge phase
            if not parsed_response.get("challenge") and challenge:
                if isinstance(challenge, dict) and "description" in challenge:
                    parsed_response["challenge"] = challenge
                else:
                    parsed_response["challenge"] = {
                        "description": str(challenge),
                        "timeframe": "24-72 hours"
                    }
            
            # Add original agent insights if present in the response
            insights_match = re.search(r"ORIGINAL AGENT INSIGHTS:(.*?)(?=\n\n|$)", response_text, re.DOTALL)
            if insights_match:
                parsed_response["original_agent_insights"] = insights_match.group(1).strip()
            
            # Log the parsed response
            # print(f"DEBUG: Parsed final response: hard_truth: {bool(parsed_response.get('hard_truth'))}, actions: {len(parsed_response.get('actions', []))}, challenge: {bool(parsed_response.get('challenge'))}")
            
            # Create the complete response
            final_response = {
                "hard_truth": parsed_response.get("hard_truth", ""),
                "actions": parsed_response.get("actions", []),
                "challenge": parsed_response.get("challenge", {}),
                "original_agent_insights": parsed_response.get("original_agent_insights", "")
            }
            
            # Mark the workflow as complete and return END to avoid recursion issues
            # print("DEBUG: Workflow complete, ending workflow")
            return {"current_phase": "complete", "response": final_response}
        
        # For other phases, just return the current state and rely on the edge logic
        # print(f"DEBUG: Chief strategist is maintaining current phase: {state['current_phase']}")
        return {"current_phase": state["current_phase"]}

    def hard_truth_teller(self, state: AdvisorState) -> Dict[str, Any]:
        """Process the hard truth insights.
        
        Args:
            state: The current state
            
        Returns:
            Updated state with hard truth insights
        """
        # Display response from hard truth teller
        print(f"\n{self.emojis['hard_truth']} HARD TRUTH TELLER")
        
        # Create hard truth phase if it doesn't exist
        if "hard_truth" not in state.get("phases", {}):
            state["phases"] = state.get("phases", {})
            state["phases"]["hard_truth"] = {
                "complete": False,
                "insights": ""
            }
        
        # Set the next phase to action design
        # print("DEBUG: Hard truth delivered. Moving to action design phase")
        return {
            "current_phase": "action",
            "phases": {
                **state.get("phases", {}),
                "hard_truth": {
                    "complete": True,
                    "insights": state["response"].get("hard_truth", "")
                }
            }
        }

    def final_synthesis(self, state: AdvisorState) -> Dict[str, Any]:
        """Process the final synthesis of all insights.
        
        Args:
            state: The current state
            
        Returns:
            Updated state ready for final synthesis
        """
        print(f"\n{self.emojis['final']} FINAL SYNTHESIS PHASE")
        # print("DEBUG: Beginning final synthesis of all insights")
        
        # Ensure we have all the necessary parts
        has_diagnostic = "diagnostic" in state.get("phases", {}) and state["phases"]["diagnostic"].get("complete", False)
        has_planning = "planning" in state.get("phases", {}) and state["phases"]["planning"].get("complete", False)
        has_hard_truth = "hard_truth" in state.get("phases", {}) and state["phases"]["hard_truth"].get("complete", False)
        has_action = "action" in state.get("phases", {}) and state["phases"]["action"].get("complete", False)
        has_challenge = "challenge" in state.get("phases", {}) and state["phases"]["challenge"].get("complete", False)
        
        # print(f"DEBUG: Phase completion status - diagnostic: {has_diagnostic}, planning: {has_planning}, hard_truth: {has_hard_truth}, action: {has_action}, challenge: {has_challenge}")
        
        # Signal to the chief strategist that we're ready for final synthesis
        return {"current_phase": "final_synthesis"}

    def complete(self, state: AdvisorState) -> Dict[str, Any]:
        """Handle the completion of the workflow.
        
        Args:
            state: The current state
            
        Returns:
            Final state to end the workflow
        """
        # print("DEBUG: Workflow completion handler triggered")
        
        # Ensure the response is captured
        if "response" not in state:
            print("WARNING: No response found in state at completion handler")
            state["response"] = {
                "hard_truth": "No insights could be generated.",
                "actions": ["Review system logs for errors."],
                "challenge": {"description": "Troubleshoot API connectivity issues.", "timeframe": "Immediate"}
            }
        
        # Final logging before ending
        # print(f"DEBUG: Workflow complete. Final response has {len(state['response'].get('hard_truth', ''))} chars in hard truth and {len(state['response'].get('actions', []))} actions")
        
        # Return __end__ as the next state to properly terminate
        return {"current_phase": "__end__"}

    def diagnostic(self, state: AdvisorState) -> Dict[str, Any]:
        """Handle the diagnostic phase of the workflow.
        
        Args:
            state: The current state
            
        Returns:
            Updated state to proceed to belief analysis
        """
        print(f"\n{self.emojis['diagnostic']} DIAGNOSTIC PHASE")
        # print("DEBUG: Beginning diagnostic analysis")
        
        # Set up the diagnostic phase if not already present
        if "diagnostic" not in state.get("phases", {}):
            state["phases"] = state.get("phases", {})
            state["phases"]["diagnostic"] = {
                "complete": False,
                "beliefs": [],
                "patterns": [],
                "diagnosis": ""
            }
        
        # Move to the belief analysis
        # print("DEBUG: Proceeding to belief system analysis")
        return {
            "current_phase": "belief_analysis",
            "phases": state.get("phases", {})
        }

    def belief_system_analyzer(self, state: AdvisorState) -> Dict[str, Any]:
        """Process the belief system analysis.
        
        Args:
            state: The current state
            
        Returns:
            Updated state with belief analysis
        """
        print(f"\n{self.emojis['belief']} BELIEF SYSTEM ANALYZER")
        
        # Get the query and context
        query = state["user"]["query"]
        context = json.dumps(state["user"].get("context", {})) if state["user"].get("context") else ""
        
        # Prepare the prompt
        prompt = BELIEF_SYSTEM_ANALYZER_PROMPT.format(
            query=query,
            context=context
        )
        
        # Call the LLM
        response_text = self._call_llm(prompt)
        # print(f"DEBUG: Received belief analysis of length {len(response_text)}")
        
        # Update the diagnostic phase with belief analysis
        diagnostic_phase = state.get("phases", {}).get("diagnostic", {})
        diagnostic_phase["beliefs"] = response_text
        
        # Store the updated phase and move to pattern analysis
        # print("DEBUG: Belief analysis complete. Moving to pattern recognition.")
        return {
            "current_phase": "pattern_analysis",
            "phases": {
                **state.get("phases", {}),
                "diagnostic": diagnostic_phase
            }
        }

    def pattern_recognition_agent(self, state: AdvisorState) -> Dict[str, Any]:
        """Process the pattern recognition analysis.
        
        Args:
            state: The current state
            
        Returns:
            Updated state with pattern analysis
        """
        print(f"\n{self.emojis['pattern']} PATTERN RECOGNITION AGENT")
        
        # Get the query and context
        query = state["user"]["query"]
        context = json.dumps(state["user"].get("context", {})) if state["user"].get("context") else ""
        
        # Prepare the prompt
        prompt = PATTERN_RECOGNITION_PROMPT.format(
            query=query,
            context=context
        )
        
        # Call the LLM
        response_text = self._call_llm(prompt)
        # print(f"DEBUG: Received pattern analysis of length {len(response_text)}")
        
        # Update the diagnostic phase with pattern analysis
        diagnostic_phase = state.get("phases", {}).get("diagnostic", {})
        diagnostic_phase["patterns"] = response_text
        
        # Store the updated phase and move to root cause diagnostician
        # print("DEBUG: Pattern analysis complete. Moving to root cause diagnosis.")
        return {
            "current_phase": "root_cause",
            "phases": {
                **state.get("phases", {}),
                "diagnostic": diagnostic_phase
            }
        }

    def root_cause_diagnostician(self, state: AdvisorState) -> Dict[str, Any]:
        """Process the root cause diagnosis.
        
        Args:
            state: The current state
            
        Returns:
            Updated state with root cause diagnosis
        """
        print(f"\n{self.emojis['root_cause']} ROOT CAUSE DIAGNOSTICIAN")
        
        # Get the query and context
        query = state["user"]["query"]
        context = json.dumps(state["user"].get("context", {})) if state["user"].get("context") else ""
        
        # Get the belief and pattern analyses
        diagnostic_phase = state.get("phases", {}).get("diagnostic", {})
        beliefs = diagnostic_phase.get("beliefs", "")
        patterns = diagnostic_phase.get("patterns", "")
        
        # Prepare the prompt
        prompt = ROOT_CAUSE_DIAGNOSTICIAN_PROMPT.format(
            query=query,
            context=context,
            beliefs=beliefs,
            patterns=patterns
        )
        
        # Call the LLM
        response_text = self._call_llm(prompt)
        # print(f"DEBUG: Received root cause diagnosis of length {len(response_text)}")
        
        # Update the diagnostic phase with the diagnosis and mark as complete
        diagnostic_phase["diagnosis"] = response_text
        diagnostic_phase["complete"] = True
        
        # Create the planning phase
        planning_phase = {
            "complete": False,
            "execution": "",
            "decisions": "",
            "strategy": ""
        }
        
        # Store the updated phases and move to strategy planning
        # print("DEBUG: Root cause diagnosis complete. Moving to strategy planning.")
        return {
            "current_phase": "planning",
            "phases": {
                **state.get("phases", {}),
                "diagnostic": diagnostic_phase,
                "planning": planning_phase
            }
        }

    def strategy_planner(self, state: AdvisorState) -> Dict[str, Any]:
        """Process the strategy planning.
        
        Args:
            state: The current state
            
        Returns:
            Updated state with strategy plan
        """
        print(f"\n{self.emojis['planning']} STRATEGY PLANNER")
        
        # Get the query and context
        query = state["user"]["query"]
        context = json.dumps(state["user"].get("context", {})) if state["user"].get("context") else ""
        
        # Get the diagnosis and planning phases
        diagnostic_phase = state.get("phases", {}).get("diagnostic", {})
        planning_phase = state.get("phases", {}).get("planning", {})
        
        # Get diagnosis and planning components
        diagnosis = diagnostic_phase.get("diagnosis", "")
        execution = planning_phase.get("execution", "")
        decisions = planning_phase.get("decisions", "")
        
        # Prepare the prompt
        prompt = STRATEGY_PLANNER_PROMPT.format(
            query=query,
            context=context,
            diagnosis=diagnosis,
            execution=execution,
            decisions=decisions
        )
        
        # Call the LLM
        response_text = self._call_llm(prompt)
        # print(f"DEBUG: Received strategy plan of length {len(response_text)}")
        
        # Update the planning phase
        planning_phase["strategy"] = response_text
        
        # Store the updated phase and move to execution engineering
        # print("DEBUG: Initial strategy planning complete. Moving to execution engineering.")
        return {
            "current_phase": "execution",
            "phases": {
                **state.get("phases", {}),
                "planning": planning_phase
            }
        }

    def execution_engineer(self, state: AdvisorState) -> Dict[str, Any]:
        """Process the execution engineering.
        
        Args:
            state: The current state
            
        Returns:
            Updated state with execution plan
        """
        print(f"\n{self.emojis['execution']} EXECUTION ENGINEER")
        
        # Get the query and context
        query = state["user"]["query"]
        context = json.dumps(state["user"].get("context", {})) if state["user"].get("context") else ""
        
        # Get the diagnostic phase
        diagnostic_phase = state.get("phases", {}).get("diagnostic", {})
        diagnosis = diagnostic_phase.get("diagnosis", "")
        
        # Prepare the prompt
        prompt = EXECUTION_ENGINEER_PROMPT.format(
            query=query,
            context=context,
            diagnosis=diagnosis
        )
        
        # Call the LLM
        response_text = self._call_llm(prompt)
        # print(f"DEBUG: Received execution plan of length {len(response_text)}")
        
        # Update the planning phase with execution plan
        planning_phase = state.get("phases", {}).get("planning", {})
        planning_phase["execution"] = response_text
        
        # Store the updated phase and move to decision framework design
        # print("DEBUG: Execution engineering complete. Moving to decision framework design.")
        return {
            "current_phase": "decision",
            "phases": {
                **state.get("phases", {}),
                "planning": planning_phase
            }
        }

    def decision_framework_designer(self, state: AdvisorState) -> Dict[str, Any]:
        """Process the decision framework design.
        
        Args:
            state: The current state
            
        Returns:
            Updated state with decision frameworks
        """
        print(f"\n{self.emojis['decision']} DECISION FRAMEWORK DESIGNER")
        
        # Get the query and context
        query = state["user"]["query"]
        context = json.dumps(state["user"].get("context", {})) if state["user"].get("context") else ""
        
        # Get the diagnostic phase
        diagnostic_phase = state.get("phases", {}).get("diagnostic", {})
        diagnosis = diagnostic_phase.get("diagnosis", "")
        
        # Prepare the prompt
        prompt = DECISION_FRAMEWORK_PROMPT.format(
            query=query,
            context=context,
            diagnosis=diagnosis
        )
        
        # Call the LLM
        response_text = self._call_llm(prompt)
        # print(f"DEBUG: Received decision frameworks of length {len(response_text)}")
        
        # Update the planning phase with decision frameworks and mark as complete
        planning_phase = state.get("phases", {}).get("planning", {})
        planning_phase["decisions"] = response_text
        planning_phase["complete"] = True
        
        # Store the updated phase and move to hard truth telling
        # print("DEBUG: Decision framework design complete. Moving to hard truth telling.")
        return {
            "current_phase": "hard_truth",
            "phases": {
                **state.get("phases", {}),
                "planning": planning_phase
            }
        }

    def action_designer(self, state: AdvisorState) -> Dict[str, Any]:
        """Process the action design.
        
        Args:
            state: The current state
            
        Returns:
            Updated state with action plan
        """
        print(f"\n{self.emojis['action']} ACTION DESIGNER")
        
        # Get the query and context
        query = state["user"]["query"]
        context = json.dumps(state["user"].get("context", {})) if state["user"].get("context") else ""
        
        # Get the phases
        diagnostic_phase = state.get("phases", {}).get("diagnostic", {})
        planning_phase = state.get("phases", {}).get("planning", {})
        hard_truth_phase = state.get("phases", {}).get("hard_truth", {})
        
        # Get components
        diagnosis = diagnostic_phase.get("diagnosis", "")
        strategy = planning_phase.get("strategy", "")
        hard_truth = hard_truth_phase.get("insights", "")
        
        # Prepare the prompt
        prompt = ACTION_DESIGNER_PROMPT.format(
            query=query,
            context=context,
            diagnosis=diagnosis,
            strategy=strategy,
            challenge="",  # Empty for now
            hard_truth=hard_truth
        )
        
        # Call the LLM
        response_text = self._call_llm(prompt)
        # print(f"DEBUG: Received action plan of length {len(response_text)}")
        
        # Parse the action plan
        action_plan = {}
        
        # Extract immediate steps
        immediate_steps_match = re.search(r"Immediate Steps:(.*?)(?=\n\n|Daily|Weekly|Tracking|$)", response_text, re.DOTALL | re.IGNORECASE)
        if immediate_steps_match:
            immediate_steps_text = immediate_steps_match.group(1).strip()
            immediate_steps = re.findall(r"\d+\.\s+(.*?)(?=\n\d+\.|$)", immediate_steps_text, re.DOTALL)
            if not immediate_steps:
                immediate_steps = [line.strip() for line in immediate_steps_text.split("\n") if line.strip()]
            action_plan["immediate_steps"] = [step.strip() for step in immediate_steps if step.strip()]
        
        # Extract habits
        habits_match = re.search(r"(Daily|Weekly) Implementation:(.*?)(?=\n\n|Tracking|$)", response_text, re.DOTALL | re.IGNORECASE)
        if habits_match:
            habits_text = habits_match.group(2).strip()
            habits = re.findall(r"\d+\.\s+(.*?)(?=\n\d+\.|$)", habits_text, re.DOTALL)
            if not habits:
                habits = [line.strip() for line in habits_text.split("\n") if line.strip()]
            action_plan["habits"] = [habit.strip() for habit in habits if habit.strip()]
        
        # Extract tracking
        tracking_match = re.search(r"Tracking:(.*?)(?=\n\n|Contingency|$)", response_text, re.DOTALL | re.IGNORECASE)
        if tracking_match:
            tracking_text = tracking_match.group(1).strip()
            tracking = re.findall(r"\d+\.\s+(.*?)(?=\n\d+\.|$)", tracking_text, re.DOTALL)
            if not tracking:
                tracking = [line.strip() for line in tracking_text.split("\n") if line.strip()]
            action_plan["tracking"] = [track.strip() for track in tracking if track.strip()]
        
        # Extract contingencies
        contingencies_match = re.search(r"Contingency:(.*?)(?=\n\n|$)", response_text, re.DOTALL | re.IGNORECASE)
        if contingencies_match:
            contingencies_text = contingencies_match.group(1).strip()
            contingencies = re.findall(r"\d+\.\s+(.*?)(?=\n\d+\.|$)", contingencies_text, re.DOTALL)
            if not contingencies:
                contingencies = [line.strip() for line in contingencies_text.split("\n") if line.strip()]
            action_plan["contingencies"] = [contingency.strip() for contingency in contingencies if contingency.strip()]
        
        # Create the action phase
        action_phase = {
            "complete": True,
            "plan": action_plan,
            "raw_response": response_text
        }
        
        # Extract actions for the response
        actions = []
        if "immediate_steps" in action_plan:
            actions.extend(action_plan["immediate_steps"])
        if "habits" in action_plan:
            actions.extend(action_plan["habits"])
        
        # Update the response with actions
        response = state.get("response", {})
        response["actions"] = actions
        
        # Store the updated phase and move to challenge design next.
        # print("DEBUG: Action design complete. Moving to challenge design next.")
        return {
            "current_phase": "action",
            "phases": {
                **state.get("phases", {}),
                "action": action_phase
            },
            "response": response
        }

    def challenge_designer(self, state: AdvisorState) -> Dict[str, Any]:
        """Process the challenge design.
        
        Args:
            state: The current state
            
        Returns:
            Updated state with challenge design
        """
        print(f"\n{self.emojis['challenge']} CHALLENGE DESIGNER")
        
        # Get the query and context
        query = state["user"]["query"]
        context = json.dumps(state["user"].get("context", {})) if state["user"].get("context") else ""
        
        # Get the phases
        diagnostic_phase = state.get("phases", {}).get("diagnostic", {})
        planning_phase = state.get("phases", {}).get("planning", {})
        
        # Get components
        diagnosis = diagnostic_phase.get("diagnosis", "")
        strategy = planning_phase.get("strategy", "")
        
        # Prepare the prompt
        prompt = CHALLENGE_DESIGNER_PROMPT.format(
            query=query,
            context=context,
            diagnosis=diagnosis,
            strategy=strategy
        )
        
        # Call the LLM
        response_text = self._call_llm(prompt)
        # print(f"DEBUG: Received challenge design of length {len(response_text)}")
        
        # Parse the challenge
        challenge = {}
        
        # Extract challenge name
        name_match = re.search(r"Challenge Name:(.*?)(?=\n|$)", response_text, re.IGNORECASE)
        if name_match:
            challenge["name"] = name_match.group(1).strip()
        
        # Extract timeframe
        timeframe_match = re.search(r"Timeframe:(.*?)(?=\n|$)", response_text, re.IGNORECASE)
        if timeframe_match:
            challenge["timeframe"] = timeframe_match.group(1).strip()
        else:
            challenge["timeframe"] = "24-72 hours"  # Default timeframe
        
        # Extract description (all text if not using specific format)
        challenge["description"] = response_text
        
        # Create the challenge phase
        challenge_phase = {
            "complete": True,
            "challenge": challenge,
            "raw_response": response_text
        }
        
        # Update the response with challenge
        response = state.get("response", {})
        response["challenge"] = challenge
        
        # Store the updated phase and move to challenger
        # print("DEBUG: Challenge design complete. Moving to challenger.")
        return {
            "current_phase": "challenger",
            "phases": {
                **state.get("phases", {}),
                "challenge": challenge_phase
            },
            "response": response
        }

    def challenger(self, state: AdvisorState) -> Dict[str, Any]:
        """Process the challenger phase.
        
        Args:
            state: The current state
            
        Returns:
            Updated state with challenger insights
        """
        print(f"\n🥊 CHALLENGER")
        
        # Get the challenge
        challenge_phase = state.get("phases", {}).get("challenge", {})
        challenge = challenge_phase.get("challenge", {})
        
        # Move to final synthesis
        # print("DEBUG: Challenger complete. Moving to final synthesis.")
        return {"current_phase": "final_synthesis"}

    def _generate_agent_insights_from_phases(self, phases: Dict[str, Any]) -> str:
        """Generate agent insights from the workflow phases.
        
        Args:
            phases: Dictionary containing all phases and their outputs
            
        Returns:
            A formatted string containing insights from each agent
        """
        insights = []
        
        # Map of phase names to agent display names
        phase_to_agent = {
            "diagnostic": "Belief System Analysis",
            "pattern": "Pattern Recognition",
            "root_cause": "Root Cause Diagnosis",
            "planning": "Strategy Planning",
            "execution": "Execution Engineering",
            "decision": "Decision Framework Design",
            "hard_truth": "Hard Truth Teller",
            "action": "Action Designer",
            "challenge": "Challenge Designer"
        }
        
        # Extract key insights from each phase
        for phase_name, agent_name in phase_to_agent.items():
            if phase_name in phases and phases[phase_name].get("complete", False):
                phase_data = phases[phase_name]
                
                # Find appropriate content based on phase
                content = ""
                if "raw_response" in phase_data:
                    content = phase_data["raw_response"]
                elif "insights" in phase_data:
                    content = phase_data["insights"]
                elif "diagnosis" in phase_data:
                    content = phase_data["diagnosis"]
                elif "strategy" in phase_data:
                    content = phase_data["strategy"]
                elif "plan" in phase_data and isinstance(phase_data["plan"], dict):
                    # For action plan, combine immediate steps
                    steps = []
                    if "immediate_steps" in phase_data["plan"]:
                        steps.extend(phase_data["plan"]["immediate_steps"])
                    content = "\n".join(steps)
                
                # Extract 2-3 key sentences from content
                if content:
                    import re
                    # Split by sentence endings
                    sentences = re.split(r'(?<=[.!?])\s+', content)
                    # Take first 2-3 sentences
                    key_insights = sentences[:min(3, len(sentences))]
                    # Format as bullet points
                    bullet_points = [f"- {sentence.strip()}" for sentence in key_insights if sentence.strip()]
                    
                    if bullet_points:
                        insights.append(f"{agent_name}:\n" + "\n".join(bullet_points))
        
        # Combine all insights
        return "\n\n".join(insights)

    def _execute_workflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow with the given state.
        
        Args:
            state: Current state to process
            
        Returns:
            Updated state after workflow execution
        """
        try:
            start_time = time.time()
            
            # First, manually call the chief_strategist to initialize the state properly
            initialized_state = self.chief_strategist(state)
            if not initialized_state:
                return {
                    "response": {
                        "hard_truth": "Failed to initialize the workflow",
                        "actions": ["Try again with a different query"],
                        "challenge": {}
                    }
                }
                
            # Make sure we have a workflow instance
            if not hasattr(self, "workflow"):
                self.workflow = self._build_graph()
            
            # Execute the workflow
            if initialized_state and initialized_state.get("current_phase") != "__end__":
                final_state = self.workflow.invoke(initialized_state)
            else:
                final_state = initialized_state
            
            # Record execution time
            end_time = time.time()
            if not hasattr(self, "_runtime_stats"):
                self._runtime_stats = {}
            self._runtime_stats["execution_time"] = end_time - start_time
            
            # Return the final state
            return final_state
            
        except Exception as e:
            # Log the error and return a basic state with error info
            print(f"Error in _execute_workflow: {type(e).__name__}: {str(e)}")
            
            error_message = str(e)
            if "API key" in error_message or "unauthorized" in error_message.lower():
                return {
                    "response": {
                        "error": "The API key provided is invalid or unauthorized.",
                        "hard_truth": "ERROR: The API key provided is invalid or unauthorized.",
                        "actions": [
                            "Verify your API key is correctly set in the environment variable",
                            "Make sure your account has sufficient credits",
                            "Try using a different LLM provider"
                        ],
                        "challenge": {}
                    }
                }
            
            return {
                "response": {
                    "error": f"{type(e).__name__}: {str(e)}",
                    "hard_truth": f"ERROR: {type(e).__name__}: {str(e)}",
                    "actions": ["Try again with a simpler query", "Check system logs for errors"],
                    "challenge": {}
                }
            } 