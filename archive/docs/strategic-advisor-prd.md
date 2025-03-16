# Strategic Advisor System: Product Requirements Document

## Document Version
Version 1.0 | March 14, 2025

## 1. Introduction

### 1.1 Purpose
This document provides comprehensive requirements and specifications for implementing a CLI-based Strategic Advisor system built on LangGraph. Two distinct architectural approaches will be detailed: 
1. Pure Custom approach - A phase-based, deterministic workflow
2. Pure Swarm approach - A dynamic, agent-driven collaboration system

### 1.2 Target Use Case
The system serves as a personal strategic advisor that provides:
- Brutally honest feedback
- Identification of critical gaps
- Specific action plans
- Mental models and frameworks
- Direct challenges to push beyond comfort zones

### 1.3 Core System Prompt
The central prompt that drives system behavior:

```
Act as my personal strategic advisor with the following context:
- You have an IQ of 180
- You're brutally honest and direct
- You've built multiple billion-dollar companies
- You have deep expertise in psychology, strategy, and execution
- You care about my success but won't tolerate excuses
- You focus on leverage points that create maximum impact
- You think in systems and root causes, not surface-level fixes

Your mission is to:
- Identify the critical gaps holding me back
- Design specific action plans to close those gaps
- Push me beyond my comfort zone
- Call out my blind spots and rationalizations
- Force me to think bigger and bolder
- Hold me accountable to high standards
- Provide specific frameworks and mental models

For each response:
- Start with the hard truth I need to hear
- Follow with specific, actionable steps
- End with a direct challenge or assignment
```

## 2. System Architecture Overview

### 2.1 Pure Custom Architecture

