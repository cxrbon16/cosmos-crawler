#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "keyword_crawler"

SPIDER_MODULES = ["keyword_crawler.spiders"]
NEWSPIDER_MODULE = "keyword_crawler.spiders"
SCHEDULER_PRIORITY_QUEUE = "scrapy.pqueues.DownloaderAwarePriorityQueue"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "keyword_crawler (+http://www.yourdomain.com)"
USER_AGENT = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

LOG_LEVEL = "INFO"
# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 100
REACTOR_THREADPOOL_MAXSIZE = 20
COOKIES_ENABLED = False
RETRY_ENABLED = False
REDIRECT_ENABLED = False
AJAXCRAWL_ENABLED = True
DNS_TIMEOUT = 1
DOWNLOAD_TIMEOUT = 2
# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en", #}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "keyword_crawler.middlewares.KeywordCrawlerSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "keyword_crawler.middlewares.KeywordCrawlerDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "keyword_crawler.pipelines.KeywordCrawlerPipeline": 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"


# ========== scrapy-redis CONFIGURATION ==========

# Redis tabanlı scheduler kullan
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# Aynı URL'leri tekrar ziyaret etmemek için Redis tabanlı dupefilter
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# Spider kapandığında scheduler'ı (kuyruğu) sakla
SCHEDULER_PERSIST = True

# Kuyruğa eklenme önceliği (default FIFO)
# Diğer seçenekler: scrapy_redis.queue.PriorityQueue (öncelik sırasına göre)
SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.FifoQueue"

# Redis bağlantı bilgileri
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

# Eğer Redis şifreliyse (şifre eklenmeli)
# REDIS_PARAMS = {'password': 'yourpassword'}

# Scrapy ayarları
CONCURRENT_REQUESTS = 32
DOWNLOAD_DELAY = 0.0  # Sunucuları yormamak için küçük bir bekleme
ROBOTSTXT_OBEY = False

