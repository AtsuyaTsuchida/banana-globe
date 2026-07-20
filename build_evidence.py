"""Compute OBJECTIVE evidence stats for the BANANA GLOBE evidence dashboard.

Everything here is derived from the project's real data — no invented numbers.
Outputs evidence.json (embedded/loaded by evidence.html).

Run:  cd ../terminal && uv run python ../globe/build_evidence.py
"""
from __future__ import annotations
import json, numpy as np, pandas as pd
from pathlib import Path
from scipy import stats

_HERE = Path(__file__).resolve().parent          # .../banana-of-wall-street/globe
PROJ = _HERE.parent / "terminal"
OUT  = _HERE / "evidence.json"
rng  = np.random.default_rng(42)

pred = pd.read_parquet(PROJ / "data/processed/predictions.parquet")
pred["ym"] = pred["date"].dt.strftime("%Y-%m")

# ---- 1. monthly cross-sectional IC (Pearson across the 8 ETFs each month) ----
def month_ic(g):
    if g["pred_return"].std() == 0 or g["actual_return"].std() == 0:
        return np.nan
    return np.corrcoef(g["pred_return"], g["actual_return"])[0, 1]

monthly = pred.groupby("ym").apply(month_ic, include_groups=False).dropna()
ic_series = monthly.values
n = len(ic_series)
ic_mean = float(ic_series.mean())
ic_std  = float(ic_series.std(ddof=1))
ic_ir   = ic_mean / ic_std * np.sqrt(n)              # t-stat
p_ttest = float(2 * stats.t.sf(abs(ic_ir), df=n - 1))

# ---- 2. permutation null distribution of the mean IC ----
# H0: banana prediction carries no info -> shuffle pred within each month,
#     breaking the pred<->actual pairing, recompute mean monthly IC. N draws.
N_PERM = 2000
piv_pred = pred.pivot_table(index="ym", columns="ticker", values="pred_return")
piv_act  = pred.pivot_table(index="ym", columns="ticker", values="actual_return")
months = piv_pred.index
P = piv_pred.values.astype(float)   # (months, tickers)
A = piv_act.values.astype(float)

def mean_ic_from(pmat, amat):
    ics = []
    for i in range(pmat.shape[0]):
        pv, av = pmat[i], amat[i]
        m = ~(np.isnan(pv) | np.isnan(av))
        if m.sum() < 3 or np.std(pv[m]) == 0 or np.std(av[m]) == 0:
            continue
        ics.append(np.corrcoef(pv[m], av[m])[0, 1])
    return float(np.mean(ics)) if ics else np.nan

actual_ic = mean_ic_from(P, A)
null_ic = np.empty(N_PERM)
for k in range(N_PERM):
    Ps = P.copy()
    for i in range(Ps.shape[0]):
        row = Ps[i]
        idx = np.where(~np.isnan(row))[0]
        row[idx] = row[rng.permutation(idx)]
    null_ic[k] = mean_ic_from(Ps, A)
null_ic = null_ic[~np.isnan(null_ic)]
# two-sided permutation p: how often |null| >= |actual|
p_perm = float((np.sum(np.abs(null_ic) >= abs(actual_ic)) + 1) / (len(null_ic) + 1))
pctile = float((np.sum(null_ic < actual_ic)) / len(null_ic) * 100)

# ---- 3. pred vs actual scatter (all obs) + pooled regression ----
sc = pred[["pred_return", "actual_return"]].dropna()
slope, intercept, r, p_reg, se = stats.linregress(sc["pred_return"], sc["actual_return"])
scatter = [[round(float(a), 5), round(float(b), 5)] for a, b in
           zip(sc["pred_return"], sc["actual_return"])]

# ---- 4. rolling 12M IC with a +/-95% noise band around 0 ----
W = 12
roll = []
for i in range(len(ic_series)):
    lo = max(0, i - W + 1)
    win = ic_series[lo:i + 1]
    band = 1.96 * (win.std(ddof=1) if len(win) > 1 else 0) / np.sqrt(len(win))
    roll.append({"ym": months[i] if i < len(months) else monthly.index[i],
                 "ic": round(float(win.mean()), 4),
                 "band": round(float(band), 4)})
