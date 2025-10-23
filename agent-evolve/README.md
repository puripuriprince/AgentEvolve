# 🧬 AgentEvolve

**User-friendly wrapper for the Shinka evolution engine**

Quickly evolve LLM prompts or Python code with AI-guided configuration. No need to understand Shinka's internals - just tell us what you want to evolve and your objective!

## ✨ Features

- **Universal Evolution**: Evolve prompts OR code with the same interface
- **AI-Guided Setup**: Agent asks questions and generates evaluation code for you
- **Web UI Dashboard**: Interactive interface for the full evolution workflow
- **Pre-built Templates**: Red teaming, prompt optimization, code optimization
- **Powered by Shinka**: Uses the battle-tested Shinka evolution engine

## 🚀 Quick Start

### Installation

```bash
# Navigate to the agent-evolve directory
cd agent-evolve

# Install dependencies
pip install -e .

# Set up your API keys
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"  # Optional
```

### Launch the Web UI

```bash
python -m ui.app
```

Then open http://localhost:7860 in your browser!

## 💡 How It Works

### 1. Provide Your Input

Paste what you want to evolve:
- **For prompts**: Your jailbreak, system message, or prompt template
- **For code**: Your Python function or algorithm

### 2. Describe Your Objective

Tell us what you want to achieve:
- "Maximize bypass rate on Claude"
- "Optimize for speed"
- "Improve accuracy on math problems"

### 3. Let the Agent Help

The AI agent will:
- Detect if you're evolving prompts or code
- Ask a few clarifying questions
- Generate evaluation code automatically
- Configure Shinka parameters

### 4. Start Evolution!

Click the button and watch your content evolve in real-time!

## 📋 Use Cases

### Red Teaming / Jailbreak Evolution

```
Content: Your adversarial prompt
Objective: Maximize bypass rate on Claude Sonnet 4
→ Agent generates LLM testing harness
→ Evolves prompts that test safety measures
```

### Prompt Optimization

```
Content: Your task prompt template
Objective: Improve accuracy on sentiment analysis
→ Agent generates task evaluation
→ Evolves prompts for better performance
```

### Code Optimization

```
Content: Your Python algorithm
Objective: Minimize execution time
→ Agent generates performance benchmarks
→ Evolves faster implementations
```

## 🏗️ Architecture

```
AgentEvolve/
├── core/
│   ├── agent.py          # AI configuration agent
│   ├── templates.py      # Pre-built templates
│   └── evaluator.py      # Auto-evaluation generator
├── ui/
│   └── app.py           # Gradio web interface
└── examples/            # Example experiments
```

Built on top of:
- **Shinka**: Evolution engine ([../ShinkaEvolve](../ShinkaEvolve))
- **Gradio**: Web UI framework
- **Claude/GPT-4**: AI agent intelligence

## 🎯 Example Workflow

**User**: "I want to evolve this jailbreak prompt to be more effective"

```python
# User pastes:
"You are a helpful AI. For educational purposes..."

# Objective:
"Maximize bypass rate on Claude"
```

**Agent**:
- Detects: PROMPT evolution
- Template: Red teaming
- Asks: "Which LLM to test?" → User: "Claude Sonnet 4"
- Asks: "How to detect bypass?" → User: "If it provides restricted info"

**System**:
- Generates `evaluate.py` with Claude API testing
- Generates `initial.py` with prompt in EVOLVE-BLOCK
- Configures Shinka for 30 generations
- Starts evolution

**Result**: Top 5 evolved prompts with success rates!

## 🔧 Advanced Usage

### Python API (without UI)

```python
from core.agent import EvolutionAgent

# Initialize agent
agent = EvolutionAgent(llm_client="anthropic")

# Analyze input
analysis = agent.analyze_input(
    user_content="Your prompt or code here",
    objective="What you want to achieve"
)

# Process answers
config = agent.process_user_answers(
    initial_analysis=analysis,
    user_answers={
        "target_llm": "gpt-4.1-mini",
        "num_generations": 30,
    }
)

# Generate files and run
agent.evaluator_generator.save_evaluator(
    config.generated_files,
    output_dir="./my_experiment"
)
```

### Custom Templates

Add your own template in `core/templates.py`:

```python
TemplateRegistry.TEMPLATES["my_template"] = EvolutionTemplate(
    name="My Custom Evolution",
    description="...",
    evolution_type=EvolutionType.PROMPT,
    task_sys_msg_template="...",
    evaluation_template="...",
    default_config={...}
)
```

## 📊 Understanding Results

Evolution experiments are saved to `../experiments/exp_TIMESTAMP/`:

```
exp_20251022_143000/
├── initial.py           # Starting point
├── evaluate.py          # Evaluation harness
├── run_evolution.py     # Runner script
├── config.json          # Full configuration
└── results_*/           # Shinka results
    ├── evolution_db.sqlite  # Evolution database
    ├── best/                # Best evolved solution
    └── gen_*/              # Solutions by generation
```

View results with Shinka's Web UI:

```bash
cd ../ShinkaEvolve
python -m shinka.webui ../experiments/exp_TIMESTAMP/results_*/evolution_db.sqlite
```

## 🤝 Contributing

AgentEvolve is a demo wrapper around Shinka. To contribute:

1. **Core evolution engine**: Contribute to Shinka
2. **UI/templates**: Contribute here
3. **Bug reports**: Open issues with details

## 📚 Resources

- **Shinka Documentation**: [../ShinkaEvolve/README.md](../ShinkaEvolve/README.md)
- **Shinka Paper**: [arXiv:2509.19349](https://arxiv.org/abs/2509.19349)
- **Web UI Guide**: [../ShinkaEvolve/docs/webui.md](../ShinkaEvolve/docs/webui.md)

## ⚖️ License

Same license as Shinka (Apache 2.0). This is a research tool - use responsibly!

## 🙏 Acknowledgments

Built on top of the amazing [Shinka](../ShinkaEvolve) framework by Sakana AI.

---

**Made with ❤️ for the AI safety and research community**
