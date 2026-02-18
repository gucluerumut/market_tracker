import uuid
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import urllib.parse
import feedparser
from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplfinance as mpf

# ==========================================
# 1. YAPILANDIRMA VE VERİ TABANI (ASSETS_DB)
# ==========================================

# Hazır Paketler (Uluslararası & Saat Bazlı)
PRESETS = {
    "🌅 09:00 - Asya & Emtia": ["dxy", "us10y", "gold", "silver", "oil_brent", "eurusd"],
    "☀️ 16:30 - ABD Açılışı": ["sp500", "nasdaq", "dxy", "vix", "gold", "btc"],
    "🌃 23:00 - Kapanış & Kripto": ["sp500", "nasdaq", "btc", "eth", "sol", "gold"]
}

# Dil Sözlüğü
LANG = {
    "tr": {
        "title": "Piyasa Takipçisi",
        "sidebar_title": "Ayarlar",
        "select_assets": "Varlıkları Seç",
        "fetch_btn": "Verileri Getir",
        "copy_title": "Kopyalanabilir Sonuç",
        "success": "Veriler başarıyla çekildi!",
        "error": "Hata oluştu:",
        "tweet_btn": "Twitter'da Paylaş",
        "loading": "Veriler çekiliyor...",
        "no_data": "Veri Yok",
        "snapshot_header": "📊 PİYASA ÖZETİ",
        "fng_title": "Korku ve Açgözlülük",
        "news_tab": "Haberler & Tweet Oluşturucu",
        "chart_tab": "Grafik Oluşturucu",
        "news_header": "📢 {0} Günü Piyasalar",
        "news_morning": "Sabah Özeti",
        "news_noon": "Borsa Gündemi",
        "news_evening": "Kripto Akşamı",
        "presets_header": "Hazır Paketler",
        "preset_morning": "☕️ Sabah Kahvesi",
        "preset_crypto": "🚀 Kripto Sepeti",
        "preset_us": "🇺🇸 ABD Borsaları"
    },
    "en": {
        "title": "Market Tracker",
        "sidebar_title": "Settings",
        "select_assets": "Select Assets",
        "fetch_btn": "Fetch Data",
        "copy_title": "Copyable Result",
        "success": "Data fetched successfully!",
        "error": "Error occurred:",
        "tweet_btn": "Share on Twitter",
        "loading": "Fetching data...",
        "no_data": "No Data",
        "snapshot_header": "📊 MARKET SNAPSHOT",
        "fng_title": "Fear & Greed",
        "news_tab": "News & Tweet Composer",
        "chart_tab": "Chart Generator",
        "news_header": "📢 {0} Market News",
        "news_morning": "Morning Brief",
        "news_noon": "Stock Market",
        "news_evening": "Crypto Night",
        "presets_header": "Presets",
        "preset_morning": "☕️ Morning Coffee",
        "preset_crypto": "🚀 Crypto Basket",
        "preset_us": "🇺🇸 US Markets"
    }
}

