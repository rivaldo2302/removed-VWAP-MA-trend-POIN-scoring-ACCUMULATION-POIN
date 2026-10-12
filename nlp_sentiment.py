import re
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup

POSITIVE_KEYWORDS = {
    "laba meroket": 5,
    "laba melonjak": 5,
    "laba bersih naik": 4,
    "laba bersih meningkat": 4,
    "akuisisi": 5,
    "diakuisisi": 4,
    "mengakuisisi": 5,
    "dividen jumbo": 5,
    "dividen spesial": 4,
    "dividen interim": 3,
    "kontrak baru": 3,
    "kontrak besar": 4,
    "ekspansi besar": 3,
    "right issue disetujui": 2,
    "buyback saham": 3,
    "rekor tertinggi": 4,
    "pendapatan rekor": 4,
    "penjualan melonjak": 3,
    "kerja sama strategis": 3,
    "restrukturisasi utang": 2,
    "stock split": 2,
    "capex besar": 2
}

NEGATIVE_KEYWORDS = {
    "rugi bersih": 5,
    "kerugian besar": 5,
    "penurunan laba": 4,
    "laba anjlok": 5,
    "laba merosot": 4,
    "gugatan pailit": 5,
    "pkpu": 5,
    "gagal bayar": 5,
    "default obligasi": 5,
    "suspensi saham": 4,
    "delisting": 5,
    "penjualan anjlok": 4,
    "penjualan merosot": 3,
    "downgrade rating": 4,
    "sanksi ojk": 4,
    "kena sanksi": 3,
    "kebakaran pabrik": 4,
    "tuntutan hukum": 3,
    "korupsi": 5,
    "phk massal": 4,
    "utang menumpuk": 3,
    "restrukturisasi darurat": 3
}

POSITIVE_THRESHOLD = 4
NEGATIVE_THRESHOLD = 4
NEWS_FEED_URL = "https://news.google.com/rss/search?q={query}&hl=id-ID&gl=ID&ceid=ID:id"
REQUEST_TIMEOUT = 8
MAX_NEWS_ITEMS = 5
REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0"}

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def fetch_stock_news(ticker_code, company_name=None):
    query_term = f"{company_name} {ticker_code} saham" if company_name else f"{ticker_code} saham"
    url = NEWS_FEED_URL.format(query=quote(query_term))
    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException:
        return []
    try:
        soup = BeautifulSoup(response.content, "xml")
    except Exception:
        soup = BeautifulSoup(response.content, "html.parser")
    items = soup.find_all("item")[:MAX_NEWS_ITEMS]
    news_list = []
    for item in items:
        title_tag = item.find("title")
        description_tag = item.find("description")
        title_text = title_tag.get_text() if title_tag else ""
        description_raw = description_tag.get_text() if description_tag else ""
        description_text = BeautifulSoup(description_raw, "html.parser").get_text()
        news_list.append(f"{title_text} {description_text}")
    return news_list

def analyze_sentiment(news_text):
    cleaned = clean_text(news_text)
    matched_positive = []
    positive_score = 0
    for keyword, weight in POSITIVE_KEYWORDS.items():
        if keyword in cleaned:
            matched_positive.append(keyword)
            positive_score += weight
    matched_negative = []
    negative_score = 0
    for keyword, weight in NEGATIVE_KEYWORDS.items():
        if keyword in cleaned:
            matched_negative.append(keyword)
            negative_score += weight
    is_heavy_positive = positive_score >= POSITIVE_THRESHOLD
    is_heavy_negative = negative_score >= NEGATIVE_THRESHOLD
    if is_heavy_positive and not is_heavy_negative:
        category = "Positif"
    elif is_heavy_negative and not is_heavy_positive:
        category = "Negatif"
    elif is_heavy_positive and is_heavy_negative:
        category = "Positif" if positive_score >= negative_score else "Negatif"
    else:
        category = "Netral"
    if matched_positive:
        catalyst_summary = ", ".join(matched_positive)
    elif matched_negative:
        catalyst_summary = ", ".join(matched_negative)
    else:
        catalyst_summary = "Tidak ada katalis signifikan"
    return {
        "category": category,
        "positive_score": positive_score,
        "negative_score": negative_score,
        "is_heavy_positive": is_heavy_positive,
        "is_heavy_negative": is_heavy_negative,
        "matched_positive_keywords": matched_positive,
        "matched_negative_keywords": matched_negative,
        "catalyst_summary": catalyst_summary
    }

def analyze_stock_sentiment(ticker_code, company_name=None):
    news_items = fetch_stock_news(ticker_code, company_name)
    if not news_items:
        return {
            "category": "Netral",
            "positive_score": 0,
            "negative_score": 0,
            "is_heavy_positive": False,
            "is_heavy_negative": False,
            "matched_positive_keywords": [],
            "matched_negative_keywords": [],
            "catalyst_summary": "Tidak ada berita ditemukan, sentimen netral",
            "news_count": 0
        }
    combined_text = " ".join(news_items)
    result = analyze_sentiment(combined_text)
    result["news_count"] = len(news_items)
    return result