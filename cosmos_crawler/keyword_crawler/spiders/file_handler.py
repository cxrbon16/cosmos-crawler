import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import os
import config
import csv
import fcntl
import pandas as pd

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
                writer.writerow(["url", "text"])

            fcntl.flock(f, fcntl.LOCK_EX)
            for url, text in zip(url_list, corpus_list):
                writer.writerow([url, text])
            fcntl.flock(f, fcntl.LOCK_UN)
        logger.info(f"Corpus saved to {filename}")

    except Exception as e:
        logger.error(f"Error saving corpus: {e}")

    return [], []


def load_visited_urls(logger):
    """
    Loads visited URLs from a CSV file into a set using a shared lock.
    A shared lock allows multiple processes to read the file simultaneously.
    """
    file_path = config.VISITED_URLS_FILEPATH
    visited = set()

    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    # PAYLAŞIMLI KİLİT AL (Diğer okuyucular erişebilir, yazarlar bekler)
                    fcntl.flock(f, fcntl.LOCK_SH)

                    # Dosyanın boş olup olmadığını kontrol et
                    if os.path.getsize(file_path) > 0:
                        reader = csv.reader(f)
                        visited = {row[0] for row in reader if row}

                finally:
                    # KİLİDİ BIRAK
                    fcntl.flock(f, fcntl.LOCK_UN)
                    logger.info(f"Loaded {len(visited)} visited URLs from {file_path}.")

        except Exception as e:
            logger.error(f"Could not load visited URLs from {file_path}: {e}")

    return visited


def save_visited_urls(urls_set, logger):
    """
    Saves a set of visited URLs to a CSV file using an exclusive lock.
    An exclusive lock prevents any other process from reading or writing.
    """

    file_path = config.VISITED_URLS_FILEPATH

    try:
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            try:
                # ÖZEL KİLİT AL (Başka hiçbir işlem bu dosyaya erişemez)
                fcntl.flock(f, fcntl.LOCK_EX)

                writer = csv.writer(f)
                for url in urls_set:
                    writer.writerow([url])

            finally:
                # KİLİDİ BIRAK
                fcntl.flock(f, fcntl.LOCK_UN)
                logger.info(f"{len(urls_set)} visited URLs saved to {file_path}.")

    except Exception as e:
        logger.error(f"Could not save visited URLs to {file_path}: {e}")


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
