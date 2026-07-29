// SmartEdit AI — Final Knowledge Transfer Guide (docx-js)
// Owned exclusively by this script. Do not merge with make_kt.js.
const fs = require("fs");
const path = require("path");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
        Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
        WidthType, ShadingType, PageNumber, PageBreak } = require("docx");

const DIR = process.env.DIAGRAMS || path.join(__dirname, "diagrams");
const OUT = process.env.OUTFILE || path.join(__dirname, "SmartEditAI_KT_Guide.docx");
const BLUE = "1A73E8", BLUED = "1457B8", INK = "1F2733", GREY = "6B7787", GREEN = "1AA260", RED = "C0392B";
const PAGE_W = 9360; // usable width in DXA (Letter, 1in margins)

// ---------------------------------------------------------------- helpers
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const h3 = (t) => new Paragraph({ spacing: { before: 160, after: 70 }, children: [new TextRun({ text: t, bold: true, size: 22, color: BLUED })] });
const para = (t) => new Paragraph({ spacing: { after: 190, line: 300 }, alignment: AlignmentType.JUSTIFIED, children: [new TextRun({ text: t, size: 22 })] });
const paraR = (runs) => new Paragraph({ spacing: { after: 190, line: 300 }, alignment: AlignmentType.JUSTIFIED, children: runs });
const bullet = (t) => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 100, line: 290 }, children: [new TextRun({ text: t, size: 22 })] });
const num = (t) => new Paragraph({ numbering: { reference: "stp", level: 0 }, spacing: { after: 110, line: 290 }, children: [new TextRun({ text: t, size: 22 })] });
const code = (t) => new Paragraph({ spacing: { after: 60 }, shading: { fill: "F0F4FA", type: ShadingType.CLEAR },
  children: [new TextRun({ text: t, font: "Consolas", size: 19, color: "0B3D91" })] });
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });
const qHead = (t) => new Paragraph({ spacing: { before: 220, after: 60 }, children: [new TextRun({ text: t, bold: true, size: 22, color: BLUED })] });
const ans = (t) => new Paragraph({ spacing: { after: 190, line: 300 }, alignment: AlignmentType.JUSTIFIED, children: [new TextRun({ text: "A. ", bold: true, size: 22, color: GREEN }), new TextRun({ text: t, size: 22 })] });

function table(headers, rows, widths) {
  const border = { style: BorderStyle.SINGLE, size: 1, color: "CCD6E6" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const head = new TableRow({ tableHeader: true, children: headers.map((h, i) =>
    new TableCell({ borders, width: { size: widths[i], type: WidthType.DXA }, shading: { fill: BLUED, type: ShadingType.CLEAR },
      margins: { top: 60, bottom: 60, left: 110, right: 110 }, children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: "FFFFFF", size: 19 })] })] })) });
  const rws = rows.map((r, ri) => new TableRow({ children: r.map((c, i) =>
    new TableCell({ borders, width: { size: widths[i], type: WidthType.DXA }, shading: { fill: ri % 2 ? "F2F6FC" : "FFFFFF", type: ShadingType.CLEAR },
      margins: { top: 60, bottom: 60, left: 110, right: 110 }, children: [new Paragraph({ children: [new TextRun({ text: c, size: 19 })] })] })) }));
  return new Table({ width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths, rows: [head, ...rws] });
}

function figure(file, n, caption, wPx, hPx) {
  try {
    return [
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 180, after: 60 },
        children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(DIR, file + ".png")),
          transformation: { width: wPx, height: hPx }, altText: { title: file, description: caption, name: file } })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 220 },
        children: [new TextRun({ text: `Figure ${n}. ${caption}`, italics: true, size: 18, color: GREY })] }),
    ];
  } catch (e) { return [para(`[Figure ${n} — ${file}.png could not be loaded]`)]; }
}

// ---------------------------------------------------------------- cover
const cover = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 700, after: 100 },
    children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(DIR, "logo.png")),
      transformation: { width: 320, height: 117 }, altText: { title: "logo", description: "SmartEdit AI", name: "logo" } })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 260, after: 60 },
    children: [new TextRun({ text: "Knowledge Transfer Guide", bold: true, size: 42, color: BLUED, font: "Georgia" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 },
    children: [new TextRun({ text: "SmartEdit AI — An Intelligent Personal Finance Web Application", size: 24, color: INK })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 320 },
    children: [new TextRun({ text: "for Indian Salaried Users", size: 24, color: INK })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 },
    children: [new TextRun({ text: "Student: Shyam Sundar", size: 22, bold: true, color: INK })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 },
    children: [new TextRun({ text: "Programme: (Insert programme name)", size: 20, color: GREY })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 },
    children: [new TextRun({ text: "Course: BITS ZG628T — Dissertation", size: 20, color: GREY })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 },
    children: [new TextRun({ text: "Student ID: (Insert student ID)", size: 20, color: GREY })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 },
    children: [new TextRun({ text: "Organisation: (Insert organisation)", size: 20, color: GREY })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 },
    children: [new TextRun({ text: "Supervisor: (Insert supervisor name)", size: 20, color: GREY })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 340, after: 200 },
    children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(DIR, "bits_logo.png")),
      transformation: { width: 88, height: 86 }, altText: { title: "bits", description: "BITS Pilani", name: "bits" } })] }),
  new Paragraph({ alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "BITS Pilani — Work Integrated Learning Programmes", size: 20, bold: true, color: INK })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
    children: [new TextRun({ text: "2026", size: 18, color: GREY })] }),
  pageBreak(),
];

// ---------------------------------------------------------------- body
const body = [];

// 1. How to read this guide
body.push(h1("1. How to Read This Guide"));
body.push(para("This guide is written for a reader who did not build SmartEdit AI but who must be able to run it, explain it, and defend it — in a viva, in a handover conversation, or while maintaining it later. It assumes no prior knowledge of the codebase and builds understanding in layers."));
body.push(para("Section 3 gets the application running from nothing. Sections 4 and 5 build a mental model of what appears on screen and what produced it, page by page and then module by module. Section 6 is deliberately argumentative: it collects the design decisions an examiner is most likely to probe and states the reasoning behind each one, so it can be defended out loud rather than merely recited. Section 7 is a bank of likely viva questions with model answers, grounded in the same facts used throughout this guide. Section 8 is a script for a live demonstration, with the exact clicks and the exact questions to type. Sections 9 and 10 are for when something does not work as expected, and for looking up an unfamiliar term."));
body.push(para("Read the guide once from the start to build the full picture; afterwards, use the headings to jump straight to the part that is needed."));

