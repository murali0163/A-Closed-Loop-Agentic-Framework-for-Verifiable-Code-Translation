"""Translate Python source into Rust using the configured language model."""
import re

from backend.agents.llm_client import call_llm

SYSTEM_INSTRUCTION = """You are an expert systems programmer specializing in modernizing legacy Python code to Rust.
Translate into idiomatic, efficient, memory-safe Rust. Return ONLY valid Rust source in a ```rust code block.
"""


class TranslatorAgent:
    """Agent responsible for initial Python-to-Rust translation."""

    def translate(self, python_code: str, file_context: str = "") -> str:
        prompt = f"""Translate the following Python code into idiomatic Rust code:

Source Python Code:
```python
{python_code}
```

Context / Function hints:
{file_context}

Return ONLY the Rust implementation inside ```rust code block.
"""
        return self._extract_code(call_llm(prompt, system_instruction=SYSTEM_INSTRUCTION))

    def _extract_code(self, raw_response: str) -> str:
        match = re.search(r"```rust\s*(.*?)\s*```", raw_response, re.DOTALL)
        if not match:
            match = re.search(r"```\s*(.*?)\s*```", raw_response, re.DOTALL)
        return match.group(1).strip() if match else raw_response.strip()
