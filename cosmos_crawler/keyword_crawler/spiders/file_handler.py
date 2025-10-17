import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import os
import config
import csv
import fcntl
import pandas as pd
import redis


def save_corpus(url_list, corpus_list, keyword, logger):
    """
    Corpus'u CSV formatında dosyaya kaydeder. Her satır URL ve metin içerir.
    """

    directory = config.CORPUS_DIRECTORY
    os.makedirs(directory, exist_ok=True)
    file_index = 1
    filename = os.path.join(directory, f"corpus_{file_index}.csv")

    while os.path.exists(filename) and os.path.getsize(filename) >= 100 * 1024 * 1024:  ## 1 mb boyutunda dosyalar.
        logger.info("filename: " + filename + " size: " + str(os.path.getsize(filename)))
        file_index += 1
        filename = os.path.join(directory, f"corpus_{file_index}.csv")

    try:
        with open(filename, "a", encoding="utf-8") as f:
            writer = csv.writer(f)

            if os.path.getsize(filename) == 0:  # Dosya boşsa, başlık yazalım.
                writer.writerow(["keyword", "url", "text"])

            fcntl.flock(f, fcntl.LOCK_EX)
            for url, text in zip(url_list, corpus_list):
                writer.writerow([keyword, url, text])
            fcntl.flock(f, fcntl.LOCK_UN)
        logger.info(f"Corpus saved to {filename}")

    except Exception as e:
        logger.error(f"Error saving corpus: {e}")

    return [], []


def fetch_keyword():
    keyword_file_path = config.KEYWORD_FILEPATH
    try:
        df = pd.read_csv(keyword_file_path)
        if df.empty:
            print("Keyword file is empty.")
            return None

        # 1. Anahtar kelimeyi DOĞRUDAN hücreden al (en doğru yöntem)
        keyword = str(df.iloc[0, 0])

        # 2. Anahtar kelimeyi güncellemeden önce dosyadan kaldır
        df_remaining = df.iloc[1:]
        df_remaining.to_csv(keyword_file_path, index=False)

        # 3. Anahtar kelimeyi temizle ve döndür
        return keyword.strip()

    except FileNotFoundError:
        print(f"Error: Keyword file not found at '{keyword_file_path}'")
        return None
    except IndexError:
        # Bu hata, dosya var ama içi tamamen boşsa oluşur
        print(f"Keyword file '{keyword_file_path}' seems to be empty or malformed.")
        return None
