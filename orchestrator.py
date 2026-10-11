"""
Closed-Loop Multi-Agent Translation Orchestrator.
Manages the translation -> verification -> diagnostic error parsing -> repair iteration workflow.
"""
import sys
from typing import Optional
from models import TranslationResult, IterationRecord, ExecutionResult
from agents.translator import TranslatorAgent
from agents.test_generator import TestGeneratorAgent
from agents.repair_agent import RepairAgent
from sandbox.runner import SandboxRunner
from config import MAX_REPAIR_ATTEMPTS

# Ensure Windows stdout handles output cleanly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

class TranslationOrchestrator:
    """Orchestrates the closed-loop multi-agent translation and verification process."""

    def __init__(self, max_attempts: int = MAX_REPAIR_ATTEMPTS):
        self.max_attempts = max_attempts
        self.translator = TranslatorAgent()
        self.test_generator = TestGeneratorAgent()
        self.repair_agent = RepairAgent()
        self.sandbox = SandboxRunner()

    def translate_and_verify(self, python_code: str, file_name: str = "script.py") -> TranslationResult:
        """Runs closed-loop translation for a given Python code string."""
        print(f"\n[Orchestrator] Starting translation pipeline for {file_name}...")
        history = []
        
        # Step 1: Initial Translation
        print("  [Step 1] Invoking Translator Agent...")
        current_rust = self.translator.translate(python_code, file_context=f"Source file: {file_name}")
        
        # Step 2: Test Suite Generation & Differential Setup
        print("  [Step 2] Invoking Test Generation & Differential Testing Agent...")
        rust_tests = self.test_generator.generate_rust_tests(python_code, current_rust)

        # Iterative Closed-Loop Verification & Repair
        for attempt in range(1, self.max_attempts + 1):
            print(f"\n--- [Iteration {attempt}/{self.max_attempts}] Verification ---")
            exec_result: ExecutionResult = self.sandbox.execute(current_rust, rust_tests)
            
            record = IterationRecord(
                iteration=attempt,
                rust_code=current_rust,
                execution_result=exec_result
            )
            history.append(record)

            if exec_result.compiled and exec_result.tests_passed:
                print(f"  [SUCCESS] Code compiled and passed all tests on iteration {attempt}!")
                return TranslationResult(
                    success=True,
                    final_rust_code=current_rust,
                    total_iterations=attempt,
                    history=history
                )
            
            # Diagnostic Feedback
            diag = exec_result.diagnostics
            print(f"  [FAILED] Iteration {attempt}: [{diag.error_category.value}] {diag.error_summary}")
            if diag.suggested_fix_hint:
                print(f"     Hint: {diag.suggested_fix_hint}")

            if attempt == self.max_attempts:
                print(f"  [WARNING] Reached max repair budget ({self.max_attempts} attempts). Terminating loop.")
                break

            # Repair Step
            print("  [Step 3] Invoking Repair Agent with diagnostic error trace...")
            current_rust = self.repair_agent.repair(python_code, current_rust, diag)

        return TranslationResult(
            success=False,
            final_rust_code=current_rust,
            total_iterations=self.max_attempts,
            history=history,
            error_message="Verification failed after max repair retries."
        )
