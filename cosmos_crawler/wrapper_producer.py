import time
import subprocess
import pandas as pd
import os

SCRIPT_NAME = "keyword_crawler/spiders/url_producer.py"

# --- Ana Döngü ---
while True:
    # Scrapy'ye temizlenmiş anahtar kelimeyi geçir
    command = [
        "python3",
        SCRIPT_NAME,
    ]
    process = subprocess.Popen(command)
    # ... (process.wait() ve diğer mantık buraya gelir)
    process.wait()
