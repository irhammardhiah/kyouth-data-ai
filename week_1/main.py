from pathlib import Path
import sys
from src.ingestor import ingest_all_mhtml
from src.processor import process_all_html
from src.loader import load_all_json
from src.profiler import run_data_profile

SOURCE_DIR = Path("data/0_source")
BRONZE_DIR = Path("data/1_bronze")
SILVER_DIR = Path("data/2_silver")
GOLD_DIR = Path("data/3_gold")
GOLD_DB = GOLD_DIR / "jobs.db"

def run_bronze():
    print("🥉 Bronze: Starting ingestion...")
    ingest_all_mhtml(SOURCE_DIR, BRONZE_DIR)

def run_silver():
    print("🥈 Silver:...")
    process_all_html(BRONZE_DIR, SILVER_DIR)

def run_gold():
    print("🥇 Gold:...")
    load_all_json(SILVER_DIR,GOLD_DIR)

def run_profiler():
    run_data_profile(GOLD_DB)

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py [ingest|process|load|profile|all]")
        return

    command = sys.argv[1]

    match command:
        case "ingest":
            run_bronze()
        case "process":
            run_silver()
        case "load":
            run_gold()
        case "profile":
            run_profiler()
        case "all":
            run_bronze()
            run_silver()
            run_gold()
            run_profiler()
        case _:
            print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
