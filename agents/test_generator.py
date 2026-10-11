"""
Test Generation & Differential Testing Agent.
Generates Python tests, captures ground truth runtime behavior, and translates tests to Rust assertions.
"""
import sys
import io
import re
from typing import List, Dict, Any, Tuple
from agents.llm_client import call_llm

SYSTEM_INSTRUCTION = """You are a Quality Assurance & Testing Expert.
Your job is to generate comprehensive unit tests for a Python function and translate those unit tests into Rust `#[test]` functions.
Ensure test inputs cover typical cases, edge cases (empty inputs, zero, negative numbers), and boundary conditions.
"""

class TestGeneratorAgent:
    """Agent responsible for test generation and differential testing across languages."""

    def generate_rust_tests(self, python_code: str, rust_code: str) -> str:
        """Generates Rust unit test module matching Python source behavior."""
        prompt = f"""Target Function Python Code:
```python
{python_code}
```

Generated Rust Code:
```rust
{rust_code}
```

Generate a Rust test module `#[cfg(test)] mod tests {{ use super::*; ... }}` containing 3 to 5 unit tests for the functions above.
Cover standard cases and edge cases.
Output ONLY the Rust code for the test module inside a ```rust code block.
"""
        response_text = call_llm(prompt, system_instruction=SYSTEM_INSTRUCTION)
        return self._extract_code(response_text)

    def execute_python_differential(self, python_code: str, test_cases: List[Tuple[Any, Any]]) -> Dict[str, Any]:
        """Runs differential testing on Python source code to record ground truth outputs."""
        results = {}
        try:
            local_scope = {}
            exec(python_code, local_scope)
            results["success"] = True
            results["outputs"] = []
            # Find the main function in Python scope
            functions = [v for k, v in local_scope.items() if callable(v) and not k.startswith("__")]
            if functions:
                target_fn = functions[0]
                for inp, expected in test_cases:
                    actual = target_fn(*inp) if isinstance(inp, tuple) else target_fn(inp)
                    results["outputs"].append({"input": inp, "expected": expected, "actual": actual, "match": actual == expected})
        except Exception as e:
            results["success"] = False
            results["error"] = str(e)
        return results

    def _extract_code(self, raw_response: str) -> str:
        match = re.search(r"```rust\s*(.*?)\s*```", raw_response, re.DOTALL)
        if match:
            return match.group(1).strip()
        match_any = re.search(r"```\s*(.*?)\s*```", raw_response, re.DOTALL)
        if match_any:
            return match_any.group(1).strip()
        return raw_response.strip()
