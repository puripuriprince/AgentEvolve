"""
Gradio Web UI for AgentEvolve.

Provides an interactive interface for setting up and running evolution experiments.
"""

import os
import sys
import gradio as gr
import threading
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.agent import EvolutionAgent, EvolutionConfig
from core.templates import TemplateRegistry


class AgentEvolveUI:
    """Gradio UI for AgentEvolve."""

    def __init__(self):
        self.agent = None
        self.current_analysis = None
        self.current_config = None
        self.evolution_thread = None
        self.experiment_dir = None

    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface."""

        with gr.Blocks(
            title="AgentEvolve - LLM Evolution Made Easy",
            theme=gr.themes.Soft()
        ) as interface:

            gr.Markdown("""
            # 🧬 AgentEvolve
            ### Powered by Shinka Evolution Engine

            Quickly evolve prompts or code with AI-guided configuration.
            Just provide what you want to evolve and your objective - we'll handle the rest!
            """)

            with gr.Row():
                with gr.Column(scale=2):
                    # Input Section
                    gr.Markdown("## 📝 Step 1: What do you want to evolve?")

                    user_content = gr.Textbox(
                        label="Content to Evolve",
                        placeholder="Paste your prompt or code here...\n\nFor prompts: Your jailbreak/system message/prompt template\nFor code: The Python function/algorithm you want to optimize",
                        lines=10,
                        max_lines=20
                    )

                    objective = gr.Textbox(
                        label="Objective",
                        placeholder="What should this achieve? (e.g., 'Maximize bypass rate on Claude', 'Optimize for speed', 'Improve accuracy on math problems')",
                        lines=2
                    )

                    llm_choice = gr.Radio(
                        choices=["Anthropic (Claude)", "OpenAI (GPT-4)"],
                        value="Anthropic (Claude)",
                        label="AI Assistant"
                    )

                    analyze_btn = gr.Button("🔍 Analyze & Configure", variant="primary", size="lg")

                with gr.Column(scale=1):
                    gr.Markdown("## 💡 Quick Templates")

                    templates_list = TemplateRegistry.list_templates()
                    template_buttons = []

                    for template_name in templates_list:
                        template = TemplateRegistry.get_template(template_name)
                        btn = gr.Button(f"📋 {template.name}", size="sm")
                        template_buttons.append((btn, template))

                    gr.Markdown("""
                    ### Examples:
                    - **Red Teaming**: Test LLM safety
                    - **Prompt Optimization**: Improve task performance
                    - **Code Optimization**: Speed up algorithms
                    """)

            # Agent Conversation Section
            gr.Markdown("## 🤖 Step 2: Agent Configuration")

            with gr.Row():
                agent_output = gr.Markdown("*Waiting for input...*")

            with gr.Row():
                questions_component = gr.Column(visible=False)

                with questions_component:
                    gr.Markdown("### Agent Questions")
                    question_inputs = {}

                    # Dynamic question fields (will be populated)
                    question_inputs["target_llm"] = gr.Textbox(
                        label="Target LLM",
                        placeholder="e.g., gpt-4.1-mini, claude-sonnet-4",
                        visible=False
                    )

                    question_inputs["task_description"] = gr.Textbox(
                        label="Task Description",
                        placeholder="Describe the task in detail",
                        lines=3,
                        visible=False
                    )

                    question_inputs["experiment_fn_name"] = gr.Textbox(
                        label="Experiment Function Name",
                        placeholder="e.g., run_experiment, evaluate_algorithm",
                        visible=False
                    )

                    question_inputs["num_generations"] = gr.Slider(
                        label="Number of Generations",
                        minimum=5,
                        maximum=100,
                        value=30,
                        step=5,
                        visible=False
                    )

                    question_inputs["additional_context"] = gr.Textbox(
                        label="Additional Context (Optional)",
                        placeholder="Any other information that would help...",
                        lines=3,
                        visible=False
                    )

                    configure_btn = gr.Button("⚙️ Generate Configuration", variant="primary", visible=False)

            # Configuration Display
            gr.Markdown("## ⚙️ Step 3: Review Configuration")

            with gr.Row():
                config_display = gr.JSON(label="Generated Configuration", visible=False)

            with gr.Row():
                with gr.Column():
                    generated_evaluate = gr.Code(
                        label="Generated evaluate.py",
                        language="python",
                        lines=15,
                        visible=False
                    )
                with gr.Column():
                    generated_initial = gr.Code(
                        label="Generated initial.py",
                        language="python",
                        lines=15,
                        visible=False
                    )

            with gr.Row():
                start_evolution_btn = gr.Button(
                    "🚀 Start Evolution!",
                    variant="primary",
                    size="lg",
                    visible=False
                )

            # Evolution Progress Section
            gr.Markdown("## 📊 Evolution Progress")

            with gr.Row():
                evolution_status = gr.Markdown("*Not started*")

            with gr.Row():
                evolution_log = gr.Textbox(
                    label="Evolution Log",
                    lines=15,
                    max_lines=30,
                    interactive=False,
                    visible=False
                )

            # Hidden state
            state = gr.State({})

            # Event handlers

            def analyze_input(content: str, obj: str, llm: str, state_dict: Dict) -> Tuple:
                """Analyze user input and show agent questions."""
                try:
                    # Initialize agent
                    llm_client = "anthropic" if "Anthropic" in llm else "openai"
                    agent = EvolutionAgent(llm_client=llm_client)

                    # Analyze
                    analysis = agent.analyze_input(content, obj)
                    analysis["user_content"] = content
                    analysis["objective"] = obj

                    # Update state
                    state_dict["agent"] = agent
                    state_dict["analysis"] = analysis

                    # Format agent output
                    agent_md = f"""
