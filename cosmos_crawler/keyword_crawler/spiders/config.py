REFRESH_STEP = 500
LEN_START_URLS = 10

VISITED_URLS_FILEPATH = "visited_urls.csv"
KEYWORD_FILEPATH = "fixed_combined_data.csv"
CORPUS_DIRECTORY = "CORPUS"

TURKISH_STOPWORDS = ["bir", "ve", "ile", "olarak", "için", "gibi", "bu", "şu", "de", "da", "ama", "ancak", "fakat"]
# BLACKLISTED_URLS = ["seslisozluk.net", "kelimeler.gen.tr", "nedemek.org", "flo.com"] NOT IMPLEMENTED YET!
BLACKLISTED_EXTENSIONS = [".pdf", ".php", ".aspx", ".jsp", ".doc", ".docx", ".xlsx", ".jpg", ".jpeg", ".png"]  # İstenmeyen uzantılar

MAX_DEPTH = 3

HEADLESS = False 
LOG_FILEPATH = "keyword_crawler.log"
