from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def run_spider():
    process = CrawlerProcess(get_project_settings())
    process.crawl("keyword_crawler")
    process.start()  # Scrapy burada çalışır ve tamamlanınca biter

if __name__ == "__main__":
    run_spider()