body.push(h1("2. If You Only Remember Five Things"));
body.push(bullet("SmartEdit AI reads Indian bank statements — inconsistent across banks and full of cryptic narrations — and turns them into readable spending information for salaried users. Everything else in the system exists to support that one job."));
body.push(bullet("The application has four layers: a server-rendered browser front end, a Flask application built from eight modules, an on-device language model, and a SQLite database reached through the SQLAlchemy ORM."));
body.push(bullet("Every rupee figure the chatbot states is computed by a real SQLAlchemy aggregate in nlq.py. The language model is handed the finished sentence and asked only to reword it, and a guard discards its reply if it invents, recalculates, or misstates a figure."));
body.push(bullet("The transaction classifier applies rules first, at full confidence, and tests generic payment-rail keywords such as UPI and NEFT only after merchant-specific keywords, so a UPI payment to a known merchant keeps its real category instead of collapsing into Transfers."));
body.push(bullet("Once its one-time download of roughly 1.5 GB is complete, the system runs entirely on the local machine with no dependency on an external AI service, and this behaviour is verified by 172 automated tests together with a live run against real imported data."));

// 3. Setup and first run
body.push(pageBreak());
body.push(h1("3. Setup and First Run"));
body.push(h2("3.1 What setup.bat Does"));
body.push(para("setup.bat is the single entry point for preparing a fresh machine to run SmartEdit AI. It performs the following steps, in order:"));
body.push(num("Locates a usable Python installation on the machine."));
body.push(num("Creates a dedicated virtual environment for the project, so its dependencies never collide with anything else installed on the machine."));
body.push(num("Installs the core Python requirements into that environment."));
body.push(num("Installs llama-cpp-python and torch from prebuilt CPU wheel indexes, rather than building them from source, so the client machine needs no C++ compiler."));
body.push(num("Runs tools/first_run_setup.py, which writes the application's settings file, downloads the 1,066 MB language model with a visible progress bar, caches the sentence-embedding model used by the chatbot, trains the transaction classifier if its model file is not already present, and creates the SQLite database."));
body.push(para("Taken together, about 1.5 GB is downloaded once. After that first run, starting the application again does not repeat any of these downloads."));
body.push(h2("3.2 What run.bat Does"));
body.push(para("run.bat starts the Flask application server and opens the default browser to it. This is the script used every time after the first setup — it does not repeat any installation or download step."));
body.push(h2("3.3 Where the Data Lives"));
body.push(para("All application data — accounts, transactions, salary profiles, savings goals, budgets, chat history, and cached embeddings — lives in a single SQLite database file created during first-run setup. The database location is configurable rather than hard-coded; this was in fact a deliberate late fix (see Section 5's discussion of the live-run defects), because Flask-SQLAlchemy binds its engine when the application initialises, and a configurable location was needed so the database file can be relocated and so automated tests can point at a separate, disposable database instead of the real one."));
body.push(para("ensure_schema() runs on every application start and adds any table or column that is missing from an existing database, without touching data that is already there. This means upgrading the code to a newer version never loses data that was already recorded."));
body.push(h2("3.4 Resetting to a Clean State"));
body.push(para("To start again from an empty account: stop the server, then delete the SQLite database file that first-run setup created. The next time the server starts, ensure_schema() recreates every table from nothing. The downloaded model, the cached embedding model, and the trained classifier file do not need to be re-downloaded or retrained — only the data file itself needs to be removed. If the settings file itself also needs to be regenerated, rerun tools/first_run_setup.py directly rather than the full setup.bat, since the large downloads are skipped automatically once the model file is already present on disk."));

// 4. Guided tour
body.push(pageBreak());
body.push(h1("4. A Guided Tour of the Eleven Pages"));
body.push(para("Every page in SmartEdit AI is server-rendered HTML with vanilla JavaScript and Chart.js, all served from the application itself rather than fetched from a CDN — so the interface works even with no internet connection. Underneath every page sits the same seven-table SQLite database, reached through SQLAlchemy: users, transactions, embeddings, chat_history, salary_profiles, savings_goals and budgets."));

body.push(...figure("04_er_diagram", 1, "Entity-relationship diagram of the seven tables behind every page — users, transactions, embeddings, chat_history, salary_profiles, savings_goals and budgets.", 520, Math.round(520/1.380)));

body.push(para("The table below lists all eleven pages, what each one shows, and which backend module is responsible for the numbers on it."));
body.push(table(
  ["Page", "What it shows", "Where its numbers come from"],
  [
    ["Login", "Credential form and the session guard that protects every other page.", "Authentication & Session"],
    ["Register", "Account creation. Passwords are hashed before they are stored; a duplicate email is rejected.", "Authentication & Session"],
    ["Dashboard", "This period's income, expenses, savings, a category chart, and AI advice. For a brand-new account it asks for a statement upload instead.", "Analytics Engine + AI Advisory"],
    ["Add Entry", "Manual entry of a single credit or debit. Leaving the category blank lets the classifier assign one automatically.", "Transaction Classifier"],
    ["View / Database", "The full table of transactions, with re-categorisation and filtering. Every row was produced by the parser or entered manually, and every row carries a stored fingerprint.", "Statement Parser + Transaction Classifier"],
    ["Tracker", "Daily, monthly and weekday trend series of money in versus money out.", "Analytics Engine"],
    ["Salary & Tax", "CTC breakdown, HRA exemption, PF, gratuity and a side-by-side comparison of the old and new tax regimes.", "Salary & Tax"],
    ["Goals", "Savings goals set by the user and progress against them.", "Analytics Engine (savings_goals table)"],
    ["Budget", "Budgets set per category and whether the current period is over or under.", "Analytics Engine (budgets table)"],
    ["Insights", "Deterministic, plain-language observations — month-on-month change, a category over 30% of spend, weekend-versus-weekday split, the largest single transaction, days with no spend, food-delivery total, annualised cost of standing charges, and the savings rate against a 20% benchmark.", "Analytics Engine"],
    ["AI Chat", "A conversational box where the user asks free-form questions about their own spending.", "Natural-Language Query Engine + RAG Chatbot + on-device model"],
  ],
  [1600, 5960, 1800]
));

// 5. Module by module
body.push(pageBreak());
body.push(h1("5. Module-by-Module Walkthrough"));
body.push(para("SmartEdit AI's backend is a Flask application built from eight modules sitting on top of a SQLite database reached through the SQLAlchemy ORM, with a fourth, separate layer for on-device language-model inference. This section covers each module in turn: what problem it solves, how it works, and the two or three design decisions worth being able to defend."));

body.push(...figure("01_system_architecture", 2, "SmartEdit AI's four-layer architecture — browser front end, Flask application with its eight modules, on-device inference, and SQLite via SQLAlchemy.", 560, Math.round(560/1.266)));

body.push(h2("5.1 Authentication & Session"));
body.push(para("Problem it solves: no user should ever be able to see or act on another user's financial data, and passwords must never be recoverable in the clear."));
body.push(para("How it works: registration and login forms sit in front of every other page. A session guard is enforced on every route in the application — this is not left to the individual page to check — and passwords are hashed before they are ever written to the database."));
body.push(para("Design decisions worth defending: the session guard is applied uniformly rather than page by page, which is why the automated route tests can assert that every single page requires a login rather than listing exceptions; and duplicate-email registration is rejected at the point of registration rather than left to fail later."));

