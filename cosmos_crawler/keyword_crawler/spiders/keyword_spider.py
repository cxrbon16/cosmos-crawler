import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import scrapy
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
    curr_w_keyword = 0
    allowed_domains = []
    start_urls = []
    visited_urls = set()
    visited_urls_file = config.VISITED_URLS_FILEPATH
    keyword_file_path = config.KEYWORD_FILEPATH
    corpus = []  # Metinlerin tutulduğu liste
    url_list = []  # URL'lerin tutulduğu liste
    curr_pagenumber = 0
    curr_charactersnumber = 0
    start_time = time.time()

    # Loglama ayarları
    logging.basicConfig(
        filename=config.LOG_FILEPATH,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.CRITICAL
    )

    def __init__(self, keyword=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visited_urls = file_handler.load_visited_urls(self.logger)
        self.start_urls = utils.bing_search_urls(keyword)
        self.logger.info(f"Starting URLs: {self.start_urls}")


    def _handle_keyword_refresh(self):
        self.curr_w_keyword = 0
        self.logger.info(f"Starting to extract keyword...")
        new_urls = []

        while not new_urls:
            time.sleep(0.5)
            keyword = file_handler.fetch_keyword(self.logger)
            new_urls = utils.bing_search_urls(keyword)
            # Save progress before starting new requests

        file_handler.save_visited_urls(urls_set=self.visited_urls, logger=self.logger)
        self.url_list, self.corpus = file_handler.save_corpus(url_list=self.url_list, corpus_list=self.corpus, logger=self.logger)

        for url in new_urls:
            yield scrapy.Request(url, callback=self.parse, errback=self.err_back)

    def parse(self, response, **kwargs):
        self.curr_pagenumber += 1
        self.curr_w_keyword += 1

        curr_in_p = self.crawler.engine.slot.scheduler.__len__() + len(self.crawler.engine.slot.inprogress)
        if (self.curr_pagenumber + 1) % self.refresh_step == 0 or curr_in_p < 5:
            yield from self._handle_keyword_refresh()
            return

        try:
            self.visited_urls.add(response.url)
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

        self.logger.info(f"Scraped Page {response.url}")
        self.logger.info(f"Total Pages Scraped: {self.curr_pagenumber}")
        self.logger.info(f"Total Characters Scraped: {self.curr_charactersnumber}")
        self.logger.info(f"Estimated Size: {estimated_size_gb:.2f} GB")
        self.logger.info(f"Time Consumed: {time_consumed} seconds")

        links = list(self.extract_links(html, response.url))
        for link in links:
            curr_in_p = self.crawler.engine.slot.scheduler.__len__() + len(self.crawler.engine.slot.inprogress)

            if link not in self.visited_urls and not utils.is_blacklisted_url(
                    link) and curr_in_p < self.refresh_step - self.curr_w_keyword + 1:
                yield scrapy.Request(link, callback=self.parse, errback=self.err_back)

        self.logger.info(
            f"{self.crawler.engine.slot.scheduler.__len__() + len(self.crawler.engine.slot.inprogress)}")

    def err_back(self, failure):
        self.curr_pagenumber += 1
        self.curr_w_keyword += 1

        self.logger.error(repr(failure))
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
            links.add(link)

        return links

    def closed(self, reason):
        """
        Spider kapatıldığında corpus'u kaydet.
        """
        file_handler.save_visited_urls(urls_set = self.visited_urls, logger=self.logger)
        file_handler.save_corpus(url_list = self.url_list, corpus_list = self.corpus, logger=self.logger)