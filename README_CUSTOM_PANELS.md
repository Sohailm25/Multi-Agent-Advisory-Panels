# Creating Custom Panels for Multi-Agent Advisory Planner

This guide walks you through the process of creating your own custom panels for the Multi-Agent Advisory Planner. Custom panels allow you to extend the system with specialized advisory capabilities tailored to your specific needs.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Understanding the Panel Factory Pattern](#understanding-the-panel-factory-pattern)
3. [Creating a Custom Panel](#creating-a-custom-panel)
4. [Step-by-Step Guide](#step-by-step-guide)
5. [Registering and Using Your Custom Panel](#registering-and-using-your-custom-panel)
6. [Advanced Customization](#advanced-customization)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

Before creating a custom panel, ensure you have:

- Python 3.8 or higher installed
- The Multi-Agent Advisory Planner codebase set up
- An Anthropic API key
- Basic understanding of Python programming
- Familiarity with LangGraph (for advanced customization)

## Understanding the Panel Factory Pattern

The Panel Factory Pattern enables dynamic discovery and instantiation of panels. This allows the system to:

- Find and register all available panels automatically
- Create panel instances on demand without hardcoding dependencies
- Support custom panels from external directories
- Provide a consistent interface for all panels

## Creating a Custom Panel

All panels in the system must inherit from the `BasePanel` class and follow a specific structure:

1. Define agent prompts that specify the roles and tasks of each agent
2. Create a LangGraph workflow that orchestrates agent interactions
3. Implement a run method that processes queries and returns results

## Step-by-Step Guide

### 1. Copy the Template

Start by copying the `custom_panel_template.py` file to your desired location:

```bash
cp custom_panel_template.py my_custom_panel.py
```

### 2. Rename the Panel Class

Edit your new file and rename the `CustomPanel` class to a name that reflects your panel's purpose:

```python
class MarketEntryPanel(BasePanel):
    """Market Entry Panel for multi-agent advisory planning.
    
    This panel provides strategic advice for entering new markets,
    including market assessment, competitive analysis, and entry strategy.
    """
```

### 3. Define Your Agent Prompts

Modify the agent prompt methods to define the roles and tasks of your specialized agents:

```python
def _get_market_analyzer_prompt(self) -> str:
    """Get the prompt for the Market Analyzer agent."""
    return """
    You are a market analyzer who assesses market opportunities. Your role is to:
    - Analyze market size, growth, and trends
    - Identify key market segments and their characteristics
    - Evaluate competitive landscape and market saturation
    - Assess regulatory environment and barriers to entry
    
    Format your response as a JSON object with the following structure:
    {
        "market_analysis": {
            "summary": "Brief summary of your market analysis",
            "market_size": "Assessment of the market size with data if available",
            "growth_potential": "Assessment of growth potential with rationale",
            "key_segments": [
                {
                    "segment": "Name of the segment",
                    "size": "Size of this segment",
                    "growth": "Growth rate of this segment",
                    "attractiveness": "High/Medium/Low with explanation"
                },
                ...
            ],
            "barriers_to_entry": ["barrier 1", "barrier 2", ...],
            "recommendations": ["recommendation 1", "recommendation 2", ...]
        }
    }
    """
```

Update all prompt methods and agent definitions to match your panel's purpose.

### 4. Define Your Graph Workflow

Customize the graph workflow in the `_build_graph` method to match the flow of your agents:

```python
def _build_graph(self) -> StateGraph:
    """Build the LangGraph workflow for the Market Entry Panel."""
    # Define the state schema
    state_schema = {
        "query": str,
        "context": dict,
        "market_analysis": dict,
        "competitor_analysis": dict,
        "entry_strategy": dict,
        "final_recommendation": dict
    }
    
    # Create the graph
    graph = StateGraph(state_schema=state_schema)
    
    # Define the nodes
    graph.add_node("market_analyzer", market_analyzer_function)
    graph.add_node("competitor_analyzer", competitor_analyzer_function)
    graph.add_node("strategy_formulator", strategy_formulator_function)
    graph.add_node("recommendation_synthesizer", recommendation_synthesizer_function)
    
    # Define the edges
    graph.add_edge("market_analyzer", "competitor_analyzer")
    graph.add_edge("competitor_analyzer", "strategy_formulator")
    graph.add_edge("strategy_formulator", "recommendation_synthesizer")
    graph.add_edge("recommendation_synthesizer", END)
    
    # Set the entry point
    graph.set_entry_point("market_analyzer")
    
    return graph
```

Make sure to define all the necessary node functions and adapt the state schema to your panel's needs.

### 5. Update the Run Method

Update the `run` method to match your panel's name and output structure:

```python
def run(self, query: str, context: str = "") -> Dict[str, Any]:
    """Run the Market Entry Panel on the given query."""
    if self.visualizer:
        self.visualizer.display_welcome("Market Entry Panel")
        self.visualizer.display_query(query)
        self.visualizer.update_status("Running Market Entry Panel")
    
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
        "market_analysis": {},
        "competitor_analysis": {},
        "entry_strategy": {},
        "final_recommendation": {}
    }
    
    # Run the graph
    try:
        result = self.graph.invoke(initial_state)
        
        if self.visualizer:
            self.visualizer.display_success("Market Entry Panel completed successfully")
            self.visualizer.display_plan(result["final_recommendation"])
        
        return result["final_recommendation"]
    except Exception as e:
        logger.error(f"Error running Market Entry Panel: {e}")
        if self.visualizer:
            self.visualizer.display_error(f"Error running Market Entry Panel: {e}")
        return {
            "error": str(e),
            "Executive Summary": "An error occurred while running the Market Entry Panel.",
            "Key Insights": ["Error in panel execution"],
            "Strategic Recommendations": [{"recommendation": "Please try again or contact support"}]
        }
```

## Registering and Using Your Custom Panel

### 1. Place Your Panel File

Place your custom panel file in a directory of your choice. You can create a dedicated directory for your custom panels:

```bash
mkdir -p my_custom_panels
mv my_custom_panel.py my_custom_panels/
```

### 2. Run the CLI with Your Custom Panel

Use the `--custom-panel-path` option to tell the CLI where to find your custom panels:

```bash
python -m iterative_research_tool.cli --custom-panel-path my_custom_panels/ --list-panels
```

This should list your custom panel along with the built-in panels.

### 3. Use Your Custom Panel

Run the CLI with your custom panel:

```bash
python -m iterative_research_tool.cli --custom-panel-path my_custom_panels/ --panel market-entry "What strategy should I use to enter the European market with my SaaS product?"
```

Note that the panel name is automatically derived from the class name (e.g., `MarketEntryPanel` becomes `market-entry`).

## Advanced Customization

### Creating Complex Agent Workflows

For more complex panels, you can create more sophisticated agent workflows:

- Parallel agent execution
- Conditional branches
- Iterative refinement loops
- Sub-workflows

See the LangGraph documentation for more details on advanced graph structures.

### Customizing Agent Behavior

You can customize agent behavior by:

- Adjusting temperature and max_tokens parameters
- Adding tool access to agents
- Implementing custom retrieval mechanisms
- Creating specialized agent roles

### Integrating External Data Sources

Enhance your panels with external data:

- Connect to APIs for real-time data
- Incorporate database queries
- Use vector databases for retrieval
- Implement file processing capabilities

## Troubleshooting

### Panel Not Found

If your panel isn't discovered:

- Ensure the panel class inherits from `BasePanel`
- Check that the file is in the directory specified with `--custom-panel-path`
- Verify that the file doesn't have syntax errors

### JSON Parsing Errors

If you encounter JSON parsing errors:

- Check agent prompts to ensure they clearly specify the JSON structure
- Adjust the max_tokens parameter if responses are being cut off
- Look for nested JSON formatting issues in the prompts

### Graph Execution Errors

For graph execution issues:

- Verify that all nodes referenced in edges are defined
- Ensure state keys match between nodes
- Check that the graph has a valid entry point
- Look for missing END nodes

## Examples

For more examples, examine the built-in panels in the codebase:

- `iterative_research_tool/panels/cognitive_diversity.py`
- `iterative_research_tool/panels/decision_intelligence.py`
- `iterative_research_tool/panels/future_scenarios.py`

These panels provide good examples of different agent structures and workflows. 