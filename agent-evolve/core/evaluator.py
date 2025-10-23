"""
Auto-generates evaluation functions based on user objectives.

Uses LLM to create evaluation code for prompt or code evolution.
"""

import os
from typing import Dict, Any, Optional
from anthropic import Anthropic
from openai import OpenAI


class EvaluatorGenerator:
    """Generates evaluation code using LLM assistance."""

    def __init__(self, llm_client: str = "anthropic"):
        """
        Initialize the evaluator generator.

        Args:
            llm_client: Which LLM to use ("anthropic" or "openai")
        """
        self.llm_client = llm_client

        if llm_client == "anthropic":
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        elif llm_client == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            raise ValueError(f"Unknown LLM client: {llm_client}")

    def generate_prompt_evaluator(
        self,
        objective: str,
        target_llm: str,
        user_content: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate evaluation code for prompt evolution.

        Args:
            objective: What the prompts should achieve
            target_llm: Which LLM to test against
            user_content: The initial prompt(s) provided by user
            additional_context: Additional guidance from user

        Returns:
            Dict with 'evaluate.py' and 'initial.py' code
        """

        system_prompt = """You are an expert at creating evaluation code for prompt evolution systems.

Your task is to generate two Python files:
1. evaluate.py - The evaluation harness that scores prompts
2. initial.py - The initial prompt(s) wrapped in EVOLVE-BLOCK markers

The evaluation code should:
- Test prompts against the target LLM
- Determine if the objective was achieved
- Return metrics including success rate and confidence
- Be robust and handle errors gracefully

Follow these requirements:
- Use the user's objective to determine success criteria
- Generate realistic evaluation logic
- Include helper functions for LLM calls and scoring
- Return standardized metrics for Shinka"""

        user_prompt = f"""Generate evaluation code for prompt evolution with these specifications:

OBJECTIVE: {objective}

TARGET LLM: {target_llm}

USER'S INITIAL CONTENT:
```
{user_content}
```

{f"ADDITIONAL CONTEXT: {additional_context}" if additional_context else ""}

Please generate:

1. **evaluate.py**: Complete evaluation script that includes:
   - get_llm_response(prompt, model) function
   - evaluate_objective(response, objective) function that returns {{"is_success": bool, "confidence": float}}
   - main() function compatible with argparse

2. **initial.py**: The initial prompts in the correct format:
```python
# EVOLVE-BLOCK-START
ADVERSARIAL_PROMPTS = [
    # prompts here
]
# EVOLVE-BLOCK-END

def run_prompt_test(num_test_scenarios: int = 3) -> tuple:
    # evaluation logic
    return (success_rate, avg_confidence, num_prompts, num_tests)
```

Make the evaluation realistic and appropriate for the objective.

Return your response in this format:
===EVALUATE.PY===
[code here]
===INITIAL.PY===
[code here]
===END==="""

        # Call LLM
        if self.llm_client == "anthropic":
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            generated_code = response.content[0].text
        else:  # openai
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=4000
            )
            generated_code = response.choices[0].message.content

        # Parse the response
        return self._parse_generated_code(generated_code)

    def generate_code_evaluator(
        self,
        objective: str,
        task_description: str,
        user_code: str,
        experiment_fn_name: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate evaluation code for algorithm/code evolution.

        Args:
            objective: What to optimize for
            task_description: Description of the task
            user_code: The initial code to evolve
            experiment_fn_name: Name of the function to call for evaluation
            additional_context: Additional guidance

        Returns:
            Dict with 'evaluate.py' and 'initial.py' code
        """

        system_prompt = """You are an expert at creating evaluation code for algorithm evolution systems.

Your task is to generate two Python files:
1. evaluate.py - The evaluation harness using Shinka's run_shinka_eval
2. initial.py - The initial algorithm wrapped in EVOLVE-BLOCK markers

The evaluation code should:
- Use Shinka's run_shinka_eval function
- Define validation and metric aggregation functions
- Test the algorithm thoroughly
- Return appropriate performance metrics"""

        user_prompt = f"""Generate evaluation code for algorithm evolution with these specifications:

OBJECTIVE: {objective}

TASK DESCRIPTION: {task_description}

USER'S INITIAL CODE:
```python
{user_code}
```

{f"EXPERIMENT FUNCTION NAME: {experiment_fn_name}" if experiment_fn_name else ""}
{f"ADDITIONAL CONTEXT: {additional_context}" if additional_context else ""}

Please generate:

1. **evaluate.py**: Complete evaluation script using Shinka's framework:
```python
from shinka.core import run_shinka_eval

def main(program_path: str, results_dir: str):
    metrics, correct, error_msg = run_shinka_eval(
        program_path=program_path,
        results_dir=results_dir,
        experiment_fn_name="...",
        num_runs=...,
        get_experiment_kwargs=get_experiment_kwargs,
        validate_fn=validate_result,
        aggregate_metrics_fn=aggregate_metrics,
    )
    # return logic

def validate_result(run_output) -> tuple:
    # validation logic
    return is_valid, error_msg

def aggregate_metrics(results, results_dir) -> dict:
    # return {{"combined_score": ..., "public": {{}}, "private": {{}}}}
```

2. **initial.py**: The initial code with EVOLVE-BLOCK markers:
```python
# EVOLVE-BLOCK-START
def your_algorithm():
    # code to evolve
    pass
# EVOLVE-BLOCK-END

def experiment_function(**kwargs):
    # entry point for evaluation
    result = your_algorithm()
    return result
```

Make the evaluation appropriate for the objective and task.

Return your response in this format:
===EVALUATE.PY===
[code here]
===INITIAL.PY===
[code here]
===END==="""

        # Call LLM
        if self.llm_client == "anthropic":
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            generated_code = response.content[0].text
        else:  # openai
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=4000
            )
            generated_code = response.choices[0].message.content

        # Parse the response
        return self._parse_generated_code(generated_code)

    def _parse_generated_code(self, generated_text: str) -> Dict[str, str]:
        """Parse the generated code into separate files."""
        result = {}

        try:
            # Split by markers
            parts = generated_text.split("===")

            # Find evaluate.py
            for i, part in enumerate(parts):
                if "EVALUATE.PY" in part.upper():
                    if i + 1 < len(parts):
                        result["evaluate.py"] = parts[i + 1].strip()

                elif "INITIAL.PY" in part.upper():
                    if i + 1 < len(parts):
                        # Extract until next === or END
                        code = parts[i + 1]
                        if "===" in code:
                            code = code.split("===")[0]
                        result["initial.py"] = code.strip()

            # Fallback: try to extract code blocks
            if not result:
                import re
                code_blocks = re.findall(r"```python\n(.*?)```", generated_text, re.DOTALL)
                if len(code_blocks) >= 2:
                    result["evaluate.py"] = code_blocks[0]
                    result["initial.py"] = code_blocks[1]

        except Exception as e:
            raise ValueError(f"Failed to parse generated code: {e}\n\nGenerated text:\n{generated_text}")

        if "evaluate.py" not in result or "initial.py" not in result:
            raise ValueError(f"Could not find both files in generated code.\n\nGenerated text:\n{generated_text}")

        return result

    def save_evaluator(self, code_dict: Dict[str, str], output_dir: str):
        """Save generated evaluation code to files."""
        os.makedirs(output_dir, exist_ok=True)

        for filename, code in code_dict.items():
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w') as f:
                f.write(code)

        print(f"✓ Generated evaluation code saved to {output_dir}/")
