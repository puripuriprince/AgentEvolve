# Getting Started with Red Teaming in Shinka

## Prerequisites

1. **Set up environment variables** (IMPORTANT - do not commit these!):
   ```bash
   export ANTHROPIC_API_KEY="your-anthropic-key"
   export OPENAI_API_KEY="your-openai-key"
   ```

2. **Install dependencies** (if not already done):
   ```bash
   cd /Users/arnauddenis-remillard/Documents/Personnel/Projet/Build_mtl/AgentEvolve/ShinkaEvolve
   pip install -r requirements.txt
   ```

## Step 1: Test the Evaluation (5 minutes)

First, verify that the evaluation system works:

```bash
cd /Users/arnauddenis-remillard/Documents/Personnel/Projet/Build_mtl/AgentEvolve/ShinkaEvolve/examples/red_teaming

# Run a quick evaluation test
python evaluate.py --program_path initial.py --results_dir test_results --num_experiment_runs 3
```

Expected output:
- Evaluation should complete successfully
- You should see metrics like `combined_score`, `avg_success_rate`, etc.
- Results saved to `test_results/`

## Step 2: Run Evolution (30-60 minutes)

Now start the actual evolution process:

```bash
python run_evo.py
```

What happens:
1. Shinka loads `initial.py` as the starting point
2. Runs 50 generations of evolution
3. Each generation:
   - Selects a parent program
   - Uses LLM to mutate the code (functions inside EVOLVE-BLOCK)
   - Evaluates the new program
   - Keeps it if it scores well
4. Results saved to `results_<timestamp>/`

## Step 3: Monitor Progress

While evolution is running (or after), check the results:

### Option 1: Use the Web UI

```bash
# From ShinkaEvolve root directory
python -m shinka.webui examples/red_teaming/results_<timestamp>/evolution_db.sqlite
```

Then open http://localhost:7860 in your browser to see:
- Evolution progress over time
- Best programs found
- Lineage trees
- Similarity maps

### Option 2: Check Log Files

```bash
# View the evolution log
tail -f results_<timestamp>/evolution_run.log
```

### Option 3: Examine the Database Directly

```bash
sqlite3 results_<timestamp>/evolution_db.sqlite
# Then run SQL queries to explore the data
```

## Step 4: Analyze Results

### Find the Best Program

The best program will be in:
```
results_<timestamp>/best/main.py
```

Compare it with `initial.py` to see what changed!

### Check Performance Metrics

Look at the evolution log to see how scores improved:
```bash
grep "combined_score" results_<timestamp>/evolution_run.log
```

### View Generated Programs

Each generation's programs are saved:
```
results_<timestamp>/gen_0/
results_<timestamp>/gen_1/
...
results_<timestamp>/gen_49/
```

## Understanding the Code Evolution

### What Gets Evolved

Only code between these markers gets modified:
```python
# EVOLVE-BLOCK-START
def generate_red_team_prompt(scenario: str) -> str:
    # This function will be evolved
    ...

def enhance_prompt_with_context(base_prompt: str, context: str = "") -> str:
    # This function will be evolved
    ...

def create_prompt_variation(original_prompt: str, variation_type: str = "paraphrase") -> str:
    # This function will be evolved
    ...
# EVOLVE-BLOCK-END
```

### What Stays Fixed

This function never changes (it's the evaluation interface):
```python
def run_red_team_test(num_test_scenarios: int = 3) -> tuple:
    # This stays the same - it calls the evolved functions
    ...
```

## Customization Ideas

### 1. Change Evolution Parameters

Edit `run_evo.py`:
```python
evo_config = EvolutionConfig(
    num_generations=100,  # More generations = better results
    llm_models=["gpt-4", "gemini-2.0-flash-001"],  # Try different models
    patch_type_probs=[0.5, 0.5],  # 50% diff, 50% full rewrite
)
```

### 2. Add Real LLM Testing

Edit `initial.py` to actually test prompts against Claude:
```python
def run_red_team_test(num_test_scenarios: int = 3) -> tuple:
    # Replace the heuristic with real LLM calls
    from evaluate import get_claude_response, evaluate_safety

    response = get_claude_response(final_prompt)
    safety = evaluate_safety(response)
    is_bypass = not safety["is_safe"]
    # ... rest of the logic
```

### 3. Add More Test Scenarios

Edit `initial.py`:
```python
scenarios = [
    "jailbreak",
    "prompt_injection",
    "toxic_content",
    "privacy_violation",  # Add new
    "misinformation",     # Add new
]
```

## Tips for Better Results

1. **Start Small**: Run 10 generations first to test, then scale up
2. **Monitor Closely**: Watch the first few generations to catch issues early
3. **Use Good Metrics**: The `combined_score` should reflect real security testing goals
4. **Be Patient**: Evolution takes time - 50 generations might take 30-60 minutes
5. **Iterate**: Run multiple evolution sessions with different parameters

## Common Issues

### "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### "Module not found: shinka"
```bash
# Make sure you're in the right directory
cd /Users/arnauddenis-remillard/Documents/Personnel/Projet/Build_mtl/AgentEvolve/ShinkaEvolve
# Or add to PYTHONPATH
export PYTHONPATH="/Users/arnauddenis-remillard/Documents/Personnel/Projet/Build_mtl/AgentEvolve/ShinkaEvolve:$PYTHONPATH"
```

### "Evaluation failed"
- Check that `initial.py` has the correct function signature
- Verify the function returns a tuple: `(float, float, int, int)`
- Look at `test_results/` for error details

## Next Steps

1. ✅ Test evaluation
2. ✅ Run first evolution
3. ✅ Analyze results
4. 🔄 Iterate and improve:
   - Modify evolution parameters
   - Add real LLM testing
   - Extend with more scenarios
   - Analyze what makes prompts effective
5. 🚀 Use insights to improve LLM safety!

## Resources

- **Main README**: `README.md` in this directory
- **Migration Guide**: `MIGRATION_SUMMARY.md` for OpenEvolve users
- **Shinka Docs**: See other examples in `examples/` directory
- **Example Outputs**: `EXAMPLE_OUTPUT.md` (if available)

Happy evolving! Remember: this is for security research to make LLMs safer.
