import json
import sqlite3
from pathlib import Path

def load_all_json(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True) #create dir if not exist

    # where db output resides
    db_path = output_path / "jobs.db" 

    # connect to sqlite - create file if not exist
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # create job table if not exist yet
    # duplicate source_id will be auto rejected - primary key
    # tech_stack nullable
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            source_id TEXT PRIMARY KEY,
            job_title TEXT,
            company TEXT,
            description TEXT,
            tech_stack TEXT
        )
    """)
    conn.commit()

    total_files = 0
    inserted = 0
    skipped = 0
    failed = 0

    for json_file in input_path.glob("*.json"):
        total_files += 1
        try:
            data = json.loads(json_file.read_text(encoding="utf-8")) # read & parse json

            # insert source_id if not yet exist, else skip - so repeated runs don't create dupe
            cursor.execute("""
                INSERT OR IGNORE INTO jobs (source_id, job_title, company, description)
                VALUES (?, ?, ?, ?) """, 
                (data["source_id"], data["job_title"], data["company"], data["description"]))
            
            if cursor.rowcount == 1:
                print(f"✅ Inserted: {json_file.name}")
                inserted += 1
            else:
                print(f"⏭️ Skipped duplicate: {json_file.name}")
                skipped += 1
        
        except Exception as e:
            print(f"❌ Failed: {json_file.name}: {e}")
            failed += 1

    #save all inserts to db
    conn.commit()
    conn.close()

    print("\n📊 Gold Summary:")
    print(f"Total: {total_files} | Inserted: {inserted} | Skipped: {skipped} | Failed: {failed}")







