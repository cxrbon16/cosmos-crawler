import time
import subprocess
import pandas as pd
import os

CRAWLER_NAME = "keyword_crawler"

# --- Ana Döngü ---
while True:
    command = [
        "scrapy",
        "crawl",
        CRAWLER_NAME,
    ]
    process = subprocess.Popen(command)
    # ... (process.wait() ve diğer mantık buraya gelir)
    process.wait()
