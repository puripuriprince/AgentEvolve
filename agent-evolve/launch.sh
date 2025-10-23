#!/bin/bash
# Quick launch script for AgentEvolve

set -e

echo "🧬 AgentEvolve - LLM Evolution Made Easy"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "ui/app.py" ]; then
    echo "❌ Error: Please run this script from the agent-evolve directory"
    echo "   cd agent-evolve && ./launch.sh"
    exit 1
fi

# Check for API keys
if [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: No API keys found!"
    echo ""
    echo "Please set at least one of:"
    echo "  export ANTHROPIC_API_KEY='your-key'"
    echo "  export OPENAI_API_KEY='your-key'"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if dependencies are installed
if ! python -c "import gradio" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -e .
fi

echo ""
echo "🚀 Launching AgentEvolve UI..."
echo "   Open your browser to: http://localhost:7860"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python -m ui.app
