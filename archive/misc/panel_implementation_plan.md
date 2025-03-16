# Multi-Agent Advisory Planner: Missing Panels Implementation Plan

This document outlines the plan for implementing the seven missing panels in the Multi-Agent Advisory Planner system.

## Current Status

The system currently has three panels implemented:
1. Cognitive Diversity Panel
2. Decision Intelligence Framework
3. Future Scenarios Planning System

The following seven panels need to be implemented:
1. Personal Development Council
2. Stakeholder Impact Advisory Board
3. Constraint Analysis Panel
4. Temporal Perspective Panel
5. Contrarian Challenge System
6. Implementation Energy Panel
7. Product Development Panel

## Implementation Approach

Each panel will be implemented following the same pattern as the existing panels:

1. Create a new Python file in the `iterative_research_tool/panels/` directory
2. Implement a panel class that inherits from `BasePanel`
3. Define the agent structure and prompts based on the specifications
4. Update the `StrategicPlanner._initialize_panel()` method to include the new panel
5. Update the CLI to include the new panel as an option

## Panel Implementation Details

### 1. Personal Development Council

**File**: `iterative_research_tool/panels/personal_development.py`

**Panel Structure**:
```
User Query → [Growth Gap Analyzer] →
  → [Habit Design Engineer] →
  → [Knowledge Acquisition Strategist] →
  → [Social Capital Developer] →
  → [Identity Evolution Guide] →
  → [Inner Critic Moderator] →
  → [Development Plan Synthesizer]
```

**Key Agents**:
- Growth Gap Analyzer: Identifies critical gaps between current state and desired outcomes
- Habit Design Engineer: Designs minimal viable habits to address development gaps
- Knowledge Acquisition Strategist: Creates learning plans and knowledge acquisition strategies
- Social Capital Developer: Focuses on building relationships and networks
- Identity Evolution Guide: Helps with identity transitions and personal growth
- Inner Critic Moderator: Manages self-criticism and promotes balanced self-assessment
- Development Plan Synthesizer: Integrates all inputs into a coherent development plan

### 2. Stakeholder Impact Advisory Board

**File**: `iterative_research_tool/panels/stakeholder_impact.py`

**Panel Structure**:
```
User Query → [Stakeholder Mapper] →
  → [Customer/Client Agent] →
  → [Team/Employee Agent] →
  → [Shareholder/Investor Agent] →
  → [Community/Society Agent] →
  → [Future Self Agent] →
  → [Synthesis and Alignment Node]
```

**Key Agents**:
- Stakeholder Mapper: Identifies all relevant stakeholders affected by the decision or strategy
- Customer/Client Agent: Represents the perspective of customers and clients
- Team/Employee Agent: Represents the perspective of team members and employees
- Shareholder/Investor Agent: Represents the perspective of shareholders and investors
- Community/Society Agent: Represents the perspective of the broader community and society
- Future Self Agent: Represents the user's future self as a stakeholder
- Synthesis and Alignment Node: Integrates stakeholder perspectives and identifies alignment opportunities

### 3. Constraint Analysis Panel

**File**: `iterative_research_tool/panels/constraint_analysis.py`

**Panel Structure**:
```
User Query → [Constraint Mapper] →
  → [Resource Constraint Agent] →
  → [Regulatory Constraint Agent] →
  → [Time Constraint Agent] →
  → [Cognitive Constraint Agent] →
  → [Social Constraint Agent] →
  → [Constraint Synthesis] → [Constraint-Aware Strategy]
```

**Key Agents**:
- Constraint Mapper: Identifies and maps all relevant constraints
- Resource Constraint Agent: Analyzes financial, material, and human resource constraints
- Regulatory Constraint Agent: Identifies legal, regulatory, and compliance constraints
- Time Constraint Agent: Analyzes time-related constraints and deadlines
- Cognitive Constraint Agent: Evaluates attention, willpower, and cognitive load factors
- Social Constraint Agent: Identifies social and cultural constraints
- Constraint Synthesis: Integrates constraint analyses into a coherent understanding

### 4. Temporal Perspective Panel

**File**: `iterative_research_tool/panels/temporal_perspective.py`

**Panel Structure**:
```
User Query → [Past Pattern Analyst] →
  → [Present Reality Assessor] →
  → [Near-Future Transition Architect] →
  → [Long-Term Vision Keeper] →
  → [Temporal Integration] → Strategy
```

**Key Agents**:
- Past Pattern Analyst: Identifies patterns and lessons from historical data
- Present Reality Assessor: Evaluates the current situation with clarity
- Near-Future Transition Architect: Plans the transition from present to desired future state
- Long-Term Vision Keeper: Maintains focus on long-term goals and vision
- Temporal Integration: Synthesizes insights across time horizons into a coherent strategy

### 5. Contrarian Challenge System

**File**: `iterative_research_tool/panels/contrarian_challenge.py`

**Panel Structure**:
```
User Query → [Initial Strategy Developer] →
  → [Devil's Advocate] →
  → [Status Quo Defender] →
  → [Radical Alternative Explorer] →
  → [Synthesis Diplomat] →
  → [Resilient Strategy]
```

**Key Agents**:
- Initial Strategy Developer: Creates a baseline strategy to be challenged
- Devil's Advocate: Systematically challenges assumptions and identifies weaknesses
- Status Quo Defender: Argues for maintaining current approaches
- Radical Alternative Explorer: Proposes unconventional alternatives
- Synthesis Diplomat: Integrates valid criticisms and alternatives into a more resilient strategy

### 6. Implementation Energy Panel

