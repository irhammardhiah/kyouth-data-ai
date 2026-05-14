# KYouth Data AI — Week 1 Pipeline
A local data pipeline that extracts job listings from saved web pages, cleans and structures the data, stores it in a database, and runs a quality check — all from the command line.

---

## Project Description
This project builds a 4-stage data pipeline using the Medallion Architecture:
- **Bronze** — Extract raw HTML from `.mhtml` files
- **Silver** — Clean and structure the HTML into JSON
- **Gold** — Load structured JSON into a SQLite database
- **Profile** — Run a data quality report on the loaded data

---

## Setup Instructions

**Prerequisites:**
- python version **3.14**.*
- `uv` version **0.8.***

**Steps:**
1. Clone the repository:
```
    git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
    cd week_1
```
2. Create and activate a virtual environment:
```
    python -m venv .venv
    source .venv/Scripts/activate # Windows
    source .venv/bin/activate # Mac/Linux
```
3. Install dependencies:
```
    python -m pip install beautifulsoup4 pydantic
```
4. Place your `.mhtml` source files inside `data/0_source/`

---

## Usage
Run each stage individually or all at once:
```
    python main.py ingest # Extract .mhtml → HTML (Bronze)
    python main.py process # Clean HTML → JSON (Silver)
    python main.py load # Load JSON → SQLite (Gold)
    python main.py profile # Run data quality report
    python main.py all # Run full pipeline in order
```

**Expected output (full pipeline):**
```
    🥉 Bronze: Starting ingestion...
    ✅ Extracted: example-job.mhtml
    📊 Bronze Summary: Total: 100 | Extracted: 100 | Failed: 0

    🥈 Silver: Starting processing...
    ✅ Processed: example-job.html
    📊 Silver Summary: Total: 100 | Processed: 84 | Skipped: 16

    🥇 Gold: Starting loading...
    ✅ Inserted: example-job.json
    📊 Gold Summary: Total: 84 | Inserted: 84 | Skipped: 0 | Failed: 0

    --- 🔍 DATA QUALITY REPORT ---
    📈 Total Records: 84
    ❓ Missing Values -> job_title: 0, company: 0, description: 0
    📝 Avg Description Length: 1740 chars
    ⚠️ Shortest Description: 53 chars
    🚨 Longest Description: 2854 chars
```

---

## Technical Reflections

### Module 1: The Extractor (Medallion & Lakehouses)
Why is it useful to keep the original raw HTML files instead of directly inserting processed data into the database? What problems become easier to debug or recover from?

- **Answer**: Keeping the raw HTML files acts as a safety net. If our cleaning logic has a bug, for example we accidentally extract the wrong field, we can fix the code and rerun the Silver stage without having to redownload all 100 job pages from the internet.
``` 
It also makes debugging easier, if a record looks wrong in the database, we can trace it back to the original HTML file and inspect exactly what the page contained.
```

---

### Module 2: Treatment Plant (ETL vs ELT & Scale)
Why do cloud systems prefer loading raw data first before cleaning it (ELT)? What problems happen when processing files sequentially, and how does distributed processing help?

- **Answer**: Cloud platforms like Snowflake and BigQuery have massive built-in compute power, so it is faster and cheaper to dump raw data in first and let the platform do the transformation at scale (ELT), rather than cleaning everything locally before loading (ETL). 
In this pipeline, we process files one by one in a loop (if we have 1 million files, that would take hours). Distributed tools like Apache Spark split the work across many machines running in parallel, so all files are processed at the same time, reducing hours of work to minutes.

---

### Module 3: The Blueprint & The Vault (Storage & Contracts)
What should happen if an important field like `job_title` disappears? Why fail early instead of silently inserting nulls into the database? How does `INSERT OR IGNORE` help prevent duplicate records?

- **Answer**: If `job_title` disappears, the pipeline should immediately warn and skip that record (not silently save a blank value). Inserting nulls into the database causes hidden problems downstream like dashboards show empty cards, reports give wrong counts, and AI models trained on the data get corrupted. 
Failing early (the ⚠️ warning in Silver) means the bad record never reaches the database, keeping the data clean. `INSERT OR IGNORE` prevents duplicates by checking if a `source_id` already exists before inserting (if it does, it skips the row instead of creating a copy), so running the pipeline twice always produces the same result.

---

### Module 4: The QA Inspector & Orchestrator (Orchestration & DAGs)
What happens if `processor.py` crashes halfway? How are automated orchestration tools more reliable than manual retries with Python scripts?

- **Answer**: If `processor.py` crashes halfway through `python main.py all` command, the rest of the pipeline stops completely. We would have to manually figure out where it failed, fix it, and rerun everything from the beginning. 
Tools like Apache Airflow solve this by treating each stage as an independent task with automatic retries, failure alerts, and the ability to resume from the exact step that failed (without rerunning the stages that already succeeded). They also support scheduling (e.g. run every day at 8am) and dependency management, which a simple Python script cannot do reliably.
