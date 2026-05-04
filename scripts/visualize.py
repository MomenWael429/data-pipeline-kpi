"""
import matplotlib.pyplot as plt
import pandas as pd

def create_chart(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    plt.figure()
    plt.plot(df["timestamp"], df["price"])
    plt.title("Bitcoin price over time")
    plt.xticks(rotation = 45)
    plt.tight_layout()
    plt.savefig("output/chart.png")"""

"""
visualize.py — 4-panel engineering dashboard.

Panels
------
1. Bitcoin price over time        (styled line chart)
2. 24h change per data point      (green/red bar chart)
3. KPI summary                    (big-number stat cards)
4. Pipeline efficiency            (donut chart — success vs failure %)
"""

import os
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch

# ── Design tokens ─────────────────────────────────────────────────────────────
BG_DARK      = "#0D1117"   # deep charcoal — page background
BG_PANEL     = "#161B22"   # slightly lighter — card backgrounds
BG_PANEL2    = "#1C2128"   # alternate card
ACCENT_TEAL  = "#00C8AA"   # primary accent
ACCENT_GOLD  = "#F0B429"   # secondary accent
SUCCESS_GREEN= "#2EA043"
FAILURE_RED  = "#DA3633"
TEXT_PRIMARY = "#E6EDF3"
TEXT_MUTED   = "#8B949E"
GRID_COLOR   = "#21262D"

FONT_TITLE   = {"fontsize": 11, "fontweight": "bold",  "color": TEXT_PRIMARY, "fontfamily": "monospace"}
FONT_MUTED   = {"fontsize":  8, "color": TEXT_MUTED,   "fontfamily": "monospace"}
FONT_BIG     = {"fontsize": 20, "fontweight": "bold",  "color": ACCENT_TEAL,  "fontfamily": "monospace"}
FONT_LABEL   = {"fontsize":  7, "color": TEXT_MUTED,   "fontfamily": "monospace"}


def _style_ax(ax, title: str) -> None:
    """Apply dark-theme base styling to any axis."""
    ax.set_facecolor(BG_PANEL)
    ax.tick_params(colors=TEXT_MUTED, labelsize=7)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COLOR)
    ax.set_title(f"  {title}", loc="left", pad=10, **FONT_TITLE)
    ax.grid(color=GRID_COLOR, linewidth=0.5, linestyle="--", zorder=0)


# ── Panel 1: Price line chart ─────────────────────────────────────────────────

def _panel_price(ax, df: pd.DataFrame) -> None:
    _style_ax(ax, "₿  BITCOIN / EUR  —  Price History")

    x = df["timestamp"]
    y = df["price"]

    # Gradient fill under the line
    ax.fill_between(x, y, alpha=0.12, color=ACCENT_TEAL, zorder=1)
    ax.plot(x, y, color=ACCENT_TEAL, linewidth=1.8, zorder=2)

    # Highlight latest point
    ax.scatter([x.iloc[-1]], [y.iloc[-1]], color=ACCENT_GOLD, s=50, zorder=5)
    ax.annotate(
        f"  €{y.iloc[-1]:,.0f}",
        (x.iloc[-1], y.iloc[-1]),
        color=ACCENT_GOLD, fontsize=8, fontfamily="monospace",
        va="bottom",
    )

    ax.set_ylabel("Price (EUR)", **FONT_MUTED)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"€{v:,.0f}"))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=7,
             color=TEXT_MUTED, fontfamily="monospace")
    plt.setp(ax.get_yticklabels(), fontsize=7, color=TEXT_MUTED, fontfamily="monospace")


# ── Panel 2: 24h change bar chart ────────────────────────────────────────────

def _panel_change(ax, df: pd.DataFrame) -> None:
    _style_ax(ax, "📈  24H CHANGE  —  Per Data Point")

    changes = df["change_24h"].values
    colors  = [SUCCESS_GREEN if c >= 0 else FAILURE_RED for c in changes]
    x_idx   = range(len(changes))

    bars = ax.bar(x_idx, changes, color=colors, width=0.6, zorder=2, edgecolor=BG_DARK, linewidth=0.4)

    # Zero line
    ax.axhline(0, color=TEXT_MUTED, linewidth=0.8, linestyle="-", zorder=3)

    # Value labels on tallest bars only
    for bar, val in zip(bars, changes):
        if abs(val) > (max(abs(c) for c in changes) * 0.3):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                val + (0.05 if val >= 0 else -0.15),
                f"{val:+.1f}%",
                ha="center", va="bottom" if val >= 0 else "top",
                fontsize=6, color=TEXT_MUTED, fontfamily="monospace",
            )

    ax.set_ylabel("Change (%)", **FONT_MUTED)
    ax.set_xlabel("Data point index", **FONT_MUTED)
    plt.setp(ax.get_yticklabels(), fontsize=7, color=TEXT_MUTED, fontfamily="monospace")
    ax.set_xticks([])


