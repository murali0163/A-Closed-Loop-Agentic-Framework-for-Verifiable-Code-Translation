"""
Translator Agent: Converts Python source code into memory-safe, idiomatic Rust.
"""
import re
from agents.llm_client import call_llm

SYSTEM_INSTRUCTION = """You are an expert systems programmer specializing in modernizing legacy Python code to Rust.
Your task is to translate Python code into idiomatic, efficient, and memory-safe Rust code.
Follow these strict guidelines:
1. Provide valid, compilable Rust code.
2. Use appropriate Rust types (e.g. Vec<T>, Option<T>, HashMap<K, V>, &str, String).
3. Be mindful of Rust's ownership, borrowing, and lifetime rules.
4. Output ONLY the Rust source code inside a standard ```rust code block.
"""

class TranslatorAgent:
    """Agent responsible for initial Python -> Rust translation."""

    def translate(self, python_code: str, file_context: str = "") -> str:
        """Translates Python code to Rust using LLM."""
        prompt = f"""Translate the following Python code into idiomatic Rust code:

Source Python Code:
```python
{python_code}
```

Context / Function hints:
{file_context}

Return ONLY the Rust implementation inside ```rust code block.
"""
        response_text = call_llm(prompt, system_instruction=SYSTEM_INSTRUCTION)
        return self._extract_code(response_text)

    def _extract_code(self, raw_response: str) -> str:
        """Extracts clean Rust code from markdown fences."""
        match = re.search(r"```rust\s*(.*?)\s*```", raw_response, re.DOTALL)
        if match:
            return match.group(1).strip()
        match_any = re.search(r"```\s*(.*?)\s*```", raw_response, re.DOTALL)
        if match_any:
            return match_any.group(1).strip()
        return raw_response.strip()
