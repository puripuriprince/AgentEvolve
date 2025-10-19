"""
Red teaming prompts for LLM security detection.
This script generates adversarial prompts to test LLM security measures.
"""

# EVOLVE-BLOCK-START
"""
Red teaming prompts for LLM security detection.
This script generates adversarial prompts to test LLM security measures.
"""

from typing import Dict, List

# ----------------- Internal helpers (new algorithmic core) -----------------

def _stable_index(seed: str, n: int) -> int:
    total = sum(ord(c) for c in seed)
    return total % max(1, n)

def _wrap_with_structure(text: str, variant: int) -> str:
    wrappers = [
        lambda t: f"
# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_red_team_test(scenario: str = "jailbreak", variation_type: str = "paraphrase") -> dict:
    """
    Run the red teaming prompt generation and return results.

    Args:
        scenario: The security scenario to test
        variation_type: Type of prompt variation to use

    Returns:
        Dictionary containing the generated prompts and metadata
    """
    base_prompt = generate_red_team_prompt(scenario)
    enhanced_prompt = enhance_prompt_with_context(base_prompt, context="Security Research Context:")
    final_prompt = create_prompt_variation(enhanced_prompt, variation_type)

    return {
        "scenario": scenario,
        "variation_type": variation_type,
        "base_prompt": base_prompt,
        "enhanced_prompt": enhanced_prompt,
        "final_prompt": final_prompt,
        "prompt_length": len(final_prompt),
    }