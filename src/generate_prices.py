"""Generate synthetic daily OHLCV price history (deterministic, seeded).

Five fictional tickers with distinct characters — a steady compounder, a
high-volatility growth name, a defensive low-beta name, a cyclical, and
one name that suffers a sharp drawdown and partial recovery — over three
years of trading days. Prices follow a geometric random walk per ticker
with ticker-specific drift and volatility; OHLC is derived from the
close path so the bars are internally consistent.

Fictional data for analysis demonstration only. Not investment advice.
"""
from __future__ import annotations

import csv
import math
import os
import random
from datetime import date, timedelta

random.seed(7)
OUT = os.path.join(os.path.dirname(__file__), "..", "data")

# ticker, company, start price, annual drift, annual volatility
TICKERS = [
    ("ACME", "Acme Industrial Group", 142.00, 0.11, 0.19),
    ("BLZE", "Blaze Semiconductor", 268.00, 0.21, 0.38),
    ("CRBN", "Carbonline Energy", 74.00, 0.04, 0.29),
    ("DVLP", "Developay Financial", 121.00, 0.08, 0.21),
    ("ECHO", "Echo Consumer Health", 96.00, 0.06, 0.16),
]

START = date(2023, 9, 1)
END = date(2026, 8, 31)
TRADING_DAYS = 252


def trading_days() -> list[date]:
    days, d = [], START
    while d <= END:
        if d.weekday() < 5:
            days.append(d)
        d += timedelta(days=1)
    return days


# Market beta per ticker: how much of each name's move is the shared
# market factor vs its own idiosyncratic noise. This is what makes the
# return correlations land in a realistic band instead of near zero.
BETAS = {"ACME": 0.75, "BLZE": 0.90, "CRBN": 0.65, "DVLP": 0.85, "ECHO": 0.45}


def path(start: float, drift: float, vol: float, n: int, ticker: str,
         market: list[float]) -> list[float]:
    daily_drift = drift / TRADING_DAYS
    daily_vol = vol / math.sqrt(TRADING_DAYS)
    beta = BETAS[ticker]
    prices = [start]
    for i in range(1, n):
        shock = beta * market[i] + math.sqrt(1 - beta ** 2) * random.gauss(0, 1)
        # ECHO: a two-week drawdown event a bit after the first year
        if ticker == "ECHO" and 265 <= i <= 278:
            shock -= 1.15
        prices.append(prices[-1] * math.exp(daily_drift + daily_vol * shock))
    return prices


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    days = trading_days()
    market = [random.gauss(0, 1) for _ in days]  # shared market factor
    rows = []
    for ticker, _name, start, drift, vol in TICKERS:
        closes = path(start, drift, vol, len(days), ticker, market)
        for i, (d, close) in enumerate(zip(days, closes)):
            prev = closes[i - 1] if i else close * 0.998
            open_ = prev * (1 + random.gauss(0, 0.002))
            high = max(open_, close) * (1 + abs(random.gauss(0, 0.004)))
            low = min(open_, close) * (1 - abs(random.gauss(0, 0.004)))
            base_volume = 1_800_000 if ticker in ("ACME", "BLZE") else 900_000
            volume = int(base_volume * random.uniform(0.6, 1.7)
                         * (1 + 2.2 * abs(close / prev - 1)))
            rows.append([d.isoformat(), ticker, round(open_, 2), round(high, 2),
                         round(low, 2), round(close, 2), volume])
    rows.sort(key=lambda r: (r[0], r[1]))
    with open(os.path.join(OUT, "prices.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["trade_date", "ticker", "open", "high", "low", "close", "volume"])
        w.writerows(rows)
    print(f"{len(rows)} OHLCV rows: {len(TICKERS)} tickers x {len(days)} trading days "
          f"({days[0]} to {days[-1]})")


if __name__ == "__main__":
    main()
