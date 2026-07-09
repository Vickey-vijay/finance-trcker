// SmartEdit AI — Mid-Semester Dissertation Report (BITS WILP format)
const fs = require("fs");
const path = require("path");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
        Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
        WidthType, ShadingType, PageNumber, PageBreak, TableOfContents, TabStopType,
        TabStopPosition } = require("docx");

const DIR = process.env.DIAGRAMS || path.join(__dirname, "diagrams");
const OUT = process.env.OUTFILE || path.join(__dirname, "SmartEditAI_MidSem_Report.docx");
const BLUE = "1A73E8", BLUED = "1457B8", INK = "1F2733", GREY = "6B7787";
const NOBORDER = { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
                   left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } };

const c = (text, o = {}) => new TextRun({ text, size: o.size || 24, bold: o.bold, italics: o.italics,
  color: o.color || INK, font: o.font, allCaps: o.allCaps });
const center = (runs, o = {}) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: o.after ?? 80, before: o.before ?? 0 }, children: Array.isArray(runs) ? runs : [runs] });
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const para = (t) => new Paragraph({ spacing: { after: 140 }, alignment: AlignmentType.JUSTIFIED, children: [new TextRun({ text: t, size: 22 })] });
const bullet = (t) => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 70 }, children: [new TextRun({ text: t, size: 22 })] });

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
    center(c("June 2026", { size: 22 }), { after: 0 }),
  ];
}

// ---------- Abstract signature block ----------
function sigBlock() {
  const cell = (lines) => new TableCell({ borders: NOBORDER, width: { size: 4680, type: WidthType.DXA },
    margins: { top: 80, bottom: 40, left: 60, right: 60 },
    children: lines.map(l => new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: l, size: 22 })] })) });
  return new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: [4680, 4680],
    rows: [new TableRow({ children: [
      cell(["Signature of the Student", "Name:", "Date:", "Place:"]),
      cell(["Signature of the Supervisor", "Name:", "Date:", "Place:"]),
    ] })] });
}

function tocLine(text, page, bold) {
  return new Paragraph({ spacing: { after: 60 }, tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX, leader: "dot" }],
    children: [new TextRun({ text, size: 22, bold }), new TextRun({ text: "\t" + page, size: 22, bold })] });
}

// ========================================================= Build document
const children = [];

// Title pages (two)
titlePage().forEach(p => children.push(p));
children.push(new Paragraph({ children: [new PageBreak()] }));
titlePage().forEach(p => children.push(p));
children.push(new Paragraph({ children: [new PageBreak()] }));

// Abstract
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "ABSTRACT", bold: true, size: 28, color: INK })] }));
children.push(para("SmartEdit AI is an intelligent personal finance management web application designed for Indian salaried users. The system reads a user's bank statement — uploaded as a PDF or CSV — extracts every transaction, classifies cryptic Indian payment descriptions (UPI, NEFT, NACH, POS, IMPS) into meaningful expense categories, and presents a clear financial dashboard of income, expenses, savings and category-wise spending trends."));
children.push(para("Indian bank statements are not standardised: SBI, HDFC, ICICI and Axis each issue statements in different layouts, and transaction descriptions are cryptic abbreviations that convey little to the user. SmartEdit AI addresses three gaps that no existing tool solves together — structured extraction of transactions from Indian bank statements, automatic India-aware classification, and an AI advisory layer that reads the user's actual financial pattern to generate specific, reasoned, rupee-level savings suggestions rather than generic tips."));
children.push(para("The application is built with Flask and SQLite. Statement parsing uses pdfplumber and pandas; transaction classification uses an interpretable, India-aware rule engine. The AI advisory and a Retrieval-Augmented Generation (RAG) chatbot are powered by a large language model accessed through a swappable provider layer (Gemini API in the current build, with a fully local Ollama model planned for the privacy-first final version). The RAG chatbot embeds the user's transactions and uses cosine-similarity search together with exact SQL aggregates so that answers are grounded in real data and never hallucinated. This mid-semester report describes the system design, methodology, implementation status and plan of work to completion."));
children.push(new Paragraph({ spacing: { before: 300 }, children: [new TextRun("")] }));
children.push(sigBlock());
children.push(new Paragraph({ children: [new PageBreak()] }));

