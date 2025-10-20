# Red Teaming Migration from OpenEvolve to Shinka

## Summary

The red_teaming example has been successfully migrated from OpenEvolve to Shinka. The core functionality remains the same: evolving code that generates adversarial prompts for LLM security testing.

## What Changed

### 1. Core Files Updated

#### `evaluate.py`
- **Before**: Used OpenEvolve's evaluation interface and controller
- **After**: Uses Shinka's `run_shinka_eval()` function
- **Key changes**:
  - Removed `openevolve.llm` imports
  - Removed `FitnessEvaluator` class
  - Added `default_aggregate_metrics()` function
  - Added `get_experiment_kwargs()` function
  - Uses environment variable `ANTHROPIC_API_KEY` instead of hardcoded key

#### `initial.py`
- **Before**: Returned a dict with prompt details
- **After**: Returns a tuple of metrics `(success_rate, avg_confidence, num_prompts, num_tests)`
- **Key changes**:
  - `run_red_team_test()` now takes `num_test_scenarios` parameter
  - Returns metrics tuple instead of dict
  - Added basic heuristic evaluation (can be extended with real LLM calls)

#### `run_evo.py`
- **Before**: Used OpenEvolve's controller and config classes
- **After**: Uses Shinka's `EvolutionRunner` and `EvolutionConfig`
- **Key changes**:
  - Import from `shinka.core` instead of `openevolve`
  - Uses `DatabaseConfig` from `shinka.database`
  - Uses `LocalJobConfig` from `shinka.launch`
  - Updated system message for Shinka's prompt format

### 2. Files No Longer Needed

The following OpenEvolve-specific files are no longer required but kept for reference:
- `controller.py` - OpenEvolve controller (Shinka uses `EvolutionRunner`)
- `database.py` - OpenEvolve database (Shinka has its own `ProgramDatabase`)
- `provider.py` - LLM providers (Shinka uses `LLMClient`)
- `metrics.py` - Metrics functions (integrated into evaluate.py)
- `templates.py` - Prompt templates (integrated into run_evo.py)
- `config_phase1.yaml` - Old config format (now uses Python-based config)

### 3. Configuration Changes

**OpenEvolve** used YAML configuration:
```yaml
max_iterations: 100
llm:
  primary_model: "google/gemini-2.0-flash-001"
  temperature: 0.7
```

**Shinka** uses Python-based configuration:
```python
evo_config = EvolutionConfig(
    num_generations=50,
    llm_models=["gpt-4.1-mini", "gemini-2.0-flash-001"],
    llm_kwargs=dict(temperatures=[0.0, 0.5, 1.0]),
)
```

## How to Use

### Quick Start

```bash
cd /Users/arnauddenis-remillard/Documents/Personnel/Projet/Build_mtl/AgentEvolve/ShinkaEvolve/examples/red_teaming
python run_evo.py
```

### Test Evaluation Only

```bash
python evaluate.py --program_path initial.py --results_dir test_results --num_experiment_runs 3
```

### Monitor Progress

```bash
# From ShinkaEvolve root
python -m shinka.webui examples/red_teaming/results_<timestamp>/evolution_db.sqlite
```

## Key Differences: OpenEvolve vs Shinka

| Feature | OpenEvolve | Shinka |
|---------|-----------|---------|
| **Config Format** | YAML files | Python dataclasses |
| **Evaluation** | `evaluate(program_path)` | `run_shinka_eval()` with experiment functions |
| **Return Values** | Dict with metrics | Tuple or dict with `combined_score` |
| **Runner** | `OpenEvolve` class | `EvolutionRunner` class |
| **Database** | `ProgramDatabase` (OpenEvolve) | `ProgramDatabase` (Shinka - different implementation) |
| **LLM Interface** | `LLMEnsemble` | `LLMClient` |
| **Prompt System** | `PromptSampler` | `PromptSampler` (Shinka version) |

## Environment Setup

Make sure you have the required environment variables:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
export OPENAI_API_KEY="your-openai-key-here"  # For GPT models
export GOOGLE_API_KEY="your-google-key-here"  # For Gemini models (if using)
```

## Next Steps

1. **Test the basic setup**: Run `python evaluate.py` to ensure evaluation works
2. **Run evolution**: Execute `python run_evo.py` to start the evolution process
3. **Monitor results**: Use the webui to visualize evolution progress
4. **Customize**: Modify `initial.py` to improve prompt generation strategies
5. **Extend**: Add real LLM API calls to `run_red_team_test()` for actual security testing

## Important Notes

- **Security**: This is for legitimate security research only
- **API Keys**: Never commit API keys to git (use environment variables)
- **Evaluation**: Current implementation uses heuristics - extend with real LLM calls for production use
- **Metrics**: The `combined_score` metric drives evolution - ensure it reflects actual security testing goals

## Troubleshooting

**Import errors?**
- Make sure you're running from the ShinkaEvolve root or have it in your PYTHONPATH
- Ensure all dependencies are installed: `pip install -r requirements.txt`

**Evolution not working?**
- Check that `initial.py` has `EVOLVE-BLOCK-START` and `EVOLVE-BLOCK-END` markers
- Verify `run_red_team_test()` returns the correct tuple format
- Ensure API keys are set in environment variables

**Low scores?**
- The heuristic evaluation is basic - extend with real LLM calls
- Adjust the scoring logic in `run_red_team_test()` to better reflect bypass success
- Increase `num_test_scenarios` for more comprehensive evaluation

## Support

For questions or issues:
1. Check the main README.md in this directory
2. Review Shinka documentation
3. Compare with other Shinka examples (e.g., `adas_aime`, `circle_packing`)
