import time
import subprocess
import pandas as pd
import os

keyword_file_path = "keyword_crawler/spiders/fixed_combined_data.csv"
CRAWLER_NAME = "keyword_crawler"

def get_and_remove_next_keyword(filepath):
    """
    Verilen CSV dosyasının en üstündeki anahtar kelimeyi okur,
    dosyadan o satırı kaldırır ve kelimeyi temizlenmiş olarak döndürür.
    Dosya boşsa veya yoksa None döndürür.
    """
    try:
        df = pd.read_csv(filepath)
        if df.empty:
            print("Keyword file is empty.")
            return None

        # 1. Anahtar kelimeyi DOĞRUDAN hücreden al (en doğru yöntem)
        keyword = str(df.iloc[0, 0])

        # 2. Anahtar kelimeyi güncellemeden önce dosyadan kaldır
        df_remaining = df.iloc[1:]
        df_remaining.to_csv(filepath, index=False)

        # 3. Anahtar kelimeyi temizle ve döndür
        return keyword.strip()

    except FileNotFoundError:
        print(f"Error: Keyword file not found at '{filepath}'")
        return None
    except IndexError:
        # Bu hata, dosya var ama içi tamamen boşsa oluşur
        print(f"Keyword file '{filepath}' seems to be empty or malformed.")
        return None

# --- Ana Döngü ---
while True:
    next_keyword = get_and_remove_next_keyword(keyword_file_path)

    if next_keyword:
        print(f"Starting Scrapy worker for keyword: '{next_keyword}'")

        # Scrapy'ye temizlenmiş anahtar kelimeyi geçir
        command = [
            "scrapy",
            "crawl",
            CRAWLER_NAME,
            "-a",
            f"keyword={next_keyword}"
        ]
        process = subprocess.Popen(command)
        # ... (process.wait() ve diğer mantık buraya gelir)
        process.wait()
    else:
        print("No keywords left to process. Stopping.")
