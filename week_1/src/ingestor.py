import email
from pathlib import Path
import quopri

def ingest_all_mhtml(input_dir, output_dir):
    # define input output directory
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True) #ensure output directory exists

    total_files = 0
    extracted = 0
    failed = 0

    # loop through all .mhtml files in input directory
    for mhtml_file in input_path.glob("*.mhtml"):
        total_files += 1
        found_html = False # reset flag for each file
        try:
            # read as raw bytes, bcs .mhtml files are mixed content (HTML, images, CSS, fonts, etc)
            raw = mhtml_file.read_bytes()

            # parse mhtml like an email message (multi-part MIME)
            msg = email.message_from_bytes(raw)

            # walk through each part of msg
            for part in msg.walk():
                content_type = part.get_content_type()
                encoding = part.get("Content-Transfer-Encoding","")

                # only process HTML part of the archive
                if content_type == "text/html":
                    payload = part.get_payload(decode=True)

                    if encoding == "quoted-printable":
                        payload = quopri.decodestring(payload)

                    # convert bytes to UTF-8 string, replacing bad characters
                    html = payload.decode("utf-8", errors="replace")

                    # save output w same base name but .html extension
                    out_file = output_path / f"{mhtml_file.stem}.html"
                    out_file.write_text(html, encoding="utf-8")

                    print(f"✅ Extracted: {mhtml_file.name}")
                    extracted += 1
                    found_html = True
                    break  # stop after first HTML part found
            
            if not found_html:
                print(f"⚠️ No HTML content found in: {mhtml_file.name}")

        except Exception as e:
            print(f"❌ Error extracting {mhtml_file.name}: {e}")
            failed += 1

    # Bronze summary
    print("\n📊 Bronze Summary:")
    print(f"Total: {total_files} | Extracted: {extracted} | Failed: {failed}")

# ingest_all_mhtml("../data/0_source", "../data/1_bronze")      