# Varlık Veritabanı
# category_key: Bu asset'in hangi kategoride olduğunu belirtir (UI'da gruplamak için)
ASSETS_DB = [
    # Kripto
    {"id": "btc", "ticker": "BTC-USD", "emoji": "🟠", "name_tr": "Bitcoin", "name_en": "Bitcoin", "cat_tr": "Kripto", "cat_en": "Crypto"},
    {"id": "eth", "ticker": "ETH-USD", "emoji": "💎", "name_tr": "Ethereum", "name_en": "Ethereum", "cat_tr": "Kripto", "cat_en": "Crypto"},
    {"id": "sol", "ticker": "SOL-USD", "emoji": "🟣", "name_tr": "Solana", "name_en": "Solana", "cat_tr": "Kripto", "cat_en": "Crypto"},
    {"id": "xrp", "ticker": "XRP-USD", "emoji": "⚫️", "name_tr": "XRP", "name_en": "XRP", "cat_tr": "Kripto", "cat_en": "Crypto"},
    {"id": "doge", "ticker": "DOGE-USD", "emoji": "🐕", "name_tr": "Dogecoin", "name_en": "Dogecoin", "cat_tr": "Kripto", "cat_en": "Crypto"},
    {"id": "ada", "ticker": "ADA-USD", "emoji": "🔵", "name_tr": "Cardano", "name_en": "Cardano", "cat_tr": "Kripto", "cat_en": "Crypto"},
    {"id": "avax", "ticker": "AVAX-USD", "emoji": "🔺", "name_tr": "Avalanche", "name_en": "Avalanche", "cat_tr": "Kripto", "cat_en": "Crypto"},
    {"id": "dot", "ticker": "DOT-USD", "emoji": "⭕️", "name_tr": "Polkadot", "name_en": "Polkadot", "cat_tr": "Kripto", "cat_en": "Crypto"},
    {"id": "link", "ticker": "LINK-USD", "emoji": "🔗", "name_tr": "Chainlink", "name_en": "Chainlink", "cat_tr": "Kripto", "cat_en": "Crypto"},
    {"id": "usdt_try", "ticker": "USDT-TRY", "emoji": "₮", "name_tr": "Tether/TL (USDT)", "name_en": "Tether/TRY (USDT)", "cat_tr": "Kripto", "cat_en": "Crypto"},

    # Borsa & Endeksler
    {"id": "sp500", "ticker": "^GSPC", "emoji": "🇺🇸", "name_tr": "SP500", "name_en": "S&P 500", "cat_tr": "Borsa & Endeksler", "cat_en": "Indices"},
    {"id": "nasdaq", "ticker": "^IXIC", "emoji": "🇺🇸", "name_tr": "NASDAQ", "name_en": "NASDAQ", "cat_tr": "Borsa & Endeksler", "cat_en": "Indices"},
    {"id": "nyse", "ticker": "^NYA", "emoji": "🇺🇸", "name_tr": "NYSE", "name_en": "NYSE", "cat_tr": "Borsa & Endeksler", "cat_en": "Indices"},
    {"id": "dow", "ticker": "^DJI", "emoji": "🇺🇸", "name_tr": "DOW JONES", "name_en": "DOW JONES", "cat_tr": "Borsa & Endeksler", "cat_en": "Indices"},
    {"id": "bist", "ticker": "^XU100", "emoji": "🇹🇷", "name_tr": "BIST 100", "name_en": "BIST 100", "cat_tr": "Borsa & Endeksler", "cat_en": "Indices"},
    {"id": "dax", "ticker": "^GDAXI", "emoji": "🇩🇪", "name_tr": "DAX", "name_en": "DAX", "cat_tr": "Borsa & Endeksler", "cat_en": "Indices"},
    {"id": "ftse", "ticker": "^FTSE", "emoji": "🇬🇧", "name_tr": "FTSE 100", "name_en": "FTSE 100", "cat_tr": "Borsa & Endeksler", "cat_en": "Indices"},
    {"id": "nikkei", "ticker": "^N225", "emoji": "🇯🇵", "name_tr": "Nikkei 225", "name_en": "Nikkei 225", "cat_tr": "Borsa & Endeksler", "cat_en": "Indices"},

    # Emtia
    {"id": "gold", "ticker": "GC=F", "emoji": "🟡", "name_tr": "Altın (Vadeli)", "name_en": "Gold (Futures)", "cat_tr": "Emtia", "cat_en": "Commodities"},
    {"id": "silver", "ticker": "SI=F", "emoji": "⚪️", "name_tr": "Gümüş (Vadeli)", "name_en": "Silver (Futures)", "cat_tr": "Emtia", "cat_en": "Commodities"},
    {"id": "oil_crude", "ticker": "CL=F", "emoji": "🛢️", "name_tr": "Petrol (Ham)", "name_en": "Crude Oil", "cat_tr": "Emtia", "cat_en": "Commodities"},
    {"id": "oil_brent", "ticker": "BZ=F", "emoji": "🛢️", "name_tr": "Petrol (Brent)", "name_en": "Brent Oil", "cat_tr": "Emtia", "cat_en": "Commodities"},
    {"id": "nat_gas", "ticker": "NG=F", "emoji": "🔥", "name_tr": "Doğalgaz", "name_en": "Natural Gas", "cat_tr": "Emtia", "cat_en": "Commodities"},
    {"id": "copper", "ticker": "HG=F", "emoji": "🥉", "name_tr": "Bakır", "name_en": "Copper", "cat_tr": "Emtia", "cat_en": "Commodities"},

    # Döviz
    {"id": "usdtry", "ticker": "TRY=X", "emoji": "💵", "name_tr": "Dolar/TL", "name_en": "USD/TRY", "cat_tr": "Döviz", "cat_en": "Forex"},
    {"id": "eurtry", "ticker": "EURTRY=X", "emoji": "💶", "name_tr": "Euro/TL", "name_en": "EUR/TRY", "cat_tr": "Döviz", "cat_en": "Forex"},
    {"id": "eurusd", "ticker": "EURUSD=X", "emoji": "💶", "name_tr": "Euro/Dolar", "name_en": "EUR/USD", "cat_tr": "Döviz", "cat_en": "Forex"},
    {"id": "gbpusd", "ticker": "GBPUSD=X", "emoji": "💷", "name_tr": "Sterlin/Dolar", "name_en": "GBP/USD", "cat_tr": "Döviz", "cat_en": "Forex"},

    # Makro & Göstergeler
    {"id": "dxy", "ticker": "DX-Y.NYB", "emoji": "💲", "name_tr": "Dolar Endeksi (DXY)", "name_en": "Dollar Index (DXY)", "cat_tr": "Makro & Göstergeler", "cat_en": "Macro & Indicators"},
    {"id": "us10y", "ticker": "^TNX", "emoji": "🇺🇸", "name_tr": "ABD 10Y Tahvil", "name_en": "US 10Y Treasury", "cat_tr": "Makro & Göstergeler", "cat_en": "Macro & Indicators"},
    {"id": "vix", "ticker": "^VIX", "emoji": "😨", "name_tr": "VIX (Korku Endeksi)", "name_en": "VIX (Volatility)", "cat_tr": "Makro & Göstergeler", "cat_en": "Macro & Indicators"}
]