**File**: `iterative_research_tool/panels/implementation_energy.py`

**Panel Structure**:
```
User Query → [Energy Mapping Agent] →
  → [Enthusiasm Sustainability Engineer] →
  → [Recovery Design Specialist] →
  → [Momentum Architecture Agent] →
  → [Energy-Optimized Strategy]
```

**Key Agents**:
- Energy Mapping Agent: Maps the energy requirements of different strategic options
- Enthusiasm Sustainability Engineer: Designs strategies to maintain motivation and enthusiasm
- Recovery Design Specialist: Plans for recovery periods and preventing burnout
- Momentum Architecture Agent: Creates structures to maintain momentum through challenges
- Energy-Optimized Strategy: Synthesizes insights into a strategy optimized for sustainable implementation

### 7. Product Development Panel

**File**: `iterative_research_tool/panels/product_development.py`

**Panel Structure**:
```
User Query → [User Need Interpreter] →
  → [Technology Feasibility Assessor] →
  → [UX Architecture Agent] →
  → [Business Model Analyzer] →
  → [Go-to-Market Strategist] →
  → [Product Strategy]
```

**Key Agents**:
- User Need Interpreter: Deeply understands and articulates user needs
- Technology Feasibility Assessor: Evaluates technical feasibility and implementation challenges
- UX Architecture Agent: Designs optimal user experiences
- Business Model Analyzer: Assesses business model viability and revenue potential
- Go-to-Market Strategist: Plans market entry and growth strategies
- Product Strategy: Synthesizes insights into a comprehensive product strategy

## Implementation Steps

### Step 1: Update the BasePanel Class

Ensure the `BasePanel` class in `__init__.py` has all necessary methods and properties for the new panels.

### Step 2: Implement Each Panel

For each panel:
1. Create the panel file with the appropriate class structure
2. Implement the agent prompts and interactions
3. Create the LangGraph workflow
4. Implement the run method to process queries

### Step 3: Update the Strategic Planner

Modify the `_initialize_panel` method in `StrategicPlanner` to include the new panels:

```python
def _initialize_panel(self, panel_type: str) -> Any:
    """Initialize the appropriate panel based on the panel type."""
    if panel_type == "cognitive-diversity":
        return CognitiveDiversityPanel(
            anthropic_api_key=self.anthropic_api_key,
            model=self.model,
            visualizer=self.visualizer
        )
    elif panel_type == "decision-intelligence":
        return DecisionIntelligencePanel(
            anthropic_api_key=self.anthropic_api_key,
            model=self.model,
            visualizer=self.visualizer
        )
    elif panel_type == "future-scenarios":
        return FutureScenariosPanel(
            anthropic_api_key=self.anthropic_api_key,
            model=self.model,
            visualizer=self.visualizer
        )
    elif panel_type == "personal-development":
        return PersonalDevelopmentPanel(
            anthropic_api_key=self.anthropic_api_key,
            model=self.model,
            visualizer=self.visualizer
        )
    elif panel_type == "stakeholder-impact":
        return StakeholderImpactPanel(
            anthropic_api_key=self.anthropic_api_key,
            model=self.model,
            visualizer=self.visualizer
        )
    elif panel_type == "constraint-analysis":
        return ConstraintAnalysisPanel(
            anthropic_api_key=self.anthropic_api_key,
            model=self.model,
            visualizer=self.visualizer
        )
    elif panel_type == "temporal-perspective":
        return TemporalPerspectivePanel(
            anthropic_api_key=self.anthropic_api_key,
            model=self.model,
            visualizer=self.visualizer
        )
    elif panel_type == "contrarian-challenge":
        return ContrarianChallengePanel(
            anthropic_api_key=self.anthropic_api_key,
            model=self.model,
            visualizer=self.visualizer
        )
    elif panel_type == "implementation-energy":
        return ImplementationEnergyPanel(
            anthropic_api_key=self.anthropic_api_key,
            model=self.model,
            visualizer=self.visualizer
        )
    elif panel_type == "product-development":
        return ProductDevelopmentPanel(
            anthropic_api_key=self.anthropic_api_key,
            model=self.model,
            visualizer=self.visualizer
        )
    else:
        raise ValueError(f"Unknown panel type: {panel_type}")
```

### Step 4: Update the CLI

Update the CLI parser to include the new panel options:

```python
parser.add_argument(
    "--panel", "-p",
    choices=[
        "cognitive-diversity", 
        "decision-intelligence", 
        "future-scenarios",
        "personal-development",
        "stakeholder-impact",
        "constraint-analysis",
        "temporal-perspective",
        "contrarian-challenge",
        "implementation-energy",
        "product-development"
    ],
    default="cognitive-diversity",
    help="Advisory panel to use"
)
```

### Step 5: Update Tests

Update the test scripts to include tests for the new panels:

1. Add test queries for each new panel in `TEST_QUERIES` and `ALT_QUERIES`
2. Add test cases for each new panel
3. Update the comprehensive test script to test all panels

### Step 6: Update Documentation

Update the README and other documentation to include information about the new panels.

## Implementation Timeline

1. **Week 1**: Implement Personal Development Council and Stakeholder Impact Advisory Board
2. **Week 2**: Implement Constraint Analysis Panel and Temporal Perspective Panel
3. **Week 3**: Implement Contrarian Challenge System and Implementation Energy Panel
4. **Week 4**: Implement Product Development Panel and update tests and documentation

## Conclusion

This implementation plan provides a structured approach to adding the seven missing panels to the Multi-Agent Advisory Planner. By following this plan, we can ensure that all panels are implemented consistently and integrated properly with the existing system. 