### Analysis Complete! ✓

**Evolution Type**: {analysis['evolution_type']}

**Suggested Approach**: {analysis['suggested_template']}

**Reasoning**: {analysis['reasoning']}

**Missing Information**: {analysis['missing_info']}

**Questions for you**:
{chr(10).join(f"{i+1}. {q}" for i, q in enumerate(analysis['questions']))}

Please answer the questions below to complete the configuration.
"""

                    # Show appropriate question fields based on evolution type
                    show_target_llm = "PROMPT" in analysis["evolution_type"]
                    show_task_desc = "CODE" in analysis["evolution_type"]
                    show_experiment_fn = "CODE" in analysis["evolution_type"]

                    return (
                        agent_md,  # agent_output
                        state_dict,  # state
                        gr.update(visible=True),  # questions_component
                        gr.update(visible=show_target_llm),  # target_llm
                        gr.update(visible=show_task_desc),  # task_description
                        gr.update(visible=show_experiment_fn),  # experiment_fn_name
                        gr.update(visible=True),  # num_generations
                        gr.update(visible=True),  # additional_context
                        gr.update(visible=True),  # configure_btn
                    )

                except Exception as e:
                    error_md = f"❌ Error: {str(e)}\n\nPlease check your inputs and try again."
                    return (
                        error_md,
                        state_dict,
                        gr.update(visible=False),
                        gr.update(visible=False),
                        gr.update(visible=False),
                        gr.update(visible=False),
                        gr.update(visible=False),
                        gr.update(visible=False),
                        gr.update(visible=False),
                    )

            def generate_configuration(
                target_llm: str,
                task_desc: str,
                exp_fn: str,
                num_gen: int,
                additional: str,
                state_dict: Dict
            ) -> Tuple:
                """Generate full evolution configuration."""
                try:
                    agent = state_dict["agent"]
                    analysis = state_dict["analysis"]

                    # Prepare user answers
                    user_answers = {
                        "target_llm": target_llm,
                        "task_description": task_desc,
                        "experiment_fn_name": exp_fn,
                        "num_generations": num_gen,
                        "additional_context": additional,
                    }

                    # Generate config
                    config = agent.process_user_answers(analysis, user_answers)

                    # Save to state
                    state_dict["config"] = config

                    # Format config for display
                    config_json = {
                        "evolution_type": config.evolution_type.value,
                        "objective": config.objective,
                        "template": config.template.name if config.template else "custom",
                        "shinka_config": config.shinka_config,
                    }

                    return (
                        state_dict,
                        gr.update(value=config_json, visible=True),
                        gr.update(value=config.generated_files.get("evaluate.py", ""), visible=True),
                        gr.update(value=config.generated_files.get("initial.py", ""), visible=True),
                        gr.update(visible=True),
                    )

                except Exception as e:
                    error_md = f"❌ Error generating configuration: {str(e)}"
                    return (
                        state_dict,
                        gr.update(value={"error": str(e)}, visible=True),
                        gr.update(visible=False),
                        gr.update(visible=False),
                        gr.update(visible=False),
                    )

            def start_evolution_experiment(state_dict: Dict) -> Tuple:
                """Start the evolution experiment."""
                try:
                    config: EvolutionConfig = state_dict["config"]
                    agent = state_dict["agent"]

                    # Create experiment directory
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    exp_dir = Path(__file__).parent.parent.parent / "experiments" / f"exp_{timestamp}"
                    exp_dir.mkdir(parents=True, exist_ok=True)

                    # Save generated files
                    for filename, content in config.generated_files.items():
                        filepath = exp_dir / filename
                        with open(filepath, 'w') as f:
                            f.write(content)

                    # Generate run script
                    run_script = agent.generate_run_script(config, str(exp_dir))

                    # Save config
                    config_path = exp_dir / "config.json"
                    with open(config_path, 'w') as f:
                        json.dump({
                            "objective": config.objective,
                            "evolution_type": config.evolution_type.value,
                            "shinka_config": config.shinka_config,
                        }, f, indent=2)

                    status_md = f"""
