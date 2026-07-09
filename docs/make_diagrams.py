"""Generate the SmartEdit AI logo and all project diagrams (blue/white theme)."""
import os
from graphviz import Digraph, Graph
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = os.path.join(os.path.dirname(__file__), "diagrams")
os.makedirs(OUT, exist_ok=True)

BLUE = "#1a73e8"; BLUE_D = "#1457b8"; LIGHT = "#e8f0fe"
INK = "#1f2733"; GREY = "#6b7787"; GREEN = "#1aa260"; WHITE = "#ffffff"


def save_gv(g, name):
    g.render(os.path.join(OUT, name), format="png", cleanup=True)
    print("saved", name)


# --------------------------------------------------------------------------- #
# 0. LOGO
# --------------------------------------------------------------------------- #
def logo():
    fig, ax = plt.subplots(figsize=(7, 2.4), dpi=200)
    ax.set_xlim(0, 10); ax.set_ylim(0, 3.4); ax.axis("off")
    fig.patch.set_facecolor("white")
    # rounded square mark
    ax.add_patch(FancyBboxPatch((0.3, 0.7), 2.0, 2.0, boxstyle="round,pad=0.02,rounding_size=0.35",
                                fc=BLUE, ec="none"))
    # upward bars (finance growth) inside mark
    for i, h in enumerate([0.5, 0.85, 1.2]):
        ax.add_patch(plt.Rectangle((0.65 + i*0.45, 1.05), 0.3, h, fc="white"))
    ax.text(2.65, 1.95, "SmartEdit AI", fontsize=34, fontweight="bold", color=BLUE_D, va="center")
    ax.text(2.68, 1.05, "Intelligent Personal Finance", fontsize=14, color=GREY, va="center")
    plt.savefig(os.path.join(OUT, "logo.png"), bbox_inches="tight", facecolor="white")
    plt.close()
    # icon-only version
    fig, ax = plt.subplots(figsize=(2.4, 2.4), dpi=200)
    ax.set_xlim(0, 3); ax.set_ylim(0, 3); ax.axis("off"); fig.patch.set_facecolor("white")
    ax.add_patch(FancyBboxPatch((0.3, 0.3), 2.4, 2.4, boxstyle="round,pad=0.02,rounding_size=0.45", fc=BLUE, ec="none"))
    for i, h in enumerate([0.6, 1.05, 1.5]):
        ax.add_patch(plt.Rectangle((0.75 + i*0.55, 0.75), 0.35, h, fc="white"))
    plt.savefig(os.path.join(OUT, "logo_icon.png"), bbox_inches="tight", facecolor="white")
    plt.close()
    print("saved logo.png, logo_icon.png")


# --------------------------------------------------------------------------- #
# 1. SYSTEM ARCHITECTURE
# --------------------------------------------------------------------------- #
def architecture():
    g = Digraph("arch")
    g.attr(rankdir="TB", bgcolor="white", fontname="Helvetica", splines="ortho")
    g.attr("node", fontname="Helvetica", fontsize="11")
    g.attr("edge", color=GREY, fontname="Helvetica", fontsize="9")

    with g.subgraph(name="cluster_client") as c:
        c.attr(label="Client (Browser)", style="rounded,filled", fillcolor=LIGHT, color=BLUE, fontcolor=BLUE_D)
        c.node("ui", "White/Blue Web UI\nLogin · Dashboard · Add · View · Tracker · Chat",
               shape="box", style="filled,rounded", fillcolor="white", color=BLUE)

    with g.subgraph(name="cluster_app") as c:
        c.attr(label="Flask Application Server", style="rounded,filled", fillcolor="#f4f8ff", color=BLUE, fontcolor=BLUE_D)
        for nid, lbl in [("auth","1 · Auth & Session"),("parse","2 · Statement Parser\n(pdfplumber / pandas)"),
                         ("clf","3 · Transaction Classifier\n(India-aware rules)"),
                         ("ana","4 · Analytics Engine"),("adv","5 · AI Advisory\n(LLM Provider)"),
                         ("rag","6 · RAG Chatbot\n(embeddings + cosine)")]:
            c.node(nid, lbl, shape="box", style="filled,rounded", fillcolor="white", color=BLUE_D)

    with g.subgraph(name="cluster_ext") as c:
        c.attr(label="AI Provider (swappable)", style="rounded,dashed", color=GREEN, fontcolor=GREEN)
        c.node("llm", "Gemini API  →  Ollama (local)\n+ offline fallback", shape="box",
               style="filled,rounded", fillcolor="#eafaf0", color=GREEN)

    g.node("db", "SQLite Database\nusers · transactions · embeddings · chat_history",
           shape="cylinder", style="filled", fillcolor=LIGHT, color=BLUE_D)

    g.edge("ui", "auth", label="HTTPS")
    for n in ["parse","clf","ana","adv","rag"]:
        g.edge("ui", n, style="invis")
    g.edge("parse", "clf"); g.edge("clf", "db"); g.edge("ana", "db")
    g.edge("auth", "db"); g.edge("adv", "llm"); g.edge("rag", "llm")
    g.edge("rag", "db"); g.edge("adv", "ana", dir="back")
    save_gv(g, "01_system_architecture")


