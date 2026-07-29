"""Generate every diagram used in the SmartEdit AI dissertation report.

All figures are drawn with matplotlib only (patches, FancyArrowPatch,
FancyBboxPatch, text) -- no graphviz. A small helper library at the top
(box, arrow, oval, diamond, class_box, table_box, sequence lifelines, crow's
foot markers, lollipop/socket markers) is reused by one function per figure.
Running this file regenerates every PNG in docs/diagrams from scratch.
"""
import math
import os
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import (Arc, Circle, Ellipse, FancyArrowPatch,
                                 FancyBboxPatch, Polygon, Rectangle)

OUT = os.path.join(os.path.dirname(__file__), "diagrams")
os.makedirs(OUT, exist_ok=True)

# --------------------------------------------------------------------------- #
#  Palette
# --------------------------------------------------------------------------- #
BLUE = "#1a73e8"
BLUE_D = "#1457b8"
LIGHT = "#e8f0fe"
INK = "#1f2733"
GREY = "#6b7787"
HAIR = "#e6eaf0"
GREEN = "#1aa260"
RED = "#e03e3e"
AMBER = "#f9ab00"
WHITE = "#ffffff"

ROUND = "round,pad=0.02,rounding_size=0.02"


# --------------------------------------------------------------------------- #
#  Shared drawing library
# --------------------------------------------------------------------------- #
def new_axes(w, h):
    """A figure whose data coordinates equal inches, origin bottom-left."""
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")
    return fig, ax


def save(fig, name):
    path = os.path.join(OUT, f"{name}.png")
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", os.path.basename(path))


def row_x(n, x0, x1):
    """n evenly spaced x positions between x0 and x1 inclusive."""
    if n == 1:
        return [(x0 + x1) / 2]
    step = (x1 - x0) / (n - 1)
    return [x0 + i * step for i in range(n)]


def wrap(text, width):
    return "\n".join(textwrap.wrap(text, width=width))


def box(ax, cx, cy, w, h, text, fc=WHITE, ec=BLUE_D, fs=10, tc=INK,
        weight="normal", lw=1.2, zorder=3, style=None, ls="-"):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                 boxstyle=style or ROUND, linewidth=lw, linestyle=ls,
                                 edgecolor=ec, facecolor=fc, zorder=zorder))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color=tc,
             weight=weight, zorder=zorder + 1, linespacing=1.4)


def note(ax, x, y, text, fs=8.5, color=GREY, ha="left", va="center", weight="normal", zorder=5, style="italic"):
    ax.text(x, y, text, fontsize=fs, color=color, ha=ha, va=va, weight=weight,
             style=style, zorder=zorder, linespacing=1.3)


def arrow(ax, p1, p2, text=None, color=BLUE_D, lw=1.4, arrowstyle="-|>",
          fs=8.5, tc=GREY, connectionstyle=None, ls="-", t=0.5, dx=0.0, dy=0.14,
          zorder=2, mutation_scale=12, text_ha="center"):
    kw = dict(arrowstyle=arrowstyle, mutation_scale=mutation_scale, color=color,
              lw=lw, linestyle=ls, zorder=zorder, shrinkA=0, shrinkB=0)
    if connectionstyle:
        kw["connectionstyle"] = connectionstyle
    ax.add_patch(FancyArrowPatch(p1, p2, **kw))
    if text:
        mx = p1[0] + (p2[0] - p1[0]) * t + dx
        my = p1[1] + (p2[1] - p1[1]) * t + dy
        ax.text(mx, my, text, ha=text_ha, va="center", fontsize=fs, color=tc,
                 zorder=zorder + 1, linespacing=1.2,
                 bbox=dict(fc="white", ec="none", pad=1.0))


def oval(ax, cx, cy, w, h, text, fc=WHITE, ec=BLUE, fs=9.3, tc=INK, lw=1.2, zorder=3):
    ax.add_patch(Ellipse((cx, cy), w, h, facecolor=fc, edgecolor=ec, linewidth=lw, zorder=zorder))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color=tc,
             zorder=zorder + 1, linespacing=1.2)


def diamond(ax, cx, cy, w, h, text, fc="#fff8e8", ec=AMBER, fs=8.3, tc=INK, zorder=3):
    pts = [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=fc, edgecolor=ec, linewidth=1.3, zorder=zorder))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color=tc,
             zorder=zorder + 1, linespacing=1.15)


def circle_proc(ax, cx, cy, r, text, fc=BLUE, tc=WHITE, ec=BLUE_D, fs=8.6, zorder=3):
    ax.add_patch(Circle((cx, cy), r, fc=fc, ec=ec, lw=1.3, zorder=zorder))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color=tc,
             weight="bold", zorder=zorder + 1, linespacing=1.15)


def data_store(ax, cx, cy, w, h, text, fs=8.6):
    y0, y1 = cy - h / 2, cy + h / 2
    x0, x1 = cx - w / 2, cx + w / 2
    ax.plot([x0, x1], [y1, y1], color=BLUE_D, lw=1.4, zorder=3)
    ax.plot([x0, x1], [y0, y0], color=BLUE_D, lw=1.4, zorder=3)
    ax.plot([x0, x0], [y0, y1], color=BLUE_D, lw=1.4, zorder=3)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color=INK,
             zorder=4, linespacing=1.15)


def stick_actor(ax, cx, cy, scale=1.0, color=INK, label_text=None, label_dy=-0.32, fs=9.5):
    ax.add_patch(Circle((cx, cy + 0.34 * scale), 0.13 * scale, fc="white", ec=color, lw=1.6, zorder=3))
    ax.plot([cx, cx], [cy + 0.21 * scale, cy - 0.30 * scale], color=color, lw=1.7, zorder=3)
    ax.plot([cx - 0.25 * scale, cx + 0.25 * scale], [cy + 0.02 * scale, cy + 0.02 * scale], color=color, lw=1.7, zorder=3)
    ax.plot([cx, cx - 0.22 * scale], [cy - 0.30 * scale, cy - 0.60 * scale], color=color, lw=1.7, zorder=3)
    ax.plot([cx, cx + 0.22 * scale], [cy - 0.30 * scale, cy - 0.60 * scale], color=color, lw=1.7, zorder=3)
    if label_text:
        ax.text(cx, cy - 0.60 * scale + label_dy, label_text, ha="center", va="top",
                 fontsize=fs, color=INK, weight="bold", zorder=4, linespacing=1.2)


def start_state(ax, cx, cy, r=0.13, color=INK, zorder=3):
    ax.add_patch(Circle((cx, cy), r, fc=color, ec=color, zorder=zorder))


def end_state(ax, cx, cy, r=0.16, color=INK, zorder=3):
    ax.add_patch(Circle((cx, cy), r, fc="white", ec=color, lw=1.4, zorder=zorder))
    ax.add_patch(Circle((cx, cy), r * 0.48, fc=color, ec=color, zorder=zorder + 1))


def fork_bar(ax, cx, cy, length, vertical=False, color=INK, thickness=0.09):
    if vertical:
        ax.add_patch(Rectangle((cx - thickness / 2, cy - length / 2), thickness, length, fc=color, ec=color, zorder=3))
    else:
        ax.add_patch(Rectangle((cx - length / 2, cy - thickness / 2), length, thickness, fc=color, ec=color, zorder=3))


def crow(ax, x, y, ux, uy, kind, size=0.16, color=BLUE_D, zorder=4):
    """Crow's-foot mark at (x, y). (ux, uy) points away from the table edge."""
    px, py = -uy, ux
    if kind == "one":
        bx, by = x + ux * size * 1.0, y + uy * size * 1.0
        ax.plot([bx - px * size * 0.55, bx + px * size * 0.55],
                 [by - py * size * 0.55, by + py * size * 0.55], color=color, lw=1.3, zorder=zorder)
        bx2, by2 = x + ux * size * 1.7, y + uy * size * 1.7
        ax.plot([bx2 - px * size * 0.55, bx2 + px * size * 0.55],
                 [by2 - py * size * 0.55, by2 + py * size * 0.55], color=color, lw=1.3, zorder=zorder)
    else:
        bx, by = x + ux * size * 1.9, y + uy * size * 1.9
        for s in (-1, 0, 1):
            ax.plot([x, bx + px * size * s], [y, by + py * size * s], color=color, lw=1.3, zorder=zorder)


def table_box(ax, cx, top_y, w, name, rows, row_h=0.30, header_h=0.42, fs=8.3):
    """A crow's-foot ER table: header strip + one row per column, PK/FK tagged.

    Returns (bottom_y, dict of {row_label: (left_x, right_x, y_center)})."""
    x0, x1 = cx - w / 2, cx + w / 2
    h = header_h + row_h * len(rows)
    y0 = top_y - h
    ax.add_patch(Rectangle((x0, y0), w, h, lw=1.3, ec=BLUE_D, fc=WHITE, zorder=2))
    ax.add_patch(Rectangle((x0, top_y - header_h), w, header_h, lw=1.3, ec=BLUE_D, fc=BLUE_D, zorder=3))
    ax.text(cx, top_y - header_h / 2, name, ha="center", va="center", fontsize=fs + 1.4,
             color="white", weight="bold", zorder=4)
    rowinfo = {}
    for i, (col, tag) in enumerate(rows):
        ry = top_y - header_h - row_h * i - row_h / 2
        if i > 0:
            ax.plot([x0, x1], [ry + row_h / 2, ry + row_h / 2], color=HAIR, lw=0.9, zorder=4)
        weight = "bold" if tag == "PK" else "normal"
        color = BLUE_D if tag else INK
        ax.text(x0 + 0.14, ry, col, ha="left", va="center", fontsize=fs, color=color, weight=weight, zorder=5)
        if tag:
            ax.text(x1 - 0.12, ry, tag, ha="right", va="center", fontsize=fs - 0.6, color=BLUE_D,
                     weight="bold", zorder=5)
        if tag == "PK":
            ax.plot([x0 + 0.14, x0 + 0.14 + 0.09 * len(col)], [ry - 0.09, ry - 0.09], color=BLUE_D, lw=0.8, zorder=5)
        rowinfo[col] = (x0, x1, ry)
    return y0, rowinfo


def class_h(n_attrs, n_methods=0, stereotype=False):
    header_h = 0.5 if stereotype else 0.36
    hh = header_h + 0.18 + n_attrs * 0.225 + 0.10
    if n_methods:
        hh += 0.16 + n_methods * 0.225
    return hh


def class_box(ax, cx, cy, w, title, attrs, methods=None, stereotype=None, fs=8.2):
    header_h = 0.5 if stereotype else 0.36
    h = class_h(len(attrs), len(methods) if methods else 0, bool(stereotype))
    x0, x1 = cx - w / 2, cx + w / 2
    y1 = cy + h / 2
    y0 = cy - h / 2
    ax.add_patch(Rectangle((x0, y0), w, h, lw=1.3, ec=BLUE_D, fc=WHITE, zorder=2))
    ax.add_patch(Rectangle((x0, y1 - header_h), w, header_h, lw=1.3, ec=BLUE_D, fc=BLUE_D, zorder=3))
    ttl = f"«{stereotype}»\n{title}" if stereotype else title
    ax.text(cx, y1 - header_h / 2, ttl, ha="center", va="center", fontsize=fs + 1.1, color="white",
             weight="bold", zorder=4, linespacing=1.1)
    ty = y1 - header_h - 0.16
    for line in attrs:
        ax.text(x0 + 0.14, ty, line, ha="left", va="top", fontsize=fs, color=INK, zorder=4)
        ty -= 0.225
    if methods:
        div_y = ty + 0.10
        ax.plot([x0, x1], [div_y, div_y], color=HAIR, lw=1.1, zorder=4)
        ty -= 0.06
        for line in methods:
            ax.text(x0 + 0.14, ty, line, ha="left", va="top", fontsize=fs, color=BLUE_D, zorder=4)
            ty -= 0.225
    return y0, y1, h