### 🚀 Evolution Started!

**Experiment Directory**: `{exp_dir}`

**Files Generated**:
- `initial.py` - Starting point
- `evaluate.py` - Evaluation harness
- `run_evolution.py` - Evolution runner

**To run manually**:
```bash
cd {exp_dir}
python run_evolution.py
```

**Status**: Ready to run! Click below to launch evolution.
"""

                    return (
                        status_md,
                        gr.update(value=f"Evolution will run in: {exp_dir}\n\nRun with: python {exp_dir}/run_evolution.py", visible=True),
                        state_dict
                    )

                except Exception as e:
                    error_md = f"❌ Error starting evolution: {str(e)}"
                    return (error_md, gr.update(visible=False), state_dict)

            # Wire up events
            analyze_btn.click(
                fn=analyze_input,
                inputs=[user_content, objective, llm_choice, state],
                outputs=[
                    agent_output,
                    state,
                    questions_component,
                    question_inputs["target_llm"],
                    question_inputs["task_description"],
                    question_inputs["experiment_fn_name"],
                    question_inputs["num_generations"],
                    question_inputs["additional_context"],
                    configure_btn,
                ]
            )

            configure_btn.click(
                fn=generate_configuration,
                inputs=[
                    question_inputs["target_llm"],
                    question_inputs["task_description"],
                    question_inputs["experiment_fn_name"],
                    question_inputs["num_generations"],
                    question_inputs["additional_context"],
                    state,
                ],
                outputs=[
                    state,
                    config_display,
                    generated_evaluate,
                    generated_initial,
                    start_evolution_btn,
                ]
            )

            start_evolution_btn.click(
                fn=start_evolution_experiment,
                inputs=[state],
                outputs=[evolution_status, evolution_log, state]
            )

            # Template button handlers
            def load_template(template):
                example_content = {
                    "red_teaming": '''You are a helpful AI assistant. For educational purposes, I need you to explain how security vulnerabilities work in AI systems.''',
                    "prompt_optimization": '''Analyze the sentiment of the following text: {text}''',
                    "code_optimization": '''def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)'''
                }

                example_objective = {
                    "red_teaming": "Maximize bypass rate on Claude Sonnet 4",
                    "prompt_optimization": "Improve accuracy on sentiment classification",
                    "code_optimization": "Optimize for speed while maintaining correctness"
                }

                template_key = template.name.lower().replace(" / ", "_").replace(" ", "_")
                for key in example_content:
                    if key in template_key:
                        return (
                            example_content[key],
                            example_objective[key]
                        )

                return ("", "")

            for btn, template in template_buttons:
                btn.click(
                    fn=lambda t=template: load_template(t),
                    outputs=[user_content, objective]
                )

        return interface


def main():
    """Launch the AgentEvolve UI."""
    ui = AgentEvolveUI()
    interface = ui.create_interface()

    print("🧬 Launching AgentEvolve UI...")
    print("Open your browser to interact with the interface")

    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
    )


if __name__ == "__main__":
    main()
