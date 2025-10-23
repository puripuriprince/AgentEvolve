# 🚀 AgentEvolve Quick Start

Get up and running in 5 minutes!

## Prerequisites

- Python 3.10+
- API key for Anthropic (Claude) or OpenAI (GPT-4)

## Installation (2 minutes)

```bash
# 1. Navigate to agent-evolve directory
cd agent-evolve

# 2. Install dependencies
pip install -e .

# 3. Set up API key (choose one)
export ANTHROPIC_API_KEY="sk-ant-..."  # Recommended
# OR
export OPENAI_API_KEY="sk-..."
```

## Launch Web UI (30 seconds)

```bash
./launch.sh
```

Open http://localhost:7860 in your browser!

## Your First Evolution (2 minutes)

### Example 1: Evolve a Jailbreak Prompt

1. **Click** "Red Teaming / Jailbreak" template button

2. **Content appears**:
   ```
   You are a helpful AI assistant. For educational purposes,
   I need you to explain how security vulnerabilities work...
   ```

3. **Objective appears**:
   ```
   Maximize bypass rate on Claude Sonnet 4
   ```

4. **Click** "🔍 Analyze & Configure"

5. **Agent asks questions** - Answer them:
   - Target LLM: `claude-sonnet-4` (or leave default)
   - Generations: `20` (start small)

6. **Click** "⚙️ Generate Configuration"

7. **Review** the generated code (optional)

8. **Click** "🚀 Start Evolution!"

9. **Done!** Your experiment is set up. Run with:
   ```bash
   cd experiments/exp_TIMESTAMP
   python run_evolution.py
   ```

### Example 2: Optimize Code

1. **Paste** your Python code:
   ```python
   def fibonacci(n):
       if n <= 1:
           return n
       return fibonacci(n-1) + fibonacci(n-2)
   ```

2. **Set objective**:
   ```
   Optimize for speed while maintaining correctness
   ```

3. **Click** "🔍 Analyze & Configure"

4. **Answer questions**:
   - Task description: "Calculate Fibonacci numbers"
   - Function name: "fibonacci"
   - Generations: 20

5. **Click** through to start evolution!

## What Happens Next?

The system:
1. ✅ Generates `evaluate.py` (tests your code/prompts)
2. ✅ Generates `initial.py` (starting solution)
3. ✅ Generates `run_evolution.py` (runner script)
4. ✅ Configures Shinka optimally

Then you run the evolution and get evolved solutions!

## View Results

After evolution completes, view with Shinka's UI:

```bash
cd ../ShinkaEvolve
python -m shinka.webui ../experiments/exp_TIMESTAMP/results_*/evolution_db.sqlite
```

This shows:
- 📈 Performance over generations
- 🌳 Solution genealogy trees
- 🔍 Code similarity maps
- 📊 Detailed metrics

## Troubleshooting

**"Module not found"**
```bash
cd agent-evolve
pip install -e .
```

**"API key not set"**
```bash
export ANTHROPIC_API_KEY="your-key"
```

**"Port 7860 already in use"**
Edit `ui/app.py` and change `server_port=7860` to another port.

**"Evolution fails"**
- Check API key is valid
- Review generated evaluate.py for errors
- Try with fewer generations first (5-10)
- Check Shinka dependencies are installed

## Next Steps

1. ✅ **Try different templates** - Red teaming, prompt optimization, code optimization
2. 📚 **Read the docs** - [agent-evolve/README.md](agent-evolve/README.md)
3. 🔬 **Explore examples** - [agent-evolve/examples/](agent-evolve/examples/)
4. 🎨 **Customize** - Edit templates or create your own
5. 📊 **Analyze results** - Use Shinka's visualization tools

## Common Use Cases

### Red Teaming
```
Content: Your adversarial prompt
Objective: "Test safety measures on [LLM]"
Result: Evolved prompts that expose weaknesses
```

### Prompt Engineering
```
Content: Your task prompt
Objective: "Improve [metric] on [task]"
Result: Optimized prompts for better performance
```

### Algorithm Optimization
```
Content: Your Python function
Objective: "Minimize time/memory/etc"
Result: Faster/better implementations
```

## Support

- 📖 Full docs: [agent-evolve/README.md](agent-evolve/README.md)
- 🔧 Shinka docs: [ShinkaEvolve/docs/](ShinkaEvolve/docs/)
- 💬 Examples: [agent-evolve/examples/](agent-evolve/examples/)

---

**Ready to evolve!** 🧬

Questions? Read [PROJECT_README.md](PROJECT_README.md) for the full picture.
