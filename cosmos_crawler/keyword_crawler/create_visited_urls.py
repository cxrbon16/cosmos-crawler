import os
import glob
import csv
import sys

# Increase CSV field size limit to handle very large fields, if CSV parsing necessary
csv.field_size_limit(sys.maxsize)

def collect_urls(input_folder, output_file, dedupe=True):
    """
    Reads each file in input_folder matching corpus_*.csv, extracts the URL
    (everything up to the first space in each line), and writes unique URLs
    to output_file.
    """
    pattern = os.path.join(input_folder, "corpus_*.csv")
    files = sorted(glob.glob(pattern))
    seen = set()

    with open(output_file, "w", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout)
        writer.writerow(["URL"])

        for fp in files:
            print(f"Processing {fp}…")
            with open(fp, "r", encoding="utf-8", errors="ignore") as fin:
                for line in fin:
                    line = line.strip()
                    if not line:
                        continue
                    # Skip header row if present
                    if line.lower().startswith("url "):
                        continue
                    # URL is the first token before a space
                    url = line.split(" ", 1)[0]
                    if not url:
                        continue
                    # Skip duplicates
                    if dedupe and url in seen:
                        continue
                    seen.add(url)
                    writer.writerow([url])

    print(f"\nCompleted! Wrote {len(seen)} unique URL(s) to {output_file}.")


if __name__ == "__main__":
    INPUT_FOLDER = "CORPUS"
    OUTPUT_FILE = "visited_urls.csv"
    collect_urls(INPUT_FOLDER, OUTPUT_FILE, dedupe=True)