body.push(h2("5.2 Statement Parser — parser.py"));
body.push(para("Problem it solves: Indian bank statements are not standardised. SBI, HDFC, ICICI and Axis each export a different column layout, with account details and blank rows above the real table, and narrations that mean nothing on their own."));
body.push(para("How it works: the parser scans the first 25 rows of a file and scores each one as a candidate header, because real exports from these banks put account details and blank lines above the actual transaction table. It holds per-bank column alias maps and recognises HDFC, ICICI, Axis, SBI, Kotak, PNB, Bank of Baroda, Canara, Yes Bank, IDFC First and IndusInd. It understands Indian amount formats such as 1,23,456.00, Rs. 4,500, and (2,000.50) for a withdrawal, along with a trailing Dr or Cr, and it understands several date formats including dd/mm/yyyy, dd-mm-yyyy, yyyy-mm-dd and dd Mon yyyy. The direction of each entry — money in or money out — is resolved in a fixed order: an explicit Dr/Cr column first, then a Dr/Cr suffix on the value itself, then the sign of the number, and only if none of those are present, the movement of the running balance. PDFs that have no ruled table fall back to line-by-line regular-expression parsing of the extracted text. Opening-balance, closing-balance, sub-total and page-number rows are recognised and rejected, and counted as skipped rather than silently imported. A password-protected PDF raises a plain-English message rather than a stack trace."));
body.push(...figure("10_parser_pipeline", 3, "Statement parser pipeline — header scoring, per-bank column mapping, amount and date normalisation, and direction resolution.", 540, Math.round(540/1.207)));

body.push(para("Measured on the bundled sample statements:"));
body.push(table(
  ["File", "Bank detected", "Rows", "Skipped"],
  [
    ["sample_statement.csv", "Unknown", "30", "0"],
    ["hdfc_statement.csv", "HDFC", "40", "0 (6 preamble rows above the header)"],
    ["icici_statement.csv", "ICICI", "35", "0 (single Amount column with a Dr/Cr column)"],
    ["axis_statement.csv", "Axis", "30", "1 (opening balance; direction taken from balance movement)"],
    ["sample_statement.pdf", "Unknown", "30", "1 (no ruled table; text fallback used)"],
  ],
  [2600, 1900, 1500, 3360]
));
body.push(para("Design decisions worth defending: scoring candidate header rows over the first 25 rows, instead of assuming row one is the header, is what makes the six-row HDFC preamble harmless; resolving direction through a fixed order of signals rather than picking one signal always is what correctly reads an Axis statement that carries no explicit Dr/Cr marker; and treating balance, sub-total and page-number rows as skipped rather than importing them keeps every imported total honest."));

body.push(h2("5.3 Transaction Classifier — classifier.py"));
body.push(para("Problem it solves: once a transaction is extracted, it still needs a category, and bank narrations such as UPI-SWIGGY-OKAXIS-XXXX1234 give no direct clue."));
body.push(para("How it works: the classifier sorts every transaction into one of 17 categories — Income, Rent, EMI / Loans, Insurance, Investments, Subscriptions, Food & Dining, Groceries, Transport, Utilities, Shopping, Health, Education, Entertainment, Travel, Transfers and Others. Rules run first and, when they match, return a confidence of 1.0. Payment-rail keywords — UPI, NEFT, IMPS, RTGS, PhonePe, GPay, Paytm — are deliberately tested last, so a UPI payment to Swiggy is filed as Food & Dining, and only a payment with no identifiable merchant becomes Transfers. Keywords shorter than four characters are matched on a word boundary rather than as a plain substring, because a plain substring search once matched EMI inside PREMIUM and filed an LIC insurance premium under EMI / Loans. Whatever the rules cannot place is handed to a trained model: TF-IDF character n-grams (char_wb, 2 to 5 characters) feeding a logistic regression, trained on 746 labelled Indian narrations held in data/category_seed.csv and persisted to data/category_model.joblib. Its held-out accuracy is 64.7% — deliberately measured on a seed corpus weighted towards ambiguous narrations, since the unambiguous ones are already resolved by the rules before the model is ever consulted. Any model prediction below 0.35 confidence falls back to Others rather than guessing. The module recognises fourteen payment-rail markers in total: UPI, NEFT, IMPS, RTGS, NACH, ECS, ACH, POS, ATM-CW, CHQ, INB, MB, CARD and EMI. If scikit-learn is not installed, the module still imports and runs on rules alone."));
body.push(para("Design decisions worth defending: testing payment rails last rather than first, so a rail marker never overrides a known merchant; matching short keywords on a word boundary rather than as a substring, which is the direct fix for the PREMIUM/EMI trap; and degrading to rules-only rather than failing outright when scikit-learn is unavailable."));

body.push(...figure("11_classifier_flow", 4, "Classifier flow — rules first at full confidence, payment rails tested last, the trained model for whatever remains.", 560, Math.round(560/1.180)));

body.push(h2("5.4 Analytics Engine — analytics.py"));
body.push(para("Problem it solves: a table of categorised transactions is not, by itself, an insight. Something has to turn rows into a period summary, a trend, and a plain-language observation."));
body.push(para("How it works: the engine produces period summaries; daily, monthly and weekday trend series; category breakdowns; top-merchant lists; month-over-month comparisons; budget status per category; and recurring-commitment detection. Recurring detection is deliberately restricted to Subscriptions, Utilities, Insurance, EMI / Loans, Rent and Investments, because a supermarket visited every week is a habit, not a standing charge. A merchant qualifies as recurring once it appears in two or more distinct months within 15% of its median amount, and the cadence — monthly, quarterly, and so on — is decided from the number of distinct months the charge appears in, rather than from the raw gap between two charges. This distinction mattered in practice: two statements that happened to cover the same calendar period otherwise read as a weekly rhythm and inflated a genuine Rs.9,500 EMI to an annualised Rs.4.94 lakh. The insights the engine produces are all deterministic and always quote a real figure: month-on-month change and the category that drove it, a category taking more than 30% of spend, the weekend-versus-weekday split, the largest single transaction, days with no spend at all, food-delivery count and total, the annualised cost of standing charges, and the savings rate measured against a 20% benchmark."));
body.push(para("Design decisions worth defending: restricting recurring detection to a fixed set of categories rather than running it over everything; and deciding cadence from the count of distinct months rather than the raw day-gap between two charges, which is precisely what fixed the EMI-inflation bug described above."));

