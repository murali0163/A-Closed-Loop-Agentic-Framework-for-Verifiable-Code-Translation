"""
CLI Interface for A Closed-Loop Agentic Framework for Verifiable Code Translation.
"""
import sys
import argparse
from orchestrator import TranslationOrchestrator
from benchmark.evaluate import run_benchmark

def main():
    parser = argparse.ArgumentParser(
        description="Closed-Loop Agentic Framework for Verifiable Python -> Rust Code Translation"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: translate
    trans_parser = subparsers.add_parser("translate", help="Translate a single Python file to Rust")
    trans_parser.add_argument("file", help="Path to source Python file")
    trans_parser.add_argument("--output", "-o", help="Optional output path for saved Rust code")

    # Command: evaluate
    eval_parser = subparsers.add_parser("evaluate", help="Run benchmark suite and compute Pass@1 vs Pass@K metrics")

    args = parser.parse_args()

    if args.command == "translate":
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                python_code = f.read()
        except Exception as e:
            print(f"[ERROR] Could not read file {args.file}: {e}")
            sys.exit(1)

        orchestrator = TranslationOrchestrator()
        result = orchestrator.translate_and_verify(python_code, file_name=args.file)

        print("\n================ FINAL TRANSLATION RESULT ================")
        print(f" Status: {'SUCCESS' if result.success else 'FAILED'}")
        print(f" Iterations Required: {result.total_iterations}")
        print("---------------- Generated Rust Code ----------------")
        print(result.final_rust_code)
        print("=========================================================")

        if args.output:
            with open(args.output, "w", encoding="utf-8") as out_f:
                out_f.write(result.final_rust_code)
            print(f"[INFO] Saved translated Rust code to {args.output}")

    elif args.command == "evaluate":
        run_benchmark()

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
