# Using Shinka CLI for Red Teaming

## Yes! You can use the Shinka CLI

Shinka provides a Hydra-based CLI called `shinka_launch` that makes running evolution much easier. The red_teaming example already has config files set up!

## Quick Start with CLI

### Option 1: Using the shinka_launch command

```bash
# From the ShinkaEvolve root directory
./shinka/shinka_launch variant=red_teaming_example
```

### Option 2: Using Python module directly

```bash
# From the ShinkaEvolve root directory
python3 -m shinka.launch_hydra variant=red_teaming_example
```

## What This Does

When you run the CLI with `variant=red_teaming_example`, Shinka automatically:

1. ✅ Loads configuration from `configs/variant/red_teaming_example.yaml`
2. ✅ Loads task config from `configs/task/red_teaming.yaml`
3. ✅ Loads evolution settings from `configs/evolution/medium_budget.yaml`
4. ✅ Loads database config from `configs/database/island_small.yaml`
5. ✅ Sets up results directory: `results/shinka_red_teaming/<timestamp>_example/`
6. ✅ Runs the evolution process
7. ✅ Saves all results and logs

## Configuration Files Explained

### 1. Variant Config (`configs/variant/red_teaming_example.yaml`)

```yaml
defaults:
  - override /database@_global_: island_small
  - override /evolution@_global_: medium_budget
  - override /task@_global_: red_teaming
  - override /cluster@_global_: local
  - _self_

variant_suffix: "_example"
```

**What it does:**
- Combines all the other configs
- Sets up defaults for this specific variant
- Adds "_example" suffix to output directory

### 2. Task Config (`configs/task/red_teaming.yaml`)

```yaml
evaluate_function:
  _target_: examples.red_teaming.evaluate.main
  program_path: ???
  results_dir: ???
  test_against_llm: true

distributed_job_config:
  _target_: shinka.launch.LocalJobConfig
  eval_program_path: "examples/red_teaming/evaluate.py"

evo_config:
  task_sys_msg: |
    You are an expert in AI security and red teaming...
  language: "python"
  init_program_path: "examples/red_teaming/initial.py"
  job_type: "local"

exp_name: "shinka_red_teaming"
```

**What it does:**
- Points to `examples/red_teaming/evaluate.py` for evaluation
- Points to `examples/red_teaming/initial.py` as starting program
- Sets the system message for LLM mutations
- Sets experiment name for results directory

### 3. Evolution Config (`configs/evolution/medium_budget.yaml`)

Check this file to see parameters like:
- `num_generations`: Number of evolution iterations
- `llm_models`: Which models to use for mutations
- `patch_types`: Types of code modifications
- `max_parallel_jobs`: Parallelization

### 4. Database Config (`configs/database/island_small.yaml`)

Check this file to see parameters like:
- `num_islands`: Number of population islands
- `archive_size`: Elite archive size
- `migration_interval`: When to migrate programs between islands

## CLI Command Examples

### Basic Usage

```bash
# Use default settings (medium budget, small islands)
./shinka/shinka_launch variant=red_teaming_example
```

### Custom Evolution Budget

```bash
# Small budget (faster, fewer generations)
./shinka/shinka_launch variant=red_teaming_example evolution=small_budget

# Large budget (more thorough, more generations)
./shinka/shinka_launch variant=red_teaming_example evolution=large_budget
```

### Custom Database Size

```bash
# Small islands (faster)
./shinka/shinka_launch variant=red_teaming_example database=island_small

# Medium islands (balanced)
./shinka/shinka_launch variant=red_teaming_example database=island_medium

# Large islands (more diversity)
./shinka/shinka_launch variant=red_teaming_example database=island_large
```

### Combine Parameters

```bash
# Large evolution with large islands
./shinka/shinka_launch variant=red_teaming_example \
    evolution=large_budget \
    database=island_large
```

### Override Specific Parameters

```bash
# Change number of generations
./shinka/shinka_launch variant=red_teaming_example \
    evo_config.num_generations=100

# Change LLM models
./shinka/shinka_launch variant=red_teaming_example \
    evo_config.llm_models=['gpt-4','claude-3-5-sonnet']

# Change max parallel jobs
./shinka/shinka_launch variant=red_teaming_example \
    evo_config.max_parallel_jobs=5

# Change results directory
./shinka/shinka_launch variant=red_teaming_example \
    results_dir=my_custom_results
```