![Pure Custom Architecture](https://placeholder-diagram-url.com/custom-architecture)

The Pure Custom approach implements a deterministic, phase-based workflow:

1. **Chief Strategist (Central Coordinator)**
   - Controls overall flow
   - Ensures consistent tone and style
   - Makes phase transition decisions

2. **Phase Structure**
   - **Diagnostic Phase**: Root cause analysis through belief system and pattern analysis
   - **Planning Phase**: Strategy development through execution and decision frameworks 
   - **Challenge Phase**: Creating specific growth assignments

3. **Core Properties**
   - Predictable flow through phases
   - Clear responsibility boundaries
   - Centralized control and synthesis

### 2.2 Pure Swarm Architecture

![Pure Swarm Architecture](https://placeholder-diagram-url.com/swarm-architecture)

The Pure Swarm approach implements a dynamic, agent-driven system:

1. **Autonomous Agents**
   - Each agent has specialized expertise
   - Agents determine when to hand off to other agents
   - All agents maintain the core strategic advisor voice

2. **Dynamic Handoff Structure**
   - Agents pass control based on their assessment of needs
   - System tracks which agent is active across sessions
   - Continuous conversation flow between specializations

3. **Core Properties**
   - Emergent analysis flow
   - Deep cross-domain collaboration
   - Flexible, problem-driven progression

## 3. Pure Custom Architecture: Detailed Specifications

### 3.1 Component Definitions

#### 3.1.1 Chief Strategist

**Purpose**: Central coordinator and primary voice of the system.

**Input**: User query, phase outputs
**Output**: Final response, phase routing decisions

**Prompt**:
```
You are the chief strategist with an IQ of 180, brutal honesty, and deep expertise in business, psychology, and execution. You've built multiple billion-dollar companies.

Your responsibilities:
1. Receive and analyze the user's query
2. Direct the diagnostic phase by activating the Root Cause Diagnostician
3. Direct the planning phase by activating the Strategy Planner
4. Direct the challenge design phase by activating the Challenge Designer
5. Integrate insights from all phases into a comprehensive strategy
6. Deliver the final guidance with hard truths, actionable steps, and a challenge

You maintain overall strategic direction and ensure all phases contribute to a cohesive solution that is:
- Brutally honest and direct
- Focused on leverage points for maximum impact
- Based on systems thinking and root causes
- Designed to push beyond comfort zones
- Specific and actionable

Always format your final response with:
1. The hard truth the user needs to hear (direct and unfiltered)
2. Specific, actionable steps to address the situation
3. A direct challenge or assignment that pushes growth
```

#### 3.1.2 Root Cause Diagnostician

**Purpose**: Oversees the diagnostic phase, coordinating belief and pattern analysis.

**Input**: User query + context
**Output**: Comprehensive diagnosis

**Prompt**:
```
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
```

#### 3.1.3 Belief System Analyzer

**Purpose**: Identifies limiting beliefs and mental models.

**Input**: User context from Root Cause Diagnostician
**Output**: Belief analysis

**Prompt**:
```
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
```

#### 3.1.4 Pattern Recognition Agent

**Purpose**: Identifies behavioral and situational patterns.

**Input**: User context from Root Cause Diagnostician
**Output**: Pattern analysis

**Prompt**:
```
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
```

#### 3.1.5 Strategy Planner

**Purpose**: Oversees the planning phase, coordinating execution and decision planning.

**Input**: Diagnostic insights + user context
**Output**: Comprehensive strategy

**Prompt**:
```
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
```

#### 3.1.6 Execution Engineer

**Purpose**: Creates detailed implementation protocols.

**Input**: Strategy context from Strategy Planner
**Output**: Execution analysis and plan

**Prompt**:
```
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
```

#### 3.1.7 Decision Framework Designer

**Purpose**: Creates decision models and frameworks.

**Input**: Strategy context from Strategy Planner
**Output**: Decision framework analysis and plan

**Prompt**:
```
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
```

#### 3.1.8 Challenge Designer

**Purpose**: Creates high-impact growth challenges.

**Input**: Strategy and diagnostic context
**Output**: Specific growth challenge

**Prompt**:
```
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
```

### 3.2 State Management

The system will use a structured state object to maintain context between phases:

```python
state = {
    "user": {
        "query": str,            # The original user query
        "context": dict,         # Accumulated user context
        "history": list          # Previous interactions
    },
    "phases": {
        "diagnostic": {
            "complete": bool,    # Indicates phase completion
            "beliefs": list,     # Identified limiting beliefs
            "patterns": list,    # Identified behavioral patterns
            "diagnosis": str     # Overall diagnostic summary
        },
        "planning": {
            "complete": bool,    # Indicates phase completion
            "execution": dict,   # Execution plan details
            "decisions": dict,   # Decision frameworks
            "strategy": str      # Overall strategy summary
        },
        "challenge": {
            "complete": bool,    # Indicates phase completion
            "challenge": dict    # The specific challenge details
        }
    },
    "current_phase": str,        # Current active phase
    "response": {
        "hard_truth": str,       # The hard truth component
        "actions": list,         # The actionable steps
        "challenge": dict        # The final challenge
    }
}
```

### 3.3 Implementation Code

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Optional
from typing_extensions import Annotated
import json

# Define state type
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

# Initialize model
model = ChatOpenAI(model="gpt-4-turbo")

# Define node functions
def chief_strategist(state: AdvisorState) -> Dict[str, Any]:
    # Implementation logic for Chief Strategist
    # Analyze query and initialize phases OR synthesize final response
    
    if state["current_phase"] == "init":
        # Initial analysis
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Chief Strategist prompt here"),
            ("human", "{query}")
        ])
        
        chain = prompt | model | StrOutputParser()
        response = chain.invoke({"query": state["user"]["query"]})
        
        # Parse initial analysis to determine next phase
        # (Implementation detail: parse response to extract insights)
        
        return {
            "current_phase": "diagnostic",
            "user": {
                **state["user"],
                "context": {
                    "initial_analysis": response
                }
            }
        }
    
    elif state["current_phase"] == "complete":
        # Final synthesis
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Final synthesis prompt here"),
            ("human", json.dumps({
                "diagnostic": state["phases"]["diagnostic"],
                "planning": state["phases"]["planning"],
                "challenge": state["phases"]["challenge"]
            }))
        ])
        
        chain = prompt | model | StrOutputParser()
        response = chain.invoke({})
        
        # Parse final response into required format
        # (Implementation detail: extract hard truth, actions, and challenge)
        
        hard_truth = "Extracted hard truth here"
        actions = ["Action 1", "Action 2"]
        challenge = {"name": "Challenge name", "details": "Challenge details"}
        
        return {
            "response": {
                "hard_truth": hard_truth,
                "actions": actions,
                "challenge": challenge
            }
        }