st.set_page_config(page_title="Piyasa Takipçisi", layout="wide")

# ==========================================
# 2. UI VE STATE YÖNETİMİ
# ==========================================

import json

# Dil Seçimi (Sidebar)
with st.sidebar:
    st.header("⚙️ Ayarlar / Settings")
    lang_choice = st.radio("Dil / Language", ["TR", "EN"], index=0)
    
    st.divider()
    
    # Portföy Kaydet / Yükle
    st.subheader("💾 Portfolio")
    
    # Kaydet Butonu
    if st.button("Save My Portfolio"):
        # Seçili ID'leri bul
        saved_ids = [k for k, v in st.session_state.items() if v is True and k in [item['id'] for item in ASSETS_DB]]
        if saved_ids:
            with open("user_portfolio.json", "w") as f:
                json.dump(saved_ids, f)
            st.success("Saved!" if lang_choice == "EN" else "Kaydedildi!")
        else:
            st.warning("Select assets first.")

    # Yükle Butonu
    if st.button("Load My Portfolio"):
        try:
            with open("user_portfolio.json", "r") as f:
                saved_ids = json.load(f)
            
            # Önce temizle
            for item in ASSETS_DB:
                st.session_state[item['id']] = False
            
            # Yüklenenleri seç
            for pid in saved_ids:
                st.session_state[pid] = True
            
            st.rerun()
        except FileNotFoundError:
            st.error("No saved portfolio found.")
            
    st.divider()

    # Hazır Paket Butonları
    st.subheader(LANG[lang_choice]["presets"])
    for preset_name, preset_ids in PRESETS.items():
        if st.button(preset_name):
            # Önce hepsini temizle
            for item in ASSETS_DB:
                st.session_state[item['id']] = False
            # Seçilileri aktif et
            for pid in preset_ids:
                st.session_state[pid] = True
            st.rerun()

# Dil metinlerini al
texts = LANG[lang_choice]

st.title(texts["title"])
st.write(texts["desc"])

# Kategori Gruplama
categories = {}
for item in ASSETS_DB:
    cat_name = item[f"cat_{lang_choice.lower()}"]
    if cat_name not in categories:
        categories[cat_name] = []
    categories[cat_name].append(item)

selected_items = []

# Kolon oluştur
cols = st.columns(len(categories))

for i, (cat_name, items) in enumerate(categories.items()):
    with cols[i]:
        st.subheader(cat_name)
        # "Tümünü Seç"
        # Session state'de checkbox durumlarını yönetmek için key kontrolü
        if f"all_{cat_name}" not in st.session_state:
             st.session_state[f"all_{cat_name}"] = False
             
        all_selected = st.checkbox(f"{texts['select_all']} ({cat_name})", key=f"all_{cat_name}")
        
        for item in items:
            item_name = item[f"name_{lang_choice.lower()}"]
            # Checkbox key'i asset id ile aynı
            # Eğer "Tümünü Seç" basıldıysa onu baz al, yoksa session state'e bak
            default_val = False
            if item['id'] not in st.session_state:
                st.session_state[item['id']] = False
            
            if all_selected:
                st.session_state[item['id']] = True
            
            is_checked = st.checkbox(f"{item['emoji']} {item_name}", key=item['id'])
            if is_checked:
                selected_items.append(item)

# ==========================================
# 3. VERİ ÇEKME VE HESAPLAMA
# ==========================================

import concurrent.futures

def get_fng_data():
    """Kripto Korku ve Açgözlülük Endeksini çeker"""
    try:
        url = "https://api.alternative.me/fng/?limit=1"
        r = requests.get(url, timeout=5)
        data = r.json()
        val = data['data'][0]['value']
        classification = data['data'][0]['value_classification']
        return val, classification
    except:
        return None, None

def generate_commentary(results_data, lang_code):
    """Basit piyasa yorumu oluşturur"""
    if not results_data: return ""
    
    # En çok artan ve düşeni bul
    best_perf = -999
    worst_perf = 999
    best_asset = ""
    worst_asset = ""
    
    for res in results_data:
        if res.get("pct_change") is not None:
            pct = res["pct_change"]
            if pct > best_perf:
                best_perf = pct
                best_asset = res["name"]
            if pct < worst_perf:
                worst_perf = pct
                worst_asset = res["name"]
                
    comment = ""
    if lang_code == "TR":
        comment = f"Piyasada {best_asset} %{best_perf:.2f} artışla öne çıkarken, {worst_asset} %{abs(worst_perf):.2f} düşüşle baskı altında."
    else:
        comment = f"{best_asset} leads with +{best_perf:.2f}%, while {worst_asset} is under pressure with {worst_perf:.2f}%."
        
    return comment

import re

