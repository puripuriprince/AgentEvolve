# AgentEvolve Examples

This directory contains examples showing different ways to use AgentEvolve.

## Examples

### 1. Red Teaming via Python API

**File**: `example_red_teaming.py`

Shows how to use AgentEvolve programmatically without the web UI. Demonstrates:
- Initializing the agent
- Analyzing input
- Providing answers to agent questions
- Generating evolution configuration
- Saving experiment files

**Usage**:
```bash
python example_red_teaming.py
```

This will create a `red_teaming_experiment/` directory with all the files needed to run evolution.

### 2. Web UI (Recommended)

The easiest way to use AgentEvolve is through the web interface:

```bash
cd ..
./launch.sh
```

Then open http://localhost:7860 in your browser.

### 3. Custom Template Example

Coming soon - shows how to create your own evolution template.

## What Gets Generated

Each example generates an experiment directory with:

```
experiment_name/
├── initial.py          # Starting solution (with EVOLVE-BLOCK)
├── evaluate.py         # Evaluation harness
├── run_evolution.py    # Script to run evolution
└── config.json         # Full configuration
```

After running `run_evolution.py`, you'll also get:

```
experiment_name/
└── results_TIMESTAMP/
    ├── evolution_db.sqlite  # Evolution database
    ├── best/                # Best solution found
    ├── gen_0/               # Generation 0 candidates
    ├── gen_1/               # Generation 1 candidates
    └── ...
```

## Viewing Results

Use Shinka's web UI to visualize evolution results:

```bash
cd ../../ShinkaEvolve
python -m shinka.webui ../agent-evolve/examples/experiment_name/results_*/evolution_db.sqlite
```

This shows:
- Evolution progress over generations
- Genealogy trees
- Code similarity maps
- Metrics and performance

## Tips

1. **Start Small**: Use fewer generations (10-20) for testing
2. **Check API Keys**: Make sure ANTHROPIC_API_KEY or OPENAI_API_KEY is set
3. **Monitor Progress**: Watch the console output during evolution
4. **Inspect Code**: Review generated evaluation code before running
5. **Iterate**: Try different objectives and configurations

## Need Help?

- Check the main README: `../README.md`
- Read Shinka docs: `../../ShinkaEvolve/docs/`
- Look at Shinka examples: `../../ShinkaEvolve/examples/`
