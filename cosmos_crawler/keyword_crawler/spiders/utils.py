import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import undetected_chromedriver as uc

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import TimeoutException
import tldextract
import base64
import re
import undetected_chromedriver as uc
import config
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.common.by import By
import time


blacklisted_extensions = config.BLACKLISTED_EXTENSIONS

def is_blacklisted_url(url, response=None):
    """
    URL'in istenmeyen bir uzantıya veya içerik tipine sahip olup olmadığını kontrol eder.
    """
    parsed_url = urlparse(url)
    path = parsed_url.path

    if any(path.lower().endswith(ext) for ext in blacklisted_extensions):
        return True

    if response:
        content_type = response.headers.get('Content-Type', b'').decode('utf-8')
        if "application/pdf" in content_type:
            return True

    return False


def decode_bing_redirect(url):
    parsed = urlparse(url)

    if "bing.com" in parsed.netloc and parsed.path.startswith("/ck/a"):
        query = parse_qs(parsed.query)
        encoded = query.get("u", [None])[0]
        if encoded:
            try:
                # Gerçek base64 kısmını tespit etmeye çalış (genellikle https ile başlar)
                match = re.search(r'(aHR0c[^\s]*)', encoded)
                if match:
                    clean_encoded = match.group(1)
                    padded = clean_encoded + "=" * (-len(clean_encoded) % 4)
                    return base64.urlsafe_b64decode(padded).decode("utf-8")
                else:
                    print("Base64 içerik bulunamadı:", encoded)
            except Exception as e:
                print("couldnt decoded:", e)
    return url


def make_driver(use_tor_proxy=False):
    options = uc.ChromeOptions()
    # Headful çalıştır (daha az tespit edilir)
    # options.headless = True  # sakın headless açmayın

    # Dil / pencere / otomasyon bayrakları
    options.add_argument("--lang=tr-TR")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--no-first-run")
    options.add_argument("--no-service-autorun")
    options.add_argument("--password-store=basic")

    # İsteğe bağlı: Tor proxy (lokalde tor çalıştırın)
    if use_tor_proxy:
        options.add_argument("--proxy-server=socks5://127.0.0.1:9050")

    driver = uc.Chrome(options=options, headless=config.HEADLESS)

    # navigator.webdriver = undefined
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', {get: () => ['tr-TR','tr']});
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
        """}
    )

    # Extra HTTP headers (Accept-Language)
    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
        "headers": {
            "Accept-Language": "tr-TR,tr;q=0.9",
            "Referer": "https://www.bing.com/"
        }
    })
    # Çerezlerle dili sabitle
    return driver


def bing_search_urls(keyword):
    print(f"keyword: {keyword}")

    driver = make_driver()
    # çok genel sorgulara otomatik site:tr ekle
    query = keyword
    # Bing URL: TR dili, TR pazarı, güvenli arama, Türkçe filtre

    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
        "headers": {"Accept-Language": "tr-TR,tr;q=0.9"}
    })
    url = f"https://www.bing.com/search?q={query}&search=Submit+Query&form=QBLH&rdr=1&rdrig=01C9B2A878CF446E9A824FA0EDB1D7A3" 
    print(url)
    driver.get(url)
    time.sleep(6)

    links = []
    elements = driver.find_elements(By.CSS_SELECTOR, "li.b_algo h2 a")

    spam_domains = [
        "livejasmin", "camgirl", "porn", "xvideos", "xnxx",
        "onlyfans", "zhihu.com"
    ]

    for elem in elements:
        href = elem.get_attribute("href")
        x = decode_bing_redirect(href)

        if not is_blacklisted_url(x) and not any(sd in x.lower() for sd in spam_domains):
            links.append(x)

    print(links)
    driver.quit()
    return links
