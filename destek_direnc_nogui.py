
import requests
import pandas as pd
from datetime import datetime

API_KEY = "023335a787744744b184cc9ecc6805d2"
SYMBOL = "XAU/USD"
INTERVAL = "4h"

def fetch_data():
    url = f"https://api.twelvedata.com/time_series?symbol={SYMBOL}&interval={INTERVAL}&outputsize=100&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    if "values" not in data:
        raise ValueError(data.get("message", "Veri alınamadı."))
    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")
    df.set_index("datetime", inplace=True)
    df = df.astype(float)
    return df

def detect_levels(df):
    levels = []
    high = df["high"]
    low = df["low"]
    for i in range(2, len(df) - 2):
        if high[i] > high[i-1] and high[i] > high[i-2] and high[i] > high[i+1] and high[i] > high[i+2]:
            levels.append(("Direnç", df.index[i], high[i]))
        if low[i] < low[i-1] and low[i] < low[i-2] and low[i] < low[i+1] and low[i] < low[i+2]:
            levels.append(("Destek", df.index[i], low[i]))
    return levels

def main():
    df = fetch_data()
    levels = detect_levels(df)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"🟡 {SYMBOL} - {INTERVAL} Zaman Dilimi | {now}")
    for t, ts, level in levels[-10:]:
        print(f"{t}: {level:.2f} ({ts.strftime('%Y-%m-%d %H:%M')})")

if __name__ == "__main__":
    main()
