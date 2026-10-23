"""Parse compiler and test logs into structured diagnostics."""
import re

from backend.models import DiagnosticReport, ErrorCategory


def parse_error_log(raw_log: str, is_compilation: bool = True) -> DiagnosticReport:
    """Parse a rustc/test log into a structured diagnostic report."""
    if not raw_log or ("error" not in raw_log.lower() and "failed" not in raw_log.lower()):
        return DiagnosticReport(False, ErrorCategory.UNKNOWN, raw_log, "No errors reported.")

    if any(token in raw_log for token in ("E0382", "E0502", "moved value", "borrowed as mutable")):
        return DiagnosticReport(True, ErrorCategory.BORROW_CHECKER, raw_log,
            "Rust Borrow Checker Error: Value moved or double-borrowed.", _extract_line_number(raw_log),
            "Borrow the value using `&` or `&mut`, or implement `.clone()` / `.to_vec()` instead of transferring ownership.")
    if "E0308" in raw_log or "mismatched types" in raw_log or "expected" in raw_log:
        return DiagnosticReport(True, ErrorCategory.TYPE_MISMATCH, raw_log,
            "Type Mismatch Error: Expression type does not match function signature.", _extract_line_number(raw_log),
            "Cast numerical types explicitly, or convert Option/Result types with `unwrap()` / `?`.")
    if "E0106" in raw_log or "lifetime" in raw_log:
        return DiagnosticReport(True, ErrorCategory.LIFETIME_ERROR, raw_log,
            "Lifetime Error: Missing explicit lifetime specifier for references.", _extract_line_number(raw_log),
            "Add lifetime annotations or return an owned `String`/`Vec`.")
    if "assertion failed" in raw_log or "panicked at" in raw_log:
        return DiagnosticReport(True, ErrorCategory.ASSERTION_FAILURE, raw_log,
            "Test Assertion Failed: Output behavior differs from expected ground truth.",
            suggested_fix_hint="Check edge cases, zero-indexing, loop boundaries, and precision differences.")
    if "syntax" in raw_log.lower() or "unmatched" in raw_log.lower() or "expected one of" in raw_log:
        return DiagnosticReport(True, ErrorCategory.SYNTAX_ERROR, raw_log,
            "Syntax Error: Malformed Rust syntax or missing braces/semicolons.",
            suggested_fix_hint="Ensure proper braces, semicolons, and standard macro syntax.")
    return DiagnosticReport(True, ErrorCategory.UNKNOWN, raw_log, "Unclassified compilation/execution error.")


def _extract_line_number(log: str):
    match = re.search(r"--> solution\.rs:(\d+):\d+", log)
    if match:
        return int(match.group(1))
    match = re.search(r"Line (\d+)", log)
    return int(match.group(1)) if match else None