# --------------------------------------------------------------------------- #
# 2. USE CASE
# --------------------------------------------------------------------------- #
def use_case():
    g = Digraph("usecase")
    g.attr(rankdir="LR", bgcolor="white", fontname="Helvetica")
    g.attr("edge", color=GREY)
    g.node("user", "User\n(Salaried Individual)", shape="box", style="filled,rounded",
           fillcolor=LIGHT, color=BLUE_D, fontname="Helvetica")
    g.node("ai", "AI Provider", shape="box", style="filled,rounded", fillcolor="#eafaf0", color=GREEN)
    cases = [("uc1","Register / Login"),("uc2","Upload Statement\n(PDF/CSV)"),
             ("uc3","Add Manual Entry"),("uc4","Auto-Categorise\nTransactions"),
             ("uc5","View Dashboard\n& Summary"),("uc6","Filter / Edit\nTransactions"),
             ("uc7","Track Trends\n(daily/monthly)"),("uc8","Get AI Savings\nAdvisory"),
             ("uc9","Chat with AI\n(RAG)")]
    with g.subgraph(name="cluster_sys") as c:
        c.attr(label="SmartEdit AI System", style="rounded,filled", fillcolor="#f7faff", color=BLUE, fontcolor=BLUE_D)
        for nid, lbl in cases:
            c.node(nid, lbl, shape="ellipse", style="filled", fillcolor="white", color=BLUE, fontname="Helvetica", fontsize="10")
    for nid, _ in cases:
        g.edge("user", nid)
    g.edge("uc4", "ai", style="dashed", label="classify/advise")
    g.edge("uc8", "ai", style="dashed")
    g.edge("uc9", "ai", style="dashed")
    save_gv(g, "02_use_case")


# --------------------------------------------------------------------------- #
# 3. CLASS DIAGRAM
# --------------------------------------------------------------------------- #
def class_diagram():
    g = Digraph("class")
    g.attr(bgcolor="white", fontname="Helvetica", rankdir="TB")
    g.attr("node", shape="record", style="filled", fillcolor="white", color=BLUE_D, fontname="Helvetica", fontsize="10")

    g.node("User", "{User|+ id: int\\l+ name: str\\l+ email: str\\l+ password_hash: str\\l+ created_at: datetime\\l|+ check_password()\\l}")
    g.node("Transaction", "{Transaction|+ id: int\\l+ user_id: FK\\l+ date: date\\l+ description: str\\l+ raw_description: str\\l+ amount: float\\l+ txn_type: credit/debit\\l+ category: str\\l+ method: str\\l+ source: str\\l|+ to_dict()\\l}")
    g.node("Embedding", "{Embedding|+ id: int\\l+ transaction_id: FK\\l+ vector: JSON[float]\\l}")
    g.node("ChatHistory", "{ChatHistory|+ id: int\\l+ user_id: FK\\l+ role: str\\l+ message: text\\l+ created_at: datetime\\l}")
    g.node("Classifier", "{Classifier «service»|+ CATEGORY_RULES\\l|+ classify(desc, type)\\l+ detect_method(desc)\\l+ clean_description(raw)\\l}")
    g.node("Parser", "{StatementParser «service»||+ parse_statement(file)\\l+ parse_pdf()\\l+ parse_csv()\\l}")
    g.node("Advisor", "{Advisor «service»||+ generate_advice(summary)\\l+ llm_generate(prompt)\\l+ rule_based_advice()\\l}")
    g.node("RAG", "{RAGChatbot «service»||+ embed_text(t)\\l+ retrieve(q)\\l+ answer(q)\\l+ cosine()\\l}")

    g.attr("edge", color=BLUE_D, fontname="Helvetica", fontsize="9", arrowhead="vee")
    g.edge("User", "Transaction", label="1..*", arrowhead="diamond", dir="back")
    g.edge("User", "ChatHistory", label="1..*", arrowhead="diamond", dir="back")
    g.edge("Transaction", "Embedding", label="1..1", arrowhead="diamond", dir="back")
    g.edge("Parser", "Classifier", style="dashed", label="uses")
    g.edge("Classifier", "Transaction", style="dashed", label="creates")
    g.edge("RAG", "Embedding", style="dashed", label="reads")
    g.edge("Advisor", "Transaction", style="dashed", label="reads")
    save_gv(g, "03_class_diagram")