def lollipop(ax, x, y, ex, ey, text, color=BLUE_D, fs=7.2, text_side="auto"):
    ax.plot([x, ex], [y, ey], color=color, lw=1.2, zorder=3)
    ax.add_patch(Circle((ex, ey), 0.075, fc="white", ec=color, lw=1.3, zorder=4))
    if text:
        dxsign = 1 if ex >= x else -1
        ha = "left" if dxsign > 0 else "right"
        ax.text(ex + 0.13 * dxsign, ey, text, fontsize=fs, color=GREY, ha=ha, va="center", zorder=5)


def socket_mark(ax, x, y, ex, ey, upward, color=BLUE_D):
    ax.plot([x, ex], [y, ey], color=color, lw=1.2, zorder=3)
    theta1, theta2 = (200, 340) if upward else (20, 160)
    ax.add_patch(Arc((ex, ey), 0.24, 0.24, angle=0, theta1=theta1, theta2=theta2, color=color, lw=1.5, zorder=4))


def frame(ax, x1, x2, y_top, y_bottom, tag, cond="", color=GREY, fs=7.6):
    ax.add_patch(Rectangle((x1, y_bottom), x2 - x1, y_top - y_bottom, fill=False,
                            ec=color, lw=1.1, zorder=1))
    tab_w = min(0.85, (x2 - x1) * 0.34)
    tab_h = 0.30
    pts = [(x1, y_top), (x1 + tab_w, y_top), (x1 + tab_w * 0.72, y_top - tab_h), (x1, y_top - tab_h)]
    ax.add_patch(Polygon(pts, closed=True, fc="#eef1f5", ec=color, lw=1.1, zorder=2))
    ax.text(x1 + 0.09, y_top - tab_h / 2, tag, fontsize=fs, weight="bold", color=INK,
             ha="left", va="center", zorder=3)
    if cond:
        ax.text(x1 + tab_w + 0.12, y_top - tab_h / 2, cond, fontsize=fs, color=INK,
                 ha="left", va="center", zorder=3, style="italic")


def frame_divider(ax, x1, x2, y, cond, color=GREY, fs=7.6):
    ax.plot([x1, x2], [y, y], color=color, lw=1.0, ls=(0, (4, 3)), zorder=2)
    ax.text(x1 + 0.12, y - 0.10, cond, fontsize=fs, color=INK, ha="left", va="top",
             zorder=3, style="italic")


# =========================================================================== #
#  01 -- SYSTEM ARCHITECTURE
# =========================================================================== #
def fig_system_architecture():
    w, h = 12.6, 9.9
    fig, ax = new_axes(w, h)

    # Layer 1: Browser front end -------------------------------------------------
    l1_y0, l1_y1 = 8.10, 9.60
    box(ax, w / 2, (l1_y0 + l1_y1) / 2, w - 0.6, l1_y1 - l1_y0, "", fc=LIGHT, ec=BLUE, lw=1.4)
    ax.text(0.55, l1_y1 - 0.20, "BROWSER FRONT END", fontsize=10, color=BLUE_D, weight="bold", ha="left")
    ax.text(0.55, l1_y1 - 0.46, "server-rendered HTML + vanilla JS + Chart.js  —  runs in the user's own browser",
             fontsize=8.2, color=GREY, ha="left")
    pages_row1 = ["Login", "Register", "Dashboard", "Add Entry", "View / Database"]
    pages_row2 = ["Tracker", "Salary & Tax", "Goals & Budget", "Insights", "AI Chat"]
    xs = row_x(5, 1.75, w - 1.75)
    for x, t in zip(xs, pages_row1):
        box(ax, x, l1_y1 - 0.78, 2.05, 0.38, t, fc=WHITE, ec=BLUE, fs=8.3, lw=1.0)
    for x, t in zip(xs, pages_row2):
        box(ax, x, l1_y1 - 1.24, 2.05, 0.38, t, fc=WHITE, ec=BLUE, fs=8.3, lw=1.0)

    # Layer 2: Flask application server ------------------------------------------
    l2_y0, l2_y1 = 4.85, 7.70
    box(ax, w / 2, (l2_y0 + l2_y1) / 2, w - 0.6, l2_y1 - l2_y0, "", fc="#f3f7ff", ec=BLUE, lw=1.4)
    ax.text(0.55, l2_y1 - 0.20, "FLASK APPLICATION SERVER", fontsize=10, color=BLUE_D, weight="bold", ha="left")
    modules_row1 = ["Authentication\n& Session", "Statement Parser\n(parser.py)",
                     "Transaction Classifier\n(classifier.py)", "Analytics Engine\n(analytics.py)"]
    modules_row2 = ["Salary & Tax Module\n(salary.py)", "NL Query Engine\n(nlq.py)",
                     "AI Advisory\n(advisor.py)", "RAG Chatbot\n(rag.py)"]
    mx = row_x(4, 2.15, w - 2.15)
    for x, t in zip(mx, modules_row1):
        box(ax, x, l2_y1 - 0.98, 2.55, 0.85, t, fc=WHITE, ec=BLUE_D, fs=8.6)
    for x, t in zip(mx, modules_row2):
        box(ax, x, l2_y1 - 1.98, 2.55, 0.85, t, fc=WHITE, ec=BLUE_D, fs=8.6)

    # Layer 3: local inference layer + optional cloud fallback -------------------
    l3_y0, l3_y1 = 2.95, 4.15
    box(ax, 4.55, (l3_y0 + l3_y1) / 2, 8.5, l3_y1 - l3_y0, "", fc="#eafaf0", ec=GREEN, lw=1.4)
    ax.text(0.55, l3_y1 - 0.22, "LOCAL INFERENCE LAYER  (llm_local.py)", fontsize=9.6, color=GREEN, weight="bold", ha="left")
    ax.text(0.55, l3_y1 - 0.50,
             "llama.cpp running Qwen2.5-1.5B-Instruct, quantised to Q4_K_M — entirely on the user's own machine",
             fontsize=8.0, color=GREY, ha="left")
    ax.text(0.55, l3_y1 - 0.85,
             "Fallback ladder:  local model  →  Ollama (if running)  →  Gemini API (only if a key is supplied)  →  deterministic rule-based advisor",
             fontsize=7.6, color=INK, ha="left")

    box(ax, 10.15, (l3_y0 + l3_y1) / 2, 1.5, 0.85, "Gemini API\n(cloud)", fc="#f2f2f2", ec="#9aa2ad", tc=GREY, fs=8.3)
    arrow(ax, (9.30, (l3_y0 + l3_y1) / 2), (9.40, (l3_y0 + l3_y1) / 2),
          text="optional, only if\na key is configured", color="#9aa2ad", ls=(0, (4, 3)), fs=6.9, tc=GREY, dy=0.42)

    # Layer 4: SQLite database ----------------------------------------------------
    l4_y0, l4_y1 = 0.45, 1.75
    box(ax, w / 2, (l4_y0 + l4_y1) / 2, w - 0.6, l4_y1 - l4_y0, "", fc=LIGHT, ec=BLUE, lw=1.4)
    ax.text(0.55, l4_y1 - 0.22, "SQLITE DATABASE  (via SQLAlchemy ORM)", fontsize=9.6, color=BLUE_D, weight="bold", ha="left")
    tables = ["users", "transactions", "embeddings", "chat_history", "salary_profiles", "savings_goals", "budgets"]
    tx = row_x(7, 1.15, w - 1.15)
    for x, t in zip(tx, tables):
        box(ax, x, l4_y1 - 0.62, 1.55, 0.36, t, fc=WHITE, ec=BLUE_D, fs=7.6)

    # inter-layer arrows -----------------------------------------------------
    arrow(ax, (w / 2, l1_y0), (w / 2, l2_y1), text="HTTP", fs=9, tc=BLUE_D, lw=1.6)
    arrow(ax, (4.55, l2_y0), (4.55, l3_y1), text="advisor.py / rag.py\ngeneration calls", fs=7.6, tc=BLUE_D, lw=1.6, dx=0.0)
    arrow(ax, (w - 1.4, l2_y0), (w - 1.4, l4_y1), text="SQLAlchemy ORM", fs=9, tc=BLUE_D, lw=1.6,
          connectionstyle="arc3,rad=0.0")

    ax.text(w - 0.55, 0.22, "Bank statements and the language model never leave this device.",
             fontsize=8.0, color=GREEN, ha="right", style="italic")
    save(fig, "01_system_architecture")


# =========================================================================== #
#  02 -- USE CASE DIAGRAM
# =========================================================================== #
def fig_use_case():
    w, h = 11.6, 9.6
    fig, ax = new_axes(w, h)

    bx0, bx1 = 2.15, 8.85
    by0, by1 = 0.55, 9.10
    box(ax, (bx0 + bx1) / 2, (by0 + by1) / 2, bx1 - bx0, by1 - by0, "", fc="#f7faff", ec=BLUE, lw=1.5)
    ax.text((bx0 + bx1) / 2, by1 - 0.24, "SmartEdit AI", fontsize=12, color=BLUE_D, weight="bold", ha="center")

    stick_actor(ax, 0.9, 4.85, scale=1.55, label_text="Salaried\nUser", fs=9)
    stick_actor(ax, 10.6, 4.85, scale=1.55, label_text="Local Language\nModel", fs=9)

    col1_x, col2_x = 4.05, 6.95
    rows_y = row_x(5, by1 - 0.85, by0 + 0.65)
    cases_col1 = ["Register / Login", "Upload Statement", "Add Manual Entry",
                  "View & Re-categorise\nTransactions", "See Dashboard"]
    cases_col2 = ["Track Trends", "Set Salary Profile", "Set Budget & Goals",
                  "Ask Chatbot", "Get Savings Advice"]

    for y, t in zip(rows_y, cases_col1):
        oval(ax, col1_x, y, 2.55, 0.80, t)
    for y, t in zip(rows_y, cases_col2):
        oval(ax, col2_x, y, 2.55, 0.80, t)

    user_edge = (1.28, 4.85)
    for y in rows_y:
        arrow(ax, user_edge, (col1_x - 1.28, y), color=GREY, lw=1.0, arrowstyle="-", zorder=1)
    for y in rows_y:
        arrow(ax, user_edge, (col2_x - 1.28, y), color=GREY, lw=1.0, arrowstyle="-", zorder=1)

    llm_edge = (10.22, 4.85)
    ai_targets = {"Ask Chatbot": rows_y[3], "Get Savings Advice": rows_y[4]}
    for y in ai_targets.values():
        arrow(ax, llm_edge, (col2_x + 1.28, y), color=GREEN, lw=1.2, arrowstyle="-", zorder=1,
              ls=(0, (4, 3)))

    save(fig, "02_use_case")


