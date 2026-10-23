# Stock Market Analysis

Risk/return analysis of a five-name portfolio over three years of daily
prices: total return, CAGR, volatility, Sharpe ratio, maximum drawdown,
moving-average trend, and return correlations — computed in Python, with
the same analytics expressed in SQL window functions.

**Fictional tickers, synthetic data** (seeded random walks with a shared
market factor, so correlations behave realistically). A methodology
demonstration — not investment advice.

## The case

| | |
|---|---|
| Scale | 3,910 daily OHLCV bars · 5 tickers · 782 trading days (Sep 2023 – Aug 2026) |
| Names | ACME (industrials) · BLZE (semiconductors) · CRBN (energy) · DVLP (financials) · ECHO (consumer health) |
| Metrics | Total return, CAGR, annualized volatility, Sharpe, max drawdown + dates, % days above SMA-200, correlation matrix |
| Stack | Python (standard library) + ANSI SQL window functions |

## Headline findings

- **BLZE earned its volatility** — +245.7% total return and the best
  Sharpe (1.26) despite the second-highest volatility (37.4%). The
  -44.4% drawdown along the way is the price of admission.
- **CRBN is the trap in the set** — second-highest volatility (30.0%)
  bought the *worst* return (+10.4%, Sharpe 0.26) and the deepest
  drawdown (-49.4%). Risk without reward.
- **ACME is the drawdown controller** — shallowest max drawdown (-18.0%)
  with a 1.04 Sharpe and +74.2% total return; it spent 84.9% of days
  above its 200-day average.
- **ECHO survived its event** — a sharp two-week selloff drove a -26.7%
  drawdown, yet the lowest volatility in the set (17.0%) and a 1.03
  Sharpe by period end.
- **Correlations are real but not uniform** — BLZE/DVLP move together
  (0.76) while ACME/ECHO is the diversifier pair (0.32). An equal-weight
  book here is genuinely diversified, not five copies of one bet.

Full numbers: `analysis/summary.csv` and `analysis/findings.md`.

## Run it

```bash
python src/generate_prices.py   # regenerate the synthetic history (seeded)
python src/analyze.py           # metrics per ticker + correlations
```

## Layout

```
data/     prices.csv (synthetic OHLCV)
src/      generate_prices.py · analyze.py
sql/      price_queries.sql  (daily returns, SMA 50/200, rolling vol,
                              drawdown-from-peak, monthly OHLC rollup)
analysis/ summary.csv · findings.md
```

## License

MIT
