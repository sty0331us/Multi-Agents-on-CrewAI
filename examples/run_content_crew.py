# examples — thin scripts that call the public API

from content_crew.crew import run_pipeline
from content_crew.logging_setup import setup_logging


def main() -> None:
    setup_logging("INFO")
    result = run_pipeline(
        "Latest Generative AI breakthroughs",
        persist=True,
    )
    print("--- Final social output ---")
    print(result.final_output)
    if result.metadata.get("output_dir"):
        print(f"\nArtifacts: {result.metadata['output_dir']}")


if __name__ == "__main__":
    main()