body.push(h2("5.5 Salary & Tax — salary.py"));
body.push(para("Problem it solves: an Indian salaried user's take-home pay depends on a chain of statutory percentages and two entirely different tax regimes, and getting any one step wrong changes every step after it."));
body.push(para("How it works, for FY 2025-26: basic pay defaults to 40% of CTC, HRA to 50% of basic. Employee and employer PF are each 12% of basic, capped at the Rs.15,000 statutory wage ceiling when the employee opts out of contributing on the full basic. Gratuity is 4.81% of basic. Gross pay is CTC minus employer PF minus gratuity. HRA exemption, available only under the old regime, is the least of three limbs: actual HRA received; rent paid minus 10% of basic; and 50% of basic in a metro city or 40% elsewhere. The standard deduction is Rs.75,000 under the new regime and Rs.50,000 under the old regime, and a 4% cess applies on the computed tax under both. The new regime's slabs are nil up to Rs.4 lakh, 5% from Rs.4–8 lakh, 10% from Rs.8–12 lakh, 15% from Rs.12–16 lakh, 20% from Rs.16–20 lakh, 25% from Rs.20–24 lakh and 30% above Rs.24 lakh, with a Section 87A rebate that brings tax to nil for taxable income up to Rs.12,00,000, and marginal relief immediately above that threshold. The old regime's slabs are nil up to Rs.2.5 lakh, 5% from Rs.2.5–5 lakh, 20% from Rs.5–10 lakh and 30% above Rs.10 lakh, with its own 87A rebate up to Rs.5,00,000. Professional tax of Rs.2,400 a year applies in Tamil Nadu, Karnataka, Maharashtra, West Bengal, Andhra Pradesh, Telangana, Gujarat and Madhya Pradesh."));
body.push(para("Design decisions worth defending: implementing marginal relief as its own explicit step rather than only the headline rebate, since it is exactly the calculation that changes just above the Rs.12,00,000 threshold; computing the three-limb HRA minimum rather than assuming one limb always wins; and capping employee PF at the statutory wage ceiling rather than always taking 12% of the full basic."));

body.push(...figure("13_salary_flow", 5, "Salary and tax computation flow, from CTC down to net monthly pay under both regimes.", 420, Math.round(420/0.853)));

body.push(h2("5.6 Natural-Language Query Engine — nlq.py"));
body.push(para("Problem it solves: a user should be able to type a question in plain English and get back an answer that is both correct and explainable — not a paragraph the model produced from nothing."));
body.push(para("How it works: nlq.parse_query turns the question into a structured query using regular expressions and keyword tables, with no language model involved at this stage, which is exactly why this step is fully explainable. nlq.execute then runs a real SQLAlchemy aggregate scoped to the signed-in user — every rupee figure in every chatbot answer originates here. The engine understands totals, counts, averages, largest, smallest, lists, breakdowns, top-N queries, period comparisons, summaries and advice requests; it understands this or last month, week, year, named months, spans such as last 3 months, explicit date ranges and financial years; and it understands everyday category words such as food, petrol, bills or clothes together with merchant names drawn from the user's own transactions rather than a fixed list. If a requested period has no data, the engine widens to the most recent month that does have data and says so explicitly in the answer."));
body.push(para("Design decisions worth defending: keeping query parsing fully rule-based rather than model-based, purely for explainability; deriving merchant vocabulary from the user's own data rather than a hard-coded list, so it works for any user's spending pattern; and widening silently-empty periods to the nearest month with data rather than returning an empty or misleading answer."));

body.push(h2("5.7 AI Advisory — advisor.py"));
body.push(para("Problem it solves: turning a categorised monthly summary into guidance a user can act on, rather than a chart with no recommendation attached."));
body.push(para("How it works: the module generates savings guidance from the figures the Analytics Engine has already computed, using the same provider ladder as the rest of the system — a local model first, Ollama if it happens to be running, Gemini only if the user has supplied a key, and a deterministic rule-based advisor as the final fallback, so an answer is always produced. During the live run recorded in Section 7, this module was the source of one of the two defects found and fixed: the dashboard advisory was, at one point, quoting savings figures the model had invented rather than figures the Analytics Engine had actually computed."));
body.push(para("Design decisions worth defending: using the same always-produces-an-answer provider ladder as the chatbot, so a missing key or missing internet connection never blocks the dashboard; and the fact that this module's failure — an invented figure reaching the user — is precisely what motivated the guard described below and in Section 6."));

body.push(h2("5.8 RAG Chatbot — rag.py"));
body.push(para("Problem it solves: answering a free-form question needs both supporting context from the user's real transactions and a numeric answer that can be trusted, and a small on-device model cannot be trusted to compute the number itself."));
body.push(para("How it works: sentence-transformers' all-MiniLM-L6-v2 model produces 384-dimensional embeddings, cached as JSON in the embeddings table, and cosine similarity — vectorised with numpy — retrieves the transactions most relevant to the question. These retrieved transactions are supporting context only; they are never the source of a rupee figure. The model is handed a sentence that nlq.execute has already computed and is asked only to reword it. A guard then inspects the model's reply and discards it, falling back to the deterministic sentence, if the reply quotes a figure that was never computed, shows arithmetic working, contains LaTeX, is written in the first person, opens with congratulations, or runs past three sentences. Multi-row answers — lists, category breakdowns, period comparisons — never reach the model at all, because a 1.5-billion-parameter model reliably garbles anything with more than one row of numbers in it."));

body.push(...figure("12_rag_pipeline", 6, "RAG pipeline — embed the question, retrieve supporting transactions by cosine similarity, compute the real figure by SQL, then ask the model only to reword the finished sentence.", 560, Math.round(560/1.687)));

body.push(para("Design decisions worth defending: the strict separation of retrieval (context), computation (SQL) and generation (wording only) into three distinct steps that never overlap; and the specific list of red flags the guard checks for, each one traced back to an actual failure observed while building the system — see Section 6.2 for the incident that produced this list."));

body.push(h2("5.9 On-Device Inference — llm_local.py"));
body.push(para("This sits outside the eight Flask modules as its own architectural layer, but every module above depends on it for generated text. It runs llama-cpp-python 0.3.34, installed from a prebuilt CPU wheel only 6.6 MB in size, so the client machine needs no compiler. The model is Qwen2.5-1.5B-Instruct, quantised to Q4_K_M in GGUF format, a 1,066 MB file downloaded once by the installer. Measured on the development machine, it takes 2.7 seconds to load and generates at 8.8 tokens per second, with a context window (n_ctx) of 4096 and a thread count equal to the number of CPU cores. The provider ladder used everywhere in the system tries the local model first, then Ollama if it happens to be running, then Gemini only if the user has supplied a key, and finally a deterministic rule-based advisor — an answer is always produced. In the default configuration, nothing leaves the machine."));

body.push(...figure("14_llm_fallback_chain", 7, "The provider fallback chain — local model, then Ollama, then Gemini with a supplied key, then the deterministic rule-based advisor. An answer is always produced.", 580, Math.round(580/2.435)));

