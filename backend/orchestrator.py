"""Orchestrate translation, verification, diagnostics, and repair iterations."""
import sys

from backend.agents.repair_agent import RepairAgent
from backend.agents.test_generator import TestGeneratorAgent
from backend.agents.translator import TranslatorAgent
from backend.config import MAX_REPAIR_ATTEMPTS
from backend.models import ExecutionResult, IterationRecord, TranslationResult
from backend.sandbox.runner import SandboxRunner

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class TranslationOrchestrator:
    """Run the closed-loop multi-agent translation and verification process."""

    def __init__(self, max_attempts: int = MAX_REPAIR_ATTEMPTS):
        self.max_attempts = max_attempts
        self.translator = TranslatorAgent()
        self.test_generator = TestGeneratorAgent()
        self.repair_agent = RepairAgent()
        self.sandbox = SandboxRunner()

    def translate_and_verify(self, python_code: str, file_name: str = "script.py") -> TranslationResult:
        print(f"\n[Orchestrator] Starting translation pipeline for {file_name}...")
        history = []
        print("  [Step 1] Invoking Translator Agent...")
        current_rust = self.translator.translate(python_code, file_context=f"Source file: {file_name}")
        print("  [Step 2] Invoking Test Generation & Differential Testing Agent...")
        rust_tests = self.test_generator.generate_rust_tests(python_code, current_rust)

        for attempt in range(1, self.max_attempts + 1):
            print(f"\n--- [Iteration {attempt}/{self.max_attempts}] Verification ---")
            exec_result: ExecutionResult = self.sandbox.execute(current_rust, rust_tests)
            history.append(IterationRecord(attempt, current_rust, exec_result))
            if exec_result.compiled and exec_result.tests_passed:
                print(f"  [SUCCESS] Code compiled and passed all tests on iteration {attempt}!")
                return TranslationResult(True, current_rust, attempt, history)

            diag = exec_result.diagnostics
            print(f"  [FAILED] Iteration {attempt}: [{diag.error_category.value}] {diag.error_summary}")
            if diag.suggested_fix_hint:
                print(f"     Hint: {diag.suggested_fix_hint}")
            if attempt == self.max_attempts:
                print(f"  [WARNING] Reached max repair budget ({self.max_attempts} attempts). Terminating loop.")
                break
            print("  [Step 3] Invoking Repair Agent with diagnostic error trace...")
            current_rust = self.repair_agent.repair(python_code, current_rust, diag)

        return TranslationResult(False, current_rust, self.max_attempts, history,
            "Verification failed after max repair retries.")
