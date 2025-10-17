import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import scrapy
import redis
import logging
import pandas as pd
import langid
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

import config
import utils
import file_handler

turkish_stop_words = config.TURKISH_STOPWORDS

class KeywordCrawlerSpider(scrapy.Spider):
    name = "keyword_crawler"
    refresh_step = config.REFRESH_STEP
    max_depth = config.MAX_DEPTH
    len_start_urls = config.LEN_START_URLS

    curr_w_keyword = 0

    corpus = []  # Metinlerin tutulduğu liste
    url_list = []  # URL'lerin tutulduğu liste

    curr_pagenumber = 0
    curr_charactersnumber = 0

    curr_keyword = ""
    start_time = time.time()

    redis = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Loglama ayarları
    logging.basicConfig(
        filename=config.LOG_FILEPATH,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.CRITICAL
    )

    def __init__(self, keyword=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def start_requests(self):
        self.logger.info("gezilmis urller cekiliyor...")

        self.logger.info("Spider başlatıldı, ilk keyword alınıyor...")
        yield from self._handle_keyword_refresh()

    def _handle_keyword_refresh(self):
        keyword = self.redis.rpop("keyword_crawler:keywords")
        new_urls = []
        if keyword:
            # keyword'e ait tüm URL'leri tüket
            while True:
                url = self.redis.rpop(f"keyword_crawler:urls:{keyword}")
                if url is None:
                    break
                new_urls.append(url)

        self.curr_keyword = keyword
        self.logger.info(f"NEW URLS \n {new_urls}")
        if len(new_urls) < self.len_start_urls:
            self.logger.warning(f"{keyword} için yeterli URL yok: {len(new_urls)} adet.")
            return

        for url in new_urls:
            yield scrapy.Request(url, callback=self.parse, errback=self.err_back, meta={"depth": 0, "keyword": keyword})

    def parse(self, response, **kwargs):
        if response.meta.get("keyword") != self.curr_keyword:
            self.logger.info(f"Skip old keyword URL: {response.url}")
            return  # 🔒 Eski keyword'e aitse işlemeden çık

        self.curr_pagenumber += 1
        self.curr_w_keyword += 1


        try:
            #TODO: Gonna be changed to redis set.
            # self.visited_urls.add(response.url)
            self.redis.sadd("keyword_crawler:visited_urls", response.url)

            html = response.text
            text = self.extract_text(html)
        except Exception as e:
            self.logger.error(f"Couldn't extract text from{response.url} Reason: {e}")
            return

        combined_text = " ".join(text)
        lang, confidence = langid.classify(combined_text)

        if lang != "tr":
            self.logger.info(f"Sayfa Türkçe değil: {response.url} (Dil: {lang}, Güven: {confidence:.2f})")
            return

        estimated_size_gb = (self.curr_charactersnumber * 1.1) / 1_000_000_000
        end_time = time.time()
        time_consumed = end_time - self.start_time

        self.curr_charactersnumber += sum(len(p) for p in text)
        self.url_list.extend([response.url] * len(text))
        self.corpus.extend(text)
        self.logger.info(f"KEYWORD: {response.meta['keyword']}")
        self.logger.info(f"Scraped Page {response.url}")
        self.logger.info(f"Total Pages Scraped: {self.curr_pagenumber}")
        self.logger.info(f"Total Characters Scraped: {self.curr_charactersnumber}")
        self.logger.info(f"Estimated Size: {estimated_size_gb:.2f} GB")
        self.logger.info(f"Time Consumed: {time_consumed} seconds")

        t = 0
        links = list(self.extract_links(html, response.url))
        for link in links:
            curr_in_p = self.crawler.engine._slot.scheduler.__len__() + len(self.crawler.engine._slot.inprogress)
            current_depth = response.meta.get('depth', 0)

            # Changed to redis set.
            is_link_visited = self.redis.sismember("keyword_crawler:visited_urls", link)
            if is_link_visited:
                self.logger.warning(f"\033[93mAlready visited: {link}\033[0m")  # yellow
            is_url_blacklisted = utils.is_blacklisted_url(link)
            is_out_of_bound = curr_in_p > self.refresh_step - self.curr_w_keyword + 1
            is_max_depth_exceeded = current_depth > self.max_depth

            if not is_link_visited and not is_url_blacklisted and not is_out_of_bound and not is_max_depth_exceeded:
                t += 1
                yield scrapy.Request(link, callback=self.parse, errback=self.err_back, meta={"depth": current_depth + 1, "keyword": response.meta.get("keyword")})

        self.logger.info(
            f"QUEUE SIZE: {self.crawler.engine._slot.scheduler.__len__() + len(self.crawler.engine._slot.inprogress)}")
        self.logger.info(f"T: {t}")

    def err_back(self, failure):
        # KAPANIŞ sürecindeysek slot None olabilir
        slot = self.crawler.engine._slot
        if not slot:
            return

        # Buradan sonrası yalnızca izleme amaçlı (refresh KALDIRILDI)
        curr_in_p = len(slot.scheduler) + len(slot.inprogress)
        self.logger.debug(f"Errback → queue size: {curr_in_p}")
        return

    def extract_text(self, html):
        """
        Sayfadan metin çıkar ve temizler.
        """
        soup = BeautifulSoup(html, 'html.parser')

        for script in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            script.decompose()

        text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'article'])
        text_list = [element.get_text(strip=True) for element in text_elements if element.get_text(strip=True)]
        text_list = list(dict.fromkeys(text_list))

        text_list = [text for text in text_list if len(text.split()) > 3]
        text_list = [re.sub(r'\s+', ' ', text).strip() for text in text_list]

        return text_list

    def extract_links(self, html, base_url):
        """
        Sayfadan linkleri çıkar.
        """
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        for a_tag in soup.find_all('a', href=True):
            link = urljoin(base_url, a_tag['href'])
            if link.startswith("javascript") or link.strip() == "":
                continue
            is_link_visited = self.redis.sismember("keyword_crawler:visited_urls", link)
            if is_link_visited:
                # self.logger.warning(f"\033[93mAlready visited: {link}\033[0m")  # yellow
                continue
            else:
                links.add(link)

        return links

    def closed(self, reason):
        """
        Spider kapatıldığında corpus'u kaydet.
        """
        self.logger.info("CLOSING. SAVING.")
        file_handler.save_corpus(url_list = self.url_list, corpus_list = self.corpus, keyword=self.curr_keyword, logger=self.logger)
