// SmartEdit AI — Final-Semester Dissertation Report (BITS WILP format)
// Extends the mid-semester report's visual pattern (title page, palette, table
// style, signature block) into a full final-semester dissertation.
const fs = require("fs");
const path = require("path");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
        Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
        WidthType, ShadingType, PageNumber, PageBreak, TableOfContents, TabStopType,
        TabStopPosition } = require("docx");

const DIR = process.env.DIAGRAMS || path.join(__dirname, "diagrams");
const OUT = process.env.OUTFILE || path.join(__dirname, "SmartEditAI_Final_Report.docx");
const BLUE = "1A73E8", BLUED = "1457B8", INK = "1F2733", GREY = "6B7787";
const NOBORDER = { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
                   left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } };

// ---------- Helpers (same pattern as the mid-semester report generator) ----------
const c = (text, o = {}) => new TextRun({ text, size: o.size || 24, bold: o.bold, italics: o.italics,
  color: o.color || INK, font: o.font, allCaps: o.allCaps });
const center = (runs, o = {}) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: o.after ?? 80, before: o.before ?? 0 }, children: Array.isArray(runs) ? runs : [runs] });
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const h3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(t)] });
const para = (t) => new Paragraph({ spacing: { after: 140 }, alignment: AlignmentType.JUSTIFIED, children: [new TextRun({ text: t, size: 22 })] });
const bullet = (t) => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 70 }, alignment: AlignmentType.JUSTIFIED, children: [new TextRun({ text: t, size: 22 })] });
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });

const img = (file, w, h) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 160, after: 40 },
  children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(DIR, file)),
    transformation: { width: w, height: h }, altText: { title: file, description: file, name: file } })] });
const caption = (t) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: t, italics: true, size: 18, color: GREY, bold: true })] });

function table(headers, rows, widths) {
  const total = widths.reduce((a, b) => a + b, 0);
  const border = { style: BorderStyle.SINGLE, size: 1, color: "999999" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const head = new TableRow({ tableHeader: true, children: headers.map((htext, i) =>
    new TableCell({ borders, width: { size: widths[i], type: WidthType.DXA }, shading: { fill: BLUED, type: ShadingType.CLEAR },
      margins: { top: 60, bottom: 60, left: 110, right: 110 }, children: [new Paragraph({ children: [new TextRun({ text: htext, bold: true, color: "FFFFFF", size: 20 })] })] })) });
  const rws = rows.map((r, ri) => new TableRow({ children: r.map((cell, i) =>
    new TableCell({ borders, width: { size: widths[i], type: WidthType.DXA }, shading: { fill: ri % 2 ? "F2F6FC" : "FFFFFF", type: ShadingType.CLEAR },
      margins: { top: 60, bottom: 60, left: 110, right: 110 }, children: [new Paragraph({ children: [new TextRun({ text: cell, size: 20 })] })] })) }));
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, rows: [head, ...rws] });
}

// ---------- Title page (used twice, per BITS sample) ----------
function titlePage() {
  return [
    center(new ImageRun({ type: "png", data: fs.readFileSync(path.join(DIR, "bits_logo.png")),
      transformation: { width: 110, height: 107 }, altText: { title: "BITS", description: "BITS logo", name: "BITS" } }), { before: 240, after: 200 }),
    center(c("SMARTEDIT AI – AN INTELLIGENT PERSONAL FINANCE WEB APPLICATION FOR INDIAN SALARIED USERS", { bold: true, size: 28, color: INK }), { after: 220 }),
    center(c("BITS ZG628T: Dissertation", { size: 24, bold: true }), { after: 200 }),
    center(c("by", { size: 22 }), { after: 60 }),
    center(c("Shyam Sundar", { size: 24, bold: true }), { after: 40 }),
    center(c("(Insert Student ID Number)", { size: 22 }), { after: 160 }),
    center(c("Dissertation work carried out at", { size: 22 }), { after: 40 }),
    center(c("(Insert Organization Name, Location Name)", { size: 22 }), { after: 160 }),
    center(c("Submitted in partial fulfilment of (Insert Programme Name)", { size: 22 }), { after: 30 }),
    center(c("degree programme", { size: 22 }), { after: 160 }),
    center(c("Under the Supervision of", { size: 22 }), { after: 40 }),
    center(c("(Insert Supervisor Name)", { size: 22, bold: true }), { after: 30 }),
    center(c("(Insert Organization Name, Location Name)", { size: 22 }), { after: 220 }),
    center(c("BIRLA INSTITUTE OF TECHNOLOGY & SCIENCE", { size: 24, bold: true }), { after: 30 }),
    center(c("PILANI (RAJASTHAN)", { size: 24, bold: true }), { after: 30 }),
    center(c("December 2026", { size: 22 }), { after: 0 }),
  ];
}

// ---------- Abstract signature block ----------
function sigBlock() {
  const cell = (lines) => new TableCell({ borders: NOBORDER, width: { size: 4680, type: WidthType.DXA },
    margins: { top: 80, bottom: 40, left: 60, right: 60 },
    children: lines.map(l => new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: l, size: 22 })] })) });
  return new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: [4680, 4680],
    rows: [new TableRow({ children: [
      cell(["Signature of the Student", "Name: Shyam Sundar", "Date:", "Place:"]),
      cell(["Signature of the Supervisor", "Name: (Insert Supervisor Name)", "Date:", "Place:"]),
    ] })] });
}

function tocLine(text, page, bold) {
  return new Paragraph({ spacing: { after: 60 }, tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX, leader: "dot" }],
    children: [new TextRun({ text, size: 22, bold }), new TextRun({ text: "\t" + page, size: 22, bold })] });
}

// ========================================================= Build document
const children = [];

// ---- Title pages (two identical) ----
titlePage().forEach(p => children.push(p));
children.push(pageBreak());
titlePage().forEach(p => children.push(p));
children.push(pageBreak());

// ---- Abstract ----
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "ABSTRACT", bold: true, size: 28, color: INK })] }));
[
 "SmartEdit AI is an intelligent, privacy-first personal finance web application built for Indian salaried users. It reads a user's bank statement — uploaded as a CSV, XLSX or PDF, in whichever layout SBI, HDFC, ICICI, Axis or any of seven other Indian banks happen to issue it in — extracts every transaction, classifies cryptic narrations such as UPI-SWIGGY-OKAXIS-XXXX1234 or NACH-LIC PREMIUM-AUTODEBIT into one of seventeen expense categories, and presents a dashboard of income, expenses, savings, category-wise spending and recurring commitments. Beyond analytics, the system models the Indian salary structure end to end — basic, HRA, provident fund, gratuity — and computes income tax exactly under both the new and the old regime, including the Section 87A rebate and the marginal-relief band that most consumer tools omit. A natural-language query engine and a retrieval-augmented chatbot let the user ask plain questions about their own spending and receive answers grounded in real SQL aggregates, phrased with the help of a language model that runs entirely on the user's own machine.",
 "The final build closes the three gaps identified at the mid-semester stage: it replaces the mid-semester rule-only classifier with a hybrid rule-first, machine-learning-assisted classifier; it replaces the cloud-hosted advisory model with a fully local, quantised language model running through llama.cpp, so that no transaction narration has to leave the user's machine in the default configuration; and it adds a dedicated grounding-and-safety layer that prevents the language model from ever being the source of a rupee figure. That layer was added because of an observed failure during development — asked to divide a total by a transaction count, the on-device model attempted the arithmetic itself and produced LaTeX notation instead of an answer. The system now computes every number deterministically through SQLAlchemy aggregates and permits the model only to reword an already-finished sentence, discarding its output if it violates any of five explicit guard conditions.",
 "The application is implemented in Flask with SQLAlchemy over SQLite, pdfplumber and pandas for statement extraction, a TF-IDF character n-gram classifier layered under an India-aware rule engine, sentence-transformers for embedding-based retrieval, and Qwen2.5-1.5B-Instruct quantised to Q4_K_M running through llama-cpp-python for on-device generation. The system is validated by 172 automated tests covering the parser, the classifier, the salary and tax engine, the analytics module, the chatbot's grounding guarantees and every application route, together with a live end-to-end run on the finished build. This report documents the requirements, architecture, database design, the statement-parsing and classification methodology, the salary and tax model with a worked numerical example, the natural-language query engine, the on-device inference and retrieval pipeline, the grounding-and-safety design that is the centrepiece of the project, the implementation, the testing evidence including two defects the live run exposed and how they were fixed, deployment, results, and the limitations that remain.",
].forEach(t => children.push(para(t)));
children.push(new Paragraph({ spacing: { before: 200 }, children: [new TextRun("")] }));
children.push(sigBlock());
children.push(pageBreak());

// ---- Acknowledgements ----
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "ACKNOWLEDGEMENTS", bold: true, size: 28, color: INK })] }));
[
 "I would like to express my sincere gratitude to my supervisor, (Insert Supervisor Name), for the guidance, feedback and patience extended throughout the course of this dissertation. The direction offered at each review helped shape both the scope and the rigour of the final system.",
 "I am grateful to the faculty of the Work Integrated Learning Programmes division of BITS Pilani for the structure and academic support that made a project of this depth possible alongside full-time employment, and to (Insert Organization Name) for the time and resources made available during the dissertation period.",
 "Finally, I thank my family and colleagues for their encouragement and understanding during the many evenings and weekends this project required.",
].forEach(t => children.push(para(t)));
children.push(pageBreak());

// ---- Contents ----
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [new TextRun({ text: "CONTENTS", bold: true, size: 28, color: INK })] }));
children.push(new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-2" }));
children.push(pageBreak());

// ---- List of Figures ----
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [new TextRun({ text: "LIST OF FIGURES", bold: true, size: 28, color: INK })] }));
const FIGURES = [
  "Figure 1: System Architecture of SmartEdit AI",
  "Figure 2: Use-Case Diagram",
  "Figure 3: Class Diagram",
  "Figure 4: Entity-Relationship Diagram",
  "Figure 5: Sequence Diagram — Statement Upload",
  "Figure 6: Sequence Diagram — Chatbot Query",
  "Figure 7: Data-Flow Diagram",
  "Figure 8: Component Diagram",
  "Figure 9: Deployment Diagram",
  "Figure 10: Statement Parser Pipeline",
  "Figure 11: Transaction Classifier Flow",
  "Figure 12: Retrieval-Augmented Generation Pipeline",
  "Figure 13: Salary and Tax Computation Flow",
  "Figure 14: LLM Provider Fallback Chain",
  "Figure 15: Module Dependency Diagram",
  "Figure 16: Transaction State Diagram",
  "Figure 17: Category Taxonomy",
  "Figure 18: Activity Diagram — User Journey",
];
FIGURES.forEach(t => children.push(tocLine(t, "")));
children.push(pageBreak());

// ---- List of Tables ----
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [new TextRun({ text: "LIST OF TABLES", bold: true, size: 28, color: INK })] }));
const TABLES = [
  "Table 1: Functional and Non-Functional Requirements",
  "Table 2: Module Responsibilities",
  "Table 3: Database Tables Overview",
  "Table 4: The transactions Table — Columns",
  "Table 5: Measured Parser Results per Sample File",
  "Table 6: Transaction Categories",
  "Table 7: Worked Example — New Regime (CTC Rs.18,00,000)",
  "Table 8: Old-Regime Comparison for the Same Profile",
  "Table 9: Marginal-Relief Evidence",
  "Table 10: Test Modules and What Each Protects",
  "Table 11: Requirements Traceability — Chapter 3 to Test Modules",
  "Table 12: Category Taxonomy with Example Merchants",
  "Table 13: Test Inventory",
  "Table 14: Settings Reference",
];
TABLES.forEach(t => children.push(tocLine(t, "")));
children.push(pageBreak());

