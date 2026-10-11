"""
Diagnostic Error Parser: Extracts structured diagnostics from compiler stdout/stderr & test failures.
"""
import re
from models import DiagnosticReport, ErrorCategory

def parse_error_log(raw_log: str, is_compilation: bool = True) -> DiagnosticReport:
    """Parses raw rustc error log into structured DiagnosticReport."""
    if not raw_log or "error" not in raw_log.lower() and "failed" not in raw_log.lower():
        return DiagnosticReport(
            has_errors=False,
            error_category=ErrorCategory.UNKNOWN,
            raw_error_log=raw_log,
            error_summary="No errors reported."
        )

    # 1. Check for Borrow Checker Errors (E0382, E0502, E0499, borrow of moved value)
    if "E0382" in raw_log or "E0502" in raw_log or "moved value" in raw_log or "borrowed as mutable" in raw_log:
        line_num = _extract_line_number(raw_log)
        return DiagnosticReport(
            has_errors=True,
            error_category=ErrorCategory.BORROW_CHECKER,
            raw_error_log=raw_log,
            error_summary="Rust Borrow Checker Error: Value moved or double-borrowed.",
            line_number=line_num,
            suggested_fix_hint="Borrow the value using `&` or `&mut`, or implement `.clone()` / `.to_vec()` instead of transferring ownership."
        )

    # 2. Check for Type Mismatch Errors (E0308, expected struct, found integer, etc.)
    if "E0308" in raw_log or "mismatched types" in raw_log or "expected" in raw_log:
        line_num = _extract_line_number(raw_log)
        return DiagnosticReport(
            has_errors=True,
            error_category=ErrorCategory.TYPE_MISMATCH,
            raw_error_log=raw_log,
            error_summary="Type Mismatch Error: Expression type does not match function signature.",
            line_number=line_num,
            suggested_fix_hint="Cast numerical types explicitly (e.g. `as i32`, `as usize`), or convert Option/Result types with `unwrap()` / `?` operator."
        )

    # 3. Check for Lifetime Specifier Errors (E0106, missing lifetime specifier)
    if "E0106" in raw_log or "lifetime" in raw_log:
        line_num = _extract_line_number(raw_log)
        return DiagnosticReport(
            has_errors=True,
            error_category=ErrorCategory.LIFETIME_ERROR,
            raw_error_log=raw_log,
            error_summary="Lifetime Error: Missing explicit lifetime specifier for references.",
            line_number=line_num,
            suggested_fix_hint="Add lifetime annotations like `'a` to reference parameters and return types, or return an owned `String`/`Vec`."
        )

    # 4. Check for Test Assertion Failures
    if "assertion failed" in raw_log or "panicked at" in raw_log:
        return DiagnosticReport(
            has_errors=True,
            error_category=ErrorCategory.ASSERTION_FAILURE,
            raw_error_log=raw_log,
            error_summary="Test Assertion Failed: Output behavior differs from expected ground truth.",
            suggested_fix_hint="Check logical edge cases, zero-indexing, loop boundaries, and precision differences."
        )

    # 5. Check for Syntax Errors
    if "syntax" in raw_log.lower() or "unmatched" in raw_log.lower() or "expected one of" in raw_log:
        return DiagnosticReport(
            has_errors=True,
            error_category=ErrorCategory.SYNTAX_ERROR,
            raw_error_log=raw_log,
            error_summary="Syntax Error: Malformed Rust syntax or missing braces/semicolons.",
            suggested_fix_hint="Ensure proper curly braces `{}`, semicolons `;`, and standard macro syntax `vec![]`."
        )

    return DiagnosticReport(
        has_errors=True,
        error_category=ErrorCategory.UNKNOWN,
        raw_error_log=raw_log,
        error_summary="Unclassified compilation/execution error."
    )

def _extract_line_number(log: str) -> int:
    match = re.search(r"--> solution\.rs:(\d+):\d+", log)
    if match:
        return int(match.group(1))
    match_line = re.search(r"Line (\d+)", log)
    if match_line:
        return int(match_line.group(1))
    return None
