"""
Data structures for multi-agent code translation, execution diagnostics, and repair loops.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

class ErrorCategory(str, Enum):
    SYNTAX_ERROR = "SYNTAX_ERROR"
    BORROW_CHECKER = "BORROW_CHECKER"
    TYPE_MISMATCH = "TYPE_MISMATCH"
    LIFETIME_ERROR = "LIFETIME_ERROR"
    ASSERTION_FAILURE = "ASSERTION_FAILURE"
    RUNTIME_PANIC = "RUNTIME_PANIC"
    UNKNOWN = "UNKNOWN"

@dataclass
class DiagnosticReport:
    """Structured report extracted from compiler/test error logs."""
    has_errors: bool
    error_category: ErrorCategory
    raw_error_log: str
    error_summary: str
    line_number: Optional[int] = None
    suggested_fix_hint: str = ""

@dataclass
class ExecutionResult:
    """Outcome of compiling and executing translated Rust code in the sandbox."""
    compiled: bool
    tests_passed: bool
    return_code: int
    stdout: str
    stderr: str
    diagnostics: DiagnosticReport

@dataclass
class IterationRecord:
    """Log of a single translation or repair iteration."""
    iteration: int
    rust_code: str
    execution_result: ExecutionResult
    repair_prompt_used: Optional[str] = None

@dataclass
class TranslationResult:
    """Final output of the closed-loop agentic translation process."""
    success: bool
    final_rust_code: str
    total_iterations: int
    history: List[IterationRecord] = field(default_factory=list)
    error_message: str = ""