// Contents
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [new TextRun({ text: "CONTENTS", bold: true, size: 28, color: INK })] }));
children.push(new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-1" }));
children.push(new Paragraph({ spacing: { before: 200, after: 80 }, children: [new TextRun({ text: "List of Figures", bold: true, size: 24, color: BLUED })] }));
[["Figure 1: System Architecture", ""], ["Figure 2: Entity-Relationship Diagram", ""], ["Figure 3: Data-Flow Diagram", ""],
 ["Figure 4: Sequence Diagram — RAG Chatbot Query", ""], ["Figure 5: Use-Case Diagram", ""], ["Figure 6: Class Diagram", ""],
 ["Figure 7: Sequence Diagram — Statement Upload", ""], ["Figure 8: Component Diagram", ""]].forEach(([t, p]) => children.push(tocLine(t, p)));
children.push(new Paragraph({ spacing: { before: 160, after: 80 }, children: [new TextRun({ text: "List of Tables", bold: true, size: 24, color: BLUED })] }));
[["Table 1: Implementation Status", ""], ["Table 2: Plan of Work (Future Plan)", ""], ["Table 3: Abbreviations", ""]].forEach(([t, p]) => children.push(tocLine(t, p)));
children.push(new Paragraph({ children: [new PageBreak()] }));

// 1. Introduction
children.push(h1("1. INTRODUCTION"));
children.push(para("Almost every salaried person, at the end of the month, opens their bank account and wonders where the money went. The rent is remembered and a few grocery runs, but the rest — food delivery, random UPI transfers, forgotten subscriptions — is a blur. The statement exists as a PDF, but reading 80 rows of strings such as 'POS-4521-RELIANCE' or 'UPI-SWIGGY-OKAXIS-XXXX' communicates almost nothing useful."));
children.push(para("SmartEdit AI is a web application that turns this raw statement into understanding. It reads the statement, classifies every transaction, shows where the money went, and provides AI-generated, data-grounded savings advice through both an advisory panel and a conversational chatbot. The objectives of the project are: to build a web app accepting PDF/CSV statements and manual entries; to parse Indian bank statement formats; to classify cryptic descriptions into categories; to present a finance dashboard; to generate explainable AI savings advice; to provide a RAG chatbot; and to support a fully local LLM for privacy in the final version."));

// 2. Modules
children.push(h1("2. MODULES IN SMARTEDIT AI"));
children.push(para("SmartEdit AI is organised as a modular client–server system. A lightweight white-and-blue web frontend communicates over HTTP with a Flask application server composed of six cooperating modules. The major components are listed below and illustrated in Figure 1."));
["Authentication & Session — registration, login, hashed passwords and session management.",
 "Statement Parser — extracts transactions from uploaded PDF/CSV bank statements (pdfplumber, pandas).",
 "Transaction Classifier — India-aware rule engine mapping descriptions to 17 expense categories.",
 "Analytics Engine — computes monthly summaries, savings rate, category breakdowns and trends.",
 "AI Advisory — generates specific, rupee-level savings advice via a swappable LLM provider.",
 "RAG Chatbot — answers free-form questions using transaction embeddings, cosine search and SQL aggregates."].forEach(t => children.push(bullet(t)));

// 3. Architecture / Functional block
children.push(h1("3. SYSTEM ARCHITECTURE / FUNCTIONAL BLOCK DIAGRAM"));
children.push(para("The frontend renders the Dashboard, Add-Entry, View/Database, Tracker and Chat screens, and communicates with the Flask server, which coordinates the six modules above. All data persists in a single SQLite database holding users, transactions, embeddings and chat history. The AI provider is abstracted behind a common interface, allowing the system to switch from the Gemini API (current build) to a local Ollama model (final build) without any other code change. The functional block diagram is shown in Figure 1."));
children.push(img("01_system_architecture.png", 600, 300));
children.push(caption("Figure 1: System Architecture of SmartEdit AI"));

// 4. Methodology
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h1("4. METHODOLOGY"));
children.push(h2("4.1 Statement Parsing"));
children.push(para("The parser dispatches by file type. CSV files are read with pandas, auto-mapping common Indian column names (Date, Narration/Particulars, Debit/Credit, Withdrawal/Deposit). PDF statements are parsed with pdfplumber, which extracts tables page by page. Each row is normalised into a (date, description, amount, type) tuple, handling mixed date formats, Indian thousands separators (e.g. 1,23,456.00), separate debit/credit columns and multi-line descriptions."));
children.push(h2("4.2 Transaction Classification"));
children.push(para("Classification uses an interpretable, India-aware rule engine that scans the raw description for keyword patterns and maps it to one of seventeen categories — for example SWIGGY/ZOMATO to Food & Dining, LIC/PREMIUM to Insurance, NETFLIX/SPOTIFY to Subscriptions, AMAZON/FLIPKART to Shopping. Payment-method markers (UPI, NEFT, NACH, POS, IMPS) are detected and stored separately for reporting. Descriptions matching no rule fall to 'Others' and can be re-categorised by the user; these flagged cases motivate the lightweight ML classifier planned for the next phase. The end-to-end data flow is shown in Figure 3."));
children.push(img("07_data_flow.png", 600, 250));
children.push(caption("Figure 3: Data-Flow Diagram"));