// ---- List of Abbreviations ----
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [new TextRun({ text: "LIST OF ABBREVIATIONS", bold: true, size: 28, color: INK })] }));
children.push(table(["Abbreviation", "Expansion"],
  [["ACH", "Automated Clearing House"], ["AI", "Artificial Intelligence"],
   ["API", "Application Programming Interface"], ["ATM-CW", "Automated Teller Machine — Cash Withdrawal"],
   ["CHQ", "Cheque"], ["CPU", "Central Processing Unit"],
   ["CSV", "Comma-Separated Values"], ["CTC", "Cost To Company"],
   ["ECS", "Electronic Clearing Service"], ["EMI", "Equated Monthly Instalment"],
   ["EPFO", "Employees' Provident Fund Organisation"], ["GGUF", "GPT-Generated Unified Format"],
   ["HRA", "House Rent Allowance"], ["IMPS", "Immediate Payment Service"],
   ["INB", "Internet Banking"], ["LLM", "Large Language Model"],
   ["MB", "Mobile Banking"], ["NACH", "National Automated Clearing House"],
   ["NEFT", "National Electronic Funds Transfer"], ["NLQ", "Natural-Language Query"],
   ["ORM", "Object-Relational Mapping"], ["PDF", "Portable Document Format"],
   ["PF", "Provident Fund"], ["POS", "Point Of Sale"],
   ["RAG", "Retrieval-Augmented Generation"], ["RAM", "Random-Access Memory"],
   ["RTGS", "Real-Time Gross Settlement"], ["SHA-1", "Secure Hash Algorithm 1"],
   ["SIP", "Systematic Investment Plan"], ["SQL", "Structured Query Language"],
   ["TDS", "Tax Deducted at Source"], ["TF-IDF", "Term Frequency – Inverse Document Frequency"],
   ["UPI", "Unified Payments Interface"], ["XLSX", "Excel Open XML Spreadsheet"]],
  [2800, 6560]));
children.push(pageBreak());

// ===================================================================
// CHAPTER 1 — INTRODUCTION
// ===================================================================
children.push(h1("1. INTRODUCTION"));
children.push(h2("1.1 The Problem"));
[
 "Almost every salaried person, at the end of the month, opens a bank statement and cannot say with confidence where the money went. The rent is remembered, and perhaps a few large purchases, but the rest — food delivery, impulse UPI transfers, forgotten subscriptions, small cash withdrawals — is a blur of eighty or more rows that, individually, communicate almost nothing. A row that reads UPI-SWIGGY-OKAXIS-XXXX1234 tells the reader that money moved, and little else without effort.",
 "The difficulty is compounded because Indian bank statements are not standardised. SBI, HDFC, ICICI and Axis — to name only the four largest — each issue statements in a different column layout, with different preamble rows above the transaction table, different date formats, and different conventions for marking a debit against a credit. A tool built against one bank's export format silently fails, or worse, silently misreads, against another's. Narrations themselves compress a payee, a payment rail and a reference number into a single string with no whitespace to separate them, so a keyword search that would work on an English sentence often does not work on an Indian bank narration at all.",
 "SmartEdit AI was built to solve this specific, well-defined problem: to turn a raw, unstandardised Indian bank statement into an understanding of where the money went, without asking the user to do any of the reading, categorising or arithmetic by hand, and without requiring the user's financial data to leave their own computer.",
].forEach(t => children.push(para(t)));

children.push(h2("1.2 Motivation"));
[
 "Three motivations shaped the project beyond the immediate convenience of automated categorisation. First, existing personal-finance tools that are convenient are rarely private — cloud-hosted aggregators require transaction data, and often bank credentials, to be handed to a third party. Second, tools that are private, such as a personal spreadsheet, are rarely convenient — they demand manual entry and offer no automated insight. Third, few tools available to an Indian salaried user model the Indian salary and tax structure accurately enough to answer a genuinely useful question such as which tax regime saves more money this year, given a specific CTC and a specific rent. SmartEdit AI set out to occupy the space that satisfies all three: automated, private and India-accurate.",
 "A fourth motivation emerged during development rather than at the outset. Once a conversational chatbot was built on top of an on-device language model, it became clear that a small model is not to be trusted with arithmetic, and that the naive approach of asking the model to both compute and phrase a financial answer is unsafe. That observation reshaped a significant part of the final-semester work, described fully in Chapter 12, and it is one of the more important engineering lessons the project produced.",
].forEach(t => children.push(para(t)));

children.push(h2("1.3 Objectives"));
[ "Extend the mid-semester prototype into a complete, tested, installable application that: accepts bank statements in CSV, XLSX and PDF form, and manual entries, from any of the major Indian banks; parses each statement's transactions correctly regardless of layout; classifies every transaction into a meaningful expense category with an interpretable, India-aware method; presents a dashboard of income, expenses, savings, category trends and recurring commitments; models the Indian salary structure and computes tax accurately under both regimes, including the Section 87A rebate and marginal relief; lets the user set savings goals and budgets and track progress against them; answers free-form natural-language questions about the user's own transactions through a chatbot whose numeric claims are always traceable to a real database query; runs its language model and embedding model entirely on the user's own machine by default, so that no transaction data needs to leave it; and is verified by an automated test suite together with a live end-to-end run on the finished build.",
].forEach(t => children.push(para(t)));

children.push(h2("1.4 Scope and What Is Deliberately Out of Scope"));
[
 "In scope: the full web application described above, running as a single-user, single-machine deployment; parsing support for the eleven Indian bank layouts whose alias maps are built into the parser; a seventeen-category classifier combining rules and a lightweight machine-learning model; salary and tax computation for financial year 2025-26 under both regimes; a deterministic analytics and insights engine; a natural-language query engine and a retrieval-augmented chatbot grounded in the user's own data; and an on-device language model with a defined fallback ladder to external providers when the user chooses to configure one.",
 "Deliberately out of scope: direct bank-account integration through an account-aggregator or banking API — the system works from statements the user exports themselves, which keeps the trust boundary simple and avoids handling banking credentials at all; income-tax e-filing or submission to any government portal — the system computes an estimate for the user's own planning, it does not file a return; investment or brokerage execution of any kind; multi-user or organisational accounts, since the design targets an individual salaried user; a native mobile application, since the web frontend is responsive and serves the same purpose; and continuous, always-on cloud hosting, since the privacy argument in Chapter 4 depends on the application running on hardware the user controls. These exclusions were design decisions taken to keep the trust boundary and the engineering scope coherent, not gaps discovered late.",
].forEach(t => children.push(para(t)));

children.push(h2("1.5 Report Structure"));
children.push(para("Chapter 2 surveys the relevant literature and tooling: statement-parsing approaches, text classification for short noisy strings, retrieval-augmented generation, on-device quantised inference, and where existing personal-finance tools leave gaps. Chapter 3 states the functional and non-functional requirements that later chapters build against and Chapter 14 traces back to. Chapters 4 and 5 describe the system architecture and database design. Chapters 6 through 12 describe the methodology in the order data flows through the system: statement parsing, transaction classification, analytics and insights, salary and tax modelling, the natural-language query engine, the on-device language model and retrieval pipeline, and finally the grounding-and-safety design that keeps the chatbot's answers trustworthy. Chapter 13 walks through the implementation. Chapter 14 presents the testing and validation evidence, including two defects a live end-to-end run exposed. Chapter 15 covers deployment and installation. Chapters 16 and 17 discuss the results, limitations, conclusions and future work. Chapter 18 lists references and Chapter 19 contains three appendices."));

// ===================================================================
// CHAPTER 2 — LITERATURE AND TOOL SURVEY
// ===================================================================
children.push(pageBreak());
children.push(h1("2. LITERATURE AND TOOL SURVEY"));

children.push(h2("2.1 Statement-Parsing Approaches"));
[
 "Extracting structured transactions from a bank statement is fundamentally a table-extraction problem complicated by inconsistent input. Two broad approaches exist in practice. The first is template-based parsing, where a fixed set of column positions or regular expressions is hand-written for each known statement layout; this is simple and accurate for the layouts it was written for, but brittle — a bank that changes its export format, or a statement type the author never saw, breaks silently. The second is heuristic, layout-inferring parsing, where the program inspects the document itself to decide where the transaction table begins and which column means what. SmartEdit AI takes the second approach: its header-scoring method, described in Chapter 6, scans candidate rows and scores each on how well it looks like a column header, rather than assuming the header is always row one.",
 "For PDF specifically, table extraction relies on the document's underlying text and line geometry rather than optical character recognition, since Indian bank statement PDFs are almost always text-based rather than scanned images. The pdfplumber library, used in this project, exposes both a ruled-table extractor and raw positioned text, which is what makes a text-based regular-expression fallback possible when a PDF has no ruled table at all — a situation encountered directly with one of the bundled sample statements, as Chapter 6 reports.",
].forEach(t => children.push(para(t)));

children.push(h2("2.2 Text Classification for Short, Noisy Strings"));
[
 "Bank transaction narrations are an unusual text-classification input: short, often under ten tokens; frequently free of whitespace, since fields are concatenated with hyphens as in UPI-SWIGGY-OKAXIS-XXXX1234; and drawn from a vocabulary that mixes merchant brand names, payment-rail codes and reference numbers with no fixed grammar. Classic bag-of-words classification, which tokenises on whitespace, performs poorly here because a concatenated string like UPISWIGGYOKAXIS is a single token that a word-level vocabulary has never seen. Character n-gram representations solve this by working below the word level: a narration is represented as the set of overlapping character sequences it contains, so SWIGGY still contributes recognisable n-grams whether or not it is surrounded by whitespace or other tokens. This is the reasoning behind the char_wb TF-IDF representation used by the SmartEdit AI classifier's machine-learning tier, described in Chapter 7.",
 "A second recurring difficulty in short-string classification is substring collision: a naive keyword match for EMI will also match inside PREMIUM, misclassifying an LIC insurance premium as a loan instalment. This is a known failure mode of substring-based rule engines in general, and it was observed directly during development of this project, as reported in Chapter 7. Word-boundary matching for short keywords is the standard mitigation and is the one adopted here.",
].forEach(t => children.push(para(t)));

children.push(h2("2.3 Retrieval-Augmented Generation"));
[
 "Retrieval-augmented generation, introduced by Lewis et al. (2020), combines a retriever that fetches relevant passages from an external knowledge source with a generator — typically a language model — that conditions its output on the retrieved content, rather than relying solely on what the model memorised during training. The original motivation was reducing hallucination on open-domain question answering by grounding the generator in real documents. SmartEdit AI applies the same idea to a different setting: the external knowledge source is not a public corpus but a single user's own transaction history, embedded and retrieved by cosine similarity, and the language model's role is narrowed further, as Chapter 12 explains, to rewording an answer whose numeric content has already been computed exactly rather than retrieved approximately. This is a stricter application of the RAG idea than the literature typically describes, motivated by the observation that a small on-device model cannot be trusted to compute financial figures on its own.",
].forEach(t => children.push(para(t)));

children.push(h2("2.4 On-Device Quantised Inference"));
[
 "Quantisation, in the context of neural network inference, is the process of representing a model's weights with fewer bits than the precision they were trained in — typically converting 16-bit or 32-bit floating-point weights to 4-bit or 8-bit integer representations, with per-group scaling factors that let the low-precision values approximate the original ones closely enough that output quality degrades only modestly. The practical benefit is size and speed: a model stored at 4 bits per weight occupies roughly a quarter of the space it would at 16 bits, and integer arithmetic on modest CPU hardware is markedly faster than floating-point arithmetic at full precision.",
 "The GGUF format and the accompanying quantisation schemes used by llama.cpp label their variants by bits and by a mixing strategy; Q4_K_M denotes 4-bit quantisation using the K-quant scheme's medium-mixed-precision variant, which keeps a small number of especially sensitive tensors at higher precision while quantising the bulk of the model to 4 bits, trading a modest amount of file size for noticeably better output quality than a uniform 4-bit scheme. This is the quantisation applied to the Qwen2.5-1.5B-Instruct model used in this project, producing a 1,066 MB model file, small enough to download once and keep resident on a laptop with no dedicated GPU.",
 "A 1.5-billion-parameter model is, by current standards, small. It fits comfortably in the RAM of an ordinary laptop alongside the operating system, the browser and the Flask process, and it can generate text on CPU alone at a rate — 8.8 tokens per second, measured on the development machine, as Chapter 11 reports — usable for a short conversational reply. The trade-off is capability: small models are known in the literature to be considerably weaker than their larger counterparts at multi-step reasoning and arithmetic, which is precisely the limitation that motivated the grounding design in Chapter 12 rather than trusting the model to compute answers directly.",
].forEach(t => children.push(para(t)));

