import yfinance as yf

# Altın için farklı sembolleri test et
tickers = ["GC=F", "XAU-USD", "GLD"]
print("Altın Sembol Testi:")
for t in tickers:
    try:
        ticker = yf.Ticker(t)
        # Fast info
        price = ticker.fast_info.last_price
        print(f"{t}: {price}")
    except Exception as e:
        print(f"{t}: Hata - {e}")