// 5. Database design
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h1("5. DATABASE DESIGN"));
children.push(para("The schema comprises four tables. A user owns many transactions and chat messages; each transaction has exactly one embedding vector used by RAG retrieval. This normalised design keeps the data model simple while supporting analytics, full transaction history and semantic search. The entity-relationship diagram is shown in Figure 2."));
children.push(img("04_er_diagram.png", 600, 250));
children.push(caption("Figure 2: Entity-Relationship Diagram of the SmartEdit AI Database"));

// 6. AI advisory & RAG
children.push(h1("6. AI ADVISORY AND RAG CHATBOT"));
children.push(h2("6.1 AI Savings Advisory"));
children.push(para("The advisory module builds a chain-of-thought prompt from the categorised monthly summary and month-on-month trend, then calls the active LLM provider. The result is specific and quantified — for example, 'your Swiggy and Zomato spend this month is Rs.1,348; capping to three orders per week would save approximately Rs.800 next month' — rather than generic advice. When no provider is reachable, a deterministic rule-based advisor produces equivalent rupee-level guidance so demonstrations never fail."));
children.push(h2("6.2 Retrieval-Augmented Generation"));
children.push(para("The chatbot follows a classic RAG pipeline. The user's question is embedded with a sentence-transformers model (all-MiniLM-L6-v2, 384 dimensions); the same embeddings are pre-computed for every stored transaction. Cosine similarity performs a symmetric search to retrieve the most relevant transactions. In parallel, exact SQL aggregates are computed for any merchant or category the user names, so quantitative answers are precise and never hallucinated. Retrieved rows plus aggregates are injected into the LLM prompt to produce a grounded natural-language answer, as shown in Figure 4."));
children.push(img("06_sequence_chat_rag.png", 600, 320));
children.push(caption("Figure 4: Sequence Diagram — RAG Chatbot Query"));

// 7. System design diagrams
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h1("7. SYSTEM DESIGN DIAGRAMS"));
children.push(h2("7.1 Use-Case Diagram"));
children.push(img("02_use_case.png", 600, 300));
children.push(caption("Figure 5: Use-Case Diagram"));
children.push(h2("7.2 Class Diagram"));
children.push(img("03_class_diagram.png", 520, 360));
children.push(caption("Figure 6: Class Diagram"));
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h2("7.3 Sequence Diagram — Statement Upload"));
children.push(img("05_sequence_upload.png", 600, 300));
children.push(caption("Figure 7: Sequence Diagram — Statement Upload"));
children.push(h2("7.4 Component Diagram"));
children.push(img("08_component_diagram.png", 460, 360));
children.push(caption("Figure 8: Component Diagram"));

