# data_loader.py
import requests
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class AlpacaAPI:
    def __init__(self, api_key: str, api_secret: str, feed: str = "iex"):
        self.headers = {"APCA-API-KEY-ID": api_key, "APCA-API-SECRET-KEY": api_secret}
        self.base_url = "https://data.alpaca.markets"
        self.feed = feed

    def get_market_range(self, days_back: int) -> tuple[str, str]:
        ny = ZoneInfo("America/New_York")
        now = datetime.now(ny)

        # END = last completed trading day @ 4 PM
        end = now.replace(hour=16, minute=0, second=0, microsecond=0)
        if now.weekday() >= 5 or now.time() < pd.Timestamp("09:30").time():
            end -= timedelta(days=1)
        while end.weekday() >= 5:
            end -= timedelta(days=1)

        # START = N trading days back
        start = end
        trading_days = 0
        while trading_days < days_back:
            start -= timedelta(days=1)
            if start.weekday() < 5:
                trading_days += 1
        start = start.replace(hour=9, minute=30, second=0, microsecond=0)

        return start.isoformat(), end.isoformat()

    def get_bars(self, symbol: str, timeframe: str, start: str, end: str) -> pd.DataFrame:
        url = f"{self.base_url}/v2/stocks/{symbol}/bars"
        params = {"timeframe": timeframe, "start": start, "end": end,
                  "limit": 10000, "adjustment": "split", "feed": self.feed}
        try:
            r = requests.get(url, headers=self.headers, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
            if not data.get("bars"):
                return pd.DataFrame()
            df = pd.DataFrame(data["bars"])
            df["timestamp"] = pd.to_datetime(df["t"], utc=True).dt.tz_convert("America/New_York")
            df = df.rename(columns={"o":"Open","h":"High","l":"Low","c":"Close","v":"Volume"})
            df = df[["timestamp","Open","High","Low","Close","Volume"]]
            df.set_index("timestamp", inplace=True)
            return df
        except:
            return pd.DataFrame()