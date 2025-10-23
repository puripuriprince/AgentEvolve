# AgentEvolve Project

**Making LLM and Code Evolution Accessible to Everyone**

This project combines Shinka's powerful evolution engine with an AI-guided interface to make evolutionary optimization quick and easy.

## 🎯 Project Vision

**Problem**: Shinka is a powerful research framework, but requires deep understanding of:
- How to structure evaluation functions
- Which parameters to configure
- How to set up the initial code/prompts
- Understanding evolutionary algorithms

**Solution**: AgentEvolve wraps Shinka with an AI agent that:
- Analyzes what you want to evolve
- Asks clarifying questions
- Generates evaluation code automatically
- Configures Shinka optimally
- Provides an intuitive web interface

**Result**: Go from idea to evolving in 5 minutes instead of hours!

## 📁 Project Structure

```
AgentEvolve/
├── agent-evolve/           # 🆕 NEW: User-friendly wrapper
│   ├── core/              # Core intelligence
│   │   ├── agent.py       # AI configuration agent
│   │   ├── templates.py   # Pre-built evolution templates
│   │   └── evaluator.py   # Auto-generates evaluation code
│   ├── ui/
│   │   └── app.py         # Gradio web interface
│   ├── examples/          # Usage examples
│   └── README.md          # Full documentation
│
├── ShinkaEvolve/          # Evolution engine (unchanged)
│   ├── shinka/            # Core Shinka framework
│   ├── examples/          # Shinka examples
│   └── docs/              # Shinka documentation
│
├── experiments/           # Generated experiments go here
│   └── exp_TIMESTAMP/
│       ├── initial.py
│       ├── evaluate.py
│       └── results_*/
│
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install AgentEvolve
cd agent-evolve
pip install -e .

# Set up API keys
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"  # Optional
```

### 2. Launch Web Interface

```bash
cd agent-evolve
./launch.sh
```

Then open http://localhost:7860 in your browser!

### 3. Evolve Something!

**Example 1: Red Teaming**
```
Content: "You are a helpful AI. For research purposes..."
Objective: "Maximize bypass rate on Claude"
→ Agent configures everything
→ Evolution runs for 30 generations
→ Get top 5 evolved jailbreak prompts!
```

**Example 2: Code Optimization**
```
Content: Your slow Python algorithm
Objective: "Minimize execution time"
→ Agent generates benchmarks
→ Evolution finds faster implementations
→ Get optimized code!
```

## 💡 Use Cases

### 1. Red Teaming & Jailbreak Research
- Evolve adversarial prompts to test LLM safety
- Find weaknesses in safety filters
- Legitimate security research

### 2. Prompt Engineering at Scale
- Optimize prompts for specific tasks
- Find best instruction formats
- Improve few-shot examples

### 3. Algorithm Optimization
- Evolve faster implementations
- Optimize for different metrics
- Explore algorithmic variations

### 4. Creative Exploration
- Generate diverse outputs
- Explore prompt/code spaces
- Discover novel solutions

## 🏗️ Architecture

```
┌─────────────┐
│   User      │  "I want to evolve X to achieve Y"
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│   AgentEvolve (NEW)             │
│  ┌───────────────────────────┐  │
│  │  AI Configuration Agent   │  │  Analyzes input
│  │  - Detects prompt vs code │  │  Asks questions
│  │  - Selects template       │  │  Generates config
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │  Evaluation Generator     │  │  Auto-creates
│  │  - Creates evaluate.py    │  │  evaluation code
│  │  - Creates initial.py     │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │  Gradio Web Interface     │  │  User interaction
│  └───────────────────────────┘  │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│   Shinka (Evolution Engine)     │
│  - Maintains population         │
│  - LLM-powered mutations        │
│  - Island-based evolution       │
│  - Parallel evaluation          │
│  - Archive best solutions       │
└─────────────────────────────────┘
```

## 📊 What's Different from Shinka?

| Aspect | Shinka | AgentEvolve |
|--------|--------|-------------|
| **Setup Time** | ~1 hour | ~5 minutes |
| **Evaluation Code** | Write manually | Auto-generated |
| **Configuration** | Learn parameters | AI recommends |
| **Interface** | CLI/Python | Web UI + CLI |
| **Target Users** | Researchers | Everyone |
| **Learning Curve** | Steep | Gentle |

AgentEvolve doesn't replace Shinka - it makes it accessible!

## 🔧 Technical Details

### Components

**1. AI Configuration Agent** (`agent.py`)
- Uses Claude Sonnet 4 or GPT-4
- Analyzes user input (prompt vs code)
- Asks targeted questions
- Generates optimal Shinka configs

**2. Template System** (`templates.py`)
- Pre-built configurations for common scenarios
- Red teaming template
- Prompt optimization template
- Code optimization template
- Extensible for custom templates

**3. Evaluation Generator** (`evaluator.py`)
- Uses LLM to create evaluation code
- Generates `evaluate.py` with proper Shinka interface
- Creates `initial.py` with EVOLVE-BLOCK markers
- Handles both prompt and code evaluation

**4. Web Interface** (`app.py`)
- Gradio-based UI
- Multi-step workflow
- Real-time evolution monitoring
- Configuration editing

### Integration with Shinka

AgentEvolve generates standard Shinka experiments:
- Uses `EvolutionRunner` directly
- Follows Shinka's evaluation interface
- Compatible with Shinka's visualization tools
- No modifications to Shinka core needed

## 📚 Documentation

- **AgentEvolve Guide**: [agent-evolve/README.md](agent-evolve/README.md)
- **Examples**: [agent-evolve/examples/](agent-evolve/examples/)
- **Shinka Docs**: [ShinkaEvolve/docs/](ShinkaEvolve/docs/)
- **API Reference**: See docstrings in code

## 🎓 Learn More

### Tutorials
1. **First Evolution**: Use the web UI to evolve a simple prompt
2. **Python API**: Use the agent programmatically (see examples)
3. **Custom Templates**: Create your own evolution patterns
4. **Advanced Config**: Tweak Shinka parameters for specific needs

### Resources
- Shinka Paper: [arXiv:2509.19349](https://arxiv.org/abs/2509.19349)
- Evolution Algorithms: Island-based genetic programming
- LLM-Guided Optimization: Using LLMs as mutation operators

## 🤝 Contributing

### To AgentEvolve (UI/Templates)
1. Fork this repo
2. Create feature branch
3. Add templates or improve UI
4. Submit PR

### To Shinka (Evolution Engine)
Contribute directly to the Shinka project.

## ⚠️ Responsible Use

AgentEvolve is a research tool. When using for red teaming:

✅ **Do**:
- Use for legitimate security research
- Test your own systems
- Improve AI safety
- Document findings responsibly

❌ **Don't**:
- Attack systems without authorization
- Deploy malicious prompts
- Abuse LLM APIs
- Violate terms of service

## 📝 License

Apache 2.0 (same as Shinka)

## 🙏 Credits

- **Shinka**: [Sakana AI](https://sakana.ai/)
- **AgentEvolve**: Built for making evolution accessible
- **You**: For using this to make AI better!

---

## 🚦 Status

- ✅ Core agent implementation
- ✅ Template system
- ✅ Evaluation generator
- ✅ Web UI
- ✅ Documentation
- ✅ Examples
- 🔄 Testing & refinement
- 📋 More templates (coming soon)
- 📋 CLI interface (coming soon)

**Current Version**: 0.1.0 (Demo)

Ready to evolve? Run `cd agent-evolve && ./launch.sh`! 🚀
