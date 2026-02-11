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
    "TR": {
        "title": "📈 Anlık Piyasa Takip ve Tweet Oluşturucu",
        "desc": "Aşağıdan istediğiniz varlıkları seçin ve güncel verileri çekin.",
        "select_all": "Tümünü Seç",
        "fetch_btn": "Verileri Getir",
        "copy_title": "📋 Kopyalanabilir Metin",
        "success": "Veriler güncellendi!",
        "error": "Hata oluştu:",
        "no_selection": "Lütfen en az bir varlık seçiniz.",
        "loading": "Veriler çekiliyor...",
        "no_data": "Veri Yok",
        "snapshot_header": "📊 PİYASA ÖZETİ",
        "presets": "Hazır Paketler",
        "tweet_btn": "🐦 Tweet At",
        "comment_title": "🤖 Piyasa Yorumu",
        "fng_title": "😨 Kripto Korku & Açgözlülük",
        "news_tab": "📰 Haber Akışı & Özet",
        "news_morning": "☕️ Sabah: Genel Ekonomi",
        "news_noon": "☀️ Öğlen: Borsa & Şirketler",
        "news_evening": "🌙 Akşam: Kripto & Kapanış",
        "news_fetch": "Haberleri Getir ve Özetle",
        "news_header": "📌 {} | Finans Özeti",
        "chart_tab": "📈 Grafik Oluşturucu",
        "chart_select": "Varlık Seçin:",
        "chart_range_label": "Zaman Aralığı:",
        "chart_btn": "Grafiği Oluştur",
        "chart_download": "Grafiği İndir (PNG)",
        "chart_title": "{} Günlük Grafik",
    },
    "EN": {
        "title": "📈 Live Market Tracker & Tweet Generator",
        "desc": "Select assets below to fetch real-time data.",
        "select_all": "Select All",
        "fetch_btn": "Fetch Data",
        "copy_title": "📋 Copyable Text",
        "success": "Data updated!",
        "error": "Error occurred:",
        "no_selection": "Please select at least one asset.",
        "loading": "Fetching data...",
        "no_data": "No Data",
        "snapshot_header": "📊 MARKET SNAPSHOT",
        "presets": "Presets",
        "tweet_btn": "🐦 Tweet This",
        "comment_title": "🤖 Market Comment",
        "fng_title": "😨 Crypto Fear & Greed",
        "news_tab": "📰 News Feed & Summary",
        "news_morning": "☕️ Morning: General Economy",
        "news_noon": "☀️ Noon: Stocks & Companies",
        "news_evening": "🌙 Evening: Crypto & Closing",
        "news_fetch": "Fetch & Summarize News",
        "news_header": "📌 {} | Finance Summary",
        "chart_tab": "📈 Chart Generator",
        "chart_select": "Select Asset:",
        "chart_range_label": "Time Range:",
        "chart_btn": "Generate Chart",
        "chart_download": "Download Chart (PNG)",
        "chart_title": "{} Daily Chart",
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

# Dil Seçimi (Sidebar)
with st.sidebar:
    st.header("⚙️ Ayarlar / Settings")
    lang_choice = st.radio("Dil / Language", ["TR", "EN"], index=0)
    
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

def fetch_finance_news(category="general"):
    """
    Yahoo Finance RSS feed'inden haberleri çeker ve basitçe formatlar.
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
    exclude_terms = ["how", "why", "what", "when", "is", "should", "could", "would", "can", "review", "opinion", "podcast", "guide", "best", "top", "vs", "?", "transcript", "motley", "zacks"]

    # Tüm kaynakları tara
    for url in source_urls:
        if len(all_headlines) >= 5: break # Yeterince haber bulduysak dur
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            feed = feedparser.parse(BytesIO(response.content))
            
            for entry in feed.entries:
                title = entry.title
                summary = entry.get("summary", "")
                
                # Temizlik
                clean_title = title.split(" - ")[0].split(" | ")[0].strip()
                lower_title = clean_title.lower()
                
                # 1. ADIM: Sıkı Filtreleme (Soru ve Clickbait engelleme)
                if any(term in lower_title.split() for term in exclude_terms):
                    continue # Yasaklı kelime varsa atla
                
                if "?" in clean_title:
                    continue # Soru işareti varsa atla
                
                # 2. ADIM: Konu Belirleme ve Formatlama
                detected_topic = None
                display_topic = None
                
                # Başlık içinde konu ara
                for key, val in topic_map.items():
                    if key in lower_title:
                        detected_topic = key
                        display_topic = val
                        break
                
                # Eğer konu bulamadıysak ve kategori 'general' değilse, kategoriyi konu yap
                if not detected_topic:
                     if category == "crypto" and ("bitcoin" not in lower_title):
                         # Kripto haberlerinde konu yoksa genel bırak
                         pass
                
                # Konu bulunduysa formatla: "Konu — Geri Kalan"
                final_text = ""
                emoji = "📰"
                
                if detected_topic:
                     # Emojiyi ayarla
                     if display_topic in ["US CPI Data", "Inflation", "GDP Data"]: emoji = "🇺🇸"
                     elif display_topic in ["Federal Reserve", "FOMC", "Jerome Powell", "Treasury Yields"]: emoji = "📉"
                     elif display_topic in ["Crude Oil", "Brent Oil"]: emoji = "🛢️"
                     elif display_topic in ["Gold", "Silver"]: emoji = "🟡"
                     elif display_topic in ["Bitcoin", "Ethereum", "Solana"]: emoji = "🟠"
                     elif display_topic in ["Nvidia", "Tesla", "Apple", "Microsoft", "Tech"]: emoji = "🤖"
                     
                     # Başlıktan konuyu temizlemeye çalış (Opsiyonel, bazen tekrar güzel durabilir)
                     # Amaç: "Bitcoin drops" -> "Bitcoin — Drops..."
                     
                     final_text = f"{emoji} {display_topic} — {clean_title}"
                else:
                    # Konu yoksa ama filtreyi geçtiyse (Önemli olabilir)
                    # Sadece kategoriye uygunsa al
                    text_to_check = (title + " " + summary).lower()
                    if any(k in text_to_check for k in keywords[category]):
                         final_text = f"📰 {clean_title}"
                
                if final_text:
                     # Mükerrer kontrol
                     if not any(clean_title in h for h in all_headlines):
                         all_headlines.append(final_text)
                
                if len(all_headlines) >= 5: break
        except:
            continue
            
    if not all_headlines:
        return ["📰 No major headlines found for this category right now."]
        
    return all_headlines

def get_symbol_data(item):
    """
    Tek bir sembol için verileri çeker (fast_info kullanarak).
    """
    ticker = item['ticker']
    try:
        t = yf.Ticker(ticker)
        # fast_info genelde daha hızlıdır ve güvenilir last_price/prev_close verir
        info = t.fast_info
        
        last_price = info.last_price
        prev_close = info.previous_close
        
        return {
            "id": item['id'],
            "last_price": last_price,
            "prev_close": prev_close,
            "error": None
        }
    except Exception as e:
        return {
            "id": item['id'],
            "last_price": None,
            "prev_close": None,
            "error": str(e)
        }

def get_market_data(selected_assets_list, lang_code):
    if not selected_assets_list:
        return texts["no_selection"]
        
    try:
        output_lines = []
        
        with st.spinner(texts["loading"]):
            # Paralel veri çekimi (Hızlandırmak için)
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
            
            # Sonuçları işle
            processed_results = []
            
            # Başlık Ekle
            header_text = LANG[lang_code]["snapshot_header"]
            output_lines.insert(0, header_text)
            
            for item in selected_assets_list:
                data = results.get(item['id'])
                name = item[f"name_{lang_code.lower()}"]
                emoji = item['emoji']
                ticker = item['ticker']
                
                res_obj = {"name": name, "pct_change": None}
                
                if data and data.get("last_price") is not None:
                    last_price = data["last_price"]
                    prev_close = data.get("prev_close")
                    
                    # Fiyat Formatı
                    price_fmt = f"${last_price:,.2f}"
                    if "TRY" in ticker:
                        price_fmt = f"₺{last_price:,.2f}"
                    
                    # Değişim Hesapla
                    change_str = ""
                    if prev_close and prev_close > 0:
                        pct_change = ((last_price - prev_close) / prev_close) * 100
                        res_obj["pct_change"] = pct_change
                        
                        # Yön Emojisi
                        if pct_change > 0:
                            dir_emoji = "🟢"
                            sign = "+"
                        elif pct_change < 0:
                            dir_emoji = "🔻"
                            sign = ""
                        else:
                            dir_emoji = "⚪️"
                            sign = ""
                            
                        if abs(pct_change) < 0.01:
                             change_str = f"⚪️ (0.00%)"
                        else:
                             change_str = f"{dir_emoji} ({sign}{pct_change:.2f}%)"
                    
                    line = f"{emoji} {name}: {price_fmt} {change_str}"
                    output_lines.append(line)
                else:
                    output_lines.append(f"{emoji} {name}: {texts['no_data']}")
                
                processed_results.append(res_obj)

            # FnG Ekle
            fng_val, fng_class = get_fng_data()
            if fng_val:
                fng_line = f"🧠 {texts['fng_title']}: {fng_val} ({fng_class})"
                output_lines.append(fng_line)

            # Yorum Ekle
            comment = generate_commentary(processed_results, lang_code)
            if comment:
                 output_lines.append(f"\n💡 {comment}")
            
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
    
    col_n1, col_n2, col_n3 = st.columns(3)
    
    news_cat = None
    if col_n1.button(texts["news_morning"]):
        news_cat = "general"
    if col_n2.button(texts["news_noon"]):
        news_cat = "stocks"
    if col_n3.button(texts["news_evening"]):
        news_cat = "crypto"
        
    if news_cat:
        with st.spinner(texts["loading"]):
            headlines = fetch_finance_news(news_cat)
            
            # Tarih ve Başlık
            today_str = datetime.now().strftime("%A")
            header = texts["news_header"].format(today_str)
            
            news_text = f"{header}\n"
            for h in headlines:
                news_text += f" {h}\n"
            
            st.code(news_text, language="text")
            
            # Tweet Butonu
            encoded_news = urllib.parse.quote(news_text)
            news_tweet_url = f"https://twitter.com/intent/tweet?text={encoded_news}"
            # st.link_button bazen eski sürümlerde 'key' hatası verebilir, garanti olsun diye parametresiz veya markdown
            try:
                st.link_button(texts["tweet_btn"], news_tweet_url)
            except:
                st.markdown(f"[🐦 {texts['tweet_btn']}]({news_tweet_url})")

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