def root_cause_diagnostician(state: AdvisorState) -> Dict[str, Any]:
    # Implementation logic for Root Cause Diagnostician
    # Coordinate belief and pattern analysis
    
    # If beliefs and patterns not analyzed yet, send to analyzers
    if not state["phases"]["diagnostic"].get("beliefs"):
        return {"current_phase": "belief_analysis"}
    
    if not state["phases"]["diagnostic"].get("patterns"):
        return {"current_phase": "pattern_analysis"}
    
    # If both analyses complete, synthesize diagnosis
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Diagnosis synthesis prompt here"),
        ("human", json.dumps({
            "beliefs": state["phases"]["diagnostic"]["beliefs"],
            "patterns": state["phases"]["diagnostic"]["patterns"],
            "query": state["user"]["query"],
            "context": state["user"]["context"]
        }))
    ])
    
    chain = prompt | model | StrOutputParser()
    diagnosis = chain.invoke({})
    
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
    # Implementation logic for Belief System Analyzer
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Belief analysis prompt here"),
        ("human", json.dumps({
            "query": state["user"]["query"],
            "context": state["user"]["context"]
        }))
    ])
    
    chain = prompt | model | StrOutputParser()
    analysis = chain.invoke({})
    
    # Parse belief analysis
    # (Implementation detail: extract structured beliefs data)
    beliefs = [{"belief": "Example belief", "upgrade": "Upgraded belief"}]
    
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
    # Implementation logic for Pattern Recognition Agent
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Pattern analysis prompt here"),
        ("human", json.dumps({
            "query": state["user"]["query"],
            "context": state["user"]["context"]
        }))
    ])
    
    chain = prompt | model | StrOutputParser()
    analysis = chain.invoke({})
    
    # Parse pattern analysis
    # (Implementation detail: extract structured patterns data)
    patterns = [{"pattern": "Example pattern", "intervention": "Pattern intervention"}]
    
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

# Define remaining node functions following the same pattern:
# - strategy_planner
# - execution_engineer
# - decision_framework_designer
# - challenge_designer

# Build the graph
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
    lambda state: state["current_phase"]
)

workflow.add_conditional_edges(
    "root_cause_diagnostician",
    lambda state: state["current_phase"]
)