# =========================================================================== #
#  03 -- CLASS DIAGRAM
# =========================================================================== #
def fig_class_diagram():
    w, h = 15.6, 10.6
    fig, ax = new_axes(w, h)

    User_attrs = ["+ id : int", "+ name : str", "+ email : str (unique)",
                  "+ password_hash : str", "+ created_at : datetime"]
    User_meth = ["+ check_password()"]
    Txn_attrs = ["+ id : int", "+ user_id : FK", "+ date : date", "+ description : str",
                 "+ amount : float", "+ txn_type : credit|debit", "+ category : str",
                 "+ method : str", "+ fingerprint : str", "+ merchant : str", "+ confidence : float"]
    Txn_meth = ["+ to_dict()", "+ make_fingerprint()"]
    Emb_attrs = ["+ id : int", "+ transaction_id : FK", "+ vector : JSON[float] (384-d)"]
    Chat_attrs = ["+ id : int", "+ user_id : FK", "+ role : user|assistant", "+ message : text",
                  "+ created_at : datetime"]
    Sal_attrs = ["+ id : int", "+ user_id : FK (unique)", "+ ctc_annual : float",
                 "+ basic_pct, hra_pct : float", "+ regime : old|new", "+ metro : bool",
                 "+ rent_paid_monthly : float", "+ state : str"]
    Goal_attrs = ["+ id : int", "+ user_id : FK", "+ name : str", "+ target_amount : float",
                  "+ target_date : date", "+ saved_amount : float", "+ status : str"]
    Budget_attrs = ["+ id : int", "+ user_id : FK", "+ category : str", "+ monthly_limit : float"]

    entities = {
        "User": (2.4, User_attrs, User_meth),
        "Transaction": (2.9, Txn_attrs, Txn_meth),
        "Embedding": (2.7, Emb_attrs, None),
        "ChatHistory": (2.6, Chat_attrs, None),
        "SalaryProfile": (2.9, Sal_attrs, None),
        "SavingsGoal": (2.6, Goal_attrs, None),
        "Budget": (2.5, Budget_attrs, None),
    }

    row_a_names = ["User", "Transaction", "Embedding", "ChatHistory"]
    row_a_x = row_x(4, 2.0, w - 2.0)
    row_a_y = h - 1.9

    row_b_names = ["SalaryProfile", "SavingsGoal", "Budget"]
    row_b_x = row_x(3, 3.4, w - 3.4)
    row_b_y = 4.55

    pos = {}
    for name, x in zip(row_a_names, row_a_x):
        width, attrs, meth = entities[name]
        y0, y1, hh = class_box(ax, x, row_a_y, width, name, attrs, meth)
        pos[name] = (x, row_a_y, width, hh)
    for name, x in zip(row_b_names, row_b_x):
        width, attrs, meth = entities[name]
        y0, y1, hh = class_box(ax, x, row_b_y, width, name, attrs, meth)
        pos[name] = (x, row_b_y, width, hh)

    services = ["StatementParser", "TransactionClassifier", "AnalyticsEngine",
                "SalaryCalculator", "QueryEngine", "RagChatbot", "LocalModel"]
    svc_methods = {
        "StatementParser": ["+ parse_statement()", "+ detect_header()"],
        "TransactionClassifier": ["+ classify()", "+ detect_method()"],
        "AnalyticsEngine": ["+ summary()", "+ budget_status()"],
        "SalaryCalculator": ["+ compute_take_home()", "+ goal_projection()"],
        "QueryEngine": ["+ parse_query()", "+ execute()"],
        "RagChatbot": ["+ retrieve()", "+ answer()"],
        "LocalModel": ["+ generate()"],
    }
    svc_x = row_x(7, 1.5, w - 1.5)
    svc_y = 0.95
    svc_w = 1.95
    svc_pos = {}
    for name, x in zip(services, svc_x):
        y0, y1, hh = class_box(ax, x, svc_y, svc_w, name, [], svc_methods[name], stereotype="service", fs=7.4)
        svc_pos[name] = (x, svc_y, svc_w, hh)

    def top(n):
        x, y, wd, hh = pos[n]
        return (x, y + hh / 2)

    def bottom(n):
        x, y, wd, hh = pos[n]
        return (x, y - hh / 2)

    def svc_top(n):
        x, y, wd, hh = svc_pos[n]
        return (x, y + hh / 2)

    # structural relationships with multiplicity ------------------------------
    def rel(a, b, mult_a, mult_b, rad=0.0):
        xa, ya, wa, ha_ = pos[a]
        xb, yb, wb, hb_ = pos[b]
        pa = (xa, ya - ha_ / 2) if ya > yb else (xa, ya + ha_ / 2)
        pb = (xb, yb + hb_ / 2) if yb < ya else (xb, yb - hb_ / 2)
        arrow(ax, pa, pb, color=BLUE_D, lw=1.3, arrowstyle="-", connectionstyle=f"arc3,rad={rad}")
        sign = 1 if pa[1] > pb[1] else -1
        ax.text(pa[0] + 0.34, pa[1] - 0.22 * sign, mult_a, fontsize=7.6, color=BLUE_D, ha="left", weight="bold",
                 bbox=dict(fc="white", ec="none", pad=0.4))
        ax.text(pb[0] + 0.34, pb[1] + 0.22 * sign, mult_b, fontsize=7.6, color=BLUE_D, ha="left", weight="bold",
                 bbox=dict(fc="white", ec="none", pad=0.4))

    rel("User", "Transaction", "1", "1..*", rad=0.10)
    rel("Transaction", "Embedding", "1", "1..1", rad=0.0)
    rel("User", "SalaryProfile", "1", "1..1", rad=0.28)
    rel("User", "SavingsGoal", "1", "1..*", rad=0.12)
    rel("User", "Budget", "1", "1..*", rad=0.0)
    rel("User", "ChatHistory", "1", "1..*", rad=-0.22)

    # dashed "uses / creates / reads" arrows from services to entities --------
    def svc_link(svc, ent, text, rad=0.0, t=0.5):
        p1 = svc_top(svc)
        x, y, wd, hh = pos[ent]
        p2 = (x, y - hh / 2)
        arrow(ax, p1, p2, text=text, color=GREEN, lw=1.1, ls=(0, (4, 3)), fs=6.6, tc=GREEN,
              connectionstyle=f"arc3,rad={rad}", t=t, dy=0.0)

    svc_link("StatementParser", "Transaction", "creates", rad=0.05, t=0.5)
    svc_link("TransactionClassifier", "Transaction", "assigns category", rad=0.05, t=0.35)
    svc_link("AnalyticsEngine", "Transaction", "aggregates", rad=-0.05, t=0.65)
    svc_link("AnalyticsEngine", "Budget", "checks", rad=0.15, t=0.4)
    svc_link("SalaryCalculator", "SalaryProfile", "computes from", rad=-0.05, t=0.5)
    svc_link("QueryEngine", "Transaction", "executes SQL over", rad=0.10, t=0.3)
    svc_link("RagChatbot", "Embedding", "retrieves", rad=-0.10, t=0.5)
    svc_link("RagChatbot", "ChatHistory", "logs", rad=0.20, t=0.6)

    p1 = svc_top("LocalModel")
    p2 = svc_top("RagChatbot")
    arrow(ax, p1, (p2[0], p2[1]), text="rephrases for", color=GREEN, lw=1.1, ls=(0, (4, 3)), fs=6.6, tc=GREEN,
          connectionstyle="arc3,rad=0.35", t=0.5)

    ax.text(w / 2, 0.20, "solid line = ORM relationship (multiplicity shown)      dashed green = uses / creates / reads",
             fontsize=8, color=GREY, ha="center", style="italic")

    save(fig, "03_class_diagram")


# =========================================================================== #
#  04 -- ER DIAGRAM
# =========================================================================== #
def fig_er_diagram():
    w, h = 15.0, 10.8
    fig, ax = new_axes(w, h)

    def rows(*specs):
        return [(c, t) for c, t in specs]

    users_rows = rows(("id", "PK"), ("name", ""), ("email (unique)", ""), ("password_hash", ""), ("created_at", ""))
    txn_rows = rows(("id", "PK"), ("user_id", "FK"), ("date", ""), ("description", ""), ("raw_description", ""),
                     ("amount", ""), ("txn_type", ""), ("category", ""), ("method", ""), ("source", ""),
                     ("fingerprint", ""), ("merchant", ""), ("confidence", ""), ("balance", ""), ("created_at", ""))
    emb_rows = rows(("id", "PK"), ("transaction_id", "FK"), ("vector (JSON)", ""))
    chat_rows = rows(("id", "PK"), ("user_id", "FK"), ("role", ""), ("message", ""), ("created_at", ""))
    sal_rows = rows(("id", "PK"), ("user_id", "FK"), ("ctc_annual", ""), ("basic_pct", ""), ("hra_pct", ""),
                     ("metro", ""), ("rent_paid_monthly", ""), ("regime", ""), ("other_allowances", ""),
                     ("pf_opt_in", ""), ("state", ""), ("updated_at", ""))
    goal_rows = rows(("id", "PK"), ("user_id", "FK"), ("name", ""), ("target_amount", ""), ("target_date", ""),
                      ("saved_amount", ""), ("created_at", ""), ("status", ""))
    budget_rows = rows(("id", "PK"), ("user_id", "FK"), ("category", ""), ("monthly_limit", ""))

    users_bot, _ = table_box(ax, 2.3, h - 0.3, 3.0, "users", users_rows)
    chat_bot, _ = table_box(ax, 2.3, users_bot - 0.5, 3.0, "chat_history", chat_rows)
    budget_bot, _ = table_box(ax, 2.3, chat_bot - 0.5, 3.0, "budgets", budget_rows)

    txn_bot, _ = table_box(ax, 7.55, h - 0.3, 3.3, "transactions", txn_rows)

    emb_bot, _ = table_box(ax, 12.9, h - 0.3, 2.9, "embeddings", emb_rows)
    sal_bot, _ = table_box(ax, 12.9, emb_bot - 0.5, 3.0, "salary_profiles", sal_rows)
    goal_bot, _ = table_box(ax, 12.9, sal_bot - 0.5, 3.0, "savings_goals", goal_rows)

    def rel(p1, u1, p2, u2, one_many=True):
        arrow(ax, p1, p2, color=BLUE_D, lw=1.3, arrowstyle="-")
        crow(ax, *p1, *u1, "one")
        crow(ax, *p2, *u2, "many" if one_many else "one")

    users_right = (2.3 + 1.5, h - 0.3 - 1.05)
    txn_left = (7.55 - 1.65, h - 0.3 - 1.05)
    rel(users_right, (1, 0), txn_left, (-1, 0))
    ax.text((users_right[0] + txn_left[0]) / 2, users_right[1] + 0.22, "1 : N", fontsize=8, color=BLUE_D, ha="center")

    users_bottom = (2.3, users_bot)
    chat_top = (2.3, users_bot - 0.0 + (users_bot - (chat_bot)) * 0 + (users_bot - 0.5) - (users_bot - 0.5))
    chat_top = (2.3, users_bot - 0.5 + (chat_bot - (users_bot - 0.5)) - (chat_bot - (users_bot - 0.5)))
    chat_top_y = (users_bot - 0.5) + ( ( (users_bot-0.5) - chat_bot ) )
    # simpler: chat table top = users_bot - 0.5
    chat_top = (2.3, users_bot - 0.5)
    rel((2.3, users_bot), (0, -1), chat_top, (0, 1))
    ax.text(2.75, (users_bot + chat_top[1]) / 2, "1 : N", fontsize=8, color=BLUE_D, ha="left")

    budget_top = (2.3, chat_bot - 0.5)
    rel((2.3, chat_bot), (0, -1), budget_top, (0, 1))
    ax.text(2.75, (chat_bot + budget_top[1]) / 2, "1 : N", fontsize=8, color=BLUE_D, ha="left")
    note(ax, 3.9, (chat_bot + budget_top[1]) / 2 - 0.35, "(users → budgets, via user_id)", fs=7, color=GREY, ha="left")

    txn_right = (7.55 + 1.65, h - 0.3 - 1.05)
    emb_left = (12.9 - 1.45, h - 0.3 - 1.05)
    rel(txn_right, (1, 0), emb_left, (-1, 0), one_many=False)
    ax.text((txn_right[0] + emb_left[0]) / 2, txn_right[1] + 0.22, "1 : 1", fontsize=8, color=BLUE_D, ha="center")

    sal_top = (12.9, emb_bot - 0.5)
    rel((12.9, emb_bot), (0, -1), sal_top, (0, 1), one_many=False)
    ax.text(13.4, (emb_bot + sal_top[1]) / 2, "users → 1 : 1", fontsize=7.4, color=BLUE_D, ha="left")

    goal_top = (12.9, sal_bot - 0.5)
    rel((12.9, sal_bot), (0, -1), goal_top, (0, 1))
    ax.text(13.4, (sal_bot + goal_top[1]) / 2, "users → 1 : N", fontsize=7.4, color=BLUE_D, ha="left")

    ax.text(w / 2, 0.20, "PK = primary key (underlined)   FK = foreign key   crow's foot = many-side of the relationship",
             fontsize=8.2, color=GREY, ha="center", style="italic")

    save(fig, "04_er_diagram")