// 8. Implementation status & results
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h1("8. IMPLEMENTATION STATUS AND RESULTS"));
children.push(para("The core application is implemented and verified end-to-end. The technology stack is Flask, SQLAlchemy over SQLite, pdfplumber and pandas for parsing, sentence-transformers for embeddings, and a provider-abstracted LLM layer. On a representative one-month sample statement of thirty transactions, the parser extracted all rows correctly, the classifier assigned them across categories including Income, Food & Dining, Groceries, Transport, Subscriptions, Shopping, Utilities, Insurance, EMI/Loans, Investments, Entertainment and Health, the dashboard computed total income, expenses, savings and savings rate, and the chatbot returned exact totals for merchant queries using the SQL-aggregate grounding."));
children.push(table(["Module", "Status", "Notes"],
  [["Authentication", "Complete", "Register/login, hashed passwords, sessions"],
   ["Statement parser", "Complete", "CSV + PDF; Indian column auto-mapping"],
   ["Classifier", "Complete", "17 categories; UPI/NEFT/NACH/POS aware"],
   ["Dashboard & analytics", "Complete", "Income/expense/savings, category chart"],
   ["Tracker", "Complete", "Daily/monthly/weekday charts"],
   ["AI advisory", "Complete", "Gemini + deterministic fallback"],
   ["RAG chatbot", "Complete", "Embeddings + cosine + SQL aggregates"],
   ["Ollama local model", "Pending", "Provider swap in final phase"],
   ["ML classifier", "Pending", "For ambiguous descriptions"]],
  [2200, 1700, 5460]));
children.push(caption("Table 1: Implementation Status"));

// 9. Future plan
children.push(h1("9. FUTURE PLAN"));
children.push(table(["Sl No", "Phase", "Start Date – End Date", "Work to be done", "Status"],
  [["1", "Dissertation outline", "Completed", "Literature review; system design & outline", "COMPLETED"],
   ["2", "Core development", "Completed", "Parser, classifier, dashboard, advisory, RAG chat", "COMPLETED"],
   ["3", "Enhancement", "Now – Wk 4", "More bank PDF formats; ML classifier for edge cases", "IN PROGRESS"],
   ["4", "Salary module", "Wk 5 – 6", "Indian CTC/PF/HRA/TDS model and savings goals", "PENDING"],
   ["5", "Local AI", "Wk 7 – 8", "Swap Gemini to local Ollama; evaluate advisory", "PENDING"],
   ["6", "Submission", "Wk 9 – 10", "End-to-end testing, documentation, final demo", "PENDING"]],
  [800, 1900, 1900, 3260, 1500]));
children.push(caption("Table 2: Plan of Work (Future Plan)"));

// 10. Abbreviations
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h1("10. ABBREVIATIONS"));
children.push(table(["Abbreviation", "Expansion"],
  [["AI", "Artificial Intelligence"], ["API", "Application Programming Interface"],
   ["CSV", "Comma-Separated Values"], ["CTC", "Cost To Company"],
   ["EMI", "Equated Monthly Instalment"], ["HRA", "House Rent Allowance"],
   ["IMPS", "Immediate Payment Service"], ["LLM", "Large Language Model"],
   ["NACH", "National Automated Clearing House"], ["NEFT", "National Electronic Funds Transfer"],
   ["NLP", "Natural Language Processing"], ["ORM", "Object-Relational Mapping"],
   ["PDF", "Portable Document Format"], ["PF", "Provident Fund"],
   ["POS", "Point Of Sale"], ["RAG", "Retrieval-Augmented Generation"],
   ["SQL", "Structured Query Language"], ["TDS", "Tax Deducted at Source"],
   ["UPI", "Unified Payments Interface"]],
  [2800, 6560]));
children.push(caption("Table 3: Abbreviations"));

// References
children.push(h1("11. REFERENCES"));
["Devlin, J. et al. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. NAACL.",
 "Wei, J. et al. (2022). Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. NeurIPS.",
 "Kang, S. & Ma, J. (2021). Automated Personal Finance Management Using NLP and Machine Learning. IEEE Big Data.",
 "Thaler, R. H. & Sunstein, C. R. (2008). Nudge: Improving Decisions About Health, Wealth, and Happiness. Yale University Press.",
 "Reserve Bank of India (2023). Annual Report on Digital Payments in India.",
 "pdfplumber — https://github.com/jsvine/pdfplumber ; sentence-transformers — https://www.sbert.net ; Ollama — https://ollama.com"]
 .forEach(t => children.push(bullet(t)));

// ---------- Document ----------
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Times New Roman", size: 24, color: INK } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, color: INK, font: "Times New Roman" }, paragraph: { spacing: { before: 240, after: 140 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: BLUED, font: "Times New Roman" }, paragraph: { spacing: { before: 160, after: 100 }, outlineLevel: 1 } },
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
