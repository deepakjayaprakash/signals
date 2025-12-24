"""
Monte Carlo trading simulator using NumPy / Pandas / Matplotlib.

Same core logic as `trading_simulator.py`:
  - R-multiple system with fixed fraction risk per trade
  - Bernoulli wins with probability = hit rate
  - Compounding equity

Differences:
  - Uses vectorised NumPy operations for speed
  - Uses NumPy / Pandas for statistics
  - Plots a sample of equity curves using Matplotlib
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from trading_simulator import (
    STARTING_CAPITAL_RUPEES,
    R_MULTIPLE,
    HIT_RATE,
    TRADES_PER_PATH,
    RISK_FRACTION_PER_TRADE,
    NUM_SIMULATIONS,
    RNG_SEED,
)


# How many equity curves to plot (sampled from the full set)
NUM_CURVES_TO_PLOT: int = 50


def run_simulation() -> tuple[pd.Series, pd.Series, np.ndarray]:
    """
    Returns:
        final_pct: Series of final PNL % for each path
        max_dd_pct: Series of max drawdown % for each path
        equity_curves: full equity matrix (paths x (trades+1))
    """
    rng = np.random.default_rng(RNG_SEED)

    # wins[i, t] = True if path i wins on trade t
    wins = rng.random((NUM_SIMULATIONS, TRADES_PER_PATH)) < HIT_RATE

    # equity_curves[i, t] = equity for path i after t trades (t=0 is start)
    equity_curves = np.empty((NUM_SIMULATIONS, TRADES_PER_PATH + 1), dtype=float)
    equity_curves[:, 0] = STARTING_CAPITAL_RUPEES

    for t in range(1, TRADES_PER_PATH + 1):
        prev_equity = equity_curves[:, t - 1]
        risk = prev_equity * RISK_FRACTION_PER_TRADE
        pnl = np.where(wins[:, t - 1], risk * R_MULTIPLE, -risk)
        equity_curves[:, t] = prev_equity + pnl

    final_rupees = equity_curves[:, -1]
    final_pct = (final_rupees - STARTING_CAPITAL_RUPEES) / STARTING_CAPITAL_RUPEES * 100.0

    # Max drawdown per path
    running_max = np.maximum.accumulate(equity_curves, axis=1)
    drawdowns = (running_max - equity_curves) / running_max * 100.0
    max_dd_pct = drawdowns.max(axis=1)

    final_pct_series = pd.Series(final_pct, name="final_pnl_pct")
    max_dd_series = pd.Series(max_dd_pct, name="max_drawdown_pct")
    return final_pct_series, max_dd_series, equity_curves


def summarize_with_libraries(final_pct: pd.Series, max_dd_pct: pd.Series) -> None:
    print("=== Monte Carlo summary (NumPy / Pandas) ===")
    print(f"Simulations (paths): {len(final_pct)}")
    print(f"Starting capital (₹): {STARTING_CAPITAL_RUPEES:,.0f}")
    print(f"Trades per path: {TRADES_PER_PATH}")
    print(f"R-multiple: {R_MULTIPLE}, hit rate: {HIT_RATE:.2f}, risk/trade: {RISK_FRACTION_PER_TRADE*100:.2f}%")
    print()

    # PNL %
    print("PNL %:")
    print(f"  mean: {final_pct.mean():.2f}")
    print(f"  median: {final_pct.median():.2f}")
    print(f"  std dev: {final_pct.std(ddof=0):.2f}")
    prob_profitable = (final_pct > 0).mean() * 100.0
    print(f"  Prob(PNL % > 0): {prob_profitable:.2f}%")
    print()

    # Max drawdown %
    print("Max drawdown %:")
    print(f"  mean: {max_dd_pct.mean():.2f}")
    print(f"  median: {max_dd_pct.median():.2f}")
    print(f"  95th percentile: {max_dd_pct.quantile(0.95):.2f}")


def plot_sample_equity_curves(equity_curves: np.ndarray) -> None:
    """
    Plot a sample of equity curves (in rupees).
    """
    num_paths = equity_curves.shape[0]
    num_to_plot = min(NUM_CURVES_TO_PLOT, num_paths)

    rng = np.random.default_rng(RNG_SEED + 1)
    idx = rng.choice(num_paths, size=num_to_plot, replace=False)

    x = np.arange(equity_curves.shape[1])

    plt.figure(figsize=(10, 6))
    for i in idx:
        plt.plot(x, equity_curves[i], alpha=0.3, linewidth=0.8)

    plt.title(
        f"Sample of {num_to_plot} equity curves\n"
        f"R={R_MULTIPLE}, hit rate={HIT_RATE:.2f}, risk/trade={RISK_FRACTION_PER_TRADE*100:.2f}%"
    )
    plt.xlabel("Trade number")
    plt.ylabel("Equity (₹)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def main() -> None:
    final_pct, max_dd_pct, equity_curves = run_simulation()
    summarize_with_libraries(final_pct, max_dd_pct)
    plot_sample_equity_curves(equity_curves)


if __name__ == "__main__":
    main()