# =========================================================================== #
#  Sequence diagram engine (shared by 05 and 06)
# =========================================================================== #
def sequence_setup(w, h, actors, left=1.1, right=None):
    fig, ax = new_axes(w, h)
    right = right if right else w - 1.1
    xs = dict(zip(actors, row_x(len(actors), left, right)))
    header_y = h - 0.55
    for a in actors:
        x = xs[a]
        box(ax, x, header_y, 1.75, 0.55, a, fc=BLUE_D, ec=BLUE_D, fs=9.2, tc="white", weight="bold")
    return fig, ax, xs, header_y


def lifelines(ax, xs, y_top, y_bottom):
    for x in xs.values():
        ax.plot([x, x], [y_top, y_bottom], color=GREY, lw=1.0, ls=(0, (4, 3)), zorder=1)


def activation(ax, x, y1, y2, w=0.13):
    ax.add_patch(Rectangle((x - w / 2, y2), w, y1 - y2, fc=WHITE, ec=BLUE_D, lw=1.0, zorder=2))


def msg(ax, xs, y, src, dst, text, fs=7.9, self_call=False, dashed=False, color=BLUE_D):
    ls = (0, (4, 3)) if dashed else "-"
    if self_call or src == dst:
        x = xs[src]
        arrow(ax, (x + 0.08, y), (x + 0.08, y - 0.34), color=color, lw=1.2, ls=ls,
              connectionstyle="arc3,rad=1.35", mutation_scale=10)
        ax.text(x + 0.55, y - 0.10, wrap(text, 30), fontsize=fs, color=INK, ha="left", va="top", linespacing=1.2)
    else:
        x1, x2 = xs[src], xs[dst]
        arrow(ax, (x1, y), (x2, y), color=color, lw=1.3, ls=ls, mutation_scale=11)
        ax.text((x1 + x2) / 2, y + 0.13, wrap(text, 34), fontsize=fs, color=INK, ha="center", va="bottom",
                 linespacing=1.15, bbox=dict(fc="white", ec="none", pad=0.6))


# =========================================================================== #
#  05 -- SEQUENCE: UPLOAD
# =========================================================================== #
def fig_sequence_upload():
    actors = ["User", "Browser", "Flask", "Parser", "Classifier", "Database", "Embedding\nIndex"]
    w, h = 14.0, 11.4
    fig, ax, xs, header_y = sequence_setup(w, h, actors)
    y_bottom = 0.5
    lifelines(ax, xs, header_y - 0.35, y_bottom)

    steps = [
        ("User", "Browser", "select file, click Upload"),
        ("Browser", "Flask", "POST /upload  (multipart file)"),
        ("Flask", "Parser", "parse_statement(name, bytes)"),
        ("Parser", "Parser", "detect header row (score top 25 rows)"),
        ("Parser", "Parser", "map bank columns / PDF text-line fallback"),
        ("Parser", "Flask", "raw transaction rows[]"),
    ]
    y = header_y - 0.85
    step_ys = []
    for src, dst, text in steps:
        self_call = src == dst
        msg(ax, xs, y, src, dst, text, self_call=self_call)
        step_ys.append(y)
        y -= 0.62 if not self_call else 0.72

    loop_top = y + 0.20
    loop_steps = [
        ("Flask", "Classifier", "classify(description, txn_type)"),
        ("Classifier", "Flask", "category, method, confidence"),
        ("Flask", "Database", "fingerprint already stored?"),
        ("Database", "Flask", "yes / no"),
    ]
    for src, dst, text in loop_steps:
        msg(ax, xs, y, src, dst, text)
        y -= 0.62

    alt_top = y + 0.22
    y -= 0.05
    msg(ax, xs, y, "Flask", "Database", "INSERT transaction row")
    y -= 0.62
    msg(ax, xs, y, "Flask", "Embedding\nIndex", "index_transaction(txn)")
    y -= 0.62
    msg(ax, xs, y, "Embedding\nIndex", "Database", "store 384-dim vector")
    y -= 0.62
    alt_mid = y + 0.30
    msg(ax, xs, y, "Flask", "Flask", "skip duplicate row", self_call=True, dashed=True, color=GREY)
    y -= 0.80
    alt_bottom = y + 0.20

    frame(ax, xs["Flask"] - 0.95, xs["Embedding\nIndex"] + 0.95, alt_top, alt_bottom, "alt", "")
    frame_divider(ax, xs["Flask"] - 0.95, xs["Embedding\nIndex"] + 0.95, alt_mid, "[else: fingerprint already exists]")
    ax.text(xs["Flask"] - 0.95 + 0.95, alt_top - 0.10, "[no duplicate found]", fontsize=7.4, color=INK,
             ha="left", va="top", style="italic")

    loop_bottom = alt_bottom - 0.05
    frame(ax, xs["Flask"] - 1.05, xs["Embedding\nIndex"] + 1.05, loop_top, loop_bottom, "loop", "for each parsed row")

    y = loop_bottom - 0.35
    msg(ax, xs, y, "Flask", "Browser", "redirect → /view  (N imported, M skipped)")
    y -= 0.62
    msg(ax, xs, y, "Browser", "User", "render categorised transaction table")
    y -= 0.45

    activation(ax, xs["Flask"], header_y - 0.60, y + 0.30)
    activation(ax, xs["Parser"], step_ys[2] + 0.30, step_ys[4] - 0.30)
    activation(ax, xs["Classifier"], loop_top - 0.05, loop_top - 0.65)
    activation(ax, xs["Database"], loop_top - 0.35, alt_bottom + 0.10)
    activation(ax, xs["Embedding\nIndex"], alt_top - 0.60, alt_top - 1.20)

    ax.set_ylim(min(y - 0.2, 0), h)
    save(fig, "05_sequence_upload")


# =========================================================================== #
#  06 -- SEQUENCE: CHAT / RAG
# =========================================================================== #
def fig_sequence_chat_rag():
    actors = ["User", "Flask", "Query\nEngine", "Database", "Retriever", "Local\nModel", "Guard"]
    w, h = 14.0, 12.0
    fig, ax, xs, header_y = sequence_setup(w, h, actors)
    y_bottom = 0.5
    lifelines(ax, xs, header_y - 0.35, y_bottom)

    y = header_y - 0.85
    steps = [
        ("User", "Flask", "POST /chat/send  { question }"),
        ("Flask", "Query\nEngine", "parse_query(question)"),
        ("Query\nEngine", "Flask", "structured spec  (matched: true/false)"),
        ("Flask", "Database", "execute(spec)  —  SQL aggregate"),
        ("Database", "Flask", "exact totals"),
        ("Flask", "Retriever", "retrieve(user_id, question)"),
        ("Retriever", "Retriever", "embed question  (MiniLM, 384-dim)"),
        ("Retriever", "Database", "fetch stored transaction vectors"),
        ("Database", "Retriever", "vectors"),
        ("Retriever", "Retriever", "cosine similarity → top-K"),
        ("Retriever", "Flask", "top-K relevant transactions"),
        ("Flask", "Local\nModel", "FACT block + rephrase prompt"),
        ("Local\nModel", "Flask", "natural-language draft answer"),
        ("Flask", "Guard", "check draft against FACT block"),
    ]
    for src, dst, text in steps:
        self_call = src == dst
        msg(ax, xs, y, src, dst, text, self_call=self_call)
        y -= 0.72 if self_call else 0.60

    guard_self_y = y
    msg(ax, xs, y, "Guard", "Guard", "scan for invented / mismatched figures", self_call=True)
    y -= 0.78

    alt_top = y + 0.22
    y -= 0.02
    msg(ax, xs, y, "Guard", "Flask", "approved answer")
    y -= 0.62
    alt_mid = y + 0.30
    msg(ax, xs, y, "Guard", "Flask", "reject → use deterministic template", dashed=True, color=RED)
    y -= 0.78
    alt_bottom = y + 0.20

    frame(ax, xs["Guard"] - 1.5, xs["Guard"] + 0.95, alt_top, alt_bottom, "alt", "")
    ax.text(xs["Guard"] - 1.5 + 0.95, alt_top - 0.10, "[figures match FACT block]", fontsize=7.4, color=INK,
             ha="left", va="top", style="italic")
    frame_divider(ax, xs["Guard"] - 1.5, xs["Guard"] + 0.95, alt_mid, "[else: hallucinated figure detected]")

    y = alt_bottom - 0.32
    msg(ax, xs, y, "Flask", "User", "final grounded answer")
    y -= 0.5

    activation(ax, xs["Flask"], header_y - 0.60, y + 0.35)
    activation(ax, xs["Guard"], guard_self_y + 0.20, alt_bottom + 0.10)
    activation(ax, xs["Query\nEngine"], header_y - 1.42, header_y - 2.05)
    activation(ax, xs["Retriever"], header_y - 3.85, header_y - 5.55)

    ax.set_ylim(min(y - 0.2, 0), h)
    save(fig, "06_sequence_chat_rag")


