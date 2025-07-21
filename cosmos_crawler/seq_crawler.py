import csv
import os
import logging
import scrapy
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import langid
import fcntl
import time
import re

turkish_stop_words = ["bir", "ve", "ile", "olarak", "için", "gibi", "bu", "şu", "de", "da", "ama", "ancak", "fakat"]
blacklisted_extensions = [".pdf", ".php", ".aspx", ".jsp", ".doc", ".docx", ".xlsx", ".jpg"]

def is_blacklisted_url(url, response=None):
    parsed_url = urlparse(url)
    path = parsed_url.path  

    if any(path.lower().endswith(ext) for ext in blacklisted_extensions):
        return True  

    if response:
        content_type = response.headers.get('Content-Type', b'').decode('utf-8')
        if "application/pdf" in content_type:
            return True  

    return False

def get_urls_from_google(query, api_key, cx, num):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": cx,
        "num": num
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        results = response.json().get("items", [])
        return [result["link"] for result in results if not is_blacklisted_url(result["link"])]
    else:
        print(f"Error: {response.status_code}")
        return []

class SequentialKeywordCrawlerSpider(scrapy.Spider):
    name = "sequential_keyword_crawler"
    
    # Class variables for managing multi-keyword crawling
    keywords_to_crawl = []  # List of keywords to crawl sequentially
    current_keyword_index = 0
    pages_per_keyword = 250

    def __init__(self, keywords=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set keywords to crawl
        self.keywords_to_crawl = keywords or []
        
        # Reset tracking variables
        self.visited_urls = set()
        self.corpus = []
        self.url_list = []
        self.curr_pagenumber = 0
        self.curr_charactersnumber = 0
        self.refresh_curr = 0
        
        # Google API credentials
        self.api_key = "AIzaSyAEVV2nKzPU8eguU3KmSdkLtjTDioGI3NU"
        self.cx = "1222d6fea3f0c4480"
        
        # Initialize with first keyword
        if self.keywords_to_crawl:
            self.keyword = self.keywords_to_crawl[0]
            self.start_urls = get_urls_from_google(self.keyword, self.api_key, self.cx, num=10)
        
        # Logging setup
        logging.basicConfig(
            filename='sequential_keyword_crawler.log',
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

    def parse(self, response):
        # Check if current keyword's page limit is reached
        if self.curr_pagenumber >= self.pages_per_keyword:
            # Move to next keyword
            self.current_keyword_index += 1
            
            # Check if more keywords exist
            if self.current_keyword_index < len(self.keywords_to_crawl):
                # Reset for new keyword
                self.keyword = self.keywords_to_crawl[self.current_keyword_index]
                self.curr_pagenumber = 0
                self.refresh_curr = 0
                self.visited_urls.clear()
                
                # Get new URLs for next keyword
                new_start_urls = get_urls_from_google(self.keyword, self.api_key, self.cx, num=10)
                
                # Yield requests for new URLs
                for url in new_start_urls:
                    yield scrapy.Request(url, callback=self.parse)
                return

        # Original parsing logic
        self.visited_urls.add(response.url)
        self.curr_pagenumber += 1
        self.refresh_curr += 1
        
        html = response.text
        text = self.extract_text(html)
        combined_text = " ".join(text)
        
        lang, confidence = langid.classify(combined_text)
        
        if lang == "tr":
            # Existing crawling logic
            links = list(self.extract_links(html, response.url))
            for link in links:
                if (link not in self.visited_urls and 
                    not is_blacklisted_url(link) and 
                    self.refresh_curr < self.pages_per_keyword):
                    yield scrapy.Request(link, callback=self.parse)
            
            # Update corpus and tracking
            self.curr_charactersnumber += sum(len(p) for p in text)
            self.url_list.extend([response.url] * len(text))
            self.corpus.extend(text)
            
            # Logging
            self.logger.info(f"Scraped Page {response.url}")
            self.logger.info(f"Current Keyword: {self.keyword}")
            self.logger.info(f"Pages Scraped for Keyword: {self.curr_pagenumber}/{self.pages_per_keyword}")
        else:
            self.logger.info(f"Page not in Turkish: {response.url} (Language: {lang}, Confidence: {confidence:.2f})")

    # Keep other methods from original spider (extract_text, extract_links, etc.) unchanged
    
    def extract_text(self, html):
        """
        Extract and clean text from the page.
        """
        soup = BeautifulSoup(html, 'html.parser')

        for script in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            script.decompose()

        text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'article', 'section', 'div', 'span'])
        text_list = [element.get_text(strip=True) for element in text_elements if element.get_text(strip=True)]
        text_list = list(dict.fromkeys(text_list))  

        text_list = [text for text in text_list if len(text.split()) > 3]
        text_list = [re.sub(r'\s+', ' ', text).strip() for text in text_list]

        return text_list

    def extract_links(self, html, base_url):
        """
        Extract links from the page.
        """
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        for a_tag in soup.find_all('a', href=True):
            link = urljoin(base_url, a_tag['href'])
            if link.startswith("javascript") or link.strip() == "":
                continue
            links.add(link)

        return links

# Example usage
def run_spider(keywords):
    from scrapy.crawler import CrawlerProcess
    
    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 16,
        'DOWNLOAD_DELAY': 1,
    })
    
    process.crawl(SequentialKeywordCrawlerSpider, keywords=keywords)
    process.start()

# Example
if __name__ == '__main__':
    keywords = ['python', 'web geliştirme', 'yapay zeka']
    run_spider(keywords)
