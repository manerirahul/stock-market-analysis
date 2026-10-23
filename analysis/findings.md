# Findings — Five-Name Portfolio, Sep 2023 to Aug 2026

Source: `data/prices.csv` (3,910 daily bars). All metrics computed by
`src/analyze.py`; reproducible end to end. Synthetic data — the value
is the method, not the tickers.

## Scoreboard

| Ticker | Total return | CAGR | Volatility | Sharpe | Max drawdown | Days above SMA-200 |
|---|---|---|---|---|---|---|
| BLZE | +245.7% | +49.1% | 37.4% | 1.26 | -44.4% | 91.8% |
| DVLP | +81.7% | +21.2% | 20.7% | 1.03 | -24.1% | 73.1% |
| ACME | +74.2% | +19.6% | 19.1% | 1.04 | -18.0% | 84.9% |
| ECHO | +64.1% | +17.3% | 17.0% | 1.03 | -26.7% | 60.5% |
| CRBN | +10.4% | +3.2% | 30.0% | 0.26 | -49.4% | 50.3% |

## What the data says

1. **Return and risk are not the same ranking.** Sorted by volatility,
   the order is BLZE > CRBN > DVLP > ACME > ECHO; sorted by Sharpe it
   is BLZE > ACME ≈ DVLP ≈ ECHO > CRBN. CRBN is the only name whose
   volatility was not compensated.
2. **Drawdown is the risk investors actually feel.** CRBN's -49.4%
   peak-to-trough (Apr → Aug 2025) needs a +98% rally just to break
   even; ACME's worst was -18.0%. Position sizing should key off
   drawdown tolerance, not volatility alone.
3. **Trend persistence differs by name.** BLZE spent 91.8% of days
   above its 200-day average (a durable uptrend); CRBN sat at 50.3% —
   a coin flip, consistent with a range-bound, news-driven name.
4. **Diversification is available but uneven.** Correlations run from
   0.32 (ACME/ECHO) to 0.76 (BLZE/DVLP). The ACME/ECHO pairing cuts
   portfolio volatility the most per unit of return given up.

## Method notes

- Sharpe uses a 0% risk-free rate and daily-return annualization
  (mean × 252 / (σ × √252)).
- Max drawdown is measured on closes, peak to subsequent trough.
- Prices are geometric random walks with a shared market factor
  (betas 0.45–0.90), which is why correlations are positive but
  imperfect — the same structure real single-name returns show.
