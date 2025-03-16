# Multi-Agent Advisory Planner

The Multi-Agent Advisory Planner is an advanced CLI tool that leverages LangGraph to orchestrate networks of specialized AI agents for strategic planning and decision-making. This tool provides users with diverse cognitive perspectives, temporal frameworks, and specialized advisory panels to enhance their strategic thinking and decision-making processes.

## Installation

```bash
# Install the package
pip install -e .

# Set up your API keys
iterative-research config --init
iterative-research config --claude-api-key YOUR_CLAUDE_API_KEY
```

## Usage``

### Basic Usage

```bash
# Run the strategic planner with a query
iterative-research strategic-planner "What's the best strategy for launching a new SaaS product?"

# Save the output to a file
iterative-research strategic-planner "How should I approach career development in AI?" --output-file career_strategy.md
```

### Using Multi-Agent Advisory Panels

```bash
# Use the Cognitive Diversity Panel
iterative-research strategic-planner --panel cognitive-diversity "What's the best approach for scaling my startup?"

# Use the Decision Intelligence Framework
iterative-research strategic-planner --panel decision-intelligence "Should I pursue an MBA or gain more industry experience?"

# Use the Future Scenario Planning System
iterative-research strategic-planner --panel future-scenarios "How might AI impact the job market in the next decade?"
```

### Using Memory and Time Travel

```bash
# Enable memory to maintain context across sessions
iterative-research strategic-planner --memory on "How should I approach my career development?"

# Rewind to a previous state and explore alternative paths
iterative-research strategic-planner --rewind 3 "What if I tried a different approach?"
```

## Available Panels

The Multi-Agent Advisory Planner offers several specialized panels:

1. **Cognitive Diversity Panel**: Provides diverse mental models and thinking frameworks to analyze problems from multiple perspectives.
2. **Decision Intelligence Framework**: Helps users make complex decisions by decomposing them into specialized analytical components.
3. **Future Scenario Planning System**: Helps users prepare for multiple possible futures by exploring diverse scenarios.
4. **Personal Development Council**: Creates a personalized development plan by analyzing gaps across multiple domains.
5. **Stakeholder Impact Advisory Board**: Analyzes decisions from the perspective of different stakeholders.
6. **Constraint Analysis Panel**: Identifies and analyzes constraints affecting strategy implementation.
7. **Temporal Perspective Panel**: Analyzes problems across different time horizons.
8. **Contrarian Challenge System**: Stress-tests strategies by challenging assumptions and exploring alternatives.
9. **Implementation Energy Panel**: Optimizes strategies for sustainable implementation energy.
10. **Product Development Panel**: Provides comprehensive product strategy advice.

## Examples

### Cognitive Diversity Panel

```bash
iterative-research strategic-planner --panel cognitive-diversity "How can I improve team collaboration in a remote work environment?"
```

This will analyze the problem using multiple mental models:
- First Principles Thinking (breaking down to fundamental truths)
- Inversion (analyzing backward from failure)
- Systems Dynamics (mapping interconnections and feedback loops)
- Opportunity Cost (evaluating trade-offs and alternatives)
- Decision Journal (documenting context, assumptions, and expected outcomes)

### Decision Intelligence Framework

```bash
iterative-research strategic-planner --panel decision-intelligence "Should our company invest in expanding to a new market or focus on deepening our current market presence?"
```

This will decompose the decision into specialized components:
- Decision Classification (analyzing decision type and complexity)
- Options Generation (creating a comprehensive set of alternatives)
- Criteria Definition (identifying evaluation criteria)
- Probability Assessment (estimating outcome probabilities)
- Consequence Mapping (mapping potential consequences)
- Decision Evaluation (evaluating options against criteria)
- Final Recommendation (synthesizing analyses into a recommendation)

### Future Scenario Planning

```bash
iterative-research strategic-planner --panel future-scenarios "How might climate change affect our agricultural business in the next 20 years?"
```

This will explore multiple possible futures:
- Trend Analysis (identifying relevant trends)
- Scenario Generation (creating distinct future scenarios)
- Opportunity Exploration (identifying opportunities in each scenario)
- Threat Analysis (identifying threats in each scenario)
- Robust Strategy Development (creating strategies that work across scenarios)
- Scenario Synthesis (integrating insights from all scenarios)

## Advanced Features

### Memory Management

The system maintains a persistent knowledge base about the user across sessions:
- Records goals, commitments, and challenges
- Tracks which approaches have been effective
- Identifies recurring patterns in user behavior
- Stores previous advice and user-reported outcomes

### Time Travel

The system allows users to explore alternative strategic paths:
- Rewind to previous states in the planning process
- Explore different approaches without losing the current trajectory
- Compare outcomes across different strategic approaches

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 