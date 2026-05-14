from pydantic import BaseModel
from pathlib import Path
from bs4 import BeautifulSoup
import json

class JobListing(BaseModel):
    source_id: str
    job_title: str
    company: str
    description: str

def process_all_html(input_dir, output_dir):
    # define input output directory
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True) #ensure output directory exists

    total_files = 0
    processed = 0
    skipped = 0

    # loop through all html files
    for html_file in input_path.glob("*.html"):
        total_files += 1
        try:
            html = html_file.read_text(encoding="utf-8")
            soup = BeautifulSoup(html, "html.parser")

            # extract source_id from og:url, job title, company name, details
            og_url_tag = soup.find("meta", property="og:url")
            source_id = og_url_tag["content"].rstrip("/").split("/")[-1] if og_url_tag else None
            
            job_title_tag = soup.find(attrs={"data-automation": "job-detail-title"})
            job_title = job_title_tag.get_text(separator=" ", strip=True) if job_title_tag else None

            company_tag = soup.find(attrs={"data-automation": "advertiser-name"})
            company = company_tag.get_text(separator=" ", strip=True) if company_tag else None

            details_tag = soup.find(attrs={"data-automation": "jobAdDetails"})
            description = details_tag.get_text(separator=" ", strip=True) if details_tag else None

            if not all([source_id, job_title, company, description]):
                if not job_title:
                    print(f"⚠️ Missing job_title in: {html_file.name}")
                if not company:
                    print(f"⚠️ Missing company in: {html_file.name}")
                if not description:
                    print(f"⚠️ Missing description in: {html_file.name}")
                skipped += 1
                continue

            listing = JobListing(
                source_id=source_id,
                job_title=job_title,
                company=company,
                description=description
            )

            out_file = output_path / f"{html_file.stem}.json"
            out_file.write_text(listing.model_dump_json(), encoding="utf-8")
            print(f"✅ Processed: {html_file.name}")
            processed += 1

        except Exception as e:
            print(f"❌ Error Processing: {html_file.name}: {e}")
            skipped += 1

    print("\n📊 Silver Summary:")
    print(f"Total: {total_files} | Processed: {processed} | Skipped: {skipped}")