children.push(h2("2.5 Personal-Finance Tools and What Each Leaves Unsolved"));
[
 "Four broad categories of existing tool were considered when scoping this project. Bank-provided statement viewers display the raw transaction list but perform no categorisation or trend analysis at all, leaving the interpretation entirely to the user. Manual spreadsheet tracking gives the user full control and full privacy but demands that every transaction be entered and categorised by hand, which does not scale past a few dozen transactions a month and offers no automated insight generation. Cloud-hosted personal-finance aggregators, common in Western markets, automate categorisation and offer dashboards, but they require the user's transaction data — and often direct bank credentials — to be sent to and stored by a third-party server, and their categorisation logic is generally tuned to Western statement formats and merchant names rather than UPI, NACH or Indian bank narrations. Rule-based categorisation features built into some Indian fintech apps handle Indian narrations reasonably well but typically stop at categorisation: they do not offer a conversational interface grounded in the user's actual ledger, they do not run locally, and none surveyed builds an explicit safety layer around what a generative model is permitted to say about the user's own numbers.",
 "SmartEdit AI is positioned to close the specific combination none of the four categories closes together: automated, India-aware categorisation; a local-first architecture that keeps data on the user's machine by default; and a conversational query interface whose numeric claims are guaranteed, by construction rather than by hope, to come from the user's real transactions.",
].forEach(t => children.push(para(t)));

// ===================================================================
// CHAPTER 3 — REQUIREMENTS
// ===================================================================
children.push(pageBreak());
children.push(h1("3. REQUIREMENTS"));
children.push(para("Requirements are grouped into functional requirements, describing what the system must do, and non-functional requirements, describing the qualities the system must have while doing it. Each requirement is numbered so that later chapters, and in particular the testing traceability in Chapter 14, can refer back to it directly. Table 1 lists all requirements."));
children.push(table(["ID", "Category", "Requirement"],
  [
   ["FR1", "Functional", "Register and log in with a hashed password and session-guarded pages."],
   ["FR2", "Functional", "Accept bank statements uploaded as CSV, XLSX or PDF, and manual transaction entry."],
   ["FR3", "Functional", "Parse statement layouts from multiple Indian banks without a fixed per-bank template."],
   ["FR4", "Functional", "Classify every transaction into one of seventeen expense categories."],
   ["FR5", "Functional", "Present a dashboard of income, expenses, savings and category-wise trends."],
   ["FR6", "Functional", "Detect recurring commitments such as subscriptions, EMIs and rent."],
   ["FR7", "Functional", "Compute the Indian salary structure and income tax under both the new and old regimes."],
   ["FR8", "Functional", "Allow the user to define savings goals and category budgets and track status against them."],
   ["FR9", "Functional", "Answer natural-language questions about the user's own transactions with a grounded chatbot."],
   ["FR10", "Functional", "Prevent a re-uploaded statement from importing the same transaction twice."],
   ["FR11", "Functional", "Allow the user to correct a transaction's assigned category."],
   ["FR12", "Functional", "Export the transaction ledger to CSV."],
   ["NFR1", "Non-functional — Privacy", "Run inference on-device by default so transaction data need not leave the machine."],
   ["NFR2", "Non-functional — Resilience", "Degrade gracefully when an optional component is unavailable, rather than fail to start."],
   ["NFR3", "Non-functional — Correctness", "Never present a rupee figure in a chatbot answer that was not computed by a deterministic aggregate."],
   ["NFR4", "Non-functional — Isolation", "Ensure one account can neither read nor modify another account's data."],
   ["NFR5", "Non-functional — Maintainability", "Upgrade the database schema in place across releases without losing existing data."],
   ["NFR6", "Non-functional — Usability", "Render every page correctly for a newly created account with no unhandled errors."],
   ["NFR7", "Non-functional — Offline operation", "Operate fully offline after the one-time setup download."],
  ], [900, 2400, 6060]));
children.push(caption("Table 1: Functional and Non-Functional Requirements"));
children.push(para("These requirements were derived from the problem described in Chapter 1 and refined across the mid-semester and final-semester phases of the project. FR7, FR8 and FR9 in particular were added after the mid-semester submission, once the salary and tax module, the goals and budgets pages, and the natural-language query engine moved from planned to implemented. NFR1 and NFR3 are the two requirements most directly responsible for the architectural decisions described in Chapters 4 and 12."));

// ===================================================================
// CHAPTER 4 — SYSTEM ARCHITECTURE
// ===================================================================
children.push(pageBreak());
children.push(h1("4. SYSTEM ARCHITECTURE"));
children.push(h2("4.1 Four Layers"));
[
 "SmartEdit AI is organised into four layers. The browser front end is server-rendered HTML with vanilla JavaScript and Chart.js, served directly from the application itself with no external content-delivery dependency; it presents eleven pages — Login, Register, Dashboard, Add Entry, View/Database, Tracker, Salary & Tax, Goals, Budget, Insights and AI Chat. Below it, a Flask application server coordinates eight modules, described in section 4.2. Below that, an on-device inference layer, llm_local.py, wraps llama.cpp to run the quantised language model locally. At the base, SQLite is accessed through the SQLAlchemy object-relational mapper, giving the rest of the application a Python object interface to the database rather than hand-written SQL scattered across modules. Figure 1 shows how these layers and the eight application modules relate.",
].forEach(t => children.push(para(t)));
children.push(img("01_system_architecture.png", 600, 300));
children.push(caption("Figure 1: System Architecture of SmartEdit AI"));

children.push(h2("4.2 The Eight Modules"));
children.push(para("Table 2 lists the eight modules that make up the Flask application server layer and the responsibility each one owns. Splitting the server into these modules — rather than one monolithic routes file — keeps each concern independently testable, which Chapter 14's six test modules map onto almost one-to-one."));
children.push(table(["Module", "Key File", "Responsibility"],
  [
   ["Authentication & Session", "auth routes", "Registration, login, password hashing, and guarding every page behind a valid session."],
   ["Statement Parser", "parser.py", "Extracts transactions from uploaded CSV, XLSX and PDF bank statements across eleven bank layouts."],
   ["Transaction Classifier", "classifier.py", "Assigns each transaction to one of seventeen categories using rules first and a trained model for the remainder."],
   ["Analytics Engine", "analytics.py", "Computes summaries, trend series, category breakdowns, recurring commitments and budget status."],
   ["Salary & Tax", "salary.py", "Models the Indian CTC structure and computes tax under both regimes for financial year 2025-26."],
   ["Natural-Language Query Engine", "nlq.py", "Turns a plain-English question into a structured, deterministic database query."],
   ["AI Advisory", "advisor.py", "Builds rupee-level savings guidance from the categorised monthly summary."],
   ["RAG Chatbot", "rag.py", "Retrieves supporting transactions by embedding similarity and produces a grounded, guarded reply."],
  ], [2000, 1800, 5560]));
children.push(caption("Table 2: Module Responsibilities"));

children.push(h2("4.3 Component and Deployment Views"));
[
 "The component diagram in Figure 8 shows the same eight modules as discrete, independently addressable units communicating through function calls within a single Flask process, rather than as separate networked services — an intentional simplification appropriate to a single-user, single-machine deployment, where the overhead of a microservice boundary would buy nothing. The deployment diagram in Figure 9 shows the corresponding physical picture: one machine runs the Flask server, the SQLite database file, the downloaded language model file and the cached embedding model, and the user's browser connects to that same machine over localhost. There is no application server, load balancer or external database to provision, which is consistent with the setup story in Chapter 15.",
].forEach(t => children.push(para(t)));
children.push(img("08_component_diagram.png", 460, 360));
children.push(caption("Figure 8: Component Diagram"));
children.push(img("09_deployment_diagram.png", 560, 300));
children.push(caption("Figure 9: Deployment Diagram"));

children.push(h2("4.4 Module Dependency"));
[
 "Figure 15 shows the dependency direction between modules: the route layer depends on the parser, classifier, analytics, salary, NLQ, advisory and RAG modules, and the advisory and RAG modules in turn depend on the on-device inference layer. Dependencies flow strictly downward — the parser has no knowledge of the classifier, and the classifier has no knowledge of the chatbot — which keeps each module testable in isolation, as Chapter 14 demonstrates, and is what allowed the salary module and the natural-language query engine to be added in the final semester without touching the parser or the classifier at all.",
].forEach(t => children.push(para(t)));
children.push(img("15_module_dependency.png", 560, 340));
children.push(caption("Figure 15: Module Dependency Diagram"));

children.push(h2("4.5 The Privacy Argument for Local Inference"));
[
 "The claim that nothing leaves the machine in the default configuration is not a policy statement layered on top of the architecture — it follows from the architecture itself. The language model runs in-process through llama-cpp-python against a model file stored on disk; the embedding model runs in-process through sentence-transformers against a model cached on disk after the first download; and the database is a single SQLite file on the same disk. None of these three components makes an outbound network call in the default configuration. The only point at which the system would send transaction data off the machine is if the user explicitly supplies a Gemini API key, which activates one rung of the provider fallback ladder described in Chapter 11 — an opt-in exception, not a default behaviour. This is a materially stronger privacy position than a cloud-hosted personal-finance aggregator can offer, where sending the data off-device is not optional but foundational to how the product works.",
].forEach(t => children.push(para(t)));

// ===================================================================
// CHAPTER 5 — DATABASE DESIGN
// ===================================================================
children.push(pageBreak());
children.push(h1("5. DATABASE DESIGN"));
children.push(h2("5.1 Seven Tables"));
children.push(para("The schema comprises seven tables, summarised in Table 3 and shown as an entity-relationship diagram in Figure 4."));
children.push(table(["Table", "Purpose"],
  [
   ["users", "Holds one row per registered account: credentials and account-level identity, the parent of every other table."],
   ["transactions", "The transaction ledger — every parsed or manually entered row belonging to a user, described in full in Table 4."],
   ["embeddings", "One retrieval vector per transaction, used by the RAG chatbot to find supporting rows for a question."],
   ["chat_history", "The conversation log between a user and the chatbot, used to display prior exchanges."],
   ["salary_profiles", "The CTC, rent and regime inputs a user has saved for the salary and tax module."],
   ["savings_goals", "User-defined savings targets tracked on the Goals page."],
   ["budgets", "Per-category spending limits tracked on the Budget page and used by the analytics engine's overspend check."],
  ], [2200, 7160]));
children.push(caption("Table 3: Database Tables Overview"));
children.push(img("04_er_diagram.png", 600, 250));
children.push(caption("Figure 4: Entity-Relationship Diagram of the SmartEdit AI Database"));

children.push(h2("5.2 The transactions Table"));
children.push(para("The transactions table is the busiest table in the schema and the one every other analytical feature ultimately reads from. Table 4 lists every column."));
children.push(table(["Column", "Type", "Purpose"],
  [
   ["id", "Integer, primary key", "Uniquely identifies the row."],
   ["user_id", "Integer, foreign key", "Owning account; the basis of the account-isolation guarantee in NFR4."],
   ["date", "Date", "Transaction date, normalised from whichever of the supported Indian date formats the statement used."],
   ["description", "Text", "Cleaned, display-ready narration shown to the user."],
   ["raw_description", "Text", "The narration exactly as it appeared in the source statement, kept for audit and re-classification."],
   ["amount", "Numeric", "Transaction amount in rupees."],
   ["txn_type", "Text (credit / debit)", "Direction of the transaction, resolved by the four-step method in Chapter 6."],
   ["category", "Text", "One of the seventeen categories assigned by the classifier or corrected by the user."],
   ["method", "Text", "Payment rail detected in the narration (UPI, NEFT, NACH, POS and so on), where identifiable."],
   ["source", "Text", "Records whether the row came from a parsed statement or manual entry."],
   ["merchant", "Text", "Normalised merchant or payee name extracted from the narration."],
   ["confidence", "Numeric, 0 to 1", "The classifier's confidence in the assigned category."],
   ["balance", "Numeric", "Running account balance, where the statement provides one; used to resolve direction by balance movement."],
   ["fingerprint", "Text, 40-character SHA-1 hex digest", "A hash over user, date, amount, type and narration; the basis of duplicate-import prevention."],
   ["created_at", "Date / timestamp", "When the row was written to the database."],
  ], [1900, 2200, 5260]));
