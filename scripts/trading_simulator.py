"""
Simple Monte Carlo simulator for an R-multiple strategy, with all
parameters configured in-code in one place.

Assumptions:
  - Each trade risks a fixed fraction of current equity (compounding).
  - A win earns R times the risk; a loss loses the risk.
  - Outcomes are Bernoulli with probability = hit rate.
  - We simulate multiple independent equity paths ("simultaneous trades").
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List, Sequence


# === Configuration (edit these) ===
# Changing the risk % per trade changes mean and median , but not the Prob 
# but it affects mean, median PNL because risk % affects compounding, drawdowns, final capital magnitude
# Your win rate (p) and R-multiple (R) define the shape of outcomes
# Expected value per trade = p * R - (1-p) = p * (R+1) - 1
# basically it is what you make if you win minus what you lose when trade is lost
# 



STARTING_CAPITAL_RUPEES: float = 200_000.0
R_MULTIPLE: float = 1.6            # reward:risk per winning trade
HIT_RATE: float = 0.4             # probability of a win (0–1)
TRADES_PER_PATH: int = 500         # trades in each simulated path
RISK_FRACTION_PER_TRADE: float = 0.01  # fraction of current equity risked per trade
NUM_SIMULATIONS: int = 5000        # number of Monte Carlo paths (simultaneous equity paths)
RNG_SEED: int = 42                 # RNG seed for reproducibility


@dataclass
class PathResult:
    equity_curve: List[float]
    final_rupees: float
    final_pct: float
    max_drawdown_pct: float


def simulate_path(
    *,
    starting_capital: float,
    r_multiple: float,
    hit_rate: float,
    trades: int,
    risk_fraction: float,
    rng: random.Random,
) -> PathResult:
    equity = starting_capital
    curve = [equity]

    for _ in range(trades):
        risk_amount = equity * risk_fraction
        if rng.random() < hit_rate:
            equity += risk_amount * r_multiple
        else:
            equity -= risk_amount
        curve.append(equity)

    max_drawdown_pct = _max_drawdown_pct(curve)
    final_rupees = curve[-1]
    final_pct = (final_rupees - starting_capital) / starting_capital * 100
    return PathResult(curve, final_rupees, final_pct, max_drawdown_pct)


def _max_drawdown_pct(curve: Sequence[float]) -> float:
    peak = curve[0]
    max_dd = 0.0
    for value in curve:
        peak = max(peak, value)
        drawdown = (peak - value) / peak * 100
        max_dd = max(max_dd, drawdown)
    return max_dd


def summarize(paths: Sequence[PathResult]) -> None:
    finals = [p.final_pct for p in paths]
    drawdowns = [p.max_drawdown_pct for p in paths]

    def pct(p: float, values: Sequence[float]) -> float:
        idx = int(len(values) * p)
        return sorted(values)[min(idx, len(values) - 1)]

    def mean(values: Sequence[float]) -> float:
        return sum(values) / len(values)

    def std(values: Sequence[float]) -> float:
        m = mean(values)
        return math.sqrt(sum((x - m) ** 2 for x in values) / len(values))

    prob_profitable = sum(1 for x in finals if x > 0) / len(finals) * 100

    print("=== Monte Carlo summary ===")
    print(f"Simulations (paths): {len(paths)}")
    print(f"Starting capital (₹): {STARTING_CAPITAL_RUPEES:,.0f}")
    print(f"Trades per path: {TRADES_PER_PATH}")
    print(f"R-multiple: {R_MULTIPLE}, hit rate: {HIT_RATE:.2f}, risk/trade: {RISK_FRACTION_PER_TRADE*100:.2f}%")
    print()
    print("PNL %:")
    print(f"  mean: {mean(finals):.2f}")
    print(f"  median: {pct(0.5, finals):.2f}")
    print(f"  std dev: {std(finals):.2f}")
    print(f"  Prob(PNL % > 0): {prob_profitable:.2f}%")
    print()
    print("Max drawdown %:")
    print(f"  mean: {mean(drawdowns):.2f}")
    print(f"  median: {pct(0.5, drawdowns):.2f}")
    print(f"  95th percentile: {pct(0.95, drawdowns):.2f}")


def main() -> None:
    rng = random.Random(RNG_SEED)

    paths = [
        simulate_path(
            starting_capital=STARTING_CAPITAL_RUPEES,
            r_multiple=R_MULTIPLE,
            hit_rate=HIT_RATE,
            trades=TRADES_PER_PATH,
            risk_fraction=RISK_FRACTION_PER_TRADE,
            rng=rng,
        )
        for _ in range(NUM_SIMULATIONS)
    ]

    summarize(paths)


if __name__ == "__main__":
    main()