# =========================================================================== #
#  07 -- DATA FLOW DIAGRAM (level 1)
# =========================================================================== #
def fig_data_flow():
    w, h = 13.0, 10.4
    fig, ax = new_axes(w, h)

    ux = 1.15
    stick_actor(ax, ux, 5.0, scale=1.5, label_text="User", fs=9.5)

    px = 5.2
    p1 = (px, 9.3)
    p2 = (px, 7.5)
    p3 = (px, 5.6)
    p4 = (px, 3.6)
    p5 = (px, 1.5)
    circle_proc(ax, *p1, 0.78, "1.0\nParse\nStatement", fs=7.4)
    circle_proc(ax, *p2, 0.78, "2.0\nClassify\nTransaction", fs=7.2)
    circle_proc(ax, *p3, 0.78, "3.0\nAggregate\nAnalytics", fs=7.2)
    circle_proc(ax, *p4, 0.78, "4.0\nAnswer\nQuestion", fs=7.4)
    circle_proc(ax, *p5, 0.78, "5.0\nGenerate\nAdvice", fs=7.4)

    dx = 9.9
    d1 = (dx, 6.55)
    d2 = (dx, 8.4)
    d3 = (ux, 1.5)
    d4 = (dx, 3.6)
    data_store(ax, *d1, 2.1, 0.55, "D1   transactions")
    data_store(ax, *d2, 2.1, 0.55, "D2   embeddings")
    data_store(ax, *d3, 2.35, 0.55, "D3   salary & goals")
    data_store(ax, *d4, 2.1, 0.55, "D4   chat history")

    arrow(ax, (ux, 5.70), p1, text="upload PDF / CSV / XLSX", fs=6.8, connectionstyle="arc3,rad=0.12", t=0.42, dy=0.20)
    arrow(ax, p1, p2, text="raw rows", fs=7.2)
    arrow(ax, p2, d1, text="categorised transactions", fs=6.6, t=0.55, dy=0.16)
    arrow(ax, p2, d2, text="384-dim vector", fs=6.6, connectionstyle="arc3,rad=-0.15", t=0.55, dy=0.16)

    arrow(ax, d1, p3, text="transaction history", fs=6.6, t=0.4, dy=-0.18)
    arrow(ax, p3, (ux, 5.34), text="dashboard summary", fs=6.8, connectionstyle="arc3,rad=0.10", t=0.55, dy=0.20)

    arrow(ax, (ux, 4.98), p4, text="question", fs=7.0, connectionstyle="arc3,rad=-0.08", t=0.4, dy=-0.18)
    arrow(ax, d1, p4, text="SQL aggregate", fs=6.6, t=0.6, dy=0.18)
    arrow(ax, d2, p4, text="cosine similarity search", fs=6.4, connectionstyle="arc3,rad=-0.12", t=0.45, dy=-0.20)
    arrow(ax, p4, (ux, 4.62), text="grounded answer", fs=6.8, connectionstyle="arc3,rad=0.10", t=0.55, dy=-0.20)
    arrow(ax, p4, d4, text="log Q & A", fs=6.8, t=0.5, dy=0.16)

    arrow(ax, (ux, 4.26), d3, text="set salary profile /\ngoals / budget", fs=6.6, t=0.55, dy=0.0)
    arrow(ax, d3, p5, text="salary & goals", fs=6.8, t=0.45, dy=0.18)
    arrow(ax, d1, p5, text="spending pattern", fs=6.6, connectionstyle="arc3,rad=-0.12", t=0.6, dy=-0.20)
    arrow(ax, p5, (ux, 3.90), text="savings advice", fs=6.8, connectionstyle="arc3,rad=-0.12", t=0.5, dy=-0.20)

    save(fig, "07_data_flow")


# =========================================================================== #
#  08 -- COMPONENT DIAGRAM
# =========================================================================== #
def fig_component_diagram():
    w, h = 14.5, 10.6
    fig, ax = new_axes(w, h)

    def component(cx, cy, cw, ch, text, fc=WHITE, ec=BLUE_D, fs=8.4):
        box(ax, cx, cy, cw, ch, text, fc=fc, ec=ec, fs=fs, style="round,pad=0.02,rounding_size=0.02")
        ax.add_patch(Rectangle((cx - cw / 2 - 0.06, cy + ch / 2 - 0.18), 0.14, 0.10, fc="white", ec=ec, lw=1.0, zorder=4))
        ax.add_patch(Rectangle((cx - cw / 2 - 0.06, cy - ch / 2 + 0.08), 0.14, 0.10, fc="white", ec=ec, lw=1.0, zorder=4))

    web_y = h - 0.85
    component(w / 2, web_y, 6.5, 0.85, "Web Layer\n(Jinja templates + Chart.js)")

    modules = ["Auth &\nSession", "Statement\nParser", "Transaction\nClassifier", "Analytics\nEngine",
               "Salary &\nTax", "NL Query\nEngine", "AI\nAdvisory", "RAG\nChatbot"]
    mod_x = row_x(8, 1.15, w - 1.15)
    mod_y = h - 3.5
    for x, t in zip(mod_x, modules):
        component(x, mod_y, 1.55, 0.9, t, fs=7.6)

    db_y = 1.05
    lm_y = 1.05
    component(4.6, db_y, 2.6, 0.85, "SQLite Database", fs=8.6)
    component(w - 4.6, lm_y, 2.6, 0.85, "Local Model\n(llama.cpp / Qwen2.5)", fs=8.0)

    for x in mod_x:
        socket_mark(ax, x, web_y - 0.42, x, mod_y + 0.45, upward=True)
    lollipop(ax, mod_x[0], web_y - 0.42, mod_x[0], web_y - 0.42, None)

    db_needers = [0, 2, 3, 4, 5, 7]
    for i in db_needers:
        x = mod_x[i]
        socket_mark(ax, x, mod_y - 0.45, x, mod_y - 0.45, upward=False)
        arrow(ax, (x, mod_y - 0.60), (4.6, db_y + 0.42), color=BLUE_D, lw=1.0, arrowstyle="-",
              connectionstyle=f"arc3,rad={(x - 4.6) * 0.02}")
    lollipop(ax, 4.6, db_y + 0.42, 4.6, db_y + 0.42, None)
    ax.text(4.6 - 1.55, db_y + 0.42 + 0.55, "IDataAccess", fontsize=7.6, color=BLUE_D, ha="center",
             weight="bold", bbox=dict(fc="white", ec=BLUE_D, lw=0.8, pad=1.6))

    for name in ["AI\nAdvisory", "RAG\nChatbot"]:
        i = modules.index(name)
        x = mod_x[i]
        socket_mark(ax, x, mod_y - 0.45, x, mod_y - 0.45, upward=False)
        arrow(ax, (x, mod_y - 0.60), (w - 4.6, lm_y + 0.42), color=GREEN, lw=1.1, arrowstyle="-",
              connectionstyle=f"arc3,rad={(x - (w - 4.6)) * -0.015}")
    lollipop(ax, w - 4.6, lm_y + 0.42, w - 4.6, lm_y + 0.42, None, color=GREEN)
    ax.text(w - 4.6 + 1.75, lm_y + 0.42 + 0.55, "IGenerate", fontsize=7.6, color=GREEN, ha="center",
             weight="bold", bbox=dict(fc="white", ec=GREEN, lw=0.8, pad=1.6))

    ax.text(w / 2, 0.20,
             "lollipop = provided interface      socket (open arc) = required interface",
             fontsize=8.2, color=GREY, ha="center", style="italic")
    save(fig, "08_component_diagram")


# =========================================================================== #
#  09 -- DEPLOYMENT DIAGRAM
# =========================================================================== #
def fig_deployment_diagram():
    w, h = 13.0, 8.0
    fig, ax = new_axes(w, h)

    nx0, nx1 = 0.6, 8.9
    ny0, ny1 = 0.6, 7.2
    skew = 0.45
    ax.add_patch(Polygon([(nx0, ny1), (nx0 + skew, ny1 + skew), (nx1 + skew, ny1 + skew), (nx1, ny1)],
                          closed=True, fc="#d8e6fc", ec=BLUE_D, lw=1.3, zorder=1))
    ax.add_patch(Polygon([(nx1, ny0), (nx1, ny1), (nx1 + skew, ny1 + skew), (nx1 + skew, ny0 + skew)],
                          closed=True, fc="#c9dcfb", ec=BLUE_D, lw=1.3, zorder=1))
    ax.add_patch(Rectangle((nx0, ny0), nx1 - nx0, ny1 - ny0, fc=LIGHT, ec=BLUE_D, lw=1.3, zorder=2))
    ax.text((nx0 + nx1) / 2 + skew / 2, ny1 + skew + 0.22, "«device»  User's Windows PC",
             fontsize=10.5, color=BLUE_D, weight="bold", ha="center")

    def artifact(cx, cy, cw, ch, title, sub):
        box(ax, cx, cy, cw, ch, "", fc=WHITE, ec=BLUE_D)
        ax.add_patch(Rectangle((cx - cw / 2 + 0.14, cy + ch / 2 - 0.30), 0.20, 0.24, fc="white", ec=BLUE_D, lw=1.0, zorder=4))
        ax.add_patch(Rectangle((cx - cw / 2 + 0.17, cy + ch / 2 - 0.27), 0.14, 0.06, fc=BLUE_D, ec="none", zorder=5))
        ax.text(cx + 0.10, cy + 0.10, title, ha="center", va="center", fontsize=8.8, color=INK, weight="bold")
        ax.text(cx + 0.10, cy - 0.22, sub, ha="center", va="center", fontsize=7.2, color=GREY)

    ax0x, ax0y = row_x(2, nx0 + 1.9, nx1 - 1.9), None
    a1x, a2x = row_x(2, nx0 + 1.9, nx1 - 1.9)
    a1y = ny1 - 1.35
    a2y = ny0 + 1.35

    artifact(a1x, a1y, 3.0, 1.15, "Browser", "renders the local Flask UI")
    artifact(a2x, a1y, 3.0, 1.15, "Flask Server Process", "app.py, 127.0.0.1:5000")
    artifact(a1x, a2y, 3.0, 1.15, "SQLite Database File", "smartedit.db")
    artifact(a2x, a2y, 3.0, 1.15, "GGUF Model File", "qwen2.5-1.5b-instruct-q4_k_m.gguf")

    arrow(ax, (a1x + 1.1, a1y), (a2x - 1.1, a1y), text="HTTP\n(localhost)", fs=7.4)
    arrow(ax, (a2x, a1y - 0.58), (a2x, a2y + 0.58), text="loads via\nllama.cpp", fs=7.4)
    arrow(ax, (a2x - 1.1, a2y), (a1x + 1.1, a2y), text="SQLAlchemy\nORM", fs=7.4)

    gx, gy = nx1 + skew + 2.1, (ny0 + ny1) / 2 + skew / 2
    ax.add_patch(Rectangle((gx - 1.5, gy - 0.75), 3.0, 1.5, fc="#f2f2f2", ec="#9aa2ad", lw=1.3, zorder=2))
    ax.text(gx, gy, "«server»\nGemini API\n(cloud, optional)", fontsize=9, color=GREY, ha="center", va="center")

    arrow(ax, (a2x + 1.5, a2y + 0.3), (gx - 1.5, gy), text="optional, only if\na key is configured",
          color="#9aa2ad", ls=(0, (4, 3)), fs=7.4, tc=GREY)

    ax.text((nx0 + nx1) / 2, ny0 - 0.30,
             "Default deployment is fully offline — the dashed link is the only path that leaves the device.",
             fontsize=8.4, color=GREEN, ha="center", style="italic")
    save(fig, "09_deployment_diagram")


