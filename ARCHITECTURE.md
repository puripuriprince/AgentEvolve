# AgentEvolve Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE                          │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Gradio Web Application                      │   │
│  │                                                           │   │
│  │  [Input Panel] → [Agent Panel] → [Config Panel] →       │   │
│  │  [Review Panel] → [Execute Panel] → [Results Panel]     │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬──────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       AGENTEVOLVE CORE                           │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Evolution Agent (agent.py)                   │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  1. analyze_input(content, objective)              │  │  │
│  │  │     • Detect: PROMPT vs CODE                       │  │  │
│  │  │     • Select template                               │  │  │
│  │  │     • Generate questions                            │  │  │
│  │  │                                                      │  │  │
│  │  │  2. process_user_answers(analysis, answers)        │  │  │
│  │  │     • Generate evaluation code                      │  │  │
│  │  │     • Create Shinka config                          │  │  │
│  │  │     • Produce run script                            │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          Template Registry (templates.py)                 │  │
│  │                                                            │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────┐ │  │
│  │  │  Red Teaming   │  │ Prompt         │  │  Code      │ │  │
│  │  │  Template      │  │ Optimization   │  │ Optimization│ │  │
│  │  │                │  │ Template       │  │ Template   │ │  │
│  │  │ • Task msg     │  │ • Task msg     │  │ • Task msg │ │  │
│  │  │ • Eval template│  │ • Eval template│  │ • Eval tpl │ │  │
│  │  │ • Config       │  │ • Config       │  │ • Config   │ │  │
│  │  └────────────────┘  └────────────────┘  └────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │      Evaluation Generator (evaluator.py)                  │  │
│  │                                                            │  │
│  │  ┌──────────────────┐          ┌──────────────────────┐  │  │
│  │  │ Prompt Evaluator │          │  Code Evaluator      │  │  │
│  │  │ Generator        │          │  Generator           │  │  │
│  │  │                  │          │                      │  │  │
│  │  │ • LLM API calls  │          │ • run_shinka_eval    │  │  │
│  │  │ • Success detect │          │ • Validation fn      │  │  │
│  │  │ • Metrics        │          │ • Aggregate metrics  │  │  │
│  │  └──────────────────┘          └──────────────────────┘  │  │
│  │                                                            │  │
│  │  Uses: Claude Sonnet 4 or GPT-4 to generate code         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬──────────────────────────────────┘
                                 │
                                 │ Generates:
                                 │ • initial.py
                                 │ • evaluate.py
                                 │ • run_evolution.py
                                 │ • config.json
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXPERIMENT DIRECTORY                          │
│                                                                   │
│  experiments/exp_TIMESTAMP/                                      │
│  ├── initial.py          # Starting solution                     │
│  ├── evaluate.py         # Evaluation harness                    │
│  ├── run_evolution.py    # Evolution runner                      │
│  └── config.json         # Configuration                         │
└────────────────────────────────┬──────────────────────────────────┘
                                 │
                                 │ User runs:
                                 │ python run_evolution.py
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SHINKA EVOLUTION ENGINE                       │
│                     (../ShinkaEvolve)                            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              EvolutionRunner                              │  │
│  │                                                            │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Population Management                             │  │  │
│  │  │  • Island-based evolution                          │  │  │
│  │  │  • Archive best solutions                          │  │  │
│  │  │  • Parent selection                                │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                            │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  LLM Mutation Operators                            │  │  │
│  │  │  • Generate code patches                           │  │  │
│  │  │  • Apply diffs or full rewrites                    │  │  │
│  │  │  • Cross-over between solutions                    │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                            │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Evaluation & Selection                            │  │  │
│  │  │  • Run evaluate.py on candidates                   │  │  │
│  │  │  • Score based on combined_score                   │  │  │
│  │  │  • Update population                               │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Output: results_TIMESTAMP/                                      │
│         ├── evolution_db.sqlite                                  │
│         ├── best/main.py                                         │
│         └── gen_*/                                               │
└─────────────────────────────────────────────────────────────────┘
```

## Component Interaction Flow

### Phase 1: User Input & Analysis

```
User
  │
  │ Provides: content + objective
  ▼
Gradio UI (app.py)
  │
  │ Calls: agent.analyze_input()
  ▼
Evolution Agent (agent.py)
  │
  │ Uses: Claude/GPT-4
  │ Accesses: Template Registry
  ▼
Analysis Result
  • Evolution type: PROMPT or CODE
  • Template: red_teaming/prompt_optimization/code_optimization
  • Questions: 2-3 targeted questions
  • Reasoning: Why this approach
```

### Phase 2: Configuration Generation

```
User
  │
  │ Provides: answers to questions
  ▼
Gradio UI (app.py)
  │
  │ Calls: agent.process_user_answers()
  ▼
Evolution Agent (agent.py)
  │
  │ Uses: Evaluation Generator
  ▼
Evaluation Generator (evaluator.py)
  │
  │ Uses: Claude/GPT-4 to generate code
  │ Uses: Template system for structure
  ▼
Generated Files
  • initial.py (with EVOLVE-BLOCK)
  • evaluate.py (evaluation harness)
  • config.json (Shinka parameters)
  │
  │ Uses: Template configs
  ▼
Run Script Generator
  │
  │ Creates: run_evolution.py
  ▼
Complete Experiment Package
```

### Phase 3: Evolution Execution

```
User
  │
  │ Runs: python run_evolution.py
  ▼
Run Script
  │
  │ Imports: Shinka components
  │ Loads: Generated config
  ▼