def clean_and_format_headline(title, source_name, topic_map):
    """
    Haber başlığını temizler, formatlar ve 'vurucu' hale getirir.
    """
    # 1. Temizlik: HTML karakterleri ve boşluklar
    clean_title = title.strip().replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')
    
    # 2. Regex ile Gereksiz Önekleri Sil
    # Örn: "Live updates:", "Stock market news:", "Watch:", "Why"
    prefixes = [
        r"^Live updates:\s*", r"^Live:\s*", r"^Update:\s*", 
        r"^Stock market news:\s*", r"^Stock market live:\s*", 
        r"^Watch:\s*", r"^Video:\s*", r"^Exclusive:\s*",
        r"^Here's why\s*", r"^Why\s*"
    ]
    for p in prefixes:
        clean_title = re.sub(p, "", clean_title, flags=re.IGNORECASE)
        
    # 3. Regex ile Gereksiz Sonekleri Sil (Kaynak isimleri vb.)
    # Örn: "- CNBC", "| Reuters", "- MarketWatch"
    suffixes = [
        r"\s*-\s*CNBC.*$", r"\s*\|\s*Reuters.*$", r"\s*-\s*MarketWatch.*$", 
        r"\s*-\s*Bloomberg.*$", r"\s*-\s*Yahoo Finance.*$",
        r"\s*-\s*CoinDesk.*$", r"\s*-\s*CoinTelegraph.*$"
    ]
    for s in suffixes:
        clean_title = re.sub(s, "", clean_title)
    
    # Baş harfi büyüt (Cümle yapısı bozulduysa)
    if clean_title:
        clean_title = clean_title[0].upper() + clean_title[1:]

    # 4. Konu Tespiti ve Emoji
    detected_topic = None
    display_topic = None
    lower_title = clean_title.lower()
    
    for key, val in topic_map.items():
        if key in lower_title:
            detected_topic = key
            display_topic = val
            break
            
    emoji = "📰"
    if display_topic:
        if display_topic in ["US CPI Data", "Inflation", "GDP Data", "Federal Reserve", "FOMC", "Jerome Powell", "Treasury Yields"]: emoji = "🇺🇸"
        elif display_topic in ["Crude Oil", "Brent Oil"]: emoji = "🛢️"
        elif display_topic in ["Gold", "Silver"]: emoji = "🟡"
        elif display_topic in ["Bitcoin", "Ethereum", "Solana"]: emoji = "🟠"
        elif display_topic in ["Nvidia", "Tesla", "Apple", "Microsoft", "Tech", "Earnings"]: emoji = "🤖"
        elif display_topic in ["US Stocks", "Wall Street", "Dow Jones", "Nasdaq", "S&P 500"]: emoji = "📈"

    # 5. Formatlama: "Emoji **Konu** | Başlık [Kaynak]"
    final_text = ""
    if display_topic:
        # Konu başlıkta zaten geçiyorsa, tekrar etmemek için bazen çıkarılabilir ama
        # tutarlılık için "Konu | Başlık" yapısı daha iyidir.
        final_text = f"{emoji} **{display_topic}** — {clean_title}"
    else:
        final_text = f"{emoji} {clean_title}"
        
    # Kaynağı ekle
    final_text += f" `[{source_name}]`"
    
    return final_text