body.push(h2("5.10 Test Coverage at a Glance"));
body.push(para("172 automated tests, all passing, sit across five files in tests/. Each one maps onto the modules above, and knowing which file to point to for which claim is worth having ready in a viva:"));
body.push(table(
  ["Test file", "What it proves, and which module it covers"],
  [
    ["test_parser.py", "Every sample layout, header detection below a preamble, balance-delta direction, noise rejection, and Indian amount and date formats — covers the Statement Parser."],
    ["test_classifier.py", "Category placement, rail-versus-merchant precedence, the PREMIUM/EMI trap, merchant normalisation, handle stripping and confidence — covers the Transaction Classifier."],
    ["test_salary.py", "Component reconciliation, statutory percentages, cess, regime differences, the HRA three-limb minimum, the PF ceiling, professional tax by state, slab rows summing to the tax, monotonic tax, and marginal relief across the whole relief band — covers Salary & Tax."],
    ["test_analytics.py", "Summary arithmetic, ordering, empty-month fallback, trend alignment, the recurring-commitment restriction, user isolation, budget overspend, fingerprint behaviour, and every function against an account with no data — covers the Analytics Engine."],
    ["test_chat.py", "Metric and period recognition, everyday category words, merchant matching, exact totals taken from SQL, the rule that no answer may contain an unexplained figure, readability with the model switched off, and each individual guard rejection reason — covers the Natural-Language Query Engine and the RAG Chatbot together."],
    ["test_routes.py", "Every page requires a login, every page renders for a brand-new account, registration and login, duplicate email, password never stored in the clear, statement upload, duplicate upload rejected, an unreadable file handled politely, manual entry, the chat endpoint, salary profile, savings goal, CSV export, re-categorisation, and that one account can neither read nor delete another account's transaction — covers Authentication & Session and every route in the application."],
  ],
  [2000, 7360]
));
body.push(para("A useful habit for a viva: if asked to justify any specific behaviour described in this guide, name the test file that exercises it before describing the behaviour itself — it turns a claim into a verifiable one."));

// 6. Why built this way
body.push(pageBreak());
body.push(h1("6. Why It Was Built This Way"));
body.push(para("This section collects the design decisions an examiner is most likely to probe, and states the reasoning behind each one directly, so it can be defended in conversation rather than read off a slide."));

body.push(h2("6.1 Why payment rails are tested last in the classifier"));
body.push(para("A payment rail such as UPI, NEFT or NACH tells you how money moved, not why. If rail keywords were tested first, every UPI payment — to Swiggy, to a landlord, to a friend — would collapse into the same generic bucket regardless of who was actually paid. Testing merchant-specific keywords first and rail keywords only as a last resort means a UPI payment to a recognised merchant keeps that merchant's real category, and only a payment with no identifiable merchant falls through to Transfers, which is the only case where 'the money moved by UPI' is actually the most useful thing that can be said about it."));

body.push(h2("6.2 Why the language model is never allowed to compute a figure"));
body.push(para("A 1.5-billion-parameter model is not reliable at arithmetic. During development, asked directly how much was spent on food given a total and a transaction count, the model attempted to divide one number by the other itself and emitted LaTeX instead of an answer. That single failure is the reason the model was removed from the calculation path entirely: nlq.execute computes every figure with a real SQLAlchemy aggregate before the model is ever invoked, and the model's only job afterwards is to reword a sentence that already contains the correct number. A guard then checks the model's output and discards it in favour of the original deterministic sentence if it shows any sign of having tried to compute something on its own."));

body.push(h2("6.3 Why multi-row answers bypass the model entirely"));
body.push(para("A list, a category breakdown, or a period comparison contains several numbers at once, and a small model reliably garbles multi-row output even when it correctly reworded a single-figure sentence moments earlier. Rather than trying to guard every possible way a multi-row answer could go wrong, the system routes these answer types around the model completely and returns the deterministic, database-computed text directly. This is a stronger guarantee than any output filter could give, because there is no generated text to check in the first place."));

body.push(h2("6.4 Why recurring-commitment detection is restricted by category"));
body.push(para("Any merchant visited repeatedly could technically be called 'recurring' — including a supermarket visited every week, which is a habit rather than a standing financial commitment. Restricting detection to Subscriptions, Utilities, Insurance, EMI / Loans, Rent and Investments keeps the feature meaningful: it surfaces the charges a user actually needs to plan around, rather than flooding the Insights page with routine weekly shopping."));

body.push(h2("6.5 Why a transaction fingerprint is stored"));
body.push(para("Every transaction is stamped with a SHA-1 fingerprint computed over the user, the date, the amount, the transaction type and the narration. This is what allows the system to recognise that a transaction has already been imported and to silently skip it, which is exactly what stops a user's statement being double-counted if it is uploaded a second time — by accident, or because the user was not sure whether the first upload had worked."));

body.push(h2("6.6 Why a quantised 1.5B model rather than a cloud API"));
body.push(para("A bank statement is among the most sensitive data a user could hand to any application. Running a small, quantised model on the user's own machine means nothing leaves it in the default configuration — there is no external service to trust with financial detail. It also means the application keeps working with no internet connection at all, which a cloud-only design cannot offer. The trade-off is capability: a 1.5-billion-parameter model is far weaker at open-ended reasoning than a large cloud model, which is precisely why the system never asks it to compute anything and only ever asks it to reword an answer that has already been produced deterministically."));

body.push(h2("6.7 Why the database location was made configurable"));
body.push(para("This was not part of the original design; it was forced by a defect the live run exposed. Flask-SQLAlchemy binds its database engine at init_app time, and a later attempt to point the application at a different database URI — specifically, so the automated route tests could run against a disposable database instead of the real one — was silently ignored, because the engine had already been created against the original path. The fix was to make the database location a genuine, respected configuration value rather than something fixed once at start-up. This mattered for two separate reasons at once: it stopped the test suite from writing to the real database, and it means the data file itself can now be relocated, backed up, or swapped without touching the application's code."));

// 7. Viva Q&A
body.push(pageBreak());
body.push(h1("7. Anticipated Viva Questions"));
body.push(para("These are grouped roughly from factual to probing. Each answer is written as something that can be said aloud in a few sentences, not read verbatim."));