# =========================================================================== #
#  10 -- PARSER PIPELINE
# =========================================================================== #
def fig_parser_pipeline():
    w, h = 12.6, 13.6
    fig, ax = new_axes(w, h)
    cx_c, cx_p = 3.6, 9.3

    y_file = h - 0.6
    box(ax, w / 2, y_file, 3.6, 0.65, "Uploaded statement file", fs=10)

    y_diamond = y_file - 1.0
    diamond(ax, w / 2, y_diamond, 3.4, 1.0, "Detect file\nextension")
    arrow(ax, (w / 2, y_file - 0.325), (w / 2, y_diamond + 0.5), color=BLUE_D)

    y_branch = y_diamond - 0.95
    box(ax, cx_c, y_branch, 3.6, 0.6, "CSV / XLSX", fc=LIGHT, ec=BLUE, weight="bold")
    box(ax, cx_p, y_branch, 3.6, 0.6, "PDF", fc=LIGHT, ec=BLUE, weight="bold")
    arrow(ax, (w / 2 - 1.0, y_diamond - 0.5), (cx_c, y_branch + 0.30), text="tabular", fs=7.6)
    arrow(ax, (w / 2 + 1.0, y_diamond - 0.5), (cx_p, y_branch + 0.30), text="pdf", fs=7.6)

    y_scan = y_branch - 0.85
    box(ax, cx_c, y_scan, 3.7, 0.72, "Scan first 25 rows,\nscore candidate header row", fs=8.6)
    arrow(ax, (cx_c, y_branch - 0.3), (cx_c, y_scan + 0.36), color=BLUE_D)
    y_map = y_scan - 0.95
    box(ax, cx_c, y_map, 3.7, 0.72, "Map columns via\nper-bank alias table", fs=8.6)
    arrow(ax, (cx_c, y_scan - 0.36), (cx_c, y_map + 0.36), color=BLUE_D)

    y_extract = y_branch - 0.85
    box(ax, cx_p, y_extract, 3.7, 0.62, "Extract tables\n(pdfplumber)", fs=8.6)
    arrow(ax, (cx_p, y_branch - 0.3), (cx_p, y_extract + 0.31), color=BLUE_D)
    y_diamond2 = y_extract - 0.90
    diamond(ax, cx_p, y_diamond2, 3.3, 1.0, "Any table\nrows found?")
    arrow(ax, (cx_p, y_extract - 0.31), (cx_p, y_diamond2 + 0.5), color=BLUE_D)
    y_fallback = y_diamond2 - 0.95
    box(ax, cx_p, y_fallback, 3.7, 0.72, "Text-line regex\nfallback (dates, amounts,\nDr / Cr tokens)", fs=8.0)
    arrow(ax, (cx_p - 1.1, y_diamond2 - 0.35), (cx_p, y_fallback + 0.36), text="no", fs=7.6, dx=-0.30)

    y_norm = min(y_map, y_fallback) - 0.90
    arrow(ax, (cx_p + 1.1, y_diamond2 - 0.35), (w / 2 + 1.4, y_norm + 0.30), text="yes", fs=7.6,
          connectionstyle="arc3,rad=-0.28", dx=0.35, t=0.35)
    arrow(ax, (cx_c, y_map - 0.36), (w / 2 - 1.4, y_norm + 0.30), color=BLUE_D)
    arrow(ax, (cx_p, y_fallback - 0.36), (w / 2 + 1.4, y_norm + 0.30), color=BLUE_D)

    box(ax, w / 2, y_norm, 4.6, 0.7, "Normalise dates & Indian amount\nformats (₹, lakh / crore separators)", fs=8.4)

    y_resolve = y_norm - 0.95
    diamond(ax, w / 2, y_resolve, 4.6, 1.15, "Resolve credit vs debit:\nDr/Cr column → suffix → sign → balance delta")
    arrow(ax, (w / 2, y_norm - 0.35), (w / 2, y_resolve + 0.575), color=BLUE_D)

    y_wrap = y_resolve - 1.05
    box(ax, w / 2, y_wrap, 4.2, 0.65, "Merge wrapped description lines", fs=8.8)
    arrow(ax, (w / 2, y_resolve - 0.575), (w / 2, y_wrap + 0.325), color=BLUE_D)

    y_drop = y_wrap - 0.85
    box(ax, w / 2, y_drop, 4.6, 0.72, "Drop opening / closing-balance,\nsub-total and header-noise rows", fs=8.4)
    arrow(ax, (w / 2, y_wrap - 0.325), (w / 2, y_drop + 0.36), color=BLUE_D)

    y_emit = y_drop - 0.9
    box(ax, w / 2, y_emit, 3.8, 0.65, "Emit transaction rows", fc=LIGHT, ec=GREEN, tc=INK, weight="bold", fs=9.6)
    arrow(ax, (w / 2, y_drop - 0.36), (w / 2, y_emit + 0.325), color=BLUE_D)

    ax.set_ylim(y_emit - 0.5, h)
    save(fig, "10_parser_pipeline")


# =========================================================================== #
#  11 -- CLASSIFIER FLOW
# =========================================================================== #
def fig_classifier_flow():
    w, h = 9.6, 12.4
    fig, ax = new_axes(w, h)
    cx = w / 2

    y = h - 0.55
    box(ax, cx, y, 3.6, 0.6, "Raw bank narration", fs=9.6)
    y -= 0.85
    box(ax, cx, y, 4.6, 0.75, "Strip payment-rail prefix &\nreference numbers (UPI / NEFT / IMPS...)", fs=8.2)
    y -= 1.0
    diamond(ax, cx, y, 4.0, 1.15, "Rule engine\nkeyword match?")

    yr = y - 1.15
    box(ax, cx - 2.35, yr, 3.0, 0.85, "Category assigned\nconfidence = 1.0", fc=LIGHT, ec=GREEN, fs=8.6)
    arrow(ax, (cx - 1.6, y - 0.15), (cx - 2.35, yr + 0.42), text="yes", fs=8, dx=-0.15)

    yn = y - 1.15
    box(ax, cx + 0.9, yn, 3.5, 0.65, "TF-IDF character\nn-gram vectoriser", fs=8.4)
    arrow(ax, (cx, y - 0.575), (cx + 0.9, yn + 0.325), text="no", fs=8, dx=0.2)
    yn2 = yn - 0.9
    box(ax, cx + 0.9, yn2, 3.5, 0.6, "Logistic regression classifier", fs=8.4)
    arrow(ax, (cx + 0.9, yn - 0.325), (cx + 0.9, yn2 + 0.30))
    yn3 = yn2 - 0.95
    diamond(ax, cx + 0.9, yn3, 3.6, 1.15, "Top predicted\nprobability < 0.35 ?")
    arrow(ax, (cx + 0.9, yn2 - 0.30), (cx + 0.9, yn3 + 0.575))

    yn4 = yn3 - 1.1
    box(ax, cx + 2.7, yn4, 2.6, 0.75, "Category = “Others”", fc="#fdeeee", ec=RED, fs=8.4)
    arrow(ax, (cx + 0.9 + 1.55, yn3 - 0.05), (cx + 2.7, yn4 + 0.375), text="yes", fs=7.8, dx=0.15)

    yn5 = yn3 - 1.1
    box(ax, cx - 0.6, yn5, 3.0, 0.85, "Predicted category\nconfidence = probability", fc=LIGHT, ec=GREEN, fs=8.2)
    arrow(ax, (cx + 0.9 - 1.6, yn3 - 0.05), (cx - 0.6, yn5 + 0.425), text="no", fs=7.8, dx=-0.15)

    yend = min(yr - 0.55, yn4 - 0.55, yn5 - 0.55) - 0.55
    box(ax, cx, yend, 4.2, 0.65, "Category stored on the transaction", fc=LIGHT, ec=BLUE, weight="bold", fs=9.2)
    arrow(ax, (cx - 2.35, yr - 0.425), (cx - 1.2, yend + 0.325 + 0.1), connectionstyle="arc3,rad=-0.15")
    arrow(ax, (cx + 2.7, yn4 - 0.375), (cx + 1.2, yend + 0.325 + 0.1), connectionstyle="arc3,rad=0.15")
    arrow(ax, (cx - 0.6, yn5 - 0.425), (cx, yend + 0.325), connectionstyle="arc3,rad=0.0")

    note(ax, 0.25, h - 1.3, "The rule engine always\nruns first; the ML model\nonly sees narrations no\nkeyword rule could place.",
         fs=7.6, color=GREY, ha="left", va="top")

    ax.set_ylim(yend - 0.5, h)
    save(fig, "11_classifier_flow")


# =========================================================================== #
#  12 -- RAG PIPELINE
# =========================================================================== #
def fig_rag_pipeline():
    w, h = 14.0, 10.0
    fig, ax = new_axes(w, h)

    box(ax, w / 2, h - 0.55, 3.4, 0.65, "User question", fc=LIGHT, ec=BLUE, weight="bold", fs=10)

    left_x, right_x = 3.6, 10.4
    y0 = h - 1.7
    box(ax, left_x, y0, 4.2, 0.65, "Deterministic parse (nlq.py)", fs=8.6)
    box(ax, right_x, y0, 4.2, 0.65, "Embed question\n(MiniLM, 384-dim)", fs=8.6)
    arrow(ax, (w / 2 - 1.0, h - 0.55 - 0.325), (left_x, y0 + 0.325), connectionstyle="arc3,rad=-0.15")
    arrow(ax, (w / 2 + 1.0, h - 0.55 - 0.325), (right_x, y0 + 0.325), connectionstyle="arc3,rad=0.15")

    y1 = y0 - 0.95
    box(ax, left_x, y1, 4.2, 0.65, "Structured query spec", fs=8.6)
    arrow(ax, (left_x, y0 - 0.325), (left_x, y1 + 0.325))
    box(ax, right_x, y1, 4.2, 0.65, "Cosine similarity vs stored\ntransaction vectors", fs=8.2)
    arrow(ax, (right_x, y0 - 0.325), (right_x, y1 + 0.325))

    y2 = y1 - 0.95
    box(ax, left_x, y2, 4.2, 0.65, "Execute as SQL —\nexact aggregate figures", fc=LIGHT, ec=GREEN, fs=8.2)
    arrow(ax, (left_x, y1 - 0.325), (left_x, y2 + 0.325))
    box(ax, right_x, y2, 4.2, 0.65, "Top-K relevant\ntransactions", fc=LIGHT, ec=GREEN, fs=8.6)
    arrow(ax, (right_x, y1 - 0.325), (right_x, y2 + 0.325))

    y3 = y2 - 1.0
    box(ax, w / 2, y3, 5.2, 0.75, "Compose FACT block\n(exact numbers + top-K transaction lines)", fs=8.6)
    arrow(ax, (left_x, y2 - 0.325), (w / 2 - 1.2, y3 + 0.375), connectionstyle="arc3,rad=0.15")
    arrow(ax, (right_x, y2 - 0.325), (w / 2 + 1.2, y3 + 0.375), connectionstyle="arc3,rad=-0.15")

    y4 = y3 - 0.95
    box(ax, w / 2, y4, 5.4, 0.65, "Local model rephrases\n(Qwen2.5-1.5B — wording only, no new numbers)", fs=8.2)
    arrow(ax, (w / 2, y3 - 0.375), (w / 2, y4 + 0.325))

    y5 = y4 - 1.05
    diamond(ax, w / 2, y5, 5.2, 1.1, "Numeric guard:\nfigures match the FACT block?")
    arrow(ax, (w / 2, y4 - 0.325), (w / 2, y5 + 0.55))

    y6 = y5 - 1.05
    box(ax, left_x + 1.4, y6, 3.4, 0.65, "Return rephrased answer", fc=LIGHT, ec=GREEN, weight="bold", fs=8.6)
    arrow(ax, (w / 2 - 1.2, y5 - 0.2), (left_x + 1.4, y6 + 0.325), text="yes", fs=8, dx=-0.2)
    box(ax, right_x - 0.6, y6, 4.0, 0.65, "Fall back to deterministic\nanswer template", fc="#fdeeee", ec=RED, fs=8.2)
    arrow(ax, (w / 2 + 1.2, y5 - 0.2), (right_x - 0.6, y6 + 0.325), text="no", fs=8, dx=0.2)

    ax.set_ylim(y6 - 0.55, h)
    save(fig, "12_rag_pipeline")