### Disable LLM Testing (Faster for Debugging)

```bash
./shinka/shinka_launch variant=red_teaming_example \
    task.evaluate_function.test_against_llm=false
```

## Where Results Are Saved

Results are saved to:
```
results/shinka_red_teaming/<timestamp>_example/
├── evolution_db.sqlite       # Evolution database
├── evolution_run.log          # Detailed logs
├── gen_0/                     # Generation 0 programs
│   └── <program_id>/
│       ├── main.py
│       └── metrics.json
├── gen_1/                     # Generation 1 programs
├── ...
├── gen_49/                    # Final generation
└── best/                      # Best program found
    ├── main.py
    └── metrics.json
```

## Monitoring Progress

### Option 1: Watch the logs

```bash
# In another terminal
tail -f results/shinka_red_teaming/<timestamp>_example/evolution_run.log
```

### Option 2: Use the Web UI

```bash
# From ShinkaEvolve root
python3 -m shinka.webui results/shinka_red_teaming/<timestamp>_example/evolution_db.sqlite
```

Then open http://localhost:7860

## Comparison: CLI vs Python Script

### Using CLI (`shinka_launch`)

**Pros:**
- ✅ Clean, simple commands
- ✅ Easy to override parameters
- ✅ Consistent configuration management
- ✅ Better for production/experiments
- ✅ Hydra features (multirun, sweeps, etc.)

**Cons:**
- ❌ Need to understand YAML configs
- ❌ Less flexible for one-off changes

**Example:**
```bash
./shinka/shinka_launch variant=red_teaming_example evolution=large_budget
```

### Using Python Script (`run_evo.py`)

**Pros:**
- ✅ Direct Python configuration
- ✅ Easy to understand and modify
- ✅ Good for development/testing
- ✅ No YAML needed

**Cons:**
- ❌ Need to edit Python file for changes
- ❌ Less portable across experiments

**Example:**
```bash
cd examples/red_teaming
python3 run_evo.py
```

## Recommended Workflow

### For Development/Testing
```bash
# Use Python script - quick iteration
cd examples/red_teaming
python3 run_evo.py
```

### For Production/Experiments
```bash
# Use CLI - clean, reproducible
./shinka/shinka_launch variant=red_teaming_example evolution=large_budget
```

## Advanced CLI Features

### Parameter Sweeps (Run Multiple Experiments)

```bash
# Run with different generation counts
./shinka/shinka_launch variant=red_teaming_example \
    evo_config.num_generations=10,50,100 \
    --multirun
```

This will run 3 separate experiments with 10, 50, and 100 generations.

### Logging and Output

```bash
# Change verbosity
./shinka/shinka_launch variant=red_teaming_example verbose=true

# Custom run name
./shinka/shinka_launch variant=red_teaming_example \
    run_name=my_experiment_v1
```

## Troubleshooting CLI

### "ModuleNotFoundError: No module named 'dotenv'"

Install missing dependencies:
```bash
pip install python-dotenv
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### "Command not found: shinka_launch"

Make sure you're in the ShinkaEvolve root directory:
```bash
cd /Users/arnauddenis-remillard/Documents/Personnel/Projet/Build_mtl/AgentEvolve/ShinkaEvolve
./shinka/shinka_launch variant=red_teaming_example
```

Or use the Python module directly:
```bash
python3 -m shinka.launch_hydra variant=red_teaming_example
```

### "Config not found"

Make sure config files exist:
```bash
ls configs/variant/red_teaming_example.yaml
ls configs/task/red_teaming.yaml
```

### Environment Variables Not Set

Make sure API keys are exported:
```bash
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

Or create a `.env` file in the ShinkaEvolve root:
```bash
echo "ANTHROPIC_API_KEY=your-key" >> .env
echo "OPENAI_API_KEY=your-key" >> .env
```

## Summary

**Yes, you can use the Shinka CLI!**

Quick command to get started:
```bash
cd /Users/arnauddenis-remillard/Documents/Personnel/Projet/Build_mtl/AgentEvolve/ShinkaEvolve
./shinka/shinka_launch variant=red_teaming_example
```

This is equivalent to running `python run_evo.py` but with:
- Better configuration management
- Easier parameter overrides
- Cleaner results organization
- Production-ready setup

Both methods work - use whichever fits your workflow!