const qa = [
["What does SmartEdit AI do, in one sentence?",
 "It reads a user's Indian bank statement, sorts every transaction into a category, and shows where the money went, with a chat assistant that can answer specific questions about the same data."],
["What problem does it actually solve?",
 "Indian bank statements are not standardised — SBI, HDFC, ICICI and Axis each use a different layout — and the narrations inside them are cryptic, such as UPI-SWIGGY-OKAXIS-XXXX1234 or NACH-LIC PREMIUM-AUTODEBIT. A salaried user cannot tell from eighty such rows where their money went; the application makes those rows legible."],
["Describe the architecture in four layers.",
 "A server-rendered browser front end using vanilla JavaScript and Chart.js; a Flask application server built from eight modules; an on-device inference layer running a quantised language model; and SQLite reached through the SQLAlchemy ORM."],
["What are the eight backend modules?",
 "Authentication & Session, the Statement Parser, the Transaction Classifier, the Analytics Engine, Salary & Tax, the Natural-Language Query Engine, AI Advisory, and the RAG Chatbot."],
["How many tables does the database have, and what is stored in transactions?",
 "Seven tables: users, transactions, embeddings, chat_history, salary_profiles, savings_goals and budgets. The transactions table holds id, user_id, date, description, raw_description, amount, txn_type, category, method, source, merchant, confidence, balance, fingerprint and created_at."],
["What is a transaction fingerprint and why does it exist?",
 "It is a SHA-1 hash computed over the user, date, amount, type and narration of a transaction. It is what stops a re-uploaded statement being imported twice — if the same transaction's fingerprint already exists for that user, the import silently skips it."],
["What does ensure_schema() do?",
 "It runs on every application start and adds any table or column missing from an existing database, in place, without touching existing data — so upgrading the code to a newer version never loses data that was already recorded."],
["Which file formats and banks does the parser support?",
 "CSV, XLSX and PDF, with per-bank column alias maps covering HDFC, ICICI, Axis, SBI, Kotak, PNB, Bank of Baroda, Canara, Yes Bank, IDFC First and IndusInd."],
["How does the parser find the header row when there is a preamble above it?",
 "It scans the first 25 rows of the file and scores each one as a candidate header, because real SBI and ICICI exports place account details and blank lines above the actual transaction table. The bundled HDFC sample, for example, has six such preamble rows and every one of its 40 transaction rows is still recovered correctly."],
["How does the parser decide whether an entry is money in or money out?",
 "In a fixed order of preference: an explicit Dr/Cr column first, then a Dr/Cr suffix on the value, then the sign of the number, and only if none of those are present, the movement of the running balance. The bundled Axis sample statement carries no explicit marker, so its direction is resolved entirely from balance movement."],
["What happens with a PDF that has no ruled table?",
 "The parser falls back to line-by-line regular-expression parsing of the extracted text, which is exactly how the bundled sample_statement.pdf is read."],
["What happens with a password-protected PDF?",
 "The parser raises a plain-English message rather than letting a low-level exception reach the user."],
["What happens if I upload the same statement twice?",
 "Nothing is imported the second time. Every transaction carries a fingerprint, and the second upload's fingerprints already exist for that user, so the import correctly recognises zero new rows — this is exactly what the live run on the finished build demonstrated."],
["How many categories does the classifier use, and how does it decide?",
 "Seventeen categories. Rules run first and return full confidence when they match; anything the rules cannot place goes to a trained model — TF-IDF character n-grams into logistic regression — and anything the model is not confident about falls back to Others."],
["Why is your classifier accuracy only 64.7%?",
 "That figure is the held-out accuracy of the fallback model alone, measured on a seed corpus that was deliberately weighted towards ambiguous narrations — the ones the rules cannot already resolve. The rules handle the unambiguous majority of real transactions at full confidence before the model is ever consulted, so 64.7% describes performance on the hard remainder, not on the system as a whole. It is an honest number precisely because the easy cases were not included to flatter it."],
["What is the PREMIUM/EMI trap and how was it fixed?",
 "A plain substring search for the keyword EMI matched inside the word PREMIUM, so an LIC insurance premium was being filed under EMI / Loans instead of Insurance. The fix restricts keywords shorter than four characters to word-boundary matching, so EMI matches the standalone word EMI and no longer matches as a fragment of PREMIUM."],
["Why are payment rails tested last rather than first in the classifier?",
 "Because a rail such as UPI describes how money moved, not why. Testing merchant keywords first means a UPI payment to Swiggy is correctly filed as Food & Dining; only a payment with no identifiable merchant falls through to the rail-based Transfers category."],
["What happens if scikit-learn is not installed?",
 "The classifier module still imports and runs — it simply operates on rules alone, with no fallback model available for the cases rules cannot resolve."],
["How do you know the chatbot is not making the numbers up?",
 "By construction, not by trust: the question is first parsed into a structured query with regular expressions, with no model involved; a real SQLAlchemy aggregate scoped to the signed-in user then computes the actual figure; the model is only shown that finished sentence and asked to reword it; and a guard inspects the model's reply afterwards and discards it — falling back to the original deterministic sentence — if it quotes a figure that was never computed, shows arithmetic working, contains LaTeX, is written in the first person, opens with congratulations, or runs past three sentences. Multi-row answers such as lists or breakdowns never go near the model at all."],
["What happens with no internet connection?",
 "The application keeps working. The local language model runs entirely on the machine, so answers and advice are still produced; retrieval and classification are also local. The only feature that specifically needs a key and a connection is the optional Gemini fallback, which is never required."],
["What happens if the model has not been downloaded?",
 "First-run setup is what downloads the 1,066 MB model file, and it shows a progress bar while doing so. If it is genuinely missing — for example the download was interrupted — the provider ladder simply moves to the next option: Ollama if it happens to be running, then Gemini if a key has been supplied, then the deterministic rule-based advisor. An answer is always produced; the system does not hang waiting for a model that is not there."],
["Why a quantised 1.5B local model instead of a cloud API?",
 "Privacy and availability. A bank statement is sensitive data, and running the model locally means nothing leaves the machine by default — there is no cloud service being trusted with it. It also means the application works with no internet connection at all. The cost is that a 1.5-billion-parameter model is weak at open-ended reasoning, which is exactly why it is never asked to compute anything, only to reword an answer that has already been computed deterministically."],
["Explain the recurring-commitment restriction by category.",
 "Detection only runs over Subscriptions, Utilities, Insurance, EMI / Loans, Rent and Investments. A merchant visited every week — a supermarket, for instance — would otherwise also look 'recurring', but that is a spending habit, not a standing financial commitment the user needs to plan around, so it is deliberately excluded."],
["What was the recurring-commitment cadence bug, and how was it fixed?",
 "Cadence was originally inferred from the raw gap in days between two charges from the same merchant. Two statements that happened to cover overlapping periods made a genuine Rs.9,500 EMI look like it recurred weekly, which annualised to Rs.4.94 lakh — nearly five times the real figure. The fix decides cadence from the number of distinct calendar months the charge appears in, rather than the day-gap between individual charges, which removed the false weekly reading."],
["How do you stop one user from seeing another user's data?",
 "Every route is behind a session guard, and every database query used to answer a request or a chat question is scoped to the signed-in user's own id. This is directly covered by the automated route tests, which assert that one account can neither read nor delete another account's transactions."],
["Walk through the Rs.18 lakh worked example.",
 "CTC of Rs.18,00,000 under the new regime, in a metro city, with rent of Rs.25,000 a month: basic works out to Rs.7,20,000 and HRA to Rs.3,60,000, giving a special allowance of Rs.5,98,968 and gross pay of Rs.16,78,968 after employer PF and gratuity are removed from CTC. Employee PF is Rs.86,400 and gratuity Rs.34,632. Taxable income comes to Rs.16,03,968, slab tax to Rs.1,20,794, cess to Rs.4,832, for a total tax of Rs.1,25,625, plus Rs.2,400 professional tax. Net annual pay is Rs.14,64,543, which is Rs.1,22,045 a month."],
["Why does the new regime beat the old regime in that example?",
 "For the same profile, the old regime works out to a total tax of Rs.2,15,145 and a net annual pay of Rs.13,75,023 — Rs.89,520 a year less than the new regime. At this income level the new regime's wider slabs and larger standard deduction outweigh the HRA exemption the old regime would otherwise offer, given the assumed rent of Rs.25,000 a month."],
["Explain marginal relief under Section 87A.",
 "The Section 87A rebate makes tax nil for taxable income up to Rs.12,00,000 under the new regime, but without marginal relief, earning even one rupee more than that would create tax on the full amount, not just the excess — a cliff-edge that would make a small raise a net loss. Marginal relief caps the tax at the amount of income actually over the threshold. In the worked evidence: at a CTC of Rs.14,00,000, taxable income is Rs.12,30,864, so the excess over Rs.12,00,000 is Rs.30,864, and the tax charged is exactly Rs.30,864 — capped at the excess. At a CTC of Rs.14,50,000, the excess is Rs.77,502 and the ordinary slab tax of Rs.71,625 applies instead, because by that point ordinary slab tax is already below the capped amount, so relief no longer changes anything."],
["What testing was actually done?",
 "172 automated tests across five files, all passing: parser tests covering every sample layout, header detection, direction resolution and format handling; classifier tests covering category placement, rail-versus-merchant precedence and the PREMIUM/EMI trap; salary tests covering statutory percentages, both regimes, HRA and PF ceiling, and marginal relief across the whole relief band; analytics tests covering summary arithmetic, recurring-commitment restriction and user isolation; and chat tests covering period and category recognition, exact SQL totals, and every guard rejection reason."],
["What did the live run actually demonstrate?",
 "On the finished build: an account was registered, two statements were uploaded, 69 transactions were imported with 69 distinct fingerprints, a third upload of an already-loaded statement correctly imported nothing, 69 embeddings were indexed, all eleven pages returned HTTP 200 with no template errors, and the chatbot correctly answered 'how much did I spend on groceries in June' with 'In June 2026, you spent Rs.4,960 on groceries.'"],
["What defects did the live run expose, and how were they fixed?",
 "Two. First, the dashboard advisory was quoting savings figures the model had invented rather than figures the Analytics Engine had computed — this is part of what motivated the chatbot guard described earlier. Second, the automated route tests were writing to the real database, because Flask-SQLAlchemy binds its engine at init_app and was ignoring a later change to the database URI; the database location was made properly configurable, which fixed the tests and, as a side benefit, lets the data file be relocated."],
["What would you do differently with more time?",
 "The classifier's 64.7% fallback accuracy is the most obvious place to invest further effort — a larger and more varied labelled corpus, and possibly a stronger model architecture for the ambiguous cases, would raise it. Bank coverage could also be widened beyond the eleven banks currently recognised, and the parser's preamble-scoring logic could be made adaptive rather than fixed at 25 rows for banks whose real-world exports turn out to need more."],
["Why does the AI advisory module exist separately from the RAG chatbot, if both use the same model?",
 "They answer different questions. AI Advisory turns a computed monthly summary into unprompted savings guidance shown on the dashboard, while the RAG chatbot answers a specific question the user has typed. Both sit behind the same provider ladder and the same principle — the model rewords, it does not compute — but they are triggered differently and produce different kinds of output."],
["How does the RAG retrieval actually work?",
 "Sentence-transformers' all-MiniLM-L6-v2 model turns text into 384-dimensional embeddings, which are cached as JSON in the embeddings table; a question is embedded the same way and compared against stored transaction embeddings by cosine similarity, computed with numpy. The transactions this retrieves are supporting context for the model's wording only — they are never the source of a number in the answer."],
["What happens if a requested period has no data?",
 "The natural-language query engine widens the period to the most recent month that does have data, and the answer says so explicitly, rather than returning an empty or silently misleading result."],
["Why does professional tax only apply in certain states?",
 "Professional tax is a state-level levy, not a central one, and only a subset of states impose it. The system applies Rs.2,400 a year in the eight states where it is charged — Tamil Nadu, Karnataka, Maharashtra, West Bengal, Andhra Pradesh, Telangana, Gujarat and Madhya Pradesh — and correctly applies none elsewhere."],
["Why does the classifier use character n-grams rather than word n-grams for its fallback model?",
 "Bank narrations are compressed and inconsistent — merchant names get truncated, run together, or padded with transaction codes and handle fragments. Character n-grams (char_wb, 2 to 5 characters) still pick up a partial or misspelled merchant name inside a messy string, which a word-level model would simply miss if the word boundary itself is corrupted by the narration format."],
["What is the difference between the deterministic advisor and the model-based advisory?",
 "Both sit at the end of the same provider ladder and both are fed the same Analytics Engine figures. The deterministic, rule-based advisor is guaranteed to be available with no dependency on any model being loaded or any key being supplied, and is exactly what keeps AI Advisory and the chatbot from ever going silent. The model-based path, when available, produces more naturally worded guidance from the same underlying numbers, but it is never trusted to originate a number of its own."],
["Why keep the classifier's rules and its fallback model as two separate stages instead of training one model over everything?",
 "The rules are fully explainable and run at full, deserved confidence — a payment to SWIGGY is Food & Dining because a keyword matched, not because a model assigned a probability. Training a single model over every narration would trade that certainty for a single accuracy number, and would make the clearest, least ambiguous transactions no more reliable than the genuinely hard ones. Keeping the two stages separate lets the fallback model's honestly modest 64.7% accuracy apply only to the transactions that actually need it."],
["Is there anything in the system that is not deterministic, and how is that risk contained?",
 "Yes — wherever a language model is used, by definition. The system contains that risk in two ways: the model is never the source of a number, only of wording, and every module that depends on it sits behind a provider ladder ending in a deterministic fallback, so the non-deterministic part can fail without the feature failing."],
];
qa.forEach(([q, a], i) => { body.push(qHead(`Q${i + 1}. ${q}`)); body.push(ans(a)); });