Shinka EvolutionRunner
  │
  │ Initializes:
  │   • DatabaseConfig (islands, archive)
  │   • EvolutionConfig (LLMs, generations)
  │   • JobConfig (evaluation)
  ▼
Evolution Loop
  │
  │ For each generation:
  │   1. Select parents from population
  │   2. Generate mutations using LLM
  │   3. Apply patches to create candidates
  │   4. Evaluate using evaluate.py
  │   5. Update population with best solutions
  │   6. Migrate between islands
  │   7. Update archive
  ▼
Results
  • evolution_db.sqlite (full history)
  • best/main.py (best solution)
  • gen_*/ (all generations)
  • metrics and logs
```

## Key Design Patterns

### 1. Template Method Pattern

```python
EvolutionTemplate
  ├── task_sys_msg_template (abstract)
  ├── evaluation_template (abstract)
  └── default_config (abstract)

Concrete Templates:
  ├── RedTeamingTemplate
  ├── PromptOptimizationTemplate
  └── CodeOptimizationTemplate
```

### 2. Strategy Pattern

```python
EvolutionAgent
  └── llm_client: Strategy
       ├── AnthropicClient
       └── OpenAIClient
```

### 3. Factory Pattern

```python
TemplateRegistry
  └── get_template(name) → EvolutionTemplate
```

### 4. Builder Pattern

```python
EvolutionAgent
  └── process_user_answers()
       ├── Build EvolutionConfig
       ├── Build evaluation code
       ├── Build run script
       └── Return complete package
```

## Data Models

### EvolutionConfig
```python
@dataclass
class EvolutionConfig:
    evolution_type: EvolutionType  # PROMPT | CODE
    objective: str                  # User's goal
    user_content: str               # Initial content
    template: EvolutionTemplate     # Selected template
    evaluation_strategy: str        # How to evaluate
    shinka_config: Dict[str, Any]   # Shinka parameters
    generated_files: Dict[str, str] # Generated code
```

### Analysis Result
```python
{
    "evolution_type": "PROMPT" | "CODE",
    "suggested_template": "red_teaming" | "prompt_optimization" | "code_optimization",
    "reasoning": "Why this approach",
    "missing_info": "What we need to know",
    "questions": ["Question 1", "Question 2", ...],
    "user_content": "Original content",
    "objective": "User's objective"
}
```

### Shinka Configuration
```python
{
    "evo_config": {
        "task_sys_msg": str,
        "num_generations": int,
        "llm_models": List[str],
        "patch_types": List[str],
        ...
    },
    "db_config": {
        "num_islands": int,
        "archive_size": int,
        ...
    },
    "job_config": {
        "eval_program_path": str,
        ...
    }
}
```

## Technology Stack

### Frontend
- **Gradio 4.0+**: Web UI framework
- **Python**: UI logic

### Backend
- **Anthropic API**: Claude Sonnet 4 (configuration agent)
- **OpenAI API**: GPT-4 (alternative)
- **Python 3.10+**: Core logic

### Evolution Engine
- **Shinka**: Core evolution framework
- **SQLite**: Evolution database
- **Various LLMs**: Mutation operators

### Infrastructure
- **Local execution**: Default
- **Slurm cluster**: Supported via Shinka

## Security Considerations

### API Keys
- Stored in environment variables
- Never committed to git
- .env.example provides template

### Generated Code
- All code generation logged
- User reviews before execution
- Sandboxed evaluation possible

### Experiment Isolation
- Each experiment in separate directory
- No cross-contamination
- Clear file structure

## Performance Characteristics

### Setup Time
- **Analysis**: ~5-10 seconds (LLM call)
- **Code generation**: ~10-20 seconds (LLM call)
- **Total setup**: ~30 seconds

### Evolution Time
- Depends on:
  - Number of generations
  - Evaluation complexity
  - LLM speed
  - Parallel jobs

### Resource Usage
- **Memory**: Depends on Shinka config
- **Compute**: Depends on evaluation
- **Storage**: ~10MB per experiment

## Extension Points

### Adding New Templates
1. Create EvolutionTemplate instance
2. Define task_sys_msg_template
3. Define evaluation_template
4. Set default_config
5. Register in TemplateRegistry

### Adding New LLM Providers
1. Implement LLM client interface
2. Add to EvolutionAgent.__init__()
3. Add to EvaluatorGenerator.__init__()
4. Update UI options

### Custom Evaluation Logic
1. Modify evaluation templates
2. Add custom validation functions
3. Extend metric aggregation

### UI Customization
1. Modify Gradio components
2. Add new panels
3. Change theme
4. Add visualizations

## Testing Strategy

### Unit Tests (Future)
- Test agent analysis logic
- Test template rendering
- Test code generation parsing
- Test configuration building

### Integration Tests (Future)
- Test full user flow
- Test Shinka integration
- Test generated code execution

### Manual Testing
- Test web UI workflow
- Test Python API
- Test different templates
- Test edge cases

## Monitoring & Debugging

### Logging
- Agent analysis logged
- Code generation logged
- Shinka evolution logged
- Errors captured

### Debugging Tips
- Check generated files
- Inspect config.json
- Review evolution logs
- Use Shinka's WebUI

## Deployment Options

### Local Development
```bash
cd agent-evolve
./launch.sh
```

### Production (Future)
- Docker container
- Cloud deployment
- Scaling considerations

---

This architecture provides a clean separation between:
- User interaction (Gradio)
- Intelligence (Agent + Templates)
- Code generation (Evaluator)
- Evolution (Shinka)

Making it easy to maintain, extend, and scale! 🚀
