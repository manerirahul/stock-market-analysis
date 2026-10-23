"""Risk/return analysis over the synthetic price history.

Per ticker: total return, CAGR, annualized volatility, Sharpe ratio
(risk-free = 0), maximum drawdown with its peak/trough dates, best and
worst single days, and days above the 200-day moving average. Plus the
pairwise correlation matrix of daily returns. Writes
analysis/summary.csv and prints the narrative findings.
"""
from __future__ import annotations

import csv
import math
import os
import statistics
from collections import defaultdict

BASE = os.path.join(os.path.dirname(__file__), "..")
TRADING_DAYS = 252


def load() -> dict[str, list[tuple[str, float]]]:
    series: dict[str, list[tuple[str, float]]] = defaultdict(list)
    with open(os.path.join(BASE, "data", "prices.csv"), newline="") as fh:
        for row in csv.DictReader(fh):
            series[row["ticker"]].append((row["trade_date"], float(row["close"])))
    for ticker in series:
        series[ticker].sort()
    return series


def daily_returns(closes: list[float]) -> list[float]:
    return [closes[i] / closes[i - 1] - 1 for i in range(1, len(closes))]


def max_drawdown(dated_closes: list[tuple[str, float]]) -> tuple[float, str, str]:
    peak_date, peak = dated_closes[0]
    worst = (0.0, peak_date, peak_date)
    for dte, price in dated_closes:
        if price > peak:
            peak, peak_date = price, dte
        dd = price / peak - 1
        if dd < worst[0]:
            worst = (dd, peak_date, dte)
    return worst


def moving_average(values: list[float], window: int) -> list[float | None]:
    out: list[float | None] = []
    for i in range(len(values)):
        if i + 1 < window:
            out.append(None)
        else:
            out.append(sum(values[i + 1 - window: i + 1]) / window)
    return out


def analyze(ticker: str, dated: list[tuple[str, float]]) -> dict:
    closes = [c for _, c in dated]
    rets = daily_returns(closes)
    years = len(closes) / TRADING_DAYS
    total_return = closes[-1] / closes[0] - 1
    cagr = (closes[-1] / closes[0]) ** (1 / years) - 1
    vol = statistics.pstdev(rets) * math.sqrt(TRADING_DAYS)
    sharpe = (statistics.mean(rets) * TRADING_DAYS) / vol if vol else 0.0
    dd, peak_d, trough_d = max_drawdown(dated)
    sma200 = moving_average(closes, 200)
    above = sum(1 for c, m in zip(closes, sma200) if m is not None and c > m)
    valid = sum(1 for m in sma200 if m is not None)
    return {
        "ticker": ticker,
        "start_close": closes[0],
        "end_close": closes[-1],
        "total_return_pct": round(total_return * 100, 1),
        "cagr_pct": round(cagr * 100, 1),
        "annual_vol_pct": round(vol * 100, 1),
        "sharpe": round(sharpe, 2),
        "max_drawdown_pct": round(dd * 100, 1),
        "drawdown_peak": peak_d,
        "drawdown_trough": trough_d,
        "best_day_pct": round(max(rets) * 100, 2),
        "worst_day_pct": round(min(rets) * 100, 2),
        "pct_days_above_sma200": round(100 * above / valid, 1) if valid else 0.0,
    }


def correlation(series: dict[str, list[tuple[str, float]]]) -> dict[tuple[str, str], float]:
    rets = {t: daily_returns([c for _, c in dated]) for t, dated in series.items()}
    tickers = sorted(rets)
    out = {}
    for i, a in enumerate(tickers):
        for b in tickers[i + 1:]:
            ra, rb = rets[a], rets[b]
            ma, mb = statistics.mean(ra), statistics.mean(rb)
            cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb)) / len(ra)
            out[(a, b)] = round(cov / (statistics.pstdev(ra) * statistics.pstdev(rb)), 2)
    return out


def main() -> None:
    series = load()
    summaries = [analyze(t, series[t]) for t in sorted(series)]

    out_path = os.path.join(BASE, "analysis", "summary.csv")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(summaries[0].keys()))
        writer.writeheader()
        writer.writerows(summaries)

    for s in summaries:
        print(f"{s['ticker']}: total {s['total_return_pct']:+.1f}%  CAGR {s['cagr_pct']:+.1f}%  "
              f"vol {s['annual_vol_pct']}%  Sharpe {s['sharpe']}  "
              f"maxDD {s['max_drawdown_pct']}% ({s['drawdown_peak']} -> {s['drawdown_trough']})  "
              f"above SMA200 {s['pct_days_above_sma200']}% of days")

    corr = correlation(series)
    pairs = sorted(corr.items(), key=lambda kv: kv[1])
    print(f"\nLowest correlation:  {pairs[0][0][0]}/{pairs[0][0][1]} at {pairs[0][1]}")
    print(f"Highest correlation: {pairs[-1][0][0]}/{pairs[-1][0][1]} at {pairs[-1][1]}")
    print(f"\nSummary written to analysis/summary.csv")


if __name__ == "__main__":
    main()