children.push(caption("Table 4: The transactions Table — Columns"));

children.push(h2("5.3 Relationships"));
children.push(para("A user owns many rows in transactions, embeddings, chat_history, salary_profiles, savings_goals and budgets; every foreign key in the schema ultimately traces back to users.id, which is what makes the account-isolation requirement, NFR4, enforceable with a single filter condition applied consistently across every query. The relationship between transactions and embeddings is one-to-one in the finished build: the live end-to-end run reported in Chapter 14 imported 69 transactions and indexed exactly 69 embeddings, confirming that every transaction acquires exactly one retrieval vector rather than zero or several."));

children.push(h2("5.4 Why a Transaction Fingerprint Is Stored"));
[
 "The fingerprint column exists to answer one specific question cheaply: has this exact transaction already been imported? A user who re-uploads the same statement — a common accident, and also a common deliberate action when a bank's export includes overlapping date ranges across two downloads — should not see every transaction duplicated. The fingerprint is computed as a SHA-1 digest over the user, the date, the amount, the type and the narration, which by definition of SHA-1 produces a fixed 40-character hexadecimal string regardless of the length of the input. Checking for a duplicate becomes a single indexed lookup against this column rather than a fuzzy comparison across every existing row, and it is why the live run's third upload of an already-loaded statement correctly imported nothing, as Chapter 14 reports.",
].forEach(t => children.push(para(t)));

children.push(h2("5.5 Upgrading the Schema in Place"));
[
 "SmartEdit AI does not use a separate migrations framework. Instead, ensure_schema() runs at start-up and adds any table or column that the code expects but the existing database file does not yet have, so that upgrading the application to a newer version never requires the user to delete or manually alter their database. This trades away some of what a dedicated migrations tool such as Alembic would offer — for instance, safely renaming or removing a column, or running a data-transforming migration — in exchange for simplicity appropriate to a single-file SQLite database managed by one developer: there is exactly one migration primitive, adding what is missing, and it is idempotent and safe to run on every start-up. The limitation is accepted deliberately rather than overlooked; it is revisited as a candidate improvement in Chapter 17.",
].forEach(t => children.push(para(t)));
children.push(img("16_transaction_state.png", 480, 320));
children.push(caption("Figure 16: Transaction State Diagram"));

// ===================================================================
// CHAPTER 6 — STATEMENT PARSING
// ===================================================================
children.push(pageBreak());
children.push(h1("6. STATEMENT PARSING"));
children.push(h2("6.1 Header Scoring"));
[
 "Real Indian bank exports rarely put the transaction table on row one. An SBI or ICICI CSV export typically opens with several rows of account details — account number, statement period, account holder name — and often a blank row or two, before the actual column header appears. A parser that assumes row one is the header will misread every subsequent row. SmartEdit AI's parser instead scans the first twenty-five rows of the file and scores each as a candidate header, favouring rows whose cells look like column names (Date, Narration, Debit, Credit and their many bank-specific spellings) over rows that look like data or free text. Twenty-five rows was chosen as a bound generous enough to cover every preamble length observed in the bundled samples — the HDFC sample statement, for instance, carries six preamble rows above its header, as Table 5 records — while still being small enough that the scan cannot mistake a genuine data row deep in the table for a header.",
].forEach(t => children.push(para(t)));

children.push(h2("6.2 Per-Bank Column Alias Maps"));
[
 "Once the header row is located, its column names are matched against per-bank alias maps that translate bank-specific column naming into the parser's internal fields. The parser detects HDFC, ICICI, Axis, SBI, Kotak, Punjab National Bank, Bank of Baroda, Canara Bank, Yes Bank, IDFC First and IndusInd layouts this way [1]. When no bank-specific alias matches, the parser falls back to a generic set of common column-name variants, so an unrecognised or unusual export is not necessarily rejected outright — the sample_statement.csv file in Table 5, whose bank is not detected, is still parsed correctly through this generic path.",
].forEach(t => children.push(para(t)));

children.push(h2("6.3 Resolving Amount, Direction and Date"));
[
 "Indian statements express amounts in several ways within a single column and sometimes within a single file: grouped thousands such as 1,23,456.00; a leading Rs. prefix as in Rs. 4,500; parentheses to denote a withdrawal as in (2,000.50); and a trailing Dr or Cr suffix on the figure itself. The parser normalises all of these to a plain signed numeric value before anything else happens.",
 "Direction — whether a row is money in or money out — is resolved through an explicit four-step priority order, applied in sequence until one step yields an answer: first, an explicit Dr/Cr column if the statement provides one; second, a Dr/Cr suffix attached to the amount value itself; third, the arithmetic sign of the amount; and fourth, as a last resort, the movement of the running balance column from the previous row to this one. This ordering exists because the four signals disagree in practice more often than a first-time reader might expect — a statement can carry a balance column but no explicit Dr/Cr marker, or a signed amount that is inconsistently signed across rows — and ordering the checks from most to least reliable produces the correct direction even when the more reliable signals are simply absent, as happens with the axis_statement.csv sample in Table 5, whose direction for the opening-balance row is resolved from balance movement alone.",
 "Dates are normalised across five observed formats: dd/mm/yyyy, dd-mm-yyyy, yyyy-mm-dd, dd Mon yyyy and dd-Mon-yyyy, covering the range of conventions used across the eleven supported banks.",
].forEach(t => children.push(para(t)));
children.push(img("10_parser_pipeline.png", 560, 260));
children.push(caption("Figure 10: Statement Parser Pipeline"));

children.push(h2("6.4 PDF Text Fallback"));
[
 "Not every PDF statement contains a ruled table that pdfplumber's table extractor [1] can recognise. When no ruled table is found, the parser falls back to reading the page's extracted text line by line and applying regular expressions tuned to the shape of a transaction row — a date, a narration, and one or two amount fields, in that order, on a single line. This fallback was exercised directly by the sample_statement.pdf file in Table 5, and it is the reason that file's one skipped row and its narrower coverage compared with the CSV samples are expected rather than a defect: text-line parsing is inherently less structured than table extraction and is used only when the more reliable path is unavailable.",
].forEach(t => children.push(para(t)));

children.push(h2("6.5 Noise Rejection and Encrypted PDFs"));
[
 "Statements routinely contain rows that are not transactions at all: an opening-balance line, a closing-balance line, a sub-total, or a page-number footer repeated on every page. Each of these is recognised by pattern and rejected, counted as a skipped row rather than silently imported as a fictitious transaction — this is why Table 5 reports a non-zero skipped count for the axis_statement.csv and sample_statement.pdf files even though both were parsed successfully overall. Password-protected PDFs are detected and raise a plain-English message asking the user to remove the password before uploading, rather than failing with a stack trace or, worse, appearing to succeed while extracting nothing.",
].forEach(t => children.push(para(t)));

children.push(h2("6.6 Measured Results"));
children.push(para("Table 5 reports the parser's measured behaviour on every sample statement bundled with the project."));
children.push(table(["File", "Bank Detected", "Rows", "Skipped"],
  [
   ["sample_statement.csv", "Unknown", "30", "0"],
   ["hdfc_statement.csv", "HDFC", "40", "0 (6 preamble rows above the header)"],
   ["icici_statement.csv", "ICICI", "35", "0 (single Amount column + Dr/Cr column)"],
   ["axis_statement.csv", "Axis", "30", "1 (opening balance; direction from balance movement)"],
   ["sample_statement.pdf", "Unknown", "30", "1 (no ruled table, text fallback used)"],
  ], [2600, 2000, 1400, 3360]));
children.push(caption("Table 5: Measured Parser Results per Sample File"));
children.push(img("05_sequence_upload.png", 600, 300));
children.push(caption("Figure 5: Sequence Diagram — Statement Upload"));

// ===================================================================
// CHAPTER 7 — TRANSACTION CLASSIFICATION
// ===================================================================
children.push(pageBreak());
children.push(h1("7. TRANSACTION CLASSIFICATION"));
children.push(h2("7.1 Seventeen Categories"));
children.push(para("Every transaction is assigned to one of the seventeen categories in Table 6."));
children.push(table(["#", "Category"],
  [["1","Income"],["2","Rent"],["3","EMI / Loans"],["4","Insurance"],["5","Investments"],
   ["6","Subscriptions"],["7","Food & Dining"],["8","Groceries"],["9","Transport"],
   ["10","Utilities"],["11","Shopping"],["12","Health"],["13","Education"],
   ["14","Entertainment"],["15","Travel"],["16","Transfers"],["17","Others"]],
  [800, 8560]));
children.push(caption("Table 6: Transaction Categories"));

children.push(h2("7.2 Rule Precedence — Why Payment Rails Must Be Tested Last"));
[
 "Classification runs a rule engine first, and any rule match is returned with confidence 1.0. The rules test merchant and purpose keywords — SWIGGY, NETFLIX, LIC and their many variants — before they test payment-rail markers such as UPI, NEFT, IMPS, RTGS, PhonePe, GPay or Paytm. The ordering matters: a narration such as UPI-SWIGGY-OKAXIS-XXXX1234 contains both a rail marker, UPI, and a merchant name, SWIGGY. If the rail check ran first, every UPI payment in the dataset — the large majority of small consumer transactions in India — would be classified as a generic Transfer regardless of who was paid, which would destroy exactly the category-level insight the application exists to provide. Testing merchant and purpose keywords first, and treating a rail marker as meaningful only once no merchant-level rule has already matched, ensures that a UPI payment to Swiggy is correctly filed as Food & Dining, and that Transfers is reserved for what it should mean: a payment to another person with no identifiable merchant or purpose behind it.",
].forEach(t => children.push(para(t)));

children.push(h2("7.3 The Word-Boundary Fix"));
[
 "An early version of the rule engine matched keywords as plain substrings, which is what let the three-letter string EMI match inside the word PREMIUM and file an LIC insurance premium debit under EMI / Loans instead of Insurance. The fix restricts keywords shorter than four characters to word-boundary matching, so EMI matches the standalone token EMI but not the substring embedded inside PREMIUM, while leaving longer, less collision-prone keywords such as SWIGGY or NETFLIX on the faster plain substring check. This defect and its fix are covered directly by a dedicated regression test described in Chapter 14, so that the PREMIUM/EMI collision cannot silently return.",
].forEach(t => children.push(para(t)));
children.push(img("11_classifier_flow.png", 560, 260));
children.push(caption("Figure 11: Transaction Classifier Flow"));

children.push(h2("7.4 The Character N-Gram Model for the Remainder"));
[
 "Transactions that no rule can place fall to a machine-learning model rather than defaulting straight to Others. The model represents each narration as TF-IDF-weighted character n-grams of length two to five, using the char_wb analyser, which — as discussed in Chapter 2 — is well suited to short, whitespace-sparse strings because it captures partial matches at the sub-word level [5][10]. These features feed a logistic regression classifier, trained on 746 labelled Indian narrations held in data/category_seed.csv and persisted to data/category_model.joblib so that training happens once rather than on every application start-up. If scikit-learn is not installed, the module still imports and runs on rules alone — an instance of the graceful-degradation requirement, NFR2, applied at the classifier level.",
 "Predictions below a confidence threshold of 0.35 fall back to Others rather than being reported with unwarranted certainty. The threshold was chosen to favour precision over recall for the model tier specifically: since the rule engine already resolves the clear cases with confidence 1.0, the model tier only ever sees the genuinely ambiguous residual, and a wrong but confident-looking guess on an ambiguous narration is worse for user trust than an honest Others.",
].forEach(t => children.push(para(t)));

