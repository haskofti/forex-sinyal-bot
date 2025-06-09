
import requests
import pandas as pd
import smtplib
from email.mime.text import MIMEText

API_KEY = "023335a787744744b184cc9ecc6805d2"
SYMBOL = "XAU/USD"
INTERVAL = "1h"

EMAIL = "hafi26@gmail.com"
PASSWORD = "wtjl jnqo xqdc hyqh"
TO = "hafi26@gmail.com"

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = TO
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)

def fetch_data(interval):
    url = f"https://api.twelvedata.com/time_series?symbol={SYMBOL}&interval={interval}&outputsize=100&apikey={API_KEY}"
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

def calculate_indicators(df):
    df["MA50"] = df["close"].rolling(window=50).mean()
    df["MA200"] = df["close"].rolling(window=200).mean()
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))
    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["20MA"] = df["close"].rolling(window=20).mean()
    df["Upper"] = df["20MA"] + 2 * df["close"].rolling(window=20).std()
    df["Lower"] = df["20MA"] - 2 * df["close"].rolling(window=20).std()
    return df

def generate_signal(df):
    latest = df.iloc[-1]
    price = latest["close"]
    rsi = latest["RSI"]
    macd_signal = "AL" if latest["MACD"] > latest["Signal"] else "SAT"
    ma_signal = "AL" if latest["MA50"] > latest["MA200"] else "SAT"
    boll_signal = "AL" if price < latest["Lower"] else "SAT" if price > latest["Upper"] else "NÖTR"
    fib_618 = 2350
    fib_382 = 2420
    fib_signal = "AL" if price < fib_618 else "SAT" if price > fib_382 else "NÖTR"
    signals = [("RSI", "AL" if rsi < 30 else "SAT" if rsi > 70 else "NÖTR"),
               ("MACD", macd_signal),
               ("MA", ma_signal),
               ("Bollinger", boll_signal),
               ("Fibonacci", fib_signal)]
    al_count = sum(1 for _, s in signals if s == "AL")
    sat_count = sum(1 for _, s in signals if s == "SAT")
    if al_count >= 4:
        return f"GÜÇLÜ AL\nFiyat: {price:.2f}"
    elif sat_count >= 4:
        return f"GÜÇLÜ SAT\nFiyat: {price:.2f}"
    else:
        return "Sinyal YOK (kararsız)"

def main():
    zaman_dilimleri = ["30min", "1h", "4h"]
    tum_sinyaller = ""

    for zaman in zaman_dilimleri:
        try:
            df = fetch_data(interval=zaman)
            df = calculate_indicators(df)
            signal = generate_signal(df)
            tum_sinyaller += f"[{zaman}] {signal}\\n"
        except Exception as e:
            tum_sinyaller += f"[{zaman}] Hata: {str(e)}\\n"

    print(tum_sinyaller)
    send_email("Forex Sinyal (Çoklu Zaman)", tum_sinyaller)
    except Exception as e:
        print("HATA:", e)

if __name__ == "__main__":
    main()
