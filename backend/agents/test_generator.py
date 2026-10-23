"""Generate Rust tests and provide Python differential execution helpers."""
import re

from backend.agents.llm_client import call_llm

SYSTEM_INSTRUCTION = """You are a quality assurance expert. Generate comprehensive unit tests for Python functions
and translate them into Rust #[test] functions, including edge cases.
"""


class TestGeneratorAgent:
    """Agent responsible for test generation and differential testing."""

    def generate_rust_tests(self, python_code: str, rust_code: str) -> str:
        prompt = f"""Target Function Python Code:
```python
{python_code}
```

Generated Rust Code:
```rust
{rust_code}
```

Generate a Rust test module #[cfg(test)] mod tests {{ use super::*; ... }} with 3 to 5 tests.
Output ONLY the test module inside a ```rust code block.
"""
        return self._extract_code(call_llm(prompt, system_instruction=SYSTEM_INSTRUCTION))

    def _extract_code(self, raw_response: str) -> str:
        match = re.search(r"```rust\s*(.*?)\s*```", raw_response, re.DOTALL)
        if not match:
            match = re.search(r"```\s*(.*?)\s*```", raw_response, re.DOTALL)
        return match.group(1).strip() if match else raw_response.strip()