children.push(h2("7.5 An Honest Reading of 64.7% Held-Out Accuracy"));
[
 "On a held-out split of the seed corpus, the model achieves 64.7% accuracy. Read in isolation, this number looks modest next to the near-perfect accuracy of the rule engine. It should not be read in isolation. The seed corpus was deliberately curated to over-represent ambiguous, hard-to-classify narrations, on the reasoning that unambiguous narrations are already handled by the rule engine and contribute nothing to evaluating the part of the system the model actually exists to help with. The 64.7% figure is therefore a measurement of performance on the hardest sub-problem the classifier faces, not a measurement of the classifier's overall accuracy across a typical statement, where most rows never reach the model tier at all.",
 "That said, 64.7% is a genuinely modest result for the residual, and it is stated here as a limitation rather than a success, consistent with the honest tone this report tries to maintain throughout. A single logistic regression over character n-grams is a lightweight, fast, easily retrainable model, chosen deliberately for a rules-first design where the model's job is to be a reasonable tie-breaker for the cases the rules could not resolve, not the primary classification mechanism. A richer model — for instance, one built on subword or transformer embeddings, trained on a larger and more diverse corpus of real Indian narrations — would likely improve this figure, and is listed as future work in Chapter 17. Below the 0.35 threshold the system falls back to Others rather than guessing, which is the safety valve that keeps a weak residual classifier from actively misleading the user.",
].forEach(t => children.push(para(t)));

children.push(h2("7.6 Payment Rails Detected"));
children.push(para("The following payment-rail markers are recognised for reporting purposes and for the rail-testing step described in section 7.2: UPI, NEFT, IMPS, RTGS, NACH, ECS, ACH, POS, ATM-CW, CHQ, INB, MB, CARD and EMI."));
children.push(img("17_category_taxonomy.png", 560, 340));
children.push(caption("Figure 17: Category Taxonomy"));

// ===================================================================
// CHAPTER 8 — ANALYTICS AND INSIGHTS
// ===================================================================
children.push(pageBreak());
children.push(h1("8. ANALYTICS AND INSIGHTS"));
children.push(h2("8.1 Aggregations"));
children.push(para("The analytics engine computes: period summaries of income, expense and savings; daily, monthly and weekday trend series; category-wise spending breakdown; top-merchant rankings; month-over-month comparison; per-category budget status; and recurring commitments. All of these are read directly from the transactions table scoped to the signed-in user, so they update immediately as new statements are imported or entries are added, with no separate batch or caching step to keep in sync."));

children.push(h2("8.2 Recurring-Commitment Detection and the Cadence Problem"));
[
 "Recurring detection deliberately restricts itself to six categories where a standing charge is plausible: Subscriptions, Utilities, Insurance, EMI / Loans, Rent and Investments. A category such as Groceries is excluded on purpose — a supermarket visited every week is a habit, not a standing charge, and treating habitual spend as a recurring commitment would clutter the feature with noise rather than the fixed obligations it is meant to surface. Within the eligible categories, a merchant qualifies as recurring once it appears in two or more distinct months at an amount within 15% of its median value across those appearances.",
 "The choice to key cadence off the count of distinct months, rather than the raw time gap between consecutive charges, was not the first design and was corrected after a concrete failure was found during development. The original version inferred cadence from the gap between charges in days, and when two overlapping statements covering the same calendar period were both imported, the same EMI appeared to recur every few days rather than monthly, and the detector projected an annualised cost of Rs.4.94 lakh for a payment that was in reality a Rs.9,500 monthly EMI. Counting distinct months instead of raw gaps fixes this directly: two statements covering the same month, however many times the EMI appears across them, still count as one month, so the annualised projection is no longer inflated by overlapping data. This fix, and the specific inflated figure it corrected, is covered by a regression test described in Chapter 14.",
].forEach(t => children.push(para(t)));

children.push(h2("8.3 Deterministic Insights"));
children.push(para("The insights engine generates the following observations, each of which quotes a real figure computed at generation time rather than a templated placeholder: the month-on-month change in spending and the category that drove it; any category taking more than 30% of total spend; the split between weekend and weekday spending; the single largest transaction in the period; the count of days with no recorded spend; the count and total value of food-delivery transactions; the annualised cost of standing charges identified by recurring-commitment detection; and the savings rate measured against a 20% benchmark. Because every insight is generated this way, the same grounding discipline that governs the chatbot's numeric claims, described fully in Chapter 12, is present here as well: nothing in the insights panel is templated with an unverified figure."));

// ===================================================================
// CHAPTER 9 — SALARY AND TAX MODELLING
// ===================================================================
children.push(pageBreak());
children.push(h1("9. SALARY AND TAX MODELLING"));
children.push(h2("9.1 The CTC Structure"));
[
 "SmartEdit AI models the Indian Cost-To-Company structure for financial year 2025-26 with the following defaults: basic pay is 40% of CTC; House Rent Allowance is 50% of basic; employee and employer provident fund contributions are each 12% of basic, capped at the statutory wage ceiling of Rs.15,000 per EPFO rules [13] when the employee has opted out of contributing on the full basic; and gratuity is provided for at 4.81% of basic. Gross salary is CTC minus the employer's provident fund contribution and the gratuity provision, since both of these are part of the employer's cost but are not paid to the employee as salary in hand.",
].forEach(t => children.push(para(t)));

children.push(h2("9.2 HRA Exemption — the Three-Limb Test"));
[
 "House Rent Allowance exemption is available only under the old tax regime, and only for the least of three amounts, as prescribed under the Income-tax Act, 1961 [11]: the actual HRA received; rent paid minus 10% of basic salary; and 50% of basic salary if the employee lives in a metro city, or 40% of basic if not. Taking the least of the three, rather than any single one of them, is what makes the exemption self-limiting — an employee who receives a generous HRA but pays comparatively little rent is exempted only on the rent-driven limb, not on the full HRA amount, which is the mechanism that stops HRA exemption from being claimed disproportionately to actual housing cost.",
].forEach(t => children.push(para(t)));

children.push(h2("9.3 Both Regimes"));
[
 "The standard deduction is Rs.75,000 under the new regime and Rs.50,000 under the old regime. A health-and-education cess of 4% is applied to the computed tax under both regimes.",
 "Under the new regime, slab rates for financial year 2025-26 are: nil up to Rs.4,00,000; 5% from Rs.4,00,000 to Rs.8,00,000; 10% from Rs.8,00,000 to Rs.12,00,000; 15% from Rs.12,00,000 to Rs.16,00,000; 20% from Rs.16,00,000 to Rs.20,00,000; 25% from Rs.20,00,000 to Rs.24,00,000; and 30% above Rs.24,00,000 [12]. The Section 87A rebate makes tax payable nil for taxable income up to Rs.12,00,000, and marginal relief applies just above that threshold, discussed in section 9.5.",
 "Under the old regime, slab rates are: nil up to Rs.2,50,000; 5% from Rs.2,50,000 to Rs.5,00,000; 20% from Rs.5,00,000 to Rs.10,00,000; and 30% above Rs.10,00,000, with the Section 87A rebate applying up to Rs.5,00,000 of taxable income.",
 "Professional tax of Rs.2,400 per year is added for employees in the states where it is levied: Tamil Nadu, Karnataka, Maharashtra, West Bengal, Andhra Pradesh, Telangana, Gujarat and Madhya Pradesh.",
].forEach(t => children.push(para(t)));
children.push(img("13_salary_flow.png", 560, 300));
children.push(caption("Figure 13: Salary and Tax Computation Flow"));

children.push(h2("9.4 Worked Example"));
children.push(para("For a CTC of Rs.18,00,000, computed under the new regime, for an employee in a metro city paying rent of Rs.25,000 a month, the module produces the breakdown in Table 7."));
children.push(table(["Component", "Amount (Rs.)"],
  [
   ["Basic", "7,20,000"], ["HRA", "3,60,000"], ["Special allowance", "5,98,968"],
   ["Gross salary", "16,78,968"], ["Employee PF", "86,400"], ["Gratuity", "34,632"],
   ["Taxable income", "16,03,968"], ["Slab tax", "1,20,794"], ["Cess (4%)", "4,832"],
   ["Total tax", "1,25,625"], ["Professional tax", "2,400"],
   ["Net annual take-home", "14,64,543"], ["Net monthly take-home", "1,22,045"],
  ], [4680, 4680]));
children.push(caption("Table 7: Worked Example — New Regime (CTC Rs.18,00,000)"));

children.push(para("Computed for the identical profile under the old regime instead, total tax rises to Rs.2,15,145 and net annual take-home falls to Rs.13,75,023, as Table 8 shows. For this profile, the new regime is better by Rs.89,520 a year — a difference large enough that the choice of regime is not a rounding-error decision for a salaried employee at this income level, and precisely the kind of comparison a generic finance tool without an India-accurate tax engine cannot make."));
children.push(table(["Metric", "New Regime (Rs.)", "Old Regime (Rs.)"],
  [
   ["Total tax", "1,25,625", "2,15,145"],
   ["Net annual take-home", "14,64,543", "13,75,023"],
  ], [3120, 3120, 3120]));
children.push(caption("Table 8: Old-Regime Comparison for the Same Profile"));

children.push(h2("9.5 Section 87A and Marginal Relief, with Boundary Evidence"));
[
 "The Section 87A rebate under the new regime is often summarised imprecisely as tax being nil up to Rs.12,00,000 of taxable income and taxed normally above it — but that summary alone would produce an unfair cliff-edge just above the threshold, where earning one rupee more than Rs.12,00,000 could otherwise mean paying tax on the entire slab structure rather than only on the amount past the threshold. Marginal relief exists to smooth that cliff: for taxable income just above Rs.12,00,000, the tax payable is capped at the amount by which taxable income exceeds Rs.12,00,000, rather than the full slab-computed tax, up to the point where ordinary slab tax becomes lower than that cap, after which ordinary slab tax applies again.",
 "Table 9 gives two measured points that demonstrate the rule operating correctly on either side of the boundary. At a CTC of Rs.14,00,000, taxable income comes to Rs.12,30,864; the excess over Rs.12,00,000 is Rs.30,864, and the tax charged is exactly Rs.30,864 — the marginal-relief cap, not the higher figure ordinary slab computation would otherwise produce. At a CTC of Rs.14,50,000, the excess over Rs.12,00,000 is Rs.77,502, and the tax charged is Rs.71,625, the ordinary slab-computed figure, because by this point ordinary slab tax has already fallen below the marginal-relief cap and the cap no longer binds. These two points together show the relief band operating exactly as intended: capping tax just above the threshold, and yielding to ordinary slab computation once the cap is no longer the smaller of the two.",
].forEach(t => children.push(para(t)));
children.push(table(["CTC (Rs.)", "Excess over Rs.12,00,000 (Rs.)", "Tax Applied (Rs.)", "Rule Triggered"],
  [
   ["14,00,000", "30,864", "30,864", "Marginal-relief cap applies (taxable income Rs.12,30,864)"],
   ["14,50,000", "77,502", "71,625", "Ordinary slab tax applies — already below the cap"],
  ], [1800, 2760, 2200, 2600]));
children.push(caption("Table 9: Marginal-Relief Evidence"));
children.push(para("This boundary behaviour is verified by a dedicated test across the whole relief band, described in Chapter 14, precisely because marginal relief is the part of the tax computation most likely to be implemented subtly wrong — an off-by-one error at the Rs.12,00,000 boundary would be easy to write and easy to miss without a test that specifically probes both sides of it."));

