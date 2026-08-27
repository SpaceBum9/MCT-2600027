"""Critical Slowing Down on a scalar order parameter (BILO2026 binding)."""
from __future__ import annotations

from typing import Iterable


def _detrend(xs: list[float]) -> list[float]:
    n = len(xs)
    if n < 3:
        return xs[:]
    k = max(3, n // 5 | 1)
    half = k // 2
    out: list[float] = []
    for i, x in enumerate(xs):
        lo = max(0, i - half)
        hi = min(n, i + half + 1)
        mean = sum(xs[lo:hi]) / (hi - lo)
        out.append(x - mean)
    return out


def rho1(xs: Iterable[float]) -> float:
    r = list(xs)
    if len(r) < 3:
        return 0.0
    a = r[:-1]
    b = r[1:]
    ma = sum(a) / len(a)
    mb = sum(b) / len(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = sum((x - ma) ** 2 for x in a)
    if den == 0:
        return 0.0
    return max(-1.0, min(1.0, num / den))


def variance(xs: Iterable[float]) -> float:
    r = list(xs)
    if len(r) < 2:
        return 0.0
    m = sum(r) / len(r)
    return sum((x - m) ** 2 for x in r) / (len(r) - 1)


def measure(series: Iterable[float]) -> dict:
    raw = [float(x) for x in series]
    resid = _detrend(raw)
    r = rho1(resid)
    v = variance(resid)
    band = "green"
    if r > 0.6 and v > 0:
        band = "yellow"
    if r > 0.85:
        band = "red"
    return {
        "marker": "BILO2026",
        "n": len(raw),
        "rho1": round(r, 4),
        "variance": round(v, 6),
        "band": band,
        "note": "band is risk, not a date",
    }