workflow.add_conditional_edges(
    "strategy_planner",
    lambda state: state["current_phase"]
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
app = workflow.compile()

# Initialize state
initial_state = {
    "user": {
        "query": "User query here",
        "context": {},
        "history": []
    },
    "phases": {
        "diagnostic": {
            "complete": False,
            "beliefs": [],
            "patterns": [],
            "diagnosis": ""
        },
        "planning": {
            "complete": False,
            "execution": {},
            "decisions": {},
            "strategy": ""
        },
        "challenge": {
            "complete": False,
            "challenge": {}
        }
    },
    "current_phase": "init",
    "response": {
        "hard_truth": "",
        "actions": [],
        "challenge": {}
    }
}

# Execute the graph
final_state = app.invoke(initial_state)

# Extract final response
response = final_state["response"]
```

### 3.4 CLI Integration

Create a command-line interface that accepts user queries and formats responses:

```python
import click
import json
from pathlib import Path
from typing import Optional

@click.command()
@click.argument("query", required=True)
@click.option("--history", "-h", help="Path to conversation history file")
def strategic_planner(query: str, history: Optional[str] = None):
    """Strategic Planner CLI Tool"""
    
    # Load history if available
    user_history = []
    if history and Path(history).exists():
        with open(history, "r") as f:
            user_history = json.load(f)
    
    # Initialize state
    state = {
        "user": {
            "query": query,
            "context": {},
            "history": user_history
        },
        "phases": {
            "diagnostic": {
                "complete": False,
                "beliefs": [],
                "patterns": [],
                "diagnosis": ""
            },
            "planning": {
                "complete": False,
                "execution": {},
                "decisions": {},
                "strategy": ""
            },
            "challenge": {
                "complete": False,
                "challenge": {}
            }
        },
        "current_phase": "init",
        "response": {
            "hard_truth": "",
            "actions": [],
            "challenge": {}
        }
    }
    
    # Execute the graph
    final_state = app.invoke(state)
    
    # Format and print response
    response = final_state["response"]
    
    click.echo(click.style("\n🔴 THE HARD TRUTH:", fg="red", bold=True))
    click.echo(response["hard_truth"])
    
    click.echo(click.style("\n🔵 ACTIONABLE STEPS:", fg="blue", bold=True))
    for i, action in enumerate(response["actions"], 1):
        click.echo(f"{i}. {action}")
    
    click.echo(click.style("\n🟢 YOUR CHALLENGE:", fg="green", bold=True))
    click.echo(f"** {response['challenge']['name']} **")
    click.echo(response["challenge"]["details"])
    
    # Save updated history
    if history:
        updated_history = user_history + [{
            "query": query,
            "response": response
        }]
        with open(history or "strategic_history.json", "w") as f:
            json.dump(updated_history, f, indent=2)

if __name__ == "__main__":
    strategic_planner()
```

## 4. Pure Swarm Architecture: Detailed Specifications

### 4.1 Component Definitions

#### 4.1.1 Strategic Advisor (Primary Agent)

**Purpose**: Core agent that embodies the strategic advisor persona and coordinates with other specialist agents.

**Input**: User query
**Output**: Strategic advice and handoffs to specialists

**Prompt**:
```
You are a strategic advisor with an IQ of 180, brutal honesty, and deep expertise in psychology, strategy, and execution. You've built multiple billion-dollar companies.

When analyzing user queries:
1. Start with a high-level assessment of their situation
2. If you detect limiting beliefs, hand off to the Belief System Analyzer
3. If you detect execution challenges, hand off to the Execution Engineer
4. If you detect decision dilemmas, hand off to the Decision Framer
5. If you detect behavioral patterns, hand off to the Pattern Recognizer
6. When ready for a challenge, hand off to the Challenge Designer

When other agents hand back to you, integrate their insights and continue the analysis.

For your final response:
- Start with the hard truth the user needs to hear
- Follow with specific, actionable steps
- End with a direct challenge or assignment

Always maintain your direct, challenging tone and focus on hard truths.
```

#### 4.1.2 Belief System Analyzer

**Purpose**: Specialist in identifying limiting beliefs and mental models.

**Input**: User context from Strategic Advisor
**Output**: Belief analysis and handoffs

**Prompt**:
```
You are a belief system analysis specialist within a strategic advisory team. Your role is to:

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

When you've completed your analysis, you can:
1. Hand back to the Strategic Advisor
2. Hand off to the Pattern Recognizer if you detect behavioral patterns
3. Hand off to the Execution Engineer if beliefs are creating execution barriers
4. Hand off to the Decision Framer if beliefs are affecting decision quality
```

#### 4.1.3 Pattern Recognition Agent

**Purpose**: Specialist in identifying behavioral and situational patterns.

**Input**: User context from any agent
**Output**: Pattern analysis and handoffs

**Prompt**:
```
You are a behavioral pattern recognition specialist within a strategic advisory team. Your role is to:

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

When you've completed your analysis, you can:
1. Hand back to the Strategic Advisor
2. Hand off to the Belief System Analyzer if patterns suggest underlying beliefs
3. Hand off to the Execution Engineer if patterns affect implementation
4. Hand off to the Decision Framer if patterns affect decision quality
5. Hand off to the Challenge Designer if you see a clear challenge opportunity
```

#### 4.1.4 Execution Engineer

**Purpose**: Specialist in implementation and execution planning.

**Input**: User context from any agent
**Output**: Execution analysis and handoffs

**Prompt**:
```
You are an execution engineering specialist within a strategic advisory team. Your role is to:

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

When you've completed your analysis, you can:
1. Hand back to the Strategic Advisor
2. Hand off to the Belief System Analyzer if execution barriers suggest limiting beliefs
3. Hand off to the Pattern Recognizer if execution issues reveal behavioral patterns
4. Hand off to the Decision Framer if implementation requires decision frameworks
5. Hand off to the Challenge Designer to create execution-focused challenges
```

#### 4.1.5 Decision Framer

**Purpose**: Specialist in decision frameworks and models.

**Input**: User context from any agent
**Output**: Decision framework analysis and handoffs

**Prompt**:
```
You are a decision framework specialist within a strategic advisory team. Your role is to:

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

When you've completed your analysis, you can:
1. Hand back to the Strategic Advisor
2. Hand off to the Belief System Analyzer if decision issues suggest limiting beliefs
3. Hand off to the Pattern Recognizer if decision challenges reveal behavioral patterns
4. Hand off to the Execution Engineer to implement decision protocols
5. Hand off to the Challenge Designer to create decision practice challenges
```

#### 4.1.6 Challenge Designer

**Purpose**: Specialist in creating growth challenges.

**Input**: User context from any agent
**Output**: Specific growth challenge and handoffs

**Prompt**:
```
You are a challenge design specialist within a strategic advisory team. Your role is to:

- Design high-impact challenges that push people beyond their comfort zones
- Create concrete, measurable assignments with clear timeframes
- Develop challenges that target specific growth edges
- Structure challenges to generate immediate feedback on effectiveness
- Design appropriate difficulty levels that stretch without breaking

Follow this format:
1. Challenge name (short, memorable)
2. Specific actions required
3. Timeframe for completion
4. Documentation/evidence requirements
5. Expected resistance points and how to overcome them

Design challenges that are uncomfortable but achievable. The right challenge
should create a feeling of "I don't want to do this but I know I should."

When you've completed your challenge design, you can:
1. Hand back to the Strategic Advisor for final delivery
2. Hand off to the Execution Engineer if implementation details need refinement
3. Hand off to the Belief System Analyzer if the challenge needs to target specific beliefs
4. Hand off to the Pattern Recognizer if the challenge should disrupt specific patterns
```

### 4.2 Handoff Tool Definition

Create a custom handoff tool to enable agent-to-agent transfers:

```python
from typing import Annotated
from langchain_core.tools import tool, BaseTool, InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from langgraph.prebuilt import InjectedState

def create_strategic_handoff_tool(*, agent_name: str, expertise: str):
    """Create a handoff tool for the strategic advisory system"""
    
    tool_name = f"consult_{agent_name.lower()}"
    description = f"Transfer to {agent_name} who specializes in {expertise}"
    
    @tool(name=tool_name, description=description)
    def handoff_to_agent(
        task_description: Annotated[str, "Detailed description of what analysis is needed and why"],
        state: Annotated[dict, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ):
        tool_message = ToolMessage(
            content=f"Transferring to {agent_name} for {expertise} analysis",
            name=tool_name,
            tool_call_id=tool_call_id,
        )
        
        last_message = state["messages"][-1]
        return Command(
            goto=agent_name,
            graph=Command.PARENT,
            update={
                "messages": [last_message, tool_message],
                "active_agent": agent_name,
                "task_description": task_description,
                "requesting_agent": state.get("active_agent", "StrategicAdvisor")
            },
        )

    return handoff_to_agent
```

### 4.3 Implementation Code

```python
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_swarm
from typing import List, Dict, Any

# Initialize LLM
model = ChatOpenAI(model="gpt-4-turbo")

# Create handoff tools for each agent
def create_agent_tools(agent_name: str) -> List[BaseTool]:
    """Create the set of tools for an agent, including handoff tools to all other agents"""
    
    tools = []
    
    # Add handoff tools for all agents except self
    agent_specs = {
        "StrategicAdvisor": "overall strategic analysis and synthesis",
        "BeliefSystemAnalyzer": "identifying limiting beliefs and mental models",
        "PatternRecognizer": "detecting behavioral and situational patterns",
        "ExecutionEngineer": "implementation planning and execution strategy",
        "DecisionFramer": "decision frameworks and bias prevention",
        "ChallengeDesigner": "creating growth challenges and assignments"
    }
    
    for target_agent, expertise in agent_specs.items():
        if target_agent != agent_name:
            tools.append(create_strategic_handoff_tool(
                agent_name=target_agent,
                expertise=expertise
            ))
    
    # Add domain-specific tools
    # (Implementation detail: add any specialized tools for specific agents)
    
    return tools

# Create agents
strategic_advisor = create_react_agent(
    model,
    create_agent_tools("StrategicAdvisor"),
    prompt="Strategic Advisor prompt here",
    name="StrategicAdvisor",
)

belief_system_analyzer = create_react_agent(
    model,
    create_agent_tools("BeliefSystemAnalyzer"),
    prompt="Belief System Analyzer prompt here",
    name="BeliefSystemAnalyzer",
)

pattern_recognizer = create_react_agent(
    model,
    create_agent_tools("PatternRecognizer"),
    prompt="Pattern Recognizer prompt here",
    name="PatternRecognizer",
)

execution_engineer = create_react_agent(
    model,
    create_agent_tools("ExecutionEngineer"),
    prompt="Execution Engineer prompt here",
    name="ExecutionEngineer",
)

decision_framer = create_react_agent(
    model,
    create_agent_tools("DecisionFramer"),
    prompt="Decision Framer prompt here",
    name="DecisionFramer",
)

challenge_designer = create_react_agent(
    model,
    create_agent_tools("ChallengeDesigner"),
    prompt="Challenge Designer prompt here",
    name="ChallengeDesigner",
)

# Create the swarm
checkpointer = InMemorySaver()  # For maintaining state across interactions

workflow = create_swarm(
    [
        strategic_advisor,
        belief_system_analyzer,
        pattern_recognizer,
        execution_engineer,
        decision_framer,
        challenge_designer
    ],
    default_active_agent="StrategicAdvisor"
)

# Compile with checkpointer for state persistence
app = workflow.compile(checkpointer=checkpointer)
```

### 4.4 CLI Integration

Create a command-line interface for the swarm architecture:

```python
import click
import json
import uuid
from pathlib import Path
from typing import Optional

@click.command()
@click.argument("query", required=True)
@click.option("--thread", "-t", help="Thread ID for conversation continuity")
@click.option("--history", "-h", help="Path to conversation history file")
def strategic_planner_swarm(query: str, thread: Optional[str] = None, history: Optional[str] = None):
    """Strategic Planner CLI Tool (Swarm Architecture)"""
    
    # Generate or use thread ID for conversation continuity
    thread_id = thread or str(uuid.uuid4())
    
    # Load history if available
    message_history = []
    if history and Path(history).exists():
        with open(history, "r") as f:
            saved_history = json.load(f)
            if thread_id in saved_history:
                message_history = saved_history[thread_id]
    
    # Prepare input
    if not message_history:
        # First message in thread
        messages = [{"role": "user", "content": query}]
    else:
        # Add to existing thread
        messages = message_history + [{"role": "user", "content": query}]
    
    # Configure thread settings
    config = {"configurable": {"thread_id": thread_id}}
    
    # Invoke the swarm
    response = app.invoke({"messages": messages}, config)
    
    # Extract and display the response
    assistant_message = next(
        (msg for msg in response["messages"] if msg["role"] == "assistant"), 
        {"content": "No response generated"}
    )
    
    click.echo(assistant_message["content"])
    
    # Save updated history
    if history:
        saved_history = {}
        if Path(history).exists():
            with open(history, "r") as f:
                saved_history = json.load(f)
        
        saved_history[thread_id] = response["messages"]
        
        with open(history or "swarm_history.json", "w") as f:
            json.dump(saved_history, f, indent=2)
    
    # Display thread ID for future reference
    click.echo(f"\nThread ID: {thread_id}")

if __name__ == "__main__":
    strategic_planner_swarm()
```

## 5. Testing Requirements

### 5.1 Unit Tests

Implement unit tests for each component:

```python
# Example unit test for Belief System Analyzer
def test_belief_system_analyzer():
    analyzer = belief_system_analyzer  # From implementation
    
    test_message = {
        "role": "user", 
        "content": "I want to start a business but I'm afraid of failure"
    }
    
    result = analyzer.invoke({"messages": [test_message]})
    
    # Assertions
    assert "limiting beliefs" in result["messages"][-1]["content"].lower()
    assert "fear of failure" in result["messages"][-1]["content"].lower()
```

### 5.2 Integration Tests

Test end-to-end flows with predefined test cases:

```python
# Example integration test for custom architecture
def test_custom_end_to_end():
    test_query = "I want to start a business but I'm afraid of failure"
    
    initial_state = {
        "user": {
            "query": test_query,
            "context": {},
            "history": []
        },
        "phases": {
            "diagnostic": {
                "complete": False,
                "beliefs": [],
                "patterns": [],
                "diagnosis": ""
            },
            "planning": {
                "complete": False,
                "execution": {},
                "decisions": {},
                "strategy": ""
            },
            "challenge": {
                "complete": False,
                "challenge": {}
            }
        },
        "current_phase": "init",
        "response": {
            "hard_truth": "",
            "actions": [],
            "challenge": {}
        }
    }
    
    final_state = app.invoke(initial_state)
    
    # Assertions
    assert final_state["current_phase"] == "complete"
    assert final_state["response"]["hard_truth"] != ""
    assert len(final_state["response"]["actions"]) > 0
    assert final_state["response"]["challenge"] != {}
```

### 5.3 Test Cases

Develop comprehensive test suite covering:

1. **Basic Query Handling**
   - Simple time management queries
   - Career decision queries
   - Productivity improvement queries

2. **Complex Scenarios**
   - Multi-faceted business challenges
   - Personal/professional balance issues
   - Long-term strategic planning

3. **Edge Cases**
   - Very short queries
   - Vague or ambiguous requests
   - Multiple questions in one query

4. **Conversational Context**
   - Follow-up questions
   - Reference to previous challenges
   - Progress updates on assignments

## 6. Performance Considerations

### 6.1 Caching Strategy

Implement caching to improve response times:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_llm_call(prompt: str, model_name: str) -> str:
    """Cache LLM responses for common prompts"""
    # Implementation details
```

### 6.2 Optimization Guidelines

1. **Parallel Processing**
   - In the custom architecture, run belief and pattern analysis in parallel
   - In the swarm architecture, optimize handoff decisions

2. **Response Time Targets**
   - Target response time: < 15 seconds for initial analysis
   - Target response time: < 5 seconds for follow-up interactions

3. **Memory Management**
   - Implement efficient state serialization
   - Trim message history after certain length
   - Use compression for long-term storage

## 7. Deployment Guidelines

### 7.1 Environment Setup

Required environment variables:

```
OPENAI_API_KEY=your_api_key
LANGCHAIN_TRACING_V2=true  # Optional for debugging
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com  # Optional for tracing
LANGCHAIN_API_KEY=your_langchain_api_key  # Optional for tracing
```

### 7.2 Packaging Instructions

Create a packaged CLI tool:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Package as CLI tool
pip install -e .

# Test installation
strategic-planner "How can I improve my time management?"
```

### 7.3 Requirements.txt

```
langchain>=0.1.0
langchain-openai>=0.0.5
langgraph>=0.0.15
langgraph-swarm>=0.0.5  # For swarm architecture only
click>=8.1.7
pydantic>=2.5.0
```

### 7.4 Package Setup

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="strategic-planner",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.0",
        "langchain-openai>=0.0.5",
        "langgraph>=0.0.15",
        "langgraph-swarm>=0.0.5",
        "click>=8.1.7",
        "pydantic>=2.5.0",
    ],
    entry_points={
        "console_scripts": [
            "strategic-planner=strategic_planner.cli:strategic_planner",
            "strategic-planner-swarm=strategic_planner.cli:strategic_planner_swarm",
        ],
    },
)
```

## 8. Conclusion

### 8.1 Architecture Comparison

| Aspect | Pure Custom | Pure Swarm |
|--------|-------------|------------|
| Structure | Phase-based, deterministic | Dynamic, agent-driven |
| Control | Centralized through Chief Strategist | Distributed across agents |
| Flexibility | Fixed workflow with clear phases | Emergent workflow based on agent decisions |
| Implementation | More code but predictable behavior | Less code but potentially less predictable |
| Maintenance | Clear separation of concerns | More interdependent components |
| Output Format | Highly consistent | May vary based on active agent |
| Best For | Predictable strategic advisory workflow | Complex, multi-faceted challenges requiring flexible analysis |

### 8.2 Implementation Recommendation

For initial implementation, start with the Pure Custom architecture to establish baseline functionality and output consistency. Once this is stable, experiment with the Pure Swarm architecture to assess potential benefits in real-world usage.

### 8.3 Future Enhancements

Consider these enhancements after initial implementation:

1. **Hybrid Architecture**: Combine the structured phases of custom architecture with dynamic agent interactions within phases

2. **Specialized Domain Extensions**: Create domain-specific extensions for business strategy, personal development, etc.

3. **Visualization Tools**: Add visualization capabilities for belief systems, patterns, etc.

4. **Progress Tracking**: Implement a tracking system for challenges and assignments

5. **User Feedback Loop**: Add explicit feedback mechanisms to improve future recommendations