// ===================================================================
// CHAPTER 10 — NATURAL-LANGUAGE QUERY ENGINE
// ===================================================================
children.push(pageBreak());
children.push(h1("10. NATURAL-LANGUAGE QUERY ENGINE"));
children.push(h2("10.1 From Question to Structured Query"));
[
 "The natural-language query engine's job is to turn a plain-English question such as how much did I spend on groceries in June into something a database can answer exactly. This happens in two stages. nlq.parse_query reads the question and, using regular expressions and keyword tables rather than a language model, identifies the metric being asked about (a total, a count, an average, a largest or smallest value, a list, a category breakdown, a top-N ranking, a period comparison, a summary, or a request for advice), the period the question refers to, and the category or merchant it refers to, if any. nlq.execute then runs a real SQLAlchemy aggregate against the transactions table, scoped to the signed-in user, to produce the actual answer.",
 "Because this parsing step uses regular expressions and keyword tables rather than a model, it is fully explainable: for any question, it is possible to say exactly which pattern matched and why, which is not something that can be said of a language model's interpretation of the same question. This matters for a financial application specifically, where a wrong interpretation of the question is just as damaging to trust as a wrong number.",
].forEach(t => children.push(para(t)));

children.push(h2("10.2 Period Grammar"));
children.push(para("The engine recognises this month, last month, this week, this year, named calendar months, relative windows such as last 3 months, explicit date ranges, and the Indian financial year. When a recognised period contains no data for the signed-in user, the engine widens the window to the most recent month that does contain data, and the answer states plainly that this happened, rather than silently returning a misleading zero for a period the user did not intend to ask about."));

children.push(h2("10.3 Category Synonyms and Merchant Resolution"));
[
 "Everyday words a user is likely to type — food, petrol, bills, clothes — are mapped to the corresponding one of the seventeen categories from Chapter 7, so the user does not need to know the application's internal category names to ask a natural question. Merchant names are resolved dynamically against the signed-in user's own transaction history rather than against a fixed dictionary, so a merchant the user actually transacts with is always recognisable by name, and one they have never transacted with correctly yields no match rather than a false positive.",
].forEach(t => children.push(para(t)));

children.push(h2("10.4 Why This Is Deterministic Rather Than Prompted"));
[
 "An alternative design would ask the language model to interpret the question directly — effectively prompting it to both understand and answer in one step. This was deliberately not the approach taken, for three reasons that Chapter 12 develops further. First, explainability: a regular-expression match can be inspected and reasoned about; a model's internal interpretation cannot. Second, correctness: the numeric answer to a question like this must be exactly right, and a model is not the component this system trusts to be exactly right, as the LaTeX incident described in Chapter 12 demonstrates directly. Third, availability: because the structured query and its SQL execution do not depend on the language model being loaded at all, the natural-language query engine keeps working — producing exact figures — even when the on-device model, or every provider on the fallback ladder, is unavailable; only the final phrasing of the answer would be less conversational in that case. Figure 12 shows how the deterministic query result and the retrieval-augmented context described in Chapter 11 come together into the final answer.",
].forEach(t => children.push(para(t)));
children.push(img("12_rag_pipeline.png", 560, 300));
children.push(caption("Figure 12: Retrieval-Augmented Generation Pipeline"));

// ===================================================================
// CHAPTER 11 — ON-DEVICE LANGUAGE MODEL AND RETRIEVAL
// ===================================================================
children.push(pageBreak());
children.push(h1("11. ON-DEVICE LANGUAGE MODEL AND RETRIEVAL"));
children.push(h2("11.1 llama.cpp and the Model"));
[
 "On-device generation is provided by llama-cpp-python 0.3.34 [7], installed from a prebuilt CPU wheel, so that the end user's machine needs no compiler toolchain to run it — the wheel itself is 6.6 MB. The model is Qwen2.5-1.5B-Instruct [8], quantised to Q4_K_M as described in Chapter 2, distributed as a 1,066 MB GGUF file that the installer downloads from Hugging Face during first-run setup.",
 "Measured on the development machine, the model takes 2.7 seconds to load and generates at 8.8 tokens per second, running with a context window of 4096 tokens and a thread count equal to the CPU's core count. These figures are modest next to a cloud-hosted large model, but they are sufficient for the role the model actually plays in this system: rewording a short, already-computed sentence, not carrying out open-ended reasoning under time pressure.",
].forEach(t => children.push(para(t)));

children.push(h2("11.2 Embedding Model and Retrieval"));
[
 "Supporting context for the chatbot's answers is supplied by embeddings, not by the generative model. Each transaction is embedded with sentence-transformers' all-MiniLM-L6-v2 [6], producing a 384-dimensional vector, cached as JSON in the embeddings table described in Chapter 5. Retrieval is a cosine-similarity search, vectorised with numpy, between the embedded question and every stored transaction embedding for the signed-in user, returning the most relevant rows as supporting context. This retrieval step exists to supply the model with real transaction narrations to reference when it reworks the deterministic answer into natural language — it never supplies the numeric answer itself, which comes only from the SQL aggregate described in Chapter 10.",
].forEach(t => children.push(para(t)));
children.push(img("06_sequence_chat_rag.png", 600, 320));
children.push(caption("Figure 6: Sequence Diagram — Chatbot Query"));

children.push(h2("11.3 Provider Fallback Ladder"));
[
 "Generation is attempted through a defined ladder of providers, in order: the local Qwen2.5 model first; Ollama, if the user happens to already have an Ollama instance running on the machine; the Gemini API, only if the user has explicitly supplied an API key; and, if none of the above is available, a deterministic rule-based advisor that produces equivalent rupee-level guidance from templates rather than a generative model. This ladder guarantees that an answer is always produced — the system never simply fails to respond because a model could not be loaded — while keeping the local, private option as the default and every networked option strictly opt-in. Figure 14 shows the ladder and the condition under which each rung is used.",
].forEach(t => children.push(para(t)));
children.push(img("14_llm_fallback_chain.png", 560, 240));
children.push(caption("Figure 14: LLM Provider Fallback Chain"));

// ===================================================================
// CHAPTER 12 — GROUNDING AND SAFETY OF GENERATED ANSWERS
// ===================================================================
children.push(pageBreak());
children.push(h1("12. GROUNDING AND SAFETY OF GENERATED ANSWERS"));
children.push(h2("12.1 The Failure That Shaped This Chapter"));
[
 "This chapter documents the single most important design decision in the project, and it begins with an honest account of a failure rather than a success. During development, the chatbot was asked directly how much had been spent on food, given only the total amount and the transaction count as context for the model to reason over. Rather than reporting the ratio correctly, the 1.5-billion-parameter on-device model attempted to perform the division itself as part of composing its answer, and produced LaTeX mathematical notation in the middle of what was meant to be a plain-English sentence. The output was not merely wrong; it was wrong in a way that would have been immediately visible and damaging to user trust had it reached the interface unfiltered.",
 "This is not a peculiar bug specific to this one model. Small language models are well documented, in the literature surveyed in Chapter 2, to be unreliable at multi-step arithmetic even when they are otherwise fluent at natural language. The correct response to this observation is not to hope for a better model, or to patch the specific prompt that triggered the failure — it is to stop asking the model to compute anything at all, and to build a pipeline in which the model's only job is to reword a sentence whose numbers are already finished and correct before the model ever sees them.",
].forEach(t => children.push(para(t)));

children.push(h2("12.2 The Five-Step Pipeline"));
[
 "1. nlq.parse_query turns the user's question into a structured query using regular expressions and keyword tables, with no model involved, so the interpretation step is fully explainable, as described in Chapter 10.",
 "2. nlq.execute runs a real SQLAlchemy aggregate scoped to the signed-in user. Every rupee figure that will appear in the eventual answer originates here, and nowhere else.",
 "3. Embeddings supply supporting transactions for context only, retrieved by the cosine-similarity search described in Chapter 11 — never as a source of the numeric answer, only as illustrative detail the model may reference when phrasing its reply.",
 "4. The model is handed the finished, numerically correct sentence and asked only to reword it — not to verify it, not to extend it with additional computation, only to restate it in more natural language.",
 "5. A guard inspects the model's reply and discards it, falling back to the original deterministic sentence unmodified, if the reply quotes a figure that was never computed in step 2, shows arithmetic working of any kind, contains LaTeX notation, is written in the first person, opens with congratulations, or runs past three sentences.",
].forEach(t => children.push(bullet(t)));
children.push(para("Each of the five guard conditions in step 5 corresponds to a specific way the model could otherwise undermine the answer's correctness or tone: an invented figure would directly violate NFR3; visible arithmetic working would suggest, misleadingly, that the model computed rather than merely reworded the answer; LaTeX notation is exactly the failure mode observed in section 12.1 and is treated as disqualifying wherever it appears; first-person phrasing and unearned congratulatory language read as artificial and undermine the neutral, factual tone the application aims for; and a reply running past three sentences is, in practice, a reply that has wandered from rewording into elaboration, which is where the earlier failures tended to occur."));

children.push(h2("12.3 Why Multi-Row Answers Never Go Near the Model"));
[
 "Lists, category breakdowns and period comparisons are returned to the user directly from the deterministic query result, formatted by application code, without passing through the language model at all. This is a stricter rule than the five-step pipeline used for single-figure answers, and it exists because a small model is even less reliable at faithfully reproducing several numbers in sequence than it is at reasoning about one. A model asked to reword a five-row category breakdown is at risk of transposing figures between rows, dropping a row, or subtly altering a number while leaving the sentence grammatically fluent and therefore undetectable by casual reading. Removing the model from this path entirely is simpler and safer than trying to guard against every way a multi-number rewording could go wrong.",
].forEach(t => children.push(para(t)));

children.push(h2("12.4 Correctness Is Architectural, Not a Matter of Trusting the Model"));
[
 "The central argument of this chapter, and arguably of the project as a whole, is that the chatbot's numeric correctness does not depend on the language model behaving well. It depends on the model never being given the opportunity to be the source of a number in the first place. The guard described in section 12.2 is a safety net, not the primary mechanism — the primary mechanism is architectural separation between computation, which is deterministic, auditable and covered by the tests described in Chapter 14, and presentation, which is delegated to a component the system does not, and should not, trust unconditionally.",
 "This separation has a consequence worth stating plainly: the model could be swapped for a different, weaker, or even actively unreliable one, and the correctness of every rupee figure the chatbot states would be unaffected, because those figures never pass through the model as anything other than already-finished text to be reworded. What could change is the fluency of the phrasing, not the truth of the content. That is a deliberately narrow and deliberately safe division of labour for a financial application, and it is the reason this project treats the LaTeX incident in section 12.1 not as an embarrassment to be omitted from the report, but as the observation that justified the architecture described in this entire chapter.",
].forEach(t => children.push(para(t)));

children.push(h2("12.5 Handling Periods with No Data"));
children.push(para("As introduced in Chapter 10, a question about a period for which the signed-in user has no transactions is not answered with a bare zero, which could easily be misread as confirming that nothing was spent rather than that no data exists for that period. Instead, the engine widens the window to the most recent month that does have data and states this explicitly in the answer, keeping the response honest about what it is actually reporting on."));

// ===================================================================
// CHAPTER 13 — IMPLEMENTATION
// ===================================================================
children.push(pageBreak());
children.push(h1("13. IMPLEMENTATION"));
children.push(h2("13.1 Project Layout"));
[
 "The application server is organised around one Python module per responsibility, matching the eight-module architecture from Chapter 4: parser.py, classifier.py, analytics.py, salary.py, nlq.py, advisor.py and rag.py sit alongside the route definitions, with llm_local.py providing the on-device inference wrapper used by advisor.py and rag.py. Supporting data lives under data/, including the classifier's training corpus, category_seed.csv, and its persisted model file, category_model.joblib. Automated tests live under tests/, one file per module family, described fully in Chapter 14. Installation tooling lives under tools/, principally first_run_setup.py, invoked by setup.bat as described in Chapter 15. Diagrams and generated reports for this dissertation live under docs/.",
].forEach(t => children.push(para(t)));

