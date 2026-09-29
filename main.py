import argparse
import logging
from pathlib import Path

from src.pipeline import ask

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "logs" / "app.log"
RESULTS_FILE = BASE_DIR / "sample_results.md"

SAMPLE_QUESTIONS = [
    "Which products contain banana?",
    "How many products contain banana?",
    "Which products from brand NutriBite are supplied by Sharma Wholesale?",
    "What did Aarav Mehta order?",
    "Which vendor supplies the Smart Watch?",
    "Which customers bought products from the brand TechNova?",
    "How many products are in each category?",
    "Which products from brand GlowUp are supplied by GreenLeaf Traders?",
    "Who is the prime minister of India?",
]


def setup_logging():
    """Write logs to a file so the terminal stays clean."""
    LOG_FILE.parent.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8")],
    )


def chat():
    """Ask questions in the terminal until the user types exit."""
    print("Ask a question about the e-commerce graph. Type 'exit' to quit.")
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in ("exit", "quit"):
            break
        if not question:
            continue

        result = ask(question)
        print("\nCypher:", result["cypher"] or "NO_QUERY")
        print("Rows retrieved:", len(result["rows"]))
        print("Answer:", result["answer"])


def run_samples():
    """Run the sample questions and save the results to sample_results.md."""
    lines = ["# Sample questions and results", ""]

    for number, question in enumerate(SAMPLE_QUESTIONS, start=1):
        print(f"Running {number}/{len(SAMPLE_QUESTIONS)}: {question}")
        result = ask(question)
        lines += [
            f"## {number}. {question}",
            "",
            "**Cypher:**",
            "```cypher",
            result["cypher"] or "NO_QUERY",
            "```",
            "",
            f"**Rows retrieved:** {len(result['rows'])}",
            "",
            "**Answer:**",
            "",
            result["answer"],
            "",
        ]

    RESULTS_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved results to {RESULTS_FILE.name}")


def main():
    parser = argparse.ArgumentParser(description="Ask questions about the e-commerce knowledge graph.")
    parser.add_argument("--samples", action="store_true", help="run the sample questions and save the results")
    args = parser.parse_args()

    setup_logging()
    if args.samples:
        run_samples()
    else:
        chat()


if __name__ == "__main__":
    main()
    