roll = [{"ym": ym, "ic": round(float(v), 4)} for ym, v in zip(monthly.index, ic_series)]
roll12 = []
vals = ic_series
for i in range(len(vals)):
    lo = max(0, i - W + 1); win = vals[lo:i + 1]
    band = 1.96 * (win.std(ddof=1) if len(win) > 1 else 0.0) / np.sqrt(len(win))
    roll12.append({"ym": monthly.index[i], "ic": round(float(win.mean()), 4),
                   "band": round(float(band), 4)})

# ---- 5. equity curves: strategies + random top-3 fan ----
bt = pd.read_parquet(PROJ / "data/processed/backtest_results.parquet")
bt["ym"] = bt["date"].dt.strftime("%Y-%m")
port = bt.groupby(["strategy", "ym"])["pnl"].sum().reset_index()  # monthly port return
eq_dates = sorted(bt["ym"].unique())
strategies = {}
for s, g in port.groupby("strategy"):
    g = g.set_index("ym").reindex(eq_dates).fillna(0.0)
    nav = (1 + g["pnl"]).cumprod()
    strategies[s] = [round(float(x), 4) for x in nav.values]

# random top-3 equal-weight fan from the actual return matrix
ret = piv_act.reindex(eq_dates)             # months x tickers actual returns
tickers = list(ret.columns)
RM = ret.values.astype(float)
N_RAND = 500
navs = np.ones((N_RAND, len(eq_dates)))
for j in range(N_RAND):
    nav = 1.0
    for i in range(len(eq_dates)):
        row = RM[i]; ok = np.where(~np.isnan(row))[0]
        if len(ok) >= 3:
            pick = rng.choice(ok, 3, replace=False)
            nav *= (1 + np.mean(row[pick]))
        navs[j, i] = nav
p05 = np.percentile(navs, 5, axis=0)
p50 = np.percentile(navs, 50, axis=0)
p95 = np.percentile(navs, 95, axis=0)
top3 = np.array(strategies.get("TOP3_LONG", p50))
final_pctile = float(np.mean(navs[:, -1] < top3[-1]) * 100)

evidence = {
    "meta": {"n_months": n, "period": [monthly.index[0], monthly.index[-1]],
             "n_perm": len(null_ic), "n_random": N_RAND, "n_obs": len(scatter)},
    "ic": {"mean": round(ic_mean, 4), "std": round(ic_std, 4),
           "ir": round(float(ic_ir), 3), "p_ttest": round(p_ttest, 4),
           "p_perm": round(p_perm, 4), "pctile": round(pctile, 1)},
    "perm": {"actual": round(actual_ic, 4),
             "null": [round(float(x), 4) for x in null_ic],
             "null_mean": round(float(null_ic.mean()), 4),
             "null_std": round(float(null_ic.std()), 4)},
    "scatter": {"points": scatter, "slope": round(float(slope), 4),
                "intercept": round(float(intercept), 5), "r": round(float(r), 4),
                "p": round(float(p_reg), 4)},
    "rolling": roll12,
    "equity": {"dates": eq_dates, "strategies": strategies,
               "random": {"p05": [round(float(x), 4) for x in p05],
                          "p50": [round(float(x), 4) for x in p50],
                          "p95": [round(float(x), 4) for x in p95],
                          "final_pctile": round(final_pctile, 1)}},
}
OUT.write_text(json.dumps(evidence))
print("wrote", OUT, OUT.stat().st_size, "bytes")
print(f"IC mean={ic_mean:.4f} p_ttest={p_ttest:.3f} p_perm={p_perm:.3f} "
      f"pctile={pctile:.1f} n={n}")
print(f"scatter r={r:.4f} (p={p_reg:.3f}), strategies={list(strategies)}, "
      f"TOP3 final vs random pctile={final_pctile:.1f}")