children.push(h2("13.2 Module Walkthrough"));
[
 "Authentication & Session guards every page behind a valid login, hashes passwords before they are stored, and scopes every subsequent database query to the signed-in user's id — the mechanism behind NFR4 and NFR5. Statement Parser dispatches by file extension to a CSV/XLSX path built on pandas or a PDF path built on pdfplumber, and normalises whatever it extracts into the same internal row shape regardless of source, so nothing downstream needs to know which format a transaction originally came from. Transaction Classifier receives that normalised row and applies the rule-then-model pipeline from Chapter 7, writing back a category, a confidence score and the detected payment method. Analytics Engine reads the transactions table on demand — there is no separate materialised summary to keep in sync — and produces the aggregations and insights described in Chapter 8. Salary & Tax is stateless with respect to the transaction ledger; it takes a CTC, a rent figure and a regime choice and returns the full breakdown described in Chapter 9, independent of anything else in the database. Natural-Language Query Engine and AI Advisory together implement the pipeline described in Chapter 12, with nlq.py owning parsing and execution and advisor.py owning the rule-based fallback phrasing. RAG Chatbot, rag.py, owns embedding-based retrieval and orchestrates the five-step grounded-answer pipeline, calling into llm_local.py for the local model and into the provider ladder from Chapter 11 when it is not available.",
].forEach(t => children.push(para(t)));
children.push(img("02_use_case.png", 600, 300));
children.push(caption("Figure 2: Use-Case Diagram"));
children.push(img("03_class_diagram.png", 520, 360));
children.push(caption("Figure 3: Class Diagram"));

children.push(h2("13.3 Key Algorithms"));
[
 "Header scoring (statement parsing): scan the first twenty-five rows; for each row, score how many cells match a known header vocabulary against how many look like data; take the highest-scoring row above a minimum threshold as the header; if none clears the threshold, fall back to the generic column-alias path.",
 "Direction resolution (statement parsing): check for an explicit Dr/Cr column; if absent, check for a Dr/Cr suffix on the amount; if absent, use the arithmetic sign of the amount; if the amount is unsigned and no marker is present, infer direction from the change in the running balance column between consecutive rows.",
 "Fingerprint computation (deduplication): concatenate the user id, the transaction date, the amount, the resolved type and the raw narration; compute a SHA-1 digest over the concatenation; before inserting a new row, check whether its fingerprint already exists for this user, and skip the insert if it does.",
 "Recurring-commitment detection (analytics): restrict candidate transactions to the six eligible categories; group by normalised merchant; count the number of distinct calendar months in which the merchant appears; if that count is two or more, and every appearance is within 15% of the group's median amount, mark the merchant as recurring and annualise its median amount by its observed monthly cadence.",
 "Grounded chatbot answer (natural-language query and safety): parse the question into a structured query; execute it as a real aggregate; retrieve supporting transactions by embedding similarity for context only; hand the finished sentence to the model for rewording; discard the model's output and fall back to the original sentence if any of the five guard conditions from Chapter 12 is triggered.",
].forEach(t => children.push(bullet(t)));

children.push(h2("13.4 Request Lifecycle — Statement Upload"));
children.push(para("The browser posts the uploaded file to the upload endpoint. The route hands the file to the Statement Parser, which dispatches by type, extracts and normalises rows, and resolves each row's direction and date as described in Chapter 6. Each normalised row is passed to the Transaction Classifier, which assigns a category, a confidence score and a detected payment method. Before each row is written, its fingerprint is computed and checked against existing rows for the user; duplicates are skipped and counted, new rows are inserted. Once all rows are processed, an embedding is generated and stored for each newly inserted transaction, and the dashboard and analytics views reflect the updated ledger on their next read, with no separate refresh step required. Figure 5 in Chapter 6 shows this sequence in full."));

children.push(h2("13.5 Request Lifecycle — A Chatbot Question"));
children.push(para("The browser posts the user's question to the chat endpoint. The Natural-Language Query Engine parses it into a structured query and executes the corresponding SQLAlchemy aggregate, scoped to the signed-in user. In parallel, the RAG Chatbot retrieves supporting transactions by embedding similarity for context. If the question resolves to a single-figure answer, the finished sentence is handed to the on-device model, or the next available provider on the fallback ladder, for rewording, subject to the five-step guard from Chapter 12; if it resolves to a multi-row answer, the result is formatted directly without involving the model at all, as explained in section 12.3. The response is appended to the chat history table and returned to the browser. Figure 6 in Chapter 11 shows this sequence in full."));
children.push(img("07_data_flow.png", 600, 250));
children.push(caption("Figure 7: Data-Flow Diagram"));
children.push(img("18_activity_user_journey.png", 560, 360));
children.push(caption("Figure 18: Activity Diagram — User Journey"));

// ===================================================================
// CHAPTER 14 — TESTING AND VALIDATION
// ===================================================================
children.push(pageBreak());
children.push(h1("14. TESTING AND VALIDATION"));
children.push(h2("14.1 Test Modules"));
children.push(para("The application is covered by 172 automated tests, all passing, organised into six test modules, summarised in Table 10 and detailed further in Appendix B."));
children.push(table(["Test Module", "What It Protects"],
  [
   ["test_parser.py", "Every sample layout, header detection below a preamble, balance-delta direction resolution, noise rejection, and Indian amount and date formats."],
   ["test_classifier.py", "Category placement, rail-versus-merchant precedence, the PREMIUM/EMI word-boundary defect, merchant normalisation, handle stripping and confidence behaviour."],
   ["test_salary.py", "Component reconciliation, statutory percentages, cess, regime differences, the HRA three-limb minimum, the PF ceiling, professional tax by state, slab rows summing correctly to the total tax, monotonic tax behaviour, and marginal relief across the whole relief band."],
   ["test_analytics.py", "Summary arithmetic, ordering, empty-month fallback, trend alignment, the recurring-commitment category restriction, user isolation, budget overspend detection, fingerprint behaviour, and every analytics function against an account with no data."],
   ["test_chat.py", "Metric and period recognition, everyday category-word matching, merchant matching, exact totals sourced from SQL, the rule that no answer may contain an unexplained figure, readability with the model switched off, and each of the five guard rejection reasons from Chapter 12."],
   ["test_routes.py", "That every page requires a login and renders for a brand-new account; registration and login; duplicate-email handling; that a password is never stored in the clear; statement upload; rejection of a duplicate upload; graceful handling of an unreadable file; manual entry; the chat endpoint; the salary profile; a savings goal; CSV export; re-categorisation; and that one account can neither read nor delete another account's transaction."],
  ], [2400, 6960]));
children.push(caption("Table 10: Test Modules and What Each Protects"));

children.push(h2("14.2 Live End-to-End Run"));
[
 "Beyond the automated suite, a live end-to-end run was carried out on the finished build. An account was registered, two statements were uploaded, and 69 transactions were imported with 69 distinct fingerprints. A third upload of an already-loaded statement correctly imported nothing, confirming the deduplication behaviour described in Chapter 5 under a real, not simulated, repeat upload. 69 embeddings were indexed, matching the transaction count one-to-one as expected from the schema relationship described in Chapter 5. All eleven application pages returned HTTP 200 with no template errors. The chatbot was asked how much did I spend on groceries in June and answered In June 2026, you spent Rs.4,960 on groceries — a single-figure, grounded answer of exactly the kind the pipeline in Chapter 12 is designed to produce.",
].forEach(t => children.push(para(t)));

children.push(h2("14.3 Two Defects the Live Run Exposed"));
[
 "The live run found two defects that the automated suite, at the time, did not catch, and both were fixed before this report was finalised. The first was in the dashboard advisory: it was found to be quoting savings figures that the language model had itself invented rather than figures computed by the analytics engine — an instance of exactly the failure mode Chapter 12 describes, but found on the dashboard's advisory panel rather than the chatbot, and fixed by extending the same grounding discipline to that panel.",
 "The second was a test-infrastructure defect rather than an application defect: the route tests in test_routes.py were found to be writing to the real, production database rather than an isolated test database, because Flask-SQLAlchemy binds its database engine once, at init_app, and was silently ignoring a later attempt to change the database URI for the test environment. The fix was to make the database file location configurable at start-up, which both corrected the test isolation problem and, as a side benefit, made it straightforward to relocate the data file for backup or migration purposes independent of the test fix.",
 "Both defects are reported here rather than omitted, in keeping with the principle that a live run's value lies specifically in finding what unit tests, run in isolation, do not.",
].forEach(t => children.push(para(t)));

children.push(h2("14.4 Requirements Traceability"));
children.push(para("Table 11 maps each requirement from Chapter 3 to the test module, or in a small number of cases the architectural chapter, that verifies it."));
children.push(table(["Requirement", "Covered By"],
  [
   ["FR1", "test_routes.py — registration, login, duplicate-email handling, session guard on every page."],
   ["FR2", "test_parser.py (extraction) and test_routes.py (upload endpoint, manual entry)."],
   ["FR3", "test_parser.py — every bundled sample layout."],
   ["FR4", "test_classifier.py."],
   ["FR5", "test_analytics.py and test_routes.py (dashboard renders for a new account)."],
   ["FR6", "test_analytics.py — recurring-commitment category restriction and cadence."],
   ["FR7", "test_salary.py."],
   ["FR8", "test_routes.py (savings goal, budget) and test_analytics.py (budget overspend)."],
   ["FR9", "test_chat.py and test_routes.py (chat endpoint)."],
   ["FR10", "test_analytics.py (fingerprint behaviour) and test_routes.py (duplicate upload rejected)."],
   ["FR11", "test_routes.py — re-categorisation."],
   ["FR12", "test_routes.py — CSV export."],
   ["NFR1", "Architectural design, Chapter 4; verified by inspection rather than a unit test."],
   ["NFR2", "test_classifier.py (runs without scikit-learn) and test_chat.py (readability with the model switched off)."],
   ["NFR3", "test_chat.py — the unexplained-figure rule and all five guard rejection reasons."],
   ["NFR4", "test_routes.py and test_analytics.py — account isolation."],
   ["NFR5", "test_routes.py — password never stored in the clear."],
   ["NFR6", "test_routes.py — every page renders for a brand-new account with no template errors."],
   ["NFR7", "Verified by the live end-to-end run, Chapter 14.2, and the installation design, Chapter 15."],
  ], [1400, 7960]));
children.push(caption("Table 11: Requirements Traceability — Chapter 3 to Test Modules"));

// ===================================================================
// CHAPTER 15 — DEPLOYMENT AND INSTALLATION
// ===================================================================
children.push(pageBreak());
children.push(h1("15. DEPLOYMENT AND INSTALLATION"));
[
 "Installation is driven by a single script, setup.bat, which locates a suitable Python interpreter, creates a dedicated virtual environment, and installs the core application requirements. It then installs llama-cpp-python and torch from prebuilt CPU wheel indexes rather than compiling either from source, which is what keeps the compiler-free installation promise from Chapter 11 true for the end user, not only for the developer's own machine.",
 "setup.bat then runs tools/first_run_setup.py, which writes the application's settings file, downloads the 1,066 MB language model with a visible progress bar, caches the sentence-transformers embedding model for offline use thereafter, trains the classifier if its persisted model file is missing, and creates the database. In total, approximately 1.5 GB is downloaded once, during this first-run setup, and never again in normal use. run.bat then starts the Flask server and opens the default browser to the application.",
 "Every optional component degrades quietly rather than blocking start-up, consistent with NFR2: if llama.cpp is unavailable, the rule-based advisor answers instead of the on-device model; if sentence-transformers is unavailable, retrieval falls back to keyword search instead of embedding similarity; and in both cases the application still starts and remains usable, with reduced conversational fluency rather than a failed launch. Once the one-time setup download is complete, the application operates fully offline: no component in the default configuration makes a network call during ordinary use, which is the deployment-level expression of the privacy argument made architecturally in Chapter 4.",
].forEach(t => children.push(para(t)));

