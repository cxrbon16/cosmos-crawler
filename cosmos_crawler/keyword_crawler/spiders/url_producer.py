import redis
import time
import utils  
import file_handler  
import config

def push_keyword_and_urls(r, keyword, urls):

    print(f"[I] {keyword}: {len(urls)} adet URL bulundu. {config.LEN_START_URLS} URL gereklidir.")
    pipe = r.pipeline()

    pipe.lpush("keyword_crawler:keywords", keyword)
    for url in urls:
        pipe.lpush(f"keyword_crawler:urls:{keyword}", url)

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
        urls = utils.search_for_url(keyword, way=config.WAY_OF_GETTING_URLS)

        push_keyword_and_urls(r, keyword, urls)

        time.sleep(1)  # Kontrollü çalışsın

if __name__ == "__main__":
    run()