def fetch_finance_news(category="general"):
    """
    Yahoo Finance, CNBC, vb. RSS feed'lerinden haberleri çeker.
    category: 'general', 'stocks', 'crypto'
    """

    
    # Kategoriye göre anahtar kelimeler
    keywords = {
        "general": ["inflation", "fed", "economy", "rates", "cpi", "gdp", "treasury", "yields", "dollar", "us", "bank", "sales", "finance", "market"],
        "stocks": ["stock", "market", "nasdaq", "sp500", "dow", "earnings", "tech", "nvidia", "apple", "tesla", "meta", "amazon", "shares", "rally", "plunge"],
        "crypto": ["bitcoin", "crypto", "ethereum", "blockchain", "coin", "wallet", "sec", "etf", "solana", "binance", "token", "digital asset"]
    }
    
    # Çoklu Kaynak Listesi (Yahoo + CNBC + Investing + WSJ + CoinDesk)
    # Reuters'in resmi ücretsiz RSS'i olmadığı için CNBC ve Investing kullanıyoruz.
    rss_sources = {
        "general": [
            "https://finance.yahoo.com/news/rssindex",
            "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664", # CNBC Finance
            "https://feeds.a.dj.com/rss/RSSMarketsMain.xml", # WSJ Markets
            "https://www.investing.com/rss/news.rss"
        ],
        "stocks": [
            "https://finance.yahoo.com/news/rssindex",
            "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114", # CNBC Top News
            "https://feeds.content.dowjones.io/public/rss/mw_topstories" # MarketWatch
        ],
        "crypto": [
            "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "https://cointelegraph.com/rss",
            "https://www.investing.com/rss/news_301.rss"
        ]
    }
    
    source_urls = rss_sources.get(category, rss_sources["general"])
    all_headlines = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Konu Eşleştirme (Keyword -> Görünen İsim)
    topic_map = {
        "cpi": "US CPI Data",
        "inflation": "Inflation",
        "fed": "Federal Reserve",
        "fomc": "FOMC",
        "powell": "Jerome Powell",
        "treasury": "Treasury Yields",
        "yield": "Treasury Yields",
        "bitcoin": "Bitcoin",
        "btc": "Bitcoin",
        "ethereum": "Ethereum",
        "eth": "Ethereum",
        "gold": "Gold",
        "silver": "Silver",
        "oil": "Crude Oil",
        "brent": "Brent Oil",
        "nvidia": "Nvidia",
        "nvda": "Nvidia",
        "tesla": "Tesla",
        "tsla": "Tesla",
        "apple": "Apple",
        "aapl": "Apple",
        "meta": "Meta",
        "google": "Alphabet",
        "microsoft": "Microsoft",
        "earnings": "Earnings",
        "jobs": "Jobs Report",
        "unemployment": "Unemployment",
        "gdp": "GDP Data",
        "retail": "Retail Sales",
        "china": "China Markets",
        "ecb": "ECB",
        "stocks": "US Stocks",
        "wall street": "Wall Street",
        "dow": "Dow Jones",
        "nasdaq": "Nasdaq",
        "s&p": "S&P 500",
        "solana": "Solana",
        "binance": "Binance",
        "sec": "SEC Regulation",
        "etf": "ETF Flows"
    }

    # Yasaklı Kelimeler (Soru cümleleri, rehberler, görüş yazıları)
    exclude_terms = [
        "how to", "what is", "when is", "should you", "could", "would", 
        "review", "opinion", "podcast", "guide", "best", "top 10", "top 5", 
        "vs.", "transcript", "motley", "zacks", "guru", "prediction",
        "subscribers only", "premium", "webinar"
    ]
    
    # -----------------------------------------------------------
    # Kaynak Bazlı RSS Tanımları
    # -----------------------------------------------------------
    rss_definitions = [
        # YAHOO FINANCE
        {"url": "https://finance.yahoo.com/news/rssindex", "name": "Yahoo", "cats": ["general", "stocks"]},
        # CNBC
        {"url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664", "name": "CNBC", "cats": ["general"]},
        {"url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114", "name": "CNBC", "cats": ["stocks"]},
        # WSJ / MARKETWATCH
        {"url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml", "name": "WSJ", "cats": ["general"]},
        {"url": "https://feeds.content.dowjones.io/public/rss/mw_topstories", "name": "MarketWatch", "cats": ["stocks"]},
        # INVESTING.COM
        {"url": "https://www.investing.com/rss/news.rss", "name": "Investing", "cats": ["general"]},
        {"url": "https://www.investing.com/rss/news_301.rss", "name": "Investing", "cats": ["crypto"]},
        # CRYPTO SPECIFIC
        {"url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "name": "CoinDesk", "cats": ["crypto"]},
        {"url": "https://cointelegraph.com/rss", "name": "CoinTelegraph", "cats": ["crypto"]}
    ]
    
    # İlgili kategorideki URL'leri filtrele
    source_list = [item for item in rss_definitions if category in item["cats"]]
    
    all_headlines = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Tüm kaynakları tara
    for src in source_list:
        if len(all_headlines) >= 8: break # Yeterince haber bulduysak dur
        
        url = src["url"]
        source_name = src["name"]
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            feed = feedparser.parse(BytesIO(response.content))
            
            for entry in feed.entries:
                if len(all_headlines) >= 8: break
                
                title = entry.title
                link = entry.link
                
                # Sıkı Filtreleme
                lower_title = title.lower()
                if any(term in lower_title for term in exclude_terms):
                    continue
                if "?" in title: # Soru cümlelerini atla
                    continue
                
                # Akıllı Formatlama
                formatted_title = clean_and_format_headline(title, source_name, topic_map)
                
                # Mükerrer kontrolü (Basitçe başlığın ilk 20 karakteri)
                if any(formatted_title[:20] in h[0] for h in all_headlines):
                    continue
                    
                all_headlines.append((formatted_title, link))
                
        except Exception as e:
            # st.error(f"RSS Error ({url}): {e}") # Hata olursa kullanıcıyı yorma, sessizce geç
            continue
            
    return all_headlines

def calculate_rsi(series, period=14):
    """
    Basit RSI (Relative Strength Index) Hesaplayıcı
    """
    if len(series) < period + 1:
        return None
        
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def get_symbol_data(item):
    """
    Tek bir sembol için verileri çeker (History kullanarak, RSI için).
    """
    ticker = item['ticker']
    try:
        t = yf.Ticker(ticker)
        # RSI için en az 1 aylık veriye ihtiyaç var (14 periyotluk hesaplama için)
        hist = t.history(period="1mo")
        
        if hist.empty:
            return {"id": item['id'], "last_price": None, "error": "No Data"}
            
        last_price = hist["Close"].iloc[-1]
        prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else last_price
        
        # RSI Hesapla
        rsi_val = calculate_rsi(hist["Close"])
        
        return {
            "id": item['id'],
            "last_price": last_price,
            "prev_close": prev_close,
            "rsi": rsi_val,
            "error": None
        }
    except Exception as e:
        return {
            "id": item['id'],
            "last_price": None,
            "prev_close": None,
            "rsi": None,
            "error": str(e)
        }

def get_market_data(selected_assets_list, lang_code="tr"):
    """
    Seçili varlıklar için verileri çeker ve formatlı metin döndürür.
    """
    if not selected_assets_list:
        return "Lütfen en az bir varlık seçin."
        
    try:
        # Ticker listesi oluştur
        tickers = [item['ticker'] for item in selected_assets_list]
        
        # Paralel veri çekme
        results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_item = {executor.submit(get_symbol_data, item): item for item in selected_assets_list}
            for future in concurrent.futures.as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    data = future.result()
                    results[data['id']] = data
                except Exception as e:
                    results[item['id']] = {"error": str(e), "last_price": None}
        
        output_lines = []
        processed_results = [] # İstatistikler için
        
        # 1. Başlık (Zamana Göre Dinamik)
        current_hour = datetime.now().hour
        if 6 <= current_hour < 12:
            header_emoji = "☕"
            header_text = "MORNING BRIEF" if lang_code == "en" else "GÜNAYDIN PİYASALAR"
        elif 12 <= current_hour < 18:
            header_emoji = "☀️"
            header_text = "MID-DAY PULSE" if lang_code == "en" else "GÜN ORTASI NABZI"
        elif 18 <= current_hour < 23:
            header_emoji = "🌙"
            header_text = "CLOSING BELL" if lang_code == "en" else "KAPANIŞ RAPORU"
        else:
            header_emoji = "🦉"
            header_text = "NIGHT WATCH" if lang_code == "en" else "GECE NÖBETİ"
            
        full_header = f"🚨 {header_emoji} **{header_text}**"
        output_lines.append(full_header)
        output_lines.append(f"🗓️ {datetime.now().strftime('%d.%m.%Y')}")
        output_lines.append("─" * 20)
        
        # 2. Varlık Listesi
        valid_data_count = 0
        positive_count = 0
        negative_count = 0
        
        asset_lines = []
        
        for item in selected_assets_list:
            data = results.get(item['id'])
            name = item[f"name_{lang_code.lower()}"]
            emoji = item['emoji']
            ticker = item['ticker']
            
            res_obj = {"name": name, "pct_change": 0.0, "valid": False}
            
            if data and data.get("last_price") is not None:
                last_price = data["last_price"]
                prev_close = data.get("prev_close")
                
                # Fiyat Formatı
                price_fmt = f"${last_price:,.2f}"
                if "TRY" in ticker:
                    price_fmt = f"₺{last_price:,.2f}"
                
                # Değişim Hesapla
                change_str = ""
                pct_change = 0.0
                
                if prev_close and prev_close > 0:
                    pct_change = ((last_price - prev_close) / prev_close) * 100
                    res_obj["pct_change"] = pct_change
                    res_obj["valid"] = True
                    valid_data_count += 1
                    
                    # Yön Emojisi
                    if pct_change > 0:
                        dir_emoji = "🟢"
                        sign = "+"
                        positive_count += 1
                    elif pct_change < 0:
                        dir_emoji = "🔻"
                        sign = ""
                        negative_count += 1
                    else:
                        dir_emoji = "⚪️"
                        sign = ""
                        
                    if abs(pct_change) < 0.01:
                         change_str = f"⚪️ (0.00%)"
                    else:
                         change_str = f"{dir_emoji} ({sign}{pct_change:.2f}%)"
                
                # RSI Sinyali
                rsi_str = ""
                rsi_val = data.get("rsi")
                if rsi_val:
                    if rsi_val < 30:
                        rsi_str = " 🔥 OVERSOLD (Al?)" if lang_code == "tr" else " 🔥 OVERSOLD"
                    elif rsi_val > 70:
                        rsi_str = " ⚠️ OVERBOUGHT (Sat?)" if lang_code == "tr" else " ⚠️ OVERBOUGHT"
                
                line = f"{emoji} {name}: {price_fmt} {change_str}{rsi_str}"
                asset_lines.append(line)
            else:
                asset_lines.append(f"{emoji} {name}: {texts['no_data']}")
            
            processed_results.append(res_obj)

        # 3. Piyasa Modu (Market Vibe)
        if valid_data_count > 0:
            if positive_count > negative_count:
                vibe = "🐂 BULLISH (Yükseliş)" if lang_code == "tr" else "🐂 BULLISH"
            elif negative_count > positive_count:
                vibe = "🐻 BEARISH (Düşüş)" if lang_code == "tr" else "🐻 BEARISH"
            else:
                vibe = "🦀 NEUTRAL (Yatay)" if lang_code == "tr" else "🦀 NEUTRAL"
            
            output_lines.insert(2, f"Mood: {vibe}\n")
        
        output_lines.extend(asset_lines)
        
        # 4. Hot Movers (En Çok Kazandıran/Kaybettiren)
        valid_items = [x for x in processed_results if x["valid"]]
        if len(valid_items) >= 2:
            sorted_items = sorted(valid_items, key=lambda x: x["pct_change"], reverse=True)
            top_gainer = sorted_items[0]
            top_loser = sorted_items[-1]
            
            output_lines.append("\n🔥 **HOT MOVERS**")
            output_lines.append(f"🚀 Top Gainer: {top_gainer['name']} (+{top_gainer['pct_change']:.2f}%)")
            output_lines.append(f"📉 Top Loser: {top_loser['name']} ({top_loser['pct_change']:.2f}%)")

        # 5. FnG Ekle
        fng_val, fng_class = get_fng_data()
        if fng_val:
            output_lines.append("─" * 20)
            fng_line = f"🧠 {texts['fng_title']}: {fng_val} ({fng_class})"
            output_lines.append(fng_line)
        
        return "\n".join(output_lines)

    except Exception as e:
        return f"{texts['error']} {str(e)}"

# ==========================================
# 4. AKSİYON
# ==========================================

# Sekmeler
tab1, tab2, tab3 = st.tabs(["📊 " + texts["title"], texts["news_tab"], texts["chart_tab"]])

with tab1:
    if st.button(texts["fetch_btn"], type="primary"):
        result_text = get_market_data(selected_items, lang_choice)
        
        st.subheader(texts["copy_title"])
        st.code(result_text, language="text")
        
        # Tweet Butonu
        encoded_text = urllib.parse.quote(result_text)
        tweet_url = f"https://twitter.com/intent/tweet?text={encoded_text}"
        st.link_button(texts["tweet_btn"], tweet_url)
        
        st.success(texts["success"])

with tab2:
    st.header(texts["news_tab"])
    
    # Session State Başlatma
    if "news_data" not in st.session_state:
        st.session_state["news_data"] = []
    
    col_n1, col_n2, col_n3, col_n4 = st.columns([1, 1, 1, 1])
    
    fetch_trigger = None
    if col_n1.button(texts["news_morning"]): fetch_trigger = "general"
    if col_n2.button(texts["news_noon"]): fetch_trigger = "stocks"
    if col_n3.button(texts["news_evening"]): fetch_trigger = "crypto"
    
    # Temizle Butonu
    if col_n4.button("🧹 Clear"):
        st.session_state["news_data"] = []
        st.experimental_rerun()
        
    if fetch_trigger:
        with st.spinner(texts["loading"]):
            headlines = fetch_finance_news(fetch_trigger)
            if not headlines:
                st.warning("No news found.")
            else:
                # Mevcut listeye ekle (En başa)
                # Format: {"id": unique, "text": h, "link": link, "selected": True}
                for h, link in reversed(headlines):
                    # Mükerrer kontrolü
                    if not any(item["text"] == h for item in st.session_state["news_data"]):
                         st.session_state["news_data"].insert(0, {
                             "id": str(uuid.uuid4()),
                             "text": h,
                             "link": link,
                             "selected": True
                         })
    
    # Haber Listesi ve Düzenleme Arayüzü
    if st.session_state["news_data"]:
        st.markdown("---")
        st.write("### 📝 Tweet Composer")
        
        # Seçili haberleri tutacak liste
        final_tweet_parts = []
        
        # Her haber için kart
        for i, item in enumerate(st.session_state["news_data"]):
            with st.container():
                c1, c2 = st.columns([0.1, 0.9])
                
                # Checkbox
                is_selected = c1.checkbox("", value=item["selected"], key=f"chk_{item['id']}")
                st.session_state["news_data"][i]["selected"] = is_selected
                
                # Text Area (Düzenlenebilir)
                new_text = c2.text_area(f"News #{i+1}", value=item["text"], height=70, key=f"txt_{item['id']}", label_visibility="collapsed")
                st.session_state["news_data"][i]["text"] = new_text
                
                # Linki göster (Opsiyonel)
                c2.caption(f"🔗 [Source]({item['link']})")
                
        # Tweet Oluşturma Bölümü
        st.markdown("---")
        st.subheader("🚀 Ready to Tweet")
        
        # Şablon Seçimi
        template_options = ["Standard", "Breaking News", "Market Recap", "Crypto Alert"]
        selected_template = st.selectbox("Choose Template", template_options)
        
        # Seçili haberleri birleştir
        selected_items = [item for item in st.session_state["news_data"] if item["selected"]]
        
        if selected_items:
            tweet_body = ""
            today_str = datetime.now().strftime("%d %B %Y")
            
            if selected_template == "Standard":
                tweet_body = f"📅 **{today_str} - Market Update**\n\n"
            elif selected_template == "Breaking News":
                tweet_body = f"🚨 **BREAKING NEWS ({today_str})**\n\n"
            elif selected_template == "Market Recap":
                tweet_body = f"📊 **Daily Market Recap**\n\n"
            elif selected_template == "Crypto Alert":
                tweet_body = f"⚡ **Crypto Flash Update**\n\n"
            
            # Haberleri ekle
            hashtags = set()
            for item in selected_items:
                tweet_body += f"{item['text']}\n\n"
                
                # Otomatik Hashtag Çıkarımı
                lower_text = item['text'].lower()
                if "bitcoin" in lower_text: hashtags.add("#Bitcoin")
                if "crypto" in lower_text: hashtags.add("#Crypto")
                if "fed " in lower_text: hashtags.add("#Fed")
                if "inflation" in lower_text: hashtags.add("#Inflation")
                if "gold" in lower_text: hashtags.add("#Gold")
                if "stock" in lower_text: hashtags.add("#Stocks")
                if "apple" in lower_text: hashtags.add("$AAPL")
                if "tesla" in lower_text: hashtags.add("$TSLA")
                if "nvidia" in lower_text: hashtags.add("$NVDA")
            
            # Hashtagleri ekle
            if hashtags:
                tweet_body += " ".join(hashtags)
            
            # Sonuç Kutusu
            st.text_area("Final Tweet", value=tweet_body, height=300)
            
            # Butonlar
            tc1, tc2 = st.columns(2)
            if tc1.button("📋 Copy to Clipboard"):
                st.toast("Copied to clipboard! (Simulation)", icon="✅")
                # Streamlit'te doğrudan panoya kopyalama kısıtlıdır, kullanıcı manuel kopyalar.
            
            # Twitter Intent
            encoded_tweet = urllib.parse.quote(tweet_body)
            tweet_link = f"https://twitter.com/intent/tweet?text={encoded_tweet}"
            tc2.link_button("🐦 Send Tweet", tweet_link)
            
        else:
            st.info("Select news items above to generate a tweet.")
            
    else:
        st.info("👆 Click buttons above to fetch news and start composing.")

with tab3:
    st.subheader(texts["chart_tab"])
    
    # Varlık Listesi (İsim + Ticker)
    asset_options = {f"{a['emoji']} {a['name_tr' if lang_choice == 'TR' else 'name_en']}": a['id'] for a in ASSETS_DB}
    
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_asset_name = st.selectbox(texts["chart_select"], list(asset_options.keys()))
    with col2:
        # Zaman Aralığı Seçimi
        range_options = ["1D (5m)", "5D (30m)", "1M (1d)"]
        selected_range = st.selectbox(texts["chart_range_label"], range_options, index=1) # Varsayılan: 5D
    
    selected_asset_id = asset_options[selected_asset_name]
    
    # Seçilen asset'in ticker'ını bul
    selected_ticker = next((a['ticker'] for a in ASSETS_DB if a['id'] == selected_asset_id), None)
    
    if st.button(texts["chart_btn"], type="primary"):
        with st.spinner(texts["loading"]):
            try:
                # Aralığa göre parametreleri belirle
                p_period = "5d"
                p_interval = "30m"
                
                if "1D" in selected_range:
                    p_period = "1d"
                    p_interval = "5m"
                elif "5D" in selected_range:
                    p_period = "5d"
                    p_interval = "30m"
                elif "1M" in selected_range:
                    p_period = "1mo"
                    p_interval = "1d"
                
                # Veri Çekme (Ticker.history ile daha stabil)
                ticker_obj = yf.Ticker(selected_ticker)
                df = ticker_obj.history(period=p_period, interval=p_interval)
                
                # Fallback: Eğer 1D boşsa 5D dene
                if df.empty and p_period == "1d":
                     st.warning("1 Günlük veri bulunamadı, 5 Günlük veriye geçiliyor...")
                     df = ticker_obj.history(period="5d", interval="30m")
                     p_period = "5d"
                
                if not df.empty:
                    # Timezone Standardizasyonu (UTC)
                    if df.index.tzinfo is None:
                        df.index = df.index.tz_localize('UTC')
                    else:
                        df.index = df.index.tz_convert('UTC')

                    # TradingView Tarzı Stil
                    mc = mpf.make_marketcolors(
                        up='#00ff88', down='#ff0055',
                        edge='inherit',
                        wick='inherit',
                        volume='in',
                        ohlc='inherit'
                    )
                    s = mpf.make_mpf_style(
                        base_mpf_style='nightclouds',
                        marketcolors=mc,
                        gridstyle='--',
                        y_on_right=True
                    )

                    # Grafik Başlığı
                    chart_title = f"\n{selected_asset_name} ({p_period.upper()} - UTC)"

                    # Grafiği Çiz (Candlestick)
                    fig, axlist = mpf.plot(
                        df,
                        type='candle',
                        style=s,
                        title=dict(title=chart_title, color='white', fontsize=14),
                        ylabel='',
                        ylabel_lower='',
                        volume=False, # Hacim verisi bazen eksik olabiliyor, şimdilik kapalı
                        figsize=(10, 5),
                        returnfig=True,
                        datetime_format='%H:%M' if p_period == "1d" else '%m-%d %H:%M',
                        tight_layout=True
                    )
                    
                    # Streamlit'te göster
                    st.pyplot(fig)

                    # Kaydet ve İndirme Butonu
                    buf = BytesIO()
                    fig.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor='black')
                    st.download_button(
                        label=texts["chart_download"],
                        data=buf.getvalue(),
                        file_name=f"{selected_asset_id}_{p_period}_chart.png",
                        mime="image/png"
                    )
                else:
                    st.error(texts["no_data"])
            except Exception as e:
                st.error(f"{texts['error']} {e}")