// 8. Demo script
body.push(pageBreak());
body.push(h1("8. Live Demo Script"));
body.push(para("This is the exact sequence used to demonstrate the finished build, matching the live run recorded in Section 7."));
body.push(num("Start the application with run.bat and open the browser it launches."));
body.push(num("Register a new account. Confirm a duplicate email is rejected if registration is attempted a second time with the same address."));
body.push(num("On the Dashboard, upload the first bank statement. Wait for the parser and classifier to finish; the summary and category chart fill in automatically."));
body.push(num("Upload a second statement covering a different period. Across the two uploads, 69 transactions should be imported, each with a distinct fingerprint, and 69 embeddings should be indexed for the chatbot to use."));
body.push(num("Upload the first statement a second time, unchanged. Confirm that zero new transactions are imported — this demonstrates the fingerprint guard against duplicate import."));
body.push(num("Visit every one of the eleven pages in turn — Login, Register, Dashboard, Add Entry, View/Database, Tracker, Salary & Tax, Goals, Budget, Insights, AI Chat — and confirm each renders with no template error."));
body.push(num("Open AI Chat and type: how much did I spend on groceries in June. Expect the answer: In June 2026, you spent Rs.4,960 on groceries."));
body.push(num("Ask a category breakdown question, for example: what did I spend the most on last month. Expect a deterministic, database-computed answer with the largest category and its real figure — this response should never touch the model, since it is a multi-row style of answer."));
body.push(num("Open View / Database and re-categorise one transaction using the dropdown; confirm it updates immediately and persists on a page reload."));
body.push(num("Open Salary & Tax, enter a CTC, and walk through the regime comparison it produces, cross-checking the figures against the worked example in Section 5.5 and Section 7."));
body.push(para("Throughout the demonstration, note that nothing shown requires an internet connection — this is worth calling out explicitly, since it is one of the system's central design decisions."));

