import sqlite3
from pathlib import Path

def run_data_profile(db_path):
    db = Path(db_path)

    if not db.exists():
        print(f"❌ Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # total records in job tbl
    cursor.execute("SELECT COUNT(*) FROM jobs")
    total = cursor.fetchone()[0] # only hv 1 return
    
    # count null
    # IS NULL db stores nothing, = '' db stores something but blank (empty string)
    # safe if data inserted from diff source
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE job_title IS NULL OR job_title = ''")
    null_titles = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM jobs WHERE company IS NULL OR company = ''")
    null_company = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM jobs WHERE description IS NULL OR description = ''")
    null_description = cursor.fetchone()[0]

    # avg description length
    cursor.execute("SELECT AVG(LENGTH(description)) FROM jobs")
    avg_len = int(cursor.fetchone()[0])

    # shortest description
    cursor.execute("SELECT LENGTH(description), source_id, job_title FROM jobs ORDER BY LENGTH(description) ASC LIMIT 1")
    shortest = cursor.fetchone()

    # longest description
    cursor.execute("SELECT LENGTH(description), source_id, job_title FROM jobs ORDER BY LENGTH(description) DESC LIMIT 1")
    longest = cursor.fetchone()

    conn.close()

    # print the quality report
    print("--- 🔍 DATA QUALITY REPORT ---")
    print(f"📈 Total Records: {total}")
    print(f"❓ Missing Values -> job_title: {null_titles}, company: {null_company}, description: {null_description}")
    print(f"📝 Avg Description Length: {avg_len} chars")
    print(f"⚠️ Shortest Description: {shortest[0]}")
    print(f"↳ source_id: {shortest[1]} | job_title: {shortest[2]}")
    print(f"🚨 Longest Description: {longest[0]}")
    print(f"↳ source_id: {longest[1]} | job_title: {longest[2]}") # [?] specific position returned by db
    
