"""
AI Agent that helps configure evolution experiments.

Analyzes user input, asks clarifying questions, and generates
optimal Shinka configurations.
"""

import os
import re
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from anthropic import Anthropic
from openai import OpenAI

from .templates import TemplateRegistry, EvolutionType, EvolutionTemplate
from .evaluator import EvaluatorGenerator


@dataclass
class EvolutionConfig:
    """Configuration for an evolution experiment."""

    evolution_type: EvolutionType
    objective: str
    user_content: str
    template: Optional[EvolutionTemplate]
    evaluation_strategy: str
    shinka_config: Dict[str, Any]
    generated_files: Dict[str, str]


class EvolutionAgent:
    """AI agent that helps users configure evolution experiments."""

    def __init__(self, llm_client: str = "anthropic"):
        """
        Initialize the evolution agent.

        Args:
            llm_client: Which LLM to use ("anthropic" or "openai")
        """
        self.llm_client = llm_client

        if llm_client == "anthropic":
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.model = "claude-sonnet-4-20250514"
        elif llm_client == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = "gpt-4"
        else:
            raise ValueError(f"Unknown LLM client: {llm_client}")

        self.evaluator_generator = EvaluatorGenerator(llm_client)
        self.conversation_history = []

    def analyze_input(self, user_content: str, objective: str) -> Dict[str, Any]:
        """
        Analyze user's input to determine what they want to evolve.

        Args:
            user_content: The code/prompt they want to evolve
            objective: What they want to achieve

        Returns:
            Analysis dict with evolution_type, suggestions, questions
        """

        system_prompt = """You are an expert AI assistant helping users set up evolution experiments using the Shinka framework.

Your job is to analyze what the user wants to evolve and provide:
1. Determine if it's PROMPT evolution or CODE evolution
2. Suggest the most appropriate template (red_teaming, prompt_optimization, or code_optimization)
3. Identify what information is missing to set up evaluation
4. Ask 1-3 specific clarifying questions

Be concise and helpful. Focus on getting the information needed to create an effective evaluation function."""

        user_prompt = f"""Analyze this evolution request:

USER'S CONTENT TO EVOLVE:
```
{user_content}
```

USER'S OBJECTIVE:
{objective}

Please provide your analysis in this format:

EVOLUTION_TYPE: [PROMPT or CODE]
SUGGESTED_TEMPLATE: [red_teaming, prompt_optimization, or code_optimization]
REASONING: [Brief explanation of why]
MISSING_INFO: [What information do you need to create evaluation?]
QUESTIONS: [1-3 specific questions to ask the user]

Example questions:
- For red teaming: "Which LLM should we test against?" "How do we know if a bypass succeeded?"
- For prompt optimization: "Do you have test cases?" "How should responses be scored?"
- For code optimization: "What's the performance metric?" "What function should we call?"

Be specific and actionable."""

        # Call LLM
        response_text = self._call_llm(system_prompt, user_prompt)

        # Parse response
        analysis = self._parse_analysis(response_text)

        self.conversation_history.append({
            "role": "agent",
            "content": response_text,
            "analysis": analysis
        })

        return analysis

    def process_user_answers(
        self,
        initial_analysis: Dict[str, Any],
        user_answers: Dict[str, str]
    ) -> EvolutionConfig:
        """
        Process user's answers and generate complete evolution configuration.

        Args:
            initial_analysis: The initial analysis from analyze_input
            user_answers: User's answers to the questions

        Returns:
            Complete EvolutionConfig ready to run
        """

        # Get the template
        template_name = initial_analysis["suggested_template"]
        template = TemplateRegistry.get_template(template_name)

        if not template:
            raise ValueError(f"Template not found: {template_name}")

        # Generate evaluation code
        evolution_type = initial_analysis["evolution_type"]
        user_content = initial_analysis["user_content"]
        objective = initial_analysis["objective"]

        if evolution_type == "PROMPT":
            # Generate prompt evaluation
            target_llm = user_answers.get("target_llm", "gpt-4.1-mini")
            additional_context = user_answers.get("additional_context", "")

            generated_files = self.evaluator_generator.generate_prompt_evaluator(
                objective=objective,
                target_llm=target_llm,
                user_content=user_content,
                additional_context=additional_context
            )

            shinka_config = self._create_shinka_config_prompt(
                template=template,
                objective=objective,
                target_llm=target_llm,
                user_answers=user_answers
            )

        else:  # CODE
            # Generate code evaluation
            task_description = user_answers.get("task_description", objective)
            experiment_fn_name = user_answers.get("experiment_fn_name", "run_experiment")
            additional_context = user_answers.get("additional_context", "")

            generated_files = self.evaluator_generator.generate_code_evaluator(
                objective=objective,
                task_description=task_description,
                user_code=user_content,
                experiment_fn_name=experiment_fn_name,
                additional_context=additional_context
            )

            shinka_config = self._create_shinka_config_code(
                template=template,
                objective=objective,
                task_description=task_description,
                user_answers=user_answers
            )

        return EvolutionConfig(
            evolution_type=EvolutionType(evolution_type.lower()),
            objective=objective,
            user_content=user_content,
            template=template,
            evaluation_strategy=user_answers.get("evaluation_strategy", "auto-generated"),
            shinka_config=shinka_config,
            generated_files=generated_files
        )

    def _create_shinka_config_prompt(
        self,
        template: EvolutionTemplate,
        objective: str,
        target_llm: str,
        user_answers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create Shinka configuration for prompt evolution."""

        # Start with template defaults
        config = template.default_config.copy()

        # Customize based on user answers
        task_sys_msg = template.render_task_msg(
            objective=objective,
            target_llm=target_llm
        )

        return {
            "evo_config": {
                "task_sys_msg": task_sys_msg,
                "num_generations": user_answers.get("num_generations", config["num_generations"]),
                "max_parallel_jobs": config["max_parallel_jobs"],
                "llm_models": config["llm_models"],
                "patch_types": config["patch_types"],
                "patch_type_probs": config["patch_type_probs"],
                "language": "python",
                "init_program_path": "initial.py",
            },
            "db_config": {
                "num_islands": config["num_islands"],
                "archive_size": config["archive_size"],
                "elite_selection_ratio": 0.3,
                "num_archive_inspirations": 3,
                "num_top_k_inspirations": 2,
            },
            "job_config": {
                "eval_program_path": "evaluate.py",
            }
        }

    def _create_shinka_config_code(
        self,
        template: EvolutionTemplate,
        objective: str,
        task_description: str,
        user_answers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create Shinka configuration for code evolution."""

        # Start with template defaults
        config = template.default_config.copy()

        # Customize based on user answers
        task_sys_msg = template.render_task_msg(
            objective=objective,
            task_description=task_description
        )

        return {
            "evo_config": {
                "task_sys_msg": task_sys_msg,
                "num_generations": user_answers.get("num_generations", config["num_generations"]),
                "max_parallel_jobs": config["max_parallel_jobs"],
                "llm_models": config["llm_models"],
                "patch_types": config["patch_types"],
                "patch_type_probs": config["patch_type_probs"],
                "language": "python",
                "init_program_path": "initial.py",
            },
            "db_config": {
                "num_islands": config["num_islands"],
                "archive_size": config["archive_size"],
                "elite_selection_ratio": 0.3,
                "num_archive_inspirations": 3,
                "num_top_k_inspirations": 2,
            },
            "job_config": {
                "eval_program_path": "evaluate.py",
            }
        }

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call the LLM and return response text."""

        if self.llm_client == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text
        else:  # openai
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000
            )
            return response.choices[0].message.content

    def _parse_analysis(self, response_text: str) -> Dict[str, Any]:
        """Parse the agent's analysis response."""

        analysis = {
            "evolution_type": "",
            "suggested_template": "",
            "reasoning": "",
            "missing_info": "",
            "questions": []
        }

        # Extract evolution type
        evo_type_match = re.search(r"EVOLUTION_TYPE:\s*\[?(\w+)\]?", response_text, re.IGNORECASE)
        if evo_type_match:
            analysis["evolution_type"] = evo_type_match.group(1).upper()

        # Extract template
        template_match = re.search(r"SUGGESTED_TEMPLATE:\s*\[?(\w+)\]?", response_text, re.IGNORECASE)
        if template_match:
            analysis["suggested_template"] = template_match.group(1).lower()

        # Extract reasoning
        reasoning_match = re.search(r"REASONING:\s*(.+?)(?=MISSING_INFO:|QUESTIONS:|$)", response_text, re.IGNORECASE | re.DOTALL)
        if reasoning_match:
            analysis["reasoning"] = reasoning_match.group(1).strip()

        # Extract missing info
        missing_match = re.search(r"MISSING_INFO:\s*(.+?)(?=QUESTIONS:|$)", response_text, re.IGNORECASE | re.DOTALL)
        if missing_match:
            analysis["missing_info"] = missing_match.group(1).strip()

        # Extract questions
        questions_match = re.search(r"QUESTIONS:\s*(.+)$", response_text, re.IGNORECASE | re.DOTALL)
        if questions_match:
            questions_text = questions_match.group(1).strip()
            # Split by line and extract questions
            lines = questions_text.split('\n')
            for line in lines:
                line = line.strip()
                # Remove bullet points, dashes, numbers
                line = re.sub(r'^[-*\d.)\]]+\s*', '', line)
                if line and len(line) > 10:  # Reasonable question length
                    analysis["questions"].append(line)

        # Include full response for debugging
        analysis["full_response"] = response_text

        return analysis

    def generate_run_script(self, config: EvolutionConfig, output_dir: str) -> str:
        """Generate a run script for the evolution experiment."""

        script = f"""#!/usr/bin/env python3
'''
Auto-generated evolution runner script.
Generated by AgentEvolve.

Objective: {config.objective}
Evolution Type: {config.evolution_type.value}
'''

import sys
import os

# Add Shinka to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'ShinkaEvolve'))

from shinka.core import EvolutionRunner, EvolutionConfig
from shinka.database import DatabaseConfig
from shinka.launch import LocalJobConfig


def main():
    '''Run the evolution experiment.'''

    # Job configuration
    job_config = LocalJobConfig(
        eval_program_path="{config.shinka_config['job_config']['eval_program_path']}"
    )

    # Database configuration
    db_config = DatabaseConfig(
        num_islands={config.shinka_config['db_config']['num_islands']},
        archive_size={config.shinka_config['db_config']['archive_size']},
        elite_selection_ratio={config.shinka_config['db_config']['elite_selection_ratio']},
        num_archive_inspirations={config.shinka_config['db_config']['num_archive_inspirations']},
        num_top_k_inspirations={config.shinka_config['db_config']['num_top_k_inspirations']},
    )

    # Evolution configuration
    evo_config = EvolutionConfig(
        task_sys_msg='''{{config.shinka_config['evo_config']['task_sys_msg']}}''',
        num_generations={config.shinka_config['evo_config']['num_generations']},
        max_parallel_jobs={config.shinka_config['evo_config']['max_parallel_jobs']},
        llm_models={config.shinka_config['evo_config']['llm_models']},
        patch_types={config.shinka_config['evo_config']['patch_types']},
        patch_type_probs={config.shinka_config['evo_config']['patch_type_probs']},
        language="{config.shinka_config['evo_config']['language']}",
        init_program_path="{config.shinka_config['evo_config']['init_program_path']}",
    )

    # Run evolution
    print("🧬 Starting evolution experiment...")
    print(f"Objective: {config.objective}")
    print(f"Generations: {{evo_config.num_generations}}")
    print()

    runner = EvolutionRunner(
        evo_config=evo_config,
        job_config=job_config,
        db_config=db_config,
        verbose=True,
    )

    runner.run()

    print()
    print("✓ Evolution complete!")
    print(f"Results saved to: {{os.path.dirname(__file__)}}/results_*/")


if __name__ == "__main__":
    main()
"""

        script_path = os.path.join(output_dir, "run_evolution.py")
        with open(script_path, 'w') as f:
            f.write(script)

        os.chmod(script_path, 0o755)  # Make executable

        return script_path