# ── Panel 3: KPI stat cards ───────────────────────────────────────────────────

def _panel_kpis(ax, kpis: dict) -> None:
    ax.set_facecolor(BG_PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COLOR)
    ax.set_title("  📊  KPI SUMMARY", loc="left", pad=10, **FONT_TITLE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    cards = [
        ("AVG PRICE",    f"€{kpis['avg_price']:,.2f}",     ACCENT_TEAL),
        ("MAX PRICE",    f"€{kpis['max_price']:,.2f}",     SUCCESS_GREEN),
        ("MIN PRICE",    f"€{kpis['min_price']:,.2f}",     FAILURE_RED),
        ("LATEST 24H Δ", f"{kpis['lastest_change']:+.2f}%", ACCENT_GOLD),
    ]

    card_w, card_h = 0.20, 0.52
    gap            = 0.035
    total_w        = len(cards) * card_w + (len(cards) - 1) * gap
    start_x        = (1 - total_w) / 2
    cy             = 0.22

    for i, (label, value, color) in enumerate(cards):
        cx = start_x + i * (card_w + gap)

        # Card background
        rect = FancyBboxPatch(
            (cx, cy), card_w, card_h,
            boxstyle="round,pad=0.01",
            facecolor=BG_PANEL2, edgecolor=color,
            linewidth=1.2, zorder=2,
        )
        ax.add_patch(rect)

        # Top accent bar
        accent = FancyBboxPatch(
            (cx, cy + card_h - 0.045), card_w, 0.045,
            boxstyle="round,pad=0.005",
            facecolor=color, edgecolor="none", zorder=3,
        )
        ax.add_patch(accent)

        # Label
        ax.text(cx + card_w / 2, cy + card_h * 0.55, label,
                ha="center", va="center",
                fontsize=7, fontfamily="monospace",
                color=TEXT_MUTED, zorder=4)

        # Value
        ax.text(cx + card_w / 2, cy + card_h * 0.25, value,
                ha="center", va="center",
                fontsize=11, fontweight="bold",
                fontfamily="monospace", color=color, zorder=4)


# ── Panel 4: Pipeline efficiency donut ───────────────────────────────────────

def _panel_pipeline(ax, build_log_path: str = "data/build_log.csv") -> None:
    ax.set_facecolor(BG_PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COLOR)
    ax.set_title("  ⚙️  PIPELINE EFFICIENCY", loc="left", pad=10, **FONT_TITLE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Load build log
    try:
        df     = pd.read_csv(build_log_path)
        total   = len(df)
        success = len(df[df["status"] == "success"])
        failure = total - success
        pct_ok  = round(success / total * 100, 1) if total else 0.0
        pct_fail= round(100 - pct_ok, 1)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        total, success, failure, pct_ok, pct_fail = 0, 0, 0, 0.0, 0.0

    # Donut via inset axes
    inset = ax.inset_axes([0.05, 0.05, 0.52, 0.88])
    inset.set_facecolor(BG_PANEL)

    if total == 0:
        inset.text(0.5, 0.5, "No runs yet", ha="center", va="center",
                   color=TEXT_MUTED, fontsize=9, fontfamily="monospace")
    else:
        sizes  = [pct_ok, pct_fail] if pct_fail > 0 else [100, 0.001]
        colors = [SUCCESS_GREEN, FAILURE_RED]
        wedges, _ = inset.pie(
            sizes, colors=colors, startangle=90,
            wedgeprops=dict(width=0.48, edgecolor=BG_PANEL, linewidth=2),
        )
        inset.text(0, 0, f"{pct_ok}%",
                   ha="center", va="center",
                   fontsize=16, fontweight="bold",
                   fontfamily="monospace", color=ACCENT_TEAL)

    # Stats on the right
    stats = [
        ("TOTAL RUNS",   str(total),   TEXT_PRIMARY),
        ("✔  SUCCESS",   str(success), SUCCESS_GREEN),
        ("✘  FAILURE",   str(failure), FAILURE_RED),
        ("SUCCESS RATE", f"{pct_ok}%", ACCENT_TEAL),
    ]
    for j, (lbl, val, col) in enumerate(stats):
        y_pos = 0.82 - j * 0.20
        ax.text(0.60, y_pos,       lbl, color=TEXT_MUTED,   fontsize=7,  fontfamily="monospace")
        ax.text(0.60, y_pos - 0.09, val, color=col,          fontsize=11, fontfamily="monospace",
                fontweight="bold")


# ── Main entry point ──────────────────────────────────────────────────────────

def create_chart(df: pd.DataFrame, kpis: dict | None = None) -> None:
    """
    Generate the 4-panel dashboard and save to output/chart.png.

    Parameters
    ----------
    df   : DataFrame with columns [timestamp, price, change_24h]
    kpis : dict from compute_kpis(); if None, derived on the fly
    """
    os.makedirs("output", exist_ok=True)

    if kpis is None:
        kpis = {
            "avg_price":      float(df["price"].mean()),
            "max_price":      float(df["price"].max()),
            "min_price":      float(df["price"].min()),
            "lastest_change": float(df["change_24h"].iloc[-1]),
        }

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # ── Layout ────────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(16, 9), facecolor=BG_DARK)

    # Title bar
    fig.text(0.5, 0.965,
             "₿  BITCOIN  ·  ENGINEERING DASHBOARD",
             ha="center", va="top",
             fontsize=16, fontweight="bold",
             fontfamily="monospace", color=TEXT_PRIMARY)
    fig.text(0.5, 0.935,
             "real-time KPI monitoring  ·  pipeline efficiency tracking",
             ha="center", va="top",
             fontsize=8, fontfamily="monospace", color=TEXT_MUTED)

    # Thin accent rule under title
    fig.add_artist(
        plt.Line2D([0.04, 0.96], [0.925, 0.925],
                   transform=fig.transFigure,
                   color=ACCENT_TEAL, linewidth=0.8, alpha=0.6)
    )

    gs = gridspec.GridSpec(
        2, 2,
        figure=fig,
        left=0.05, right=0.97,
        top=0.90,  bottom=0.07,
        hspace=0.38, wspace=0.25,
    )

    ax_price    = fig.add_subplot(gs[0, 0])
    ax_change   = fig.add_subplot(gs[0, 1])
    ax_kpis     = fig.add_subplot(gs[1, 0])
    ax_pipeline = fig.add_subplot(gs[1, 1])

    _panel_price(ax_price, df)
    _panel_change(ax_change, df)
    _panel_kpis(ax_kpis, kpis)
    _panel_pipeline(ax_pipeline)

    # Footer
    from datetime import datetime
    fig.text(0.97, 0.02,
             f"generated {datetime.now().strftime('%Y-%m-%d %H:%M')}",
             ha="right", va="bottom",
             fontsize=6, fontfamily="monospace", color=TEXT_MUTED, alpha=0.6)

    plt.savefig("output/chart.png", dpi=150, bbox_inches="tight",
                facecolor=BG_DARK)
    plt.close(fig)
    print("[visualize] Dashboard saved → output/chart.png")


# ── Quick local test ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import numpy as np
    from datetime import datetime, timedelta

    # Simulate a few data points
    now    = datetime.now()
    times  = [now - timedelta(minutes=10 * i) for i in range(12, 0, -1)]
    prices = [85000 + np.random.randn() * 800 for _ in times]
    changes= [round(np.random.uniform(-3, 3), 2) for _ in times]

    sample_df = pd.DataFrame({
        "timestamp":  times,
        "price":      prices,
        "price_eur":  prices,
        "change_24h": changes,
    })

    # Simulate a build log
    os.makedirs("data", exist_ok=True)
    pd.DataFrame({
        "timestamp": times,
        "status":    ["success", "success", "failure", "success",
                      "success", "failure", "success", "success",
                      "success", "success", "failure", "success"],
    }).to_csv("data/build_log.csv", index=False)

    create_chart(sample_df)
    print("Done — check output/chart.png")