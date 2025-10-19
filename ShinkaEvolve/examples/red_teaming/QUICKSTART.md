# Red Teaming Quick Start

## Run with shinka_launch (One Command)

From the project root:

```bash
shinka_launch variant=red_teaming_example
```

That's it! The system will now:
1. Generate adversarial prompts
2. Test them against GPT-4.1-nano
3. Use a judge LLM to score success
4. Evolve better prompt generation code
5. Repeat for 100 generations

## What's Happening

```
Generation 1:  Initial prompt generator creates basic prompts
               ↓
               Tests against target LLM → Judge evaluates → Score: 1.2/5.0
               ↓
Generation 2:  Code mutated based on score
               ↓
               New prompts tested → Score: 1.8/5.0 (improving!)
               ↓
Generation 10: Score: 3.5/5.0 (finding effective patterns)
               ↓
Generation 50: Score: 4.2/5.0 (consistently bypassing safety)
```

## Quick Options

```bash
# Faster evolution (fewer generations, less LLM diversity)
shinka_launch variant=red_teaming_example evolution=small_budget

# More thorough evolution (more generations, more LLM models)
shinka_launch variant=red_teaming_example evolution=large_budget

# Disable actual LLM testing (much faster, for debugging only)
shinka_launch variant=red_teaming_example task.evaluate_function.test_against_llm=false

# Change number of generations
shinka_launch variant=red_teaming_example evolution.evo_config.num_generations=200
```

## View Results

```bash
# Find the latest run
ls -lt results/shinka_red_teaming/

# View in web UI (replace <timestamp> with actual value)
python -m shinka.webui results/shinka_red_teaming/<timestamp>/evolution_db.sqlite

# Check sample prompts
cat results/shinka_red_teaming/<timestamp>/programs/<program_id>/sample_prompts.txt
```

## Configuration Files

The system uses these configs:
- `configs/task/red_teaming.yaml` - Task definition and system prompt
- `configs/variant/red_teaming_example.yaml` - Combines task + evolution + database settings
- `configs/evolution/medium_budget.yaml` - Evolution parameters (LLMs, generations, etc.)
- `configs/database/island_small.yaml` - Database and parent selection strategy

You can override any parameter on the command line!

## Cost Estimate

With default settings (medium_budget):
- ~100 generations
- ~5 evaluations per generation
- Each evaluation tests 3 prompts
- Each test = 1 target LLM call + 1 judge LLM call

**Total LLM calls**: ~100 × 5 × 3 × 2 = ~3,000 calls
**Estimated cost**: $5-15 depending on models used

Use `evolution=small_budget` to reduce cost for initial testing.
