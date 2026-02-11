import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import sys

# Takip edilecek varlıklar ve sembolleri
ASSETS = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Gold": "GC=F",
    "Silver": "SI=F",
    "SP500": "^GSPC",
    "NASDAQ": "^IXIC",
    "NYSE": "^NYA",
    "DOW JONES": "^DJI"
}

def get_market_data():
    """
    Yahoo Finance üzerinden anlık verileri çeker ve formatlar.
    """
    tickers = list(ASSETS.values())
    
    try:
        # Verileri çek (son 1 gün, 1 dakika aralıklı - son fiyatı almak için)
        # progress=False ile terminal kirliliğini önlüyoruz
        data = yf.download(tickers, period="1d", interval="1m", progress=False)
        
        # Sadece 'Close' (Kapanış) fiyatlarını alıyoruz
        if isinstance(data.columns, pd.MultiIndex):
            closes = data['Close']
        elif 'Close' in data.columns:
            closes = data[['Close']] # DataFrame olarak kalsın
        else:
            closes = data
            
        output_lines = []
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output_lines.append(f"📅 Tarih: {current_time}")
        output_lines.append("-" * 30)

        # Her varlık için son fiyatı bul
        for name, ticker in ASSETS.items():
            try:
                # Ticker verisi var mı kontrol et
                if ticker in closes.columns:
                    series = closes[ticker].dropna()
                    
                    if not series.empty:
                        last_price = series.iloc[-1]
                        # Formatlama: Virgüllü ayraç ve 2 ondalık basamak
                        formatted_price = f"${last_price:,.2f}"
                        output_lines.append(f"{name}: {formatted_price}")
                    else:
                        output_lines.append(f"{name}: Veri Yok (Piyasa Kapalı Olabilir)")
                else:
                    # Tek ticker durumu (Series dönebilir) veya kolon bulunamadı
                    if isinstance(closes, pd.Series):
                        # Tek ticker varsa ve isim uyuşmuyorsa bile eldeki veriyi kullanmayı dene
                        series = closes.dropna()
                        if not series.empty:
                            last_price = series.iloc[-1]
                            output_lines.append(f"{name}: ${last_price:,.2f}")
                        else:
                            output_lines.append(f"{name}: Veri Yok")
                    else:
                        output_lines.append(f"{name}: Veri İndirilemedi")
            except Exception as e:
                output_lines.append(f"{name}: Hata ({str(e)})")
        
        return "\n".join(output_lines)

    except Exception as e:
        return f"Genel Veri Çekme Hatası: {str(e)}"

def main():
    print("Market Takip Sistemi Başlatılıyor... (Çıkış için Ctrl+C)")
    print("Her 60 saniyede bir güncellenecek.\n")
    
    try:
        while True:
            tweet_content = get_market_data()
            print(tweet_content)
            print("\n" + "="*30 + "\n")
            
            # 60 saniye bekle
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nSistem durduruldu.")
        sys.exit(0)

if __name__ == "__main__":
    main()