# =========================================================================== #
#  13 -- SALARY FLOW
# =========================================================================== #
def fig_salary_flow():
    w, h = 11.6, 13.8
    fig, ax = new_axes(w, h)
    cx = w / 2

    y = h - 0.55
    box(ax, cx, y, 3.2, 0.6, "CTC (annual)", fc=LIGHT, ec=BLUE, weight="bold", fs=9.6)
    y -= 0.85
    box(ax, cx, y, 3.6, 0.6, "Basic = 40% of CTC", fs=8.8)
    y -= 0.85
    box(ax, cx, y, 3.8, 0.6, "HRA = 50% of Basic", fs=8.8)
    y -= 0.85
    box(ax, cx, y, 4.4, 0.6, "Special Allowance = remaining cash pay", fs=8.4)
    y -= 0.85
    box(ax, cx, y, 5.4, 0.75, "Gross = CTC − Employer PF (12% of Basic)\n− Gratuity (4.81% of Basic)", fs=8.2)
    y -= 1.0

    diamond(ax, cx, y, 3.2, 1.05, "Regime?")
    y_old_top = y - 1.0
    ox, nx = cx - 3.0, cx + 3.0
    box(ax, ox, y_old_top, 2.9, 0.6, "OLD REGIME", fc=LIGHT, ec=BLUE_D, weight="bold", fs=8.6)
    box(ax, nx, y_old_top, 2.9, 0.6, "NEW REGIME", fc=LIGHT, ec=BLUE_D, weight="bold", fs=8.6)
    arrow(ax, (cx - 1.6, y - 0.1), (ox, y_old_top + 0.30), text="old", fs=8)
    arrow(ax, (cx + 1.6, y - 0.1), (nx, y_old_top + 0.30), text="new", fs=8)

    yo = y_old_top - 0.85
    box(ax, ox, yo, 3.4, 1.0, "HRA exemption =\nmin( HRA, Rent − 10% Basic,\n50%/40% of Basic )", fs=7.6)
    yo -= 1.1
    box(ax, ox, yo, 3.0, 0.55, "Standard Deduction\n₹50,000", fs=7.8)
    yo -= 0.8
    box(ax, ox, yo, 3.0, 0.6, "Taxable Income\n(old regime)", fs=8.0)
    yo -= 0.85
    box(ax, ox, yo, 3.2, 0.7, "Old-regime slabs:\n0–5L nil · 5–10L 20% · 10L+ 30%", fs=7.2)
    yo -= 0.9
    box(ax, ox, yo, 3.3, 0.75, "Section 87A rebate\n(taxable ≤ ₹5,00,000)\n+ marginal relief", fs=7.4)

    yn = y_old_top - 0.85
    box(ax, nx, yn, 3.0, 0.55, "No HRA exemption", fc="#f4f4f4", ec=GREY, tc=GREY, fs=7.8)
    yn -= 0.8
    box(ax, nx, yn, 3.0, 0.55, "Standard Deduction\n₹75,000", fs=7.8)
    yn -= 0.8
    box(ax, nx, yn, 3.0, 0.6, "Taxable Income\n(new regime)", fs=8.0)
    yn -= 0.85
    box(ax, nx, yn, 3.3, 0.85, "New-regime slabs:\n0–4L nil · 4–8L 5% · 8–12L 10%\n... up to 30% above 24L", fs=7.0)
    yn -= 0.95
    box(ax, nx, yn, 3.3, 0.75, "Section 87A rebate\n(taxable ≤ ₹12,00,000)\n+ marginal relief", fs=7.4)

    arrow(ax, (ox, y_old_top - 0.3), (ox, y_old_top - 0.85 + 0.5))
    arrow(ax, (ox, y_old_top - 0.85 - 0.5), (ox, y_old_top - 1.95 + 0.275))
    arrow(ax, (ox, y_old_top - 1.95 - 0.275), (ox, y_old_top - 2.75 + 0.3))
    arrow(ax, (ox, y_old_top - 2.75 - 0.3), (ox, y_old_top - 3.6 + 0.35))
    arrow(ax, (ox, y_old_top - 3.6 - 0.35), (ox, y_old_top - 4.5 + 0.375))

    arrow(ax, (nx, y_old_top - 0.3), (nx, y_old_top - 0.85 + 0.275))
    arrow(ax, (nx, y_old_top - 0.85 - 0.275), (nx, y_old_top - 1.65 + 0.275))
    arrow(ax, (nx, y_old_top - 1.65 - 0.275), (nx, y_old_top - 2.45 + 0.3))
    arrow(ax, (nx, y_old_top - 2.45 - 0.3), (nx, y_old_top - 3.3 + 0.425))
    arrow(ax, (nx, y_old_top - 3.3 - 0.425), (nx, y_old_top - 4.25 + 0.375))

    ymerge = min(yo, yn) - 0.95
    box(ax, cx, ymerge, 4.6, 0.6, "+ Health & Education Cess (4% of tax)", fs=8.4)
    arrow(ax, (ox, yo - 0.375), (cx - 1.3, ymerge + 0.30), connectionstyle="arc3,rad=0.12")
    arrow(ax, (nx, yn - 0.375), (cx + 1.3, ymerge + 0.30), connectionstyle="arc3,rad=-0.12")

    y2 = ymerge - 0.85
    box(ax, cx, y2, 4.8, 0.6, "− Professional Tax (state-based, monthly)", fs=8.4)
    arrow(ax, (cx, ymerge - 0.3), (cx, y2 + 0.3))

    y3 = y2 - 0.85
    box(ax, cx, y3, 4.4, 0.65, "Net Monthly Take-Home", fc=LIGHT, ec=GREEN, weight="bold", fs=9.6)
    arrow(ax, (cx, y2 - 0.3), (cx, y3 + 0.325))

    for yy0, yy1 in [(h - 0.55 - 0.30, h - 0.85 + 0.30), (h - 0.85 - 0.30, h - 1.7 + 0.30),
                     (h - 1.7 - 0.30, h - 2.55 + 0.30), (h - 2.55 - 0.30, h - 3.4 + 0.30),
                     (h - 3.4 - 0.30, y + 0.525)]:
        arrow(ax, (cx, yy0), (cx, yy1))

    ax.set_ylim(y3 - 0.55, h)
    save(fig, "13_salary_flow")


# =========================================================================== #
#  14 -- LLM FALLBACK CHAIN
# =========================================================================== #
def fig_llm_fallback_chain():
    w, h = 14.0, 5.6
    fig, ax = new_axes(w, h)
    cy = h - 1.7

    steps = [
        ("Local model\ndownloaded &\nllama.cpp available?", "Local model\n(Qwen2.5-1.5B, Q4_K_M)"),
        ("Ollama server\nreachable on\nlocalhost?", "Ollama\n(user-installed model)"),
        ("Gemini API key\nconfigured?", "Google Gemini API"),
    ]
    x = 1.55
    step_w = 2.65
    gap = 0.95
    for cond, used in steps:
        diamond(ax, x, cy, step_w, 1.55, cond, fs=7.6)
        box(ax, x, cy - 1.55, step_w + 0.2, 0.65, used, fc=LIGHT, ec=GREEN, fs=7.8)
        arrow(ax, (x, cy - 0.775), (x, cy - 1.55 + 0.325), text="yes", fs=7.6, dx=0.28)
        x_next = x + step_w / 2 + gap + step_w / 2
        if used != steps[-1][1]:
            arrow(ax, (x + step_w / 2, cy), (x_next - step_w / 2, cy), text="no", fs=7.6, dy=0.20)
        x = x_next

    final_x = x
    box(ax, final_x, cy, step_w + 0.35, 1.35, "Deterministic\nrule-based advisor\n(always available)", fc=LIGHT, ec=GREEN, weight="bold", fs=8.0)
    arrow(ax, (x - step_w - gap - step_w / 2 + step_w / 2, cy), (final_x - (step_w + 0.35) / 2, cy), text="no", fs=7.6, dy=0.20)

    ax.text(w / 2, 0.55, "Every hop has a working fallback beneath it, so the system always produces an answer.",
             fontsize=9.2, color=GREEN, ha="center", weight="bold")
    save(fig, "14_llm_fallback_chain")