# --------------------------------------------------------------------------- #
# 4. ER / DB SCHEMA
# --------------------------------------------------------------------------- #
def er_diagram():
    g = Digraph("er")
    g.attr(bgcolor="white", fontname="Helvetica", rankdir="LR")
    g.attr("node", shape="plaintext", fontname="Helvetica")

    def tbl(name, rows):
        body = f'<tr><td bgcolor="{BLUE}" align="center"><font color="white"><b>{name}</b></font></td></tr>'
        for r in rows:
            body += f'<tr><td align="left">{r}</td></tr>'
        return f'<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">{body}</table>>'

    g.node("users", tbl("users", ["🔑 id (PK)","name","email (unique)","password_hash","created_at"]))
    g.node("transactions", tbl("transactions", ["🔑 id (PK)","🔗 user_id (FK)","date","description","raw_description","amount","txn_type","category","method","source","created_at"]))
    g.node("embeddings", tbl("embeddings", ["🔑 id (PK)","🔗 transaction_id (FK)","vector (JSON)"]))
    g.node("chat_history", tbl("chat_history", ["🔑 id (PK)","🔗 user_id (FK)","role","message","created_at"]))

    g.attr("edge", color=BLUE_D, fontname="Helvetica", fontsize="9")
    g.edge("users", "transactions", label="1 : N")
    g.edge("transactions", "embeddings", label="1 : 1")
    g.edge("users", "chat_history", label="1 : N")
    save_gv(g, "04_er_diagram")


# --------------------------------------------------------------------------- #
# 5. SEQUENCE — UPLOAD
# --------------------------------------------------------------------------- #
def seq_upload():
    _sequence(
        "05_sequence_upload",
        ["User", "Web UI", "Flask", "Parser", "Classifier", "Database"],
        [("User","Web UI","Upload statement (PDF/CSV)"),
         ("Web UI","Flask","POST /upload"),
         ("Flask","Parser","parse_statement(file)"),
         ("Parser","Flask","raw transactions[]"),
         ("Flask","Classifier","classify(desc) for each"),
         ("Classifier","Flask","category + method"),
         ("Flask","Database","INSERT transactions + embeddings"),
         ("Database","Flask","ok"),
         ("Flask","Web UI","redirect → View (N imported)"),
         ("Web UI","User","Show categorised table")])


# --------------------------------------------------------------------------- #
# 6. SEQUENCE — CHAT / RAG
# --------------------------------------------------------------------------- #
def seq_chat():
    _sequence(
        "06_sequence_chat_rag",
        ["User", "Web UI", "Flask", "RAG", "Database", "LLM"],
        [("User","Web UI","Ask question"),
         ("Web UI","Flask","POST /chat/send"),
         ("Flask","RAG","answer(question)"),
         ("RAG","RAG","embed query"),
         ("RAG","Database","fetch txn embeddings + SQL aggregates"),
         ("Database","RAG","vectors + exact totals"),
         ("RAG","RAG","cosine similarity → top-K"),
         ("RAG","LLM","prompt + retrieved context"),
         ("LLM","RAG","grounded answer"),
         ("RAG","Flask","reply"),
         ("Flask","Web UI","JSON reply"),
         ("Web UI","User","Show answer")])