// ===================================================================
// CHAPTER 16 — RESULTS AND DISCUSSION
// ===================================================================
children.push(pageBreak());
children.push(h1("16. RESULTS AND DISCUSSION"));
children.push(h2("16.1 What Works, and the Evidence for It"));
[
 "The statement parser correctly extracted transactions from every bundled sample across five distinct layouts, including one PDF with no ruled table, with skipped rows correctly limited to genuine non-transaction noise, as Table 5 records. The classifier's rule engine, tested directly against the word-boundary defect it once had, correctly separates payment-rail markers from merchant identity, and the seventeen-category taxonomy covers the range of transactions observed in the sample data. The salary and tax module reproduces the Indian CTC structure, both regimes, and the marginal-relief boundary correctly, as the worked example and boundary evidence in Chapter 9 demonstrate. The full application passes 172 automated tests and was validated further by a live end-to-end run that imported 69 real transactions, correctly rejected a duplicate upload, indexed 69 embeddings, served all eleven pages without error, and returned a correctly grounded chatbot answer, as Chapter 14 reports. The grounding-and-safety pipeline in Chapter 12 is not a theoretical design; it exists because a concrete failure was observed and it is verified by a dedicated set of guard-condition tests.",
].forEach(t => children.push(para(t)));

children.push(h2("16.2 Limitations, Stated Plainly"));
[
 "The on-device language model is a 1.5-billion-parameter model. It paraphrases rather than reasons, and the entire design of Chapter 12 exists because this limitation was taken as a fixed constraint to be engineered around, not a problem expected to disappear with better prompting. Any future task that requires the model to genuinely reason about the user's finances, rather than reword an already-computed answer, would need either a materially larger model or a fundamentally different, still deterministic, computation path.",
 "The classifier's machine-learning tier is a lightweight TF-IDF character n-gram model over logistic regression, chosen deliberately for speed and easy retraining rather than maximum accuracy, and its 64.7% held-out accuracy on a deliberately hard residual, discussed fully in Chapter 7, should be read as a modest result on a genuinely difficult sub-problem rather than as representative of the classifier's overall behaviour across a typical statement.",
 "Bank coverage is limited to the layouts actually exercised. Alias maps exist for eleven Indian banks, but the measured results in Table 5 cover only HDFC, ICICI and Axis directly, alongside an unrecognised-bank CSV and a PDF fallback case. SBI, Kotak, Punjab National Bank, Bank of Baroda, Canara Bank, Yes Bank, IDFC First and IndusInd have alias-map support built in but were not part of the measured sample set, and their real-world accuracy should be regarded as supported but not yet independently verified in this report.",
].forEach(t => children.push(para(t)));

// ===================================================================
// CHAPTER 17 — CONCLUSION AND FUTURE WORK
// ===================================================================
children.push(pageBreak());
children.push(h1("17. CONCLUSION AND FUTURE WORK"));
children.push(h2("17.1 Objectives Revisited"));
[
 "Chapter 1 set eight objectives. All eight were met by the finished build. The application accepts CSV, XLSX and PDF statements and manual entries, and parses eleven Indian bank layouts through the header-scoring and alias-map approach of Chapter 6. Every transaction is classified into one of seventeen categories through the rule-first, model-assisted approach of Chapter 7. The dashboard presents income, expenses, savings, category trends and recurring commitments through the analytics engine of Chapter 8. The salary and tax module of Chapter 9 computes the Indian CTC structure and both regimes accurately, including marginal relief, with worked and boundary evidence to support it. Savings goals and budgets are supported and tracked. The natural-language query engine and grounded chatbot of Chapters 10 and 12 answer free-form questions with numeric claims that are architecturally guaranteed to trace back to a real database query. The language model and embedding model both run on the user's own machine by default, as Chapter 11 documents, satisfying the privacy objective without requiring the user to trust a remote server with their transaction data. And the system is verified by 172 automated tests plus a live end-to-end run, with defects the live run exposed reported honestly and fixed, as Chapter 14 documents.",
].forEach(t => children.push(para(t)));

children.push(h2("17.2 Future Work"));
[
 "Broaden the measured bank-coverage evidence to the remaining eight banks whose alias maps already exist but were not part of the sample set evaluated in this report, so that Table 5's coverage matches the parser's actual claimed support.",
 "Strengthen the classifier's residual-case accuracy beyond 64.7%, either by growing the labelled seed corpus with a larger and more diverse set of real Indian narrations, or by replacing the character n-gram and logistic regression pipeline with subword or transformer-based embeddings, while keeping the rules-first architecture that already resolves the unambiguous majority of transactions.",
 "Adopt a dedicated schema-migration tool in place of the current ensure_schema() additive-only approach, to support column renames and data-transforming migrations that the current approach cannot express, as noted as a limitation in Chapter 5.",
 "Track the classifier's and the natural-language query engine's real-world accuracy over time with a small regression benchmark, so that improvements or regressions in either component are measured rather than assumed.",
 "As consumer hardware capability grows, evaluate a larger on-device model within the same grounding-and-safety architecture from Chapter 12, which would improve phrasing quality without weakening the correctness guarantee, since that guarantee never depended on the model's capability in the first place.",
 "Extend the natural-language query engine's period grammar to a still wider range of everyday phrasing, informed by real user questions once the application has a broader user base to observe.",
].forEach(t => children.push(bullet(t)));

// ===================================================================
// CHAPTER 18 — REFERENCES
// ===================================================================
children.push(pageBreak());
children.push(h1("18. REFERENCES"));
[
 "[1] pdfplumber — PDF table and text extraction library. https://github.com/jsvine/pdfplumber",
 "[2] pandas — Python data analysis library used for CSV and XLSX parsing. https://pandas.pydata.org",
 "[3] Flask — Python web application framework. https://flask.palletsprojects.com",
 "[4] SQLAlchemy — Python SQL toolkit and object-relational mapper. https://www.sqlalchemy.org",
 "[5] scikit-learn — Machine learning library providing the TF-IDF vectoriser and logistic regression classifier. https://scikit-learn.org",
 "[6] Reimers, N. & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. EMNLP-IJCNLP. (sentence-transformers / all-MiniLM-L6-v2 — https://www.sbert.net)",
 "[7] Gerganov, G. et al. llama.cpp — Inference of large language models in C/C++, with the llama-cpp-python bindings used in this project. https://github.com/ggerganov/llama.cpp",
 "[8] Qwen Team, Alibaba Group. Qwen2.5 Technical Report (2024). https://arxiv.org/abs/2412.15115",
 "[9] Lewis, P. et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS.",
 "[10] Joachims, T. (1998). Text Categorization with Support Vector Machines: Learning with Many Relevant Features. ECML. (TF-IDF and character n-gram text classification foundations)",
 "[11] Income-tax Act, 1961, Government of India — provisions governing HRA exemption (Section 10(13A)) and the Section 87A rebate.",
 "[12] Finance Act, 2025, Government of India — slab rates and standard deduction under the new tax regime for financial year 2025-26.",
 "[13] Employees' Provident Fund Organisation (EPFO) — Employees' Provident Funds Scheme, 1952, statutory wage ceiling for mandatory contribution.",
].forEach(t => children.push(bullet(t)));

// ===================================================================
// CHAPTER 19 — APPENDICES
// ===================================================================
children.push(pageBreak());
children.push(h1("19. APPENDICES"));
children.push(h2("Appendix A: Category Taxonomy with Example Merchants"));
children.push(table(["Category", "Example Merchants / Narrations"],
  [
   ["Income", "Salary credit narrations from an employer's payroll account."],
   ["Rent", "Monthly rent transfer to a landlord, often a recurring UPI or NEFT payment."],
   ["EMI / Loans", "Bank loan EMI debit narrations, distinguished by word-boundary matching from PREMIUM (see Chapter 7)."],
   ["Insurance", "LIC and other insurer premium debits, for example NACH-LIC PREMIUM-AUTODEBIT."],
   ["Investments", "Mutual fund SIP debits, stockbroker narrations."],
   ["Subscriptions", "NETFLIX, SPOTIFY and similar recurring digital-service debits."],
   ["Food & Dining", "SWIGGY, ZOMATO and other food-delivery or restaurant narrations."],
   ["Groceries", "POS narrations from supermarkets, for example POS-4521-RELIANCE FRESH."],
   ["Transport", "Ride-hailing, fuel, metro or rail-recharge narrations."],
   ["Utilities", "Electricity, water, broadband and DTH bill payment narrations."],
   ["Shopping", "AMAZON, FLIPKART and other e-commerce narrations."],
   ["Health", "Pharmacy, hospital and diagnostic-centre narrations."],
   ["Education", "School or tuition fee payment narrations."],
   ["Entertainment", "Cinema and event-ticketing narrations."],
   ["Travel", "Airline, hotel and rail-booking narrations."],
   ["Transfers", "Person-to-person UPI payments with no identifiable merchant or purpose."],
   ["Others", "Narrations that match no rule and fall below the classifier's confidence threshold."],
  ], [2400, 6960]));
children.push(caption("Table 12: Category Taxonomy with Example Merchants"));

children.push(h2("Appendix B: Test Inventory"));
children.push(table(["Test File", "Coverage Areas"],
  [
   ["test_parser.py", "Every sample layout; header detection below a preamble; balance-delta direction; noise rejection; Indian amount and date formats."],
   ["test_classifier.py", "Category placement; rail-versus-merchant precedence; the PREMIUM/EMI trap; merchant normalisation; handle stripping; confidence."],
   ["test_salary.py", "Component reconciliation; statutory percentages; cess; regime differences; HRA three-limb minimum; PF ceiling; professional tax by state; slab rows summing to the tax; monotonic tax; marginal relief across the whole relief band."],
   ["test_analytics.py", "Summary arithmetic; ordering; empty-month fallback; trend alignment; recurring-commitment restriction; user isolation; budget overspend; fingerprint behaviour; every function against an account with no data."],
   ["test_chat.py", "Metric and period recognition; everyday category words; merchant matching; exact totals from SQL; the rule that no answer may contain an unexplained figure; readability with the model switched off; each guard rejection reason."],
   ["test_routes.py", "Every page requires a login; every page renders for a brand-new account; registration and login; duplicate email; password never stored in the clear; statement upload; duplicate upload rejected; unreadable file handled politely; manual entry; chat endpoint; salary profile; savings goal; CSV export; re-categorisation; one account cannot read or delete another account's transaction."],
  ], [2200, 7160]));
children.push(caption("Table 13: Test Inventory"));

children.push(h2("Appendix C: Settings Reference"));
children.push(table(["Setting", "Description"],
  [
   ["Database file location", "Configurable path to the SQLite database file; made configurable after the live run exposed the test-isolation defect described in Chapter 14, and also allows the data file to be relocated for backup."],
   ["Local model path", "Location of the downloaded Q4_K_M-quantised GGUF model file used by llama-cpp-python."],
   ["Gemini API key", "Optional; when the user supplies a key, this enables the Gemini rung of the provider fallback ladder described in Chapter 11."],
   ["Ollama endpoint", "Optional; used automatically when an Ollama instance is already running on the same machine."],
   ["Embedding model cache", "Local cache directory for the sentence-transformers all-MiniLM-L6-v2 model, populated on first download so retrieval works offline thereafter."],
   ["Classifier model file", "data/category_model.joblib; retrained automatically by the installer if the file is missing."],
  ], [2400, 6960]));
children.push(caption("Table 14: Settings Reference"));

// ---------- Document ----------
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Times New Roman", size: 24, color: INK } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, color: INK, font: "Times New Roman" }, paragraph: { spacing: { before: 240, after: 140 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: BLUED, font: "Times New Roman" }, paragraph: { spacing: { before: 160, after: 100 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, italics: true, color: INK, font: "Times New Roman" }, paragraph: { spacing: { before: 120, after: 80 }, outlineLevel: 2 } },
    ],
  },
  numbering: { config: [{ reference: "bul",
    levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 600, hanging: 280 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: GREY })] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log("WROTE", OUT, buf.length); });
