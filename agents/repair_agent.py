"""
Repair Agent: Generates target patches for failing Rust code based on compiler diagnostics.
"""
import re
from models import DiagnosticReport
from agents.llm_client import call_llm

SYSTEM_INSTRUCTION = """You are an expert Rust compiler diagnostic and repair engineer.
Your job is to fix compilation errors, borrow-checker violations, lifetime mismatches, and test failures in generated Rust code.
Be precise: fix the specific error identified in the diagnostic trace without breaking existing valid logic.
Return ONLY the corrected Rust code inside a ```rust code block.
"""

class RepairAgent:
    """Agent responsible for targeted code repair using diagnostic feedback."""

    def repair(self, python_code: str, failing_rust_code: str, diagnostic: DiagnosticReport) -> str:
        """Generates repaired Rust code using compiler diagnostic trace."""
        prompt = f"""Original Python Code:
```python
{python_code}
```

Failing Rust Code:
```rust
{failing_rust_code}
```

Diagnostic Error Report:
- Error Category: {diagnostic.error_category.value}
- Summary: {diagnostic.error_summary}
- Line Number: {diagnostic.line_number or "N/A"}
- Fix Hint: {diagnostic.suggested_fix_hint}

Raw Error Trace:
```
{diagnostic.raw_error_log}
```

Generate a corrected, valid Rust implementation addressing the diagnostic errors.
Output ONLY the repaired Rust code inside a ```rust code block.
"""
        response_text = call_llm(prompt, system_instruction=SYSTEM_INSTRUCTION)
        return self._extract_code(response_text)

    def _extract_code(self, raw_response: str) -> str:
        match = re.search(r"```rust\s*(.*?)\s*```", raw_response, re.DOTALL)
        if match:
            return match.group(1).strip()
        match_any = re.search(r"```\s*(.*?)\s*```", raw_response, re.DOTALL)
        if match_any:
            return match_any.group(1).strip()
        return raw_response.strip()