def _sequence(name, actors, messages):
    fig, ax = plt.subplots(figsize=(12, 0.6 * len(messages) + 2), dpi=150)
    ax.axis("off")
    n = len(actors)
    xs = {a: i * (10.0 / (n - 1)) for i, a in enumerate(actors)}
    top = len(messages) + 1
    for a in actors:
        ax.add_patch(FancyBboxPatch((xs[a]-0.85, top+0.2), 1.7, 0.6,
                     boxstyle="round,pad=0.05", fc=BLUE, ec="none"))
        ax.text(xs[a], top+0.5, a, ha="center", va="center", color="white", fontsize=10, fontweight="bold")
        ax.plot([xs[a], xs[a]], [0.2, top+0.1], color=GREY, lw=1, ls=(0,(4,3)))
    for i, (src, dst, msg) in enumerate(messages):
        y = top - 0.6 - i * 0.8
        x1, x2 = xs[src], xs[dst]
        if x1 == x2:
            ax.annotate("", xy=(x1+0.9, y-0.12), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="->", color=BLUE_D, connectionstyle="arc3,rad=-1.4"))
            ax.text(x1+0.15, y+0.12, msg, fontsize=8.5, color=INK)
        else:
            ax.annotate("", xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="->", color=BLUE_D, lw=1.3))
            ax.text((x1+x2)/2, y+0.1, msg, ha="center", fontsize=8.5, color=INK)
    ax.set_xlim(-1.3, 11.3); ax.set_ylim(0, top+1.2)
    plt.savefig(os.path.join(OUT, name + ".png"), bbox_inches="tight", facecolor="white")
    plt.close(); print("saved", name)


# --------------------------------------------------------------------------- #
# 7. DATA FLOW (DFD)
# --------------------------------------------------------------------------- #
def dfd():
    g = Digraph("dfd")
    g.attr(rankdir="LR", bgcolor="white", fontname="Helvetica", splines="spline")
    g.attr("node", fontname="Helvetica", fontsize="10")
    g.node("u", "User", shape="box", style="filled", fillcolor=LIGHT, color=BLUE_D)
    for nid, lbl in [("p1","1.0\nParse Statement"),("p2","2.0\nClassify Txn"),
                     ("p3","3.0\nCompute Analytics"),("p4","4.0\nGenerate Advisory"),
                     ("p5","5.0\nRAG Answer")]:
        g.node(nid, lbl, shape="circle", style="filled", fillcolor=BLUE, fontcolor="white", width="1.1")
    g.node("d1", "D1 | transactions", shape="box", style="filled", fillcolor="white", color=BLUE_D)
    g.node("d2", "D2 | embeddings", shape="box", style="filled", fillcolor="white", color=BLUE_D)
    g.attr("edge", color=GREY, fontname="Helvetica", fontsize="9")
    g.edge("u","p1","PDF/CSV"); g.edge("p1","p2","raw txns")
    g.edge("p2","d1","categorised"); g.edge("p2","d2","vectors")
    g.edge("d1","p3"); g.edge("p3","p4","summary"); g.edge("p4","u","savings advice")
    g.edge("u","p5","question"); g.edge("d2","p5","cosine search"); g.edge("d1","p5","aggregates")
    g.edge("p5","u","grounded answer")
    save_gv(g, "07_data_flow")


# --------------------------------------------------------------------------- #
# 8. COMPONENT DIAGRAM
# --------------------------------------------------------------------------- #
def component():
    g = Digraph("component")
    g.attr(rankdir="TB", bgcolor="white", fontname="Helvetica")
    g.attr("node", shape="component", style="filled", fillcolor="white", color=BLUE_D, fontname="Helvetica", fontsize="10")
    with g.subgraph(name="cluster_fe") as c:
        c.attr(label="Frontend (Templates + CSS + Chart.js)", style="rounded,filled", fillcolor=LIGHT, color=BLUE, fontcolor=BLUE_D)
        c.node("tpl", "Jinja Templates")
        c.node("css", "White/Blue Theme")
    with g.subgraph(name="cluster_be") as c:
        c.attr(label="Backend (Flask)", style="rounded,filled", fillcolor="#f4f8ff", color=BLUE, fontcolor=BLUE_D)
        for nid, lbl in [("app","app.py (routes)"),("models","models.py (ORM)"),
                         ("parser","parser.py"),("clf","classifier.py"),
                         ("adv","advisor.py"),("rag","rag.py")]:
            c.node(nid, lbl)
    g.node("db", "SQLite", shape="cylinder", fillcolor=LIGHT, color=BLUE_D, style="filled")
    g.node("llm", "Gemini / Ollama", shape="box", style="filled,rounded", fillcolor="#eafaf0", color=GREEN)
    g.attr("edge", color=GREY)
    g.edge("tpl","app"); g.edge("app","models"); g.edge("app","parser")
    g.edge("app","clf"); g.edge("app","adv"); g.edge("app","rag")
    g.edge("models","db"); g.edge("adv","llm"); g.edge("rag","llm")
    save_gv(g, "08_component_diagram")


if __name__ == "__main__":
    logo(); architecture(); use_case(); class_diagram(); er_diagram()
    seq_upload(); seq_chat(); dfd(); component()
    print("ALL DIAGRAMS DONE")
