"""Command-line entrypoint for translation, benchmarking, and the web app."""
import argparse
import sys

from backend.benchmark.evaluate import run_benchmark
from backend.orchestrator import TranslationOrchestrator
from backend.web import serve


def main():
    parser = argparse.ArgumentParser(description="Python-to-Rust translation and verification framework")
    subparsers = parser.add_subparsers(dest="command")

    translate_parser = subparsers.add_parser("translate", help="Translate a Python file to Rust")
    translate_parser.add_argument("file", help="Python source file")
    translate_parser.add_argument("--output", "-o", help="Where to save generated Rust")
    subparsers.add_parser("evaluate", help="Run the benchmark suite")
    web_parser = subparsers.add_parser("serve", help="Start the frontend and backend web app")
    web_parser.add_argument("--host", default="127.0.0.1")
    web_parser.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()
    if args.command == "translate":
        try:
            with open(args.file, "r", encoding="utf-8") as source_file:
                source = source_file.read()
        except OSError as exc:
            print(f"[ERROR] Could not read {args.file}: {exc}")
            return 1
        result = TranslationOrchestrator().translate_and_verify(source, file_name=args.file)
        print("\n================ FINAL TRANSLATION RESULT ================")
        print(f" Status: {'SUCCESS' if result.success else 'FAILED'}")
        print(f" Iterations Required: {result.total_iterations}")
        print("---------------- Generated Rust Code ----------------")
        print(result.final_rust_code)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as output_file:
                output_file.write(result.final_rust_code)
            print(f"[INFO] Saved translated Rust code to {args.output}")
        return 0 if result.success else 1
    if args.command == "evaluate":
        run_benchmark()
    elif args.command == "serve":
        serve(args.host, args.port)
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
