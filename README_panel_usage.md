# Using Panels in Iterative Research Tool

## Summary of Findings

After thorough testing, we've determined the correct ways to use the Iterative Research Tool with panels. The CLI implementation has specific ways to invoke panels that differ from some documentation examples.

## Available Panels

The following panels are available in the tool:

- cognitive-diversity
- constraint-analysis
- contrarian-challenge
- decision-intelligence
- future-scenarios
- implementation-energy
- personal-development
- product-development
- stakeholder-impact
- temporal-perspective

## Recommended Methods for Using Panels

Based on testing, here are the recommended ways to use the tool with panels:

### 1. Interactive UI (Recommended)

The most reliable way to use panels is through the interactive UI:

```bash
python -m iterative_research_tool.cli panelsui
```

This launches an interactive interface where you can:
1. Select the strategy type (panels, strat-custom, or strat-swarm)
2. Select a specific panel (if using the panels strategy)
3. Enter your query
4. Configure other settings like LLM provider and API key

### 2. Using Strategic Advisors

For strategic advice without panel selection, use either:

```bash
# Using custom strategic advisor
python -m iterative_research_tool.cli strat-custom "Your query here" --api-key YOUR_API_KEY

# Using swarm strategic advisor
python -m iterative_research_tool.cli strat-swarm "Your query here" --api-key YOUR_API_KEY
```

These commands work reliably and are well-implemented in the CLI.

## Panel Information and Discovery

To get information about available panels:

```bash
# List all available panels
python -m iterative_research_tool.cli --list-panels

# Get info about a specific panel
python -m iterative_research_tool.cli --panel-info panel-name
```

## Setting Up Default Output Location

You can configure a default output directory for all results:

```bash
# Set default output directory
python -m iterative_research_tool.cli config --set-output-dir /path/to/your/output/directory

# View current configuration
python -m iterative_research_tool.cli config
```

The default output directory will be used for all analyses unless overridden with the `--output-dir` flag.

You can also set a default output directory through the environment variable:

```bash
# In your .bashrc, .zshrc, or equivalent
export ITERATIVE_RESEARCH_TOOL_OUTPUT_DIR=/path/to/your/output/directory
```

The configuration is stored in `~/.iterative_research_tool_config` and follows this priority:
1. Command-line argument (`--output-dir`)
2. Configuration file
3. Environment variable
4. Default fallback (`~/iterative_research_tool_output`)

## Implementation Notes

The CLI's command structure requires specific ordering and commands. Key findings from our analysis:

1. Direct panel usage through the CLI is not implemented as expected
2. The `run_with_panel` function exists internally but is only called from:
   - The `panelsui` interactive interface
   - The main function for specific command patterns

3. Based on the implementation in `cli.py`, panels are intended to be used either:
   - Through the interactive UI
   - Through one of the strategic advisor implementations

## Technical Details

The CLI is implemented with an argument parser that has specific subcommands:
- `panelsui`: Launches the interactive UI
- `strat-custom`: Runs the custom strategic advisor
- `strat-swarm`: Runs the swarm strategic advisor
- `config`: Configures default settings

The `run_with_panel` function exists but is not directly exposed as a command-line option. It's used internally when selections are made through the interactive UI.

## Synthesizing Information Across Agents

Each panel and strategic advisor strategy uses a dedicated synthesis agent to combine insights from all previous agents:

1. **Panel Synthesis**: Each panel (e.g., Temporal Perspective, Cognitive Diversity) has a dedicated synthesizer agent that combines all insights from specialized agents into a comprehensive report.

2. **Strategic Advisor Synthesis**:
   - **Swarm Architecture**: Uses a dedicated synthesizer agent that consolidates inputs from all previous agents.
   - **Custom Architecture**: Uses a chief strategist function that synthesizes the diagnostic, planning, and challenge phases into a final response.

The synthesis in each case ensures that:
- Key insights from each agent are preserved
- Contradictions or tensions between agent perspectives are addressed
- A coherent, integrated response is generated
- The final output has a consistent format with actionable recommendations

## Troubleshooting

If you encounter issues:

1. Verify your API key is set properly (either as an environment variable or using `--api-key`)
2. For recursion limit errors with `strat-custom`, consider using `strat-swarm` instead
3. When in doubt, use the interactive UI with `panelsui` command

## Future Improvements

The tool could be improved by:

1. Adding direct CLI support for panel usage similar to the strategic advisors
2. Documenting the expected command structure more clearly
3. Handling command-line arguments more consistently across different usage patterns 