# =========================================================================== #
#  15 -- MODULE DEPENDENCY GRAPH
# =========================================================================== #
def fig_module_dependency():
    w, h = 13.0, 6.6
    fig, ax = new_axes(w, h)

    box(ax, w / 2, h - 0.6, 2.4, 0.6, "app.py", fc=BLUE_D, ec=BLUE_D, tc="white", weight="bold", fs=10)

    row2_names = ["parser", "classifier", "analytics", "salary", "nlq", "advisor", "rag"]
    row2_x = row_x(7, 1.1, w - 1.1)
    row2_y = h - 1.6
    row2 = {}
    for name, x in zip(row2_names, row2_x):
        box(ax, x, row2_y, 1.55, 0.6, name + ".py", fs=8.2)
        row2[name] = x

    row3_names = ["models", "config", "llm_local"]
    row3_x = dict(zip(row3_names, row_x(3, 3.0, w - 3.0)))
    row3_y = h - 3.7
    row3 = {}
    for name in row3_names:
        x = row3_x[name]
        box(ax, x, row3_y, 1.75, 0.6, name + ".py", fc=LIGHT, ec=BLUE, fs=8.2)
        row3[name] = x

    for name in row2_names + ["models", "config"]:
        target = row2[name] if name in row2 else row3[name]
        arrow(ax, (w / 2, h - 0.6 - 0.3), (target, row2_y + 0.3 if name in row2 else row3_y + 0.3),
              color=GREY, lw=1.0)

    def cross(a, b, rad=0.0, color=BLUE_D):
        if a in row2 and b in row2:
            arrow(ax, (row2[a], row2_y), (row2[b], row2_y), color=color, lw=1.2, connectionstyle=f"arc3,rad={rad}")
        else:
            arrow(ax, (row2[a], row2_y - 0.3), (row3[b], row3_y + 0.3), color=color, lw=1.2,
                  connectionstyle=f"arc3,rad={rad}")

    cross("rag", "nlq", rad=-0.35, color=GREEN)
    cross("rag", "advisor", rad=-0.35, color=GREEN)
    cross("rag", "models", rad=0.15, color=GREEN)
    cross("advisor", "llm_local", rad=0.15, color=AMBER)
    cross("advisor", "config", rad=-0.2, color=AMBER)
    cross("analytics", "classifier", rad=0.3, color=BLUE_D)
    cross("analytics", "models", rad=0.15, color=BLUE_D)
    cross("nlq", "models", rad=-0.1, color=BLUE_D)
    cross("nlq", "classifier", rad=0.35, color=BLUE_D)

    ax.text(w / 2, 0.30, "grey = imported by app.py directly      coloured = module-to-module imports",
             fontsize=8, color=GREY, ha="center", style="italic")
    save(fig, "15_module_dependency")


# =========================================================================== #
#  16 -- TRANSACTION STATE DIAGRAM
# =========================================================================== #
def fig_transaction_state():
    w, h = 14.5, 6.4
    fig, ax = new_axes(w, h)
    cy = h - 2.1

    start_state(ax, 0.7, cy)
    states = ["Extracted", "Classified", "Stored", "Indexed", "Included in\nAnalytics"]
    xs = row_x(5, 2.3, w - 2.3)
    for x, s in zip(xs, states):
        box(ax, x, cy, 1.9, 0.75, s, fs=8.8)

    arrow(ax, (0.85, cy), (xs[0] - 0.95, cy))
    for i in range(len(xs) - 1):
        lbl = None
        if states[i] == "Classified":
            lbl = "fingerprint\nunique"
        arrow(ax, (xs[i] + 0.95, cy), (xs[i + 1] - 0.95, cy), text=lbl, fs=7.2, dy=0.28)

    end_state(ax, xs[-1] + 1.15, cy)
    arrow(ax, (xs[-1] + 0.95, cy), (xs[-1] + 1.0, cy))

    dup_y = cy - 1.7
    box(ax, xs[1], dup_y, 2.6, 0.65, "Discarded\n(duplicate fingerprint)", fc="#fdeeee", ec=RED, fs=7.8)
    arrow(ax, (xs[1], cy - 0.375), (xs[1], dup_y + 0.325), text="fingerprint already\nseen for this user", fs=6.8, dx=0.9, dy=0.0, color=RED, tc=RED)
    end_state(ax, xs[1], dup_y - 0.55)
    arrow(ax, (xs[1], dup_y - 0.325), (xs[1], dup_y - 0.55 + 0.16), color=RED)

    reclass_y = cy + 1.55
    box(ax, xs[3], reclass_y, 2.6, 0.65, "Re-categorised\n(user override)", fc="#fff8e8", ec=AMBER, fs=8.0)
    arrow(ax, (xs[3], cy + 0.375), (xs[3], reclass_y - 0.325), text="user edits category", fs=6.8, dx=0.0, dy=0.0)
    arrow(ax, (xs[3] + 1.0, reclass_y), (xs[4], cy + 0.375), text="", connectionstyle="arc3,rad=-0.2")

    save(fig, "16_transaction_state")


# =========================================================================== #
#  17 -- CATEGORY TAXONOMY
# =========================================================================== #
def fig_category_taxonomy():
    w, h = 16.4, 9.2
    fig, ax = new_axes(w, h)

    root_y = h - 0.5
    box(ax, w / 2, root_y, 3.4, 0.55, "Transaction Categories", fc=BLUE_D, ec=BLUE_D, tc="white", weight="bold", fs=9.6)

    income_x, expense_x = 2.6, w / 2 + 1.5
    branch_y = root_y - 1.15
    box(ax, income_x, branch_y, 2.4, 0.6, "Income", fc=LIGHT, ec=GREEN, weight="bold", fs=9.6)
    box(ax, expense_x, branch_y, 2.4, 0.6, "Expense", fc=LIGHT, ec=BLUE, weight="bold", fs=9.6)
    arrow(ax, (w / 2 - 1.0, root_y - 0.275), (income_x, branch_y + 0.30), connectionstyle="arc3,rad=0.2")
    arrow(ax, (w / 2 + 1.0, root_y - 0.275), (expense_x, branch_y + 0.30), connectionstyle="arc3,rad=-0.2")

    note(ax, income_x, branch_y - 1.0, "Salary · Interest\nRefund · Cashback", fs=7.6, ha="center")
    arrow(ax, (income_x, branch_y - 0.30), (income_x, branch_y - 0.65), color=GREY)

    expense_cats = ["Rent", "EMI / Loans", "Insurance", "Investments", "Subscriptions",
                     "Food & Dining", "Groceries", "Transport", "Utilities", "Shopping",
                     "Health", "Education", "Entertainment", "Travel", "Transfers", "Others"]
    examples = {
        "Food & Dining": "Swiggy, Zomato",
        "Groceries": "BigBasket, DMart, Zepto",
        "Transport": "Uber, Ola, IRCTC",
        "Utilities": "Airtel, TNEB, Jio",
        "Shopping": "Amazon, Flipkart, Myntra",
        "Subscriptions": "Netflix, Spotify, Hotstar",
    }

    row1 = expense_cats[:8]
    row2 = expense_cats[8:]
    y_row1 = branch_y - 1.55
    y_row2 = branch_y - 3.05
    x_row1 = row_x(8, 1.0, w - 1.0)
    x_row2 = row_x(8, 1.0, w - 1.0)

    bus_y = branch_y - 0.55
    ax.plot([expense_x, expense_x], [branch_y - 0.30, bus_y], color=GREY, lw=0.9, zorder=2)
    ax.plot([x_row1[0], x_row1[-1]], [bus_y, bus_y], color=GREY, lw=0.9, zorder=2)
    for x, cat in zip(x_row1, row1):
        box(ax, x, y_row1, 1.85, 0.55, cat, fs=7.8)
        arrow(ax, (x, bus_y), (x, y_row1 + 0.275), color=GREY, lw=0.9)
        if cat in examples:
            note(ax, x, y_row1 - 0.45, examples[cat], fs=6.6, ha="center")

    for x, cat in zip(x_row2, row2):
        box(ax, x, y_row2, 1.85, 0.55, cat, fs=7.8)
        arrow(ax, (x, y_row1 - 0.275), (x, y_row2 + 0.275), color=GREY, lw=0.9)
        if cat in examples:
            note(ax, x, y_row2 - 0.45, examples[cat], fs=6.6, ha="center")

    save(fig, "17_category_taxonomy")


# =========================================================================== #
#  18 -- ACTIVITY DIAGRAM: USER JOURNEY
# =========================================================================== #
def fig_activity_user_journey():
    w, h = 12.6, 15.2
    fig, ax = new_axes(w, h)
    cx = w / 2

    y = h - 0.4
    start_state(ax, cx, y)
    y -= 0.55
    box(ax, cx, y, 2.6, 0.55, "Register", fs=9)
    y -= 0.85
    box(ax, cx, y, 2.6, 0.55, "Login", fs=9)
    y -= 0.75

    fork_y = y
    fork_bar(ax, cx, fork_y, 6.2)
    arrow(ax, (cx, y + 0.75 - 0.275), (cx, fork_y + 0.05))

    lx, rx = cx - 3.0, cx + 3.0
    ya = fork_y - 0.75
    box(ax, lx, ya, 3.0, 0.65, "Upload Statement\n(PDF / CSV / XLSX)", fs=8.2)
    box(ax, rx, ya, 3.0, 0.65, "Set Salary Profile", fs=8.6)
    arrow(ax, (lx, fork_y - 0.05), (lx, ya + 0.325))
    arrow(ax, (rx, fork_y - 0.05), (rx, ya + 0.325))

    ya2 = ya - 0.9
    box(ax, lx, ya2, 3.0, 0.65, "Parsed & auto-\ncategorised", fs=8.2)
    box(ax, rx, ya2, 3.0, 0.65, "Take-home\ncomputed", fs=8.6)
    arrow(ax, (lx, ya - 0.325), (lx, ya2 + 0.325))
    arrow(ax, (rx, ya - 0.325), (rx, ya2 + 0.325))

    join_y = ya2 - 0.75
    fork_bar(ax, cx, join_y, 6.2)
    arrow(ax, (lx, ya2 - 0.325), (lx, join_y + 0.05))
    arrow(ax, (rx, ya2 - 0.325), (rx, join_y + 0.05))

    y = join_y - 0.75
    box(ax, cx, y, 3.4, 0.6, "View Dashboard\n(now meaningful)", fc=LIGHT, ec=BLUE, weight="bold", fs=8.8)
    arrow(ax, (cx, join_y - 0.05), (cx, y + 0.30))

    y -= 0.9
    box(ax, cx, y, 3.2, 0.55, "Set Budget & Goals", fs=8.8)
    arrow(ax, (cx, y + 0.9 - 0.30), (cx, y + 0.275))
    y -= 0.85
    box(ax, cx, y, 3.0, 0.55, "Track Trends &\nExplore Insights", fs=8.2)
    arrow(ax, (cx, y + 0.85 - 0.275), (cx, y + 0.275))
    y -= 0.85
    box(ax, cx, y, 2.8, 0.55, "Ask Chatbot", fs=9)
    arrow(ax, (cx, y + 0.85 - 0.275), (cx, y + 0.275))
    y -= 0.85
    box(ax, cx, y, 3.2, 0.55, "Get Savings Advice", fs=8.8)
    arrow(ax, (cx, y + 0.85 - 0.275), (cx, y + 0.275))
    y -= 0.85
    box(ax, cx, y, 3.6, 0.6, "Act on Advice\n(adjust spending / update goal)", fc=LIGHT, ec=GREEN, weight="bold", fs=8.2)
    arrow(ax, (cx, y + 0.85 - 0.30), (cx, y + 0.30))
    y -= 0.85
    end_state(ax, cx, y)
    arrow(ax, (cx, y + 0.85 - 0.30), (cx, y + 0.18))

    ax.set_ylim(y - 0.4, h)
    save(fig, "18_activity_user_journey")


if __name__ == "__main__":
    fig_system_architecture()
    fig_use_case()
    fig_class_diagram()
    fig_er_diagram()
    fig_sequence_upload()
    fig_sequence_chat_rag()
    fig_data_flow()
    fig_component_diagram()
    fig_deployment_diagram()
    fig_parser_pipeline()
    fig_classifier_flow()
    fig_rag_pipeline()
    fig_salary_flow()
    fig_llm_fallback_chain()
    fig_module_dependency()
    fig_transaction_state()
    fig_category_taxonomy()
    fig_activity_user_journey()
    print("ALL DIAGRAMS DONE")
