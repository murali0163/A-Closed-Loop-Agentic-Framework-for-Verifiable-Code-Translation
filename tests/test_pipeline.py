"""
Unit tests for the Closed-Loop Agentic Code Translation Framework.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from models import DiagnosticReport, ErrorCategory, ExecutionResult
from agents.error_parser import parse_error_log
from sandbox.runner import SandboxRunner
from orchestrator import TranslationOrchestrator

def test_borrow_checker_error_parsing():
    raw_log = "error[E0382]: use of moved value: `arr` at Line 12"
    diag = parse_error_log(raw_log, is_compilation=True)
    assert diag.has_errors is True
    assert diag.error_category == ErrorCategory.BORROW_CHECKER
    assert "Borrow Checker" in diag.error_summary

def test_type_mismatch_error_parsing():
    raw_log = "error[E0308]: mismatched types expected `i32`, found `f64` at Line 8"
    diag = parse_error_log(raw_log, is_compilation=True)
    assert diag.has_errors is True
    assert diag.error_category == ErrorCategory.TYPE_MISMATCH

def test_sandbox_runner_execution():
    runner = SandboxRunner()
    valid_rust = '''fn add(a: i32, b: i32) -> i32 { a + b }'''
    result = runner.execute(valid_rust)
    assert result.compiled is True

def test_orchestrator_closed_loop():
    orchestrator = TranslationOrchestrator()
    code = "def add(a, b): return a + b"
    res = orchestrator.translate_and_verify(code, file_name="test_add.py")
    assert res.success is True
    assert res.total_iterations >= 1
