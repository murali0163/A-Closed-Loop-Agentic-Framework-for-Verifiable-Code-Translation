"""
Evaluation runner for benchmarking Pass@1 vs Closed-Loop Pass@K performance.
"""
import os
import glob
from orchestrator import TranslationOrchestrator

def run_benchmark():
    benchmark_dir = os.path.join(os.path.dirname(__file__), "sample_python")
    py_files = glob.glob(os.path.join(benchmark_dir, "*.py"))
    
    if not py_files:
        print("No benchmark Python files found in", benchmark_dir)
        return

    orchestrator = TranslationOrchestrator(max_attempts=5)
    
    total_files = len(py_files)
    pass_at_1 = 0
    pass_at_k = 0
    total_iterations_used = 0

    print("==================================================================")
    print(f"   STARTING BENCHMARK EVALUATION ({total_files} Benchmark Files)")
    print("==================================================================")

    for py_file in py_files:
        file_name = os.path.basename(py_file)
        with open(py_file, "r", encoding="utf-8") as f:
            code = f.read()

        result = orchestrator.translate_and_verify(code, file_name=file_name)
        
        if result.success:
            pass_at_k += 1
            if result.total_iterations == 1:
                pass_at_1 += 1
        total_iterations_used += result.total_iterations

    print("\n==================================================================")
    print("                    EVALUATION SUMMARY REPORT                     ")
    print("==================================================================")
    print(f" Total Benchmark Scripts Tested: {total_files}")
    print(f" Baseline Single-Pass (Pass@1) : {pass_at_1}/{total_files} ({pass_at_1/total_files*100:.1f}%)")
    print(f" Closed-Loop Agentic (Pass@K)  : {pass_at_k}/{total_files} ({pass_at_k/total_files*100:.1f}%)")
    print(f" Average Repair Iterations     : {total_iterations_used/total_files:.2f}")
    print("==================================================================")

if __name__ == "__main__":
    run_benchmark()
