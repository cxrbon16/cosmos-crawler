import redis
import time
import utils  # Bing search fonksiyonun burada
import file_handler  # Keyword çekmek için burada olduğunu varsayıyorum
import config

SEED_KEY_QUEUE = "seed:keywords"          # anahtar‑sözcük listesi
SEED_URLS_PREFIX  = "seed:urls"         # her keyword için URL listesi

def push_keyword_and_urls(r, keyword, urls):

    if len(urls) < config.LEN_START_URLS:
        print(f"[X] {keyword}: {len(urls)} adet URL bulundu. 5 URL gereklidir.")
        return False

    if len(urls) > config.LEN_START_URLS:
        urls = urls[:config.LEN_START_URLS]

    pipe = r.pipeline()
    pipe.lpush(SEED_KEY_QUEUE, keyword)
    for url in urls:
        pipe.lpush(SEED_URLS_PREFIX + f":{keyword}", url)

    pipe.execute()
    print(f"[✓] {keyword} ve {config.LEN_START_URLS} URL Redis'e eklendi.")
    return True

def run():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    while True:
        keyword = file_handler.fetch_keyword()
        if not keyword:
            print("[!] Yeni keyword yok. Bekleniyor...")
            time.sleep(3)
            continue

        print(f"[🔍] Keyword: {keyword}")
        urls = utils.bing_search_urls(keyword)

        push_keyword_and_urls(r, keyword, urls)

        time.sleep(1)  # Kontrollü çalışsın

if __name__ == "__main__":
    run()