// 9. Troubleshooting
body.push(pageBreak());
body.push(h1("9. Troubleshooting"));
body.push(h3("Port already in use"));
body.push(para("run.bat could not bind its port because another process is already listening on it. Close whatever else is using that port, or stop and restart run.bat once it is free."));
body.push(h3("Python missing"));
body.push(para("setup.bat needs a Python installation to locate before it can create the virtual environment. Install Python first, then rerun setup.bat from the start."));
body.push(h3("Model download interrupted"));
body.push(para("If the 1,066 MB model download is interrupted partway through, rerun tools/first_run_setup.py directly. It will resume the setup steps; a partially downloaded model file should be removed first so the download is not resumed from a corrupt partial file."));
body.push(h3("A statement will not parse"));
body.push(para("First check whether the file is password-protected — the parser raises a plain-English message for this specific case rather than failing silently. If the bank is not one of the eleven currently recognised, or the layout is unusually irregular, the parser may not find a header row within its first-25-rows scan; in that case, try the CSV export instead of the PDF if the bank offers one, since CSV parsing does not depend on the PDF text-fallback path."));
body.push(h3("No charts appearing"));
body.push(para("Charts appear once there is at least one imported or manually entered transaction for the current period — an empty account correctly shows no chart rather than a broken one. If a chart still does not appear after data exists, confirm the page loaded without a template error, since Chart.js is served from the application itself rather than a CDN and a failed page load would prevent it from running at all."));
body.push(h3("The first chat answer feels slow"));
body.push(para("Loading the on-device model takes about 2.7 seconds; this happens once per server run, not once per question. After the model is loaded, generation runs at roughly 8.8 tokens per second, so later answers in the same session should feel noticeably quicker than the very first one."));
body.push(h3("A transaction is filed under the wrong category"));
body.push(para("Open View / Database and change the category using the dropdown on that row; the change applies immediately. This is expected to happen occasionally, since the fallback model's honestly reported held-out accuracy is 64.7% on the ambiguous narrations it is asked to handle — the rules ahead of it resolve the unambiguous majority at full confidence and rarely need correcting."));

// 10. Glossary
body.push(pageBreak());
body.push(h1("10. Glossary"));
body.push(table(
  ["Term", "Meaning"],
  [
    ["CTC", "Cost to Company — the total annual cost of employing someone, before any statutory deductions."],
    ["Basic pay", "The base component of salary that most other components (HRA, PF, gratuity) are calculated as a percentage of."],
    ["HRA", "House Rent Allowance — a salary component that can be partly tax-exempt under the old regime."],
    ["PF", "Provident Fund — a statutory retirement contribution, 12% of basic from both employee and employer."],
    ["Gratuity", "A statutory lump-sum benefit, calculated here as 4.81% of basic."],
    ["Standard deduction", "A fixed amount subtracted from gross salary before tax is calculated — Rs.75,000 new regime, Rs.50,000 old regime."],
    ["Cess", "An additional 4% charge applied on top of computed income tax."],
    ["Section 87A rebate", "A rebate that brings tax to nil below a threshold — Rs.12,00,000 taxable income under the new regime, Rs.5,00,000 under the old."],
    ["Marginal relief", "A cap that prevents tax from exceeding the amount of income actually over the 87A threshold, avoiding a cliff-edge just above it."],
    ["Professional tax", "A state-level annual levy, Rs.2,400 in the states where it applies."],
    ["Fingerprint", "A SHA-1 hash of a transaction's user, date, amount, type and narration, used to detect and skip duplicate imports."],
    ["ORM", "Object-Relational Mapper — SQLAlchemy, which lets the application work with database rows as Python objects."],
    ["RAG", "Retrieval-Augmented Generation — retrieving relevant real data before asking a model to generate a wording, rather than asking it to generate an answer from nothing."],
    ["Embedding", "A numeric vector representation of text, here 384-dimensional, that lets similar pieces of text be compared by distance."],
    ["Cosine similarity", "A measure of how close two embeddings are in direction, used here to find transactions related to a question."],
    ["TF-IDF", "Term Frequency–Inverse Document Frequency — a way of turning text into numeric features weighted by how distinctive each term is."],
    ["char_wb n-gram", "A text feature made of overlapping sequences of 2 to 5 characters within word boundaries, used as input to the classifier's fallback model."],
    ["Logistic regression", "A statistical classification model, used here as the classifier's fallback for narrations the rules cannot place."],
    ["GGUF", "A file format for storing quantised language model weights, used by llama.cpp."],
    ["Q4_K_M quantisation", "A specific 4-bit quantisation scheme that shrinks a model's size and memory use with a controlled accuracy trade-off."],
    ["n_ctx", "The context window size of the language model, in tokens — 4096 here."],
    ["Confidence score", "A number attached to a classifier decision indicating how sure the classifier is; below 0.35 the classifier falls back to Others."],
    ["Held-out accuracy", "Accuracy measured on data the model was not trained on, used here to report the classifier fallback model's 64.7% figure honestly."],
    ["UPI / NEFT / IMPS / RTGS / NACH / ECS / ACH / POS / ATM-CW / CHQ / INB / MB / CARD / EMI", "Payment-rail markers the classifier recognises in a narration — these describe how money moved, and are tested last, after merchant-specific keywords."],
  ],
  [2400, 6960]
));
body.push(new Paragraph({ spacing: { before: 260 }, alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: "End of guide.", italics: true, size: 20, color: GREY })] }));

// ---------------------------------------------------------------- assemble
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Calibri", size: 22, color: INK } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 30, bold: true, color: BLUED, font: "Georgia" }, paragraph: { spacing: { before: 280, after: 150 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: BLUE }, paragraph: { spacing: { before: 200, after: 110 }, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 600, hanging: 280 } } } }] },
    { reference: "stp", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 600, hanging: 320 } } } }] },
  ] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "SmartEdit AI — Knowledge Transfer Guide", size: 16, color: GREY })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Page ", size: 16, color: GREY }), new TextRun({ children: [PageNumber.CURRENT], size: 16, color: GREY })] })] }) },
    children: [...cover, ...body],
  }],
});

Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log("WROTE", OUT, buf.length); });
