"""Repair generated Rust code using compiler diagnostics."""
import re

from backend.agents.llm_client import call_llm
from backend.models import DiagnosticReport

SYSTEM_INSTRUCTION = """You are an expert Rust compiler diagnostic and repair engineer.
Fix the reported Rust error precisely. Return ONLY corrected Rust code inside a ```rust code block.
"""


class RepairAgent:
    """Agent responsible for targeted code repair."""

    def repair(self, python_code: str, failing_rust_code: str, diagnostic: DiagnosticReport) -> str:
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

Generate corrected Rust code addressing the diagnostic errors. Output ONLY Rust code inside a ```rust code block.
"""
        response = call_llm(prompt, system_instruction=SYSTEM_INSTRUCTION)
        match = re.search(r"```rust\s*(.*?)\s*```", response, re.DOTALL)
        if not match:
            match = re.search(r"```\s*(.*?)\s*```", response, re.DOTALL)
        return match.group(1).strip() if match else response.strip()
