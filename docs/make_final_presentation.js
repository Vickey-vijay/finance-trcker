// SmartEdit AI — Final Viva Presentation (pptxgenjs)
// Owned exclusively by this script. Do not merge with make_presentation.js.
const pptxgen = require("pptxgenjs");
const path = require("path");

const DIR = process.env.DIAGRAMS || path.join(__dirname, "diagrams");
const OUT = process.env.OUTFILE || path.join(__dirname, "SmartEditAI_Viva_Presentation.pptx");

const BLUE = "1A73E8", BLUED = "1457B8", INK = "1F2733", GREY = "6B7787",
      LIGHT = "E8F0FE", GREEN = "1AA260", WHITE = "FFFFFF", BG = "F6F9FC", RED = "C0392B";

const p = new pptxgen();
p.layout = "LAYOUT_WIDE";            // 13.3 x 7.5
p.author = "Shyam Sundar";
p.title = "SmartEdit AI — Final Viva Presentation";
const W = 13.3, H = 7.5;
const TOTAL = 29;
const shadow = () => ({ type: "outer", color: "1457B8", blur: 8, offset: 2, angle: 135, opacity: 0.12 });

function footer(s, n) {
  s.addText("SmartEdit AI  ·  Final Viva Presentation", { x: 0.5, y: H - 0.45, w: 8, h: 0.3, fontSize: 9, color: GREY });
  s.addText(`${n} / ${TOTAL}`, { x: W - 1.3, y: H - 0.45, w: 0.8, h: 0.3, fontSize: 9, color: GREY, align: "right" });
}
function title(s, t, sub) {
  s.addText(t, { x: 0.5, y: 0.4, w: W - 1, h: 0.6, fontSize: 30, bold: true, color: BLUED, fontFace: "Georgia", margin: 0 });
  if (sub) s.addText(sub, { x: 0.5, y: 1.05, w: W - 1, h: 0.4, fontSize: 14, color: GREY, italic: true, margin: 0 });
}
function card(s, x, y, w, h, fill) {
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill || WHITE }, line: { color: LIGHT, width: 1 }, rectRadius: 0.08, shadow: shadow() });
}
function bulletBlock(s, items, opts) {
  s.addText(items.map(t => ({ text: t, options: { bullet: true, breakLine: true, paraSpaceAfter: opts.gap || 7 } })),
    Object.assign({ fontSize: 13, color: INK, valign: "top", margin: 0 }, opts));
}
function numBlock(s, items, opts) {
  s.addText(items.map(t => ({ text: t, options: { bullet: { type: "number" }, breakLine: true, paraSpaceAfter: opts.gap || 7 } })),
    Object.assign({ fontSize: 13, color: INK, valign: "top", margin: 0 }, opts));
}
function fig(s, file, x, y, w, h) {
  try { s.addImage({ path: path.join(DIR, file), x, y, sizing: { type: "contain", w, h } }); }
  catch (e) { /* image missing — skip silently */ }
}

// =================================================================== 1. Title
let s = p.addSlide(); s.background = { color: BLUED };
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.9, y: 2.5, w: 1.5, h: 1.5, fill: { color: WHITE }, rectRadius: 0.2 });
[0.55, 0.95, 1.35].forEach((hh, i) =>
  s.addShape(p.shapes.RECTANGLE, { x: 1.2 + i * 0.33, y: 3.5 - hh, w: 0.22, h: hh, fill: { color: BLUE } }));
s.addText("SmartEdit AI", { x: 2.7, y: 2.5, w: 9.5, h: 1.0, fontSize: 52, bold: true, color: WHITE, fontFace: "Georgia", margin: 0 });
s.addText("An Intelligent Personal Finance Web Application for Indian Salaried Users",
  { x: 2.72, y: 3.55, w: 9.5, h: 0.6, fontSize: 18, color: "CADCFC", margin: 0 });
s.addText("Final Viva Presentation", { x: 2.72, y: 4.15, w: 9, h: 0.4, fontSize: 14, color: "9DB8F0", italic: true, margin: 0 });
s.addText([
  { text: "Student: Shyam Sundar", options: { breakLine: true } },
  { text: "Student ID: (Insert student ID)", options: { breakLine: true } },
  { text: "Course: BITS ZG628T — Dissertation  ·  BITS Pilani (WILP)", options: { breakLine: true } },
  { text: "Supervisor: (Insert supervisor name)  ·  Organisation: (Insert organisation)", options: { breakLine: true } },
  { text: "2026" }],
  { x: 0.9, y: 5.55, w: 11, h: 1.4, fontSize: 12.5, color: "CADCFC" });
s.addNotes("Introduce yourself and the project by name. One-line pitch: SmartEdit AI reads an Indian salaried user's own bank statement and turns cryptic bank narrations into a clear, trustworthy picture of where the money went, with a chat assistant that can answer specific questions about that same data. State student ID, supervisor and organisation as printed on the slide before continuing.");

// =================================================================== 2. Agenda
s = p.addSlide(); s.background = { color: BG }; title(s, "Agenda");
const agenda = ["The Problem", "Objectives & What Changed This Semester", "System Architecture & Database",
  "Statement Parsing", "Transaction Classification", "Analytics & Insights", "Salary & Tax",
  "Natural-Language Chat & Grounding", "Privacy, Testing & Live Run", "Limitations, Future Work & Conclusion"];
agenda.forEach((t, i) => {
  const col = i % 2, row = Math.floor(i / 2);
  const x = 0.6 + col * 6.3, y = 1.7 + row * 1.0;
  card(s, x, y, 6.0, 0.82);
  s.addShape(p.shapes.OVAL, { x: x + 0.2, y: y + 0.16, w: 0.5, h: 0.5, fill: { color: BLUE } });
  s.addText(String(i + 1), { x: x + 0.2, y: y + 0.16, w: 0.5, h: 0.5, fontSize: 16, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
  s.addText(t, { x: x + 0.85, y: y, w: 5.0, h: 0.82, fontSize: 14, bold: true, color: INK, valign: "middle", margin: 0 });
});
footer(s, 2);
s.addNotes("Walk through the agenda briefly: the problem being solved, what changed since mid-semester, the architecture and database, then each of the eight modules grouped by theme, ending with grounding and trust, privacy and testing, and a closing assessment of limitations and future work.");

// =================================================================== 3. The problem
s = p.addSlide(); s.background = { color: BG }; title(s, "The Problem", "Indian bank statements are not standardised, and narrations are cryptic");
card(s, 0.6, 1.7, 6.0, 4.9, BLUED);
s.addText("A real narration, unchanged:", { x: 0.9, y: 1.9, w: 5.4, h: 0.35, fontSize: 13, bold: true, color: "CADCFC", margin: 0 });
s.addText([
  { text: "UPI-SWIGGY-OKAXIS-XXXX1234\n", options: { fontSize: 16, color: WHITE, fontFace: "Consolas", breakLine: true } },
  { text: "POS-4521-RELIANCE FRESH\n", options: { fontSize: 16, color: WHITE, fontFace: "Consolas", breakLine: true } },
  { text: "NACH-LIC PREMIUM-AUTODEBIT", options: { fontSize: 16, color: WHITE, fontFace: "Consolas" } }],
  { x: 0.9, y: 2.35, w: 5.4, h: 1.5, valign: "top", margin: 0 });
s.addText("A salaried user cannot tell from eighty rows like these where their money actually went.",
  { x: 0.9, y: 4.05, w: 5.4, h: 1.2, fontSize: 14, italic: true, color: "DCE7FF", valign: "top", margin: 0 });
s.addText("Why this is genuinely hard:", { x: 6.9, y: 1.7, w: 5.9, h: 0.4, fontSize: 15, bold: true, color: BLUED, margin: 0 });
const probs = [
  ["No standard layout", "SBI, HDFC, ICICI and Axis each export a different column structure, with account details and blank rows above the real table."],
  ["No standard narration format", "The same merchant appears differently depending on the payment rail — UPI, POS, NACH — used for that transaction."],
  ["No arithmetic from a small model", "A 1.5-billion-parameter model cannot be trusted to compute a rupee figure directly from raw transactions."]];
probs.forEach(([h, d], i) => {
  const y = 2.15 + i * 1.35; card(s, 6.9, y, 5.9, 1.15);
  s.addText(h, { x: 7.15, y: y + 0.12, w: 5.4, h: 0.4, fontSize: 14, bold: true, color: INK, margin: 0 });
  s.addText(d, { x: 7.15, y: y + 0.5, w: 5.45, h: 0.6, fontSize: 11.5, color: GREY, margin: 0 });
});
footer(s, 3);
s.addNotes("Read the three narrations aloud as written — they mean nothing to a normal reader. This is the actual raw input the system has to work with: no two banks format it the same way, and the meaning is buried inside abbreviations and codes. Emphasise the third gap especially, since it foreshadows the grounding discussion later in the deck.");

// =================================================================== 4. Objectives
s = p.addSlide(); s.background = { color: BG }; title(s, "Objectives");
card(s, 0.6, 1.7, 12.1, 4.9);
bulletBlock(s, [
  "Parse Indian bank statement CSV, XLSX and PDF exports across eleven banks, recovering every genuine transaction row and rejecting balance and sub-total rows.",
  "Classify cryptic narrations into 17 spending categories, resolving payment-rail markers correctly against merchant identity.",
  "Turn categorised transactions into a period summary, trend series and a set of deterministic, plain-language insights.",
  "Compute an Indian salaried user's take-home pay and compare the old and new tax regimes, including marginal relief.",
  "Answer free-form natural-language questions about a user's own spending with an answer that is provably grounded in real data, never invented.",
  "Run the entire system, including its language model, on the user's own machine, with no dependency on an external AI service in the default configuration.",
], { x: 0.95, y: 1.95, w: 11.6, h: 4.5, fontSize: 15, gap: 14 });
footer(s, 4);
s.addNotes("Each objective maps directly onto one or more of the eight backend modules covered later in the deck. The last objective — running entirely on-device — is the one most likely to be probed, since it is the least common design choice among comparable applications; be ready to explain that this was a deliberate privacy and availability decision, not a limitation.");

// =================================================================== 5. Delivered this semester vs mid-semester
s = p.addSlide(); s.background = { color: BG }; title(s, "What Was Delivered This Semester");
card(s, 0.6, 1.7, 5.9, 4.9);
s.addText("Mid-Semester", { x: 0.9, y: 1.9, w: 5.3, h: 0.4, fontSize: 16, bold: true, color: GREY, margin: 0 });
bulletBlock(s, [
  "Five pages: Dashboard, Add Entry, View/Database, Tracker, AI Chat",
  "PDF/CSV parsing and a rule-based classifier",
  "AI advisory and a RAG chatbot using the Gemini API",
  "A deterministic offline fallback so a demo never fails",
], { x: 0.95, y: 2.35, w: 5.5, h: 3.9, fontSize: 13.5, gap: 10 });
card(s, 6.8, 1.7, 5.9, 4.9, BLUED);
s.addText("Final Semester", { x: 7.1, y: 1.9, w: 5.3, h: 0.4, fontSize: 16, bold: true, color: WHITE, margin: 0 });
bulletBlock(s, [
  "Eleven pages, including Salary & Tax, Goals, Budget and Insights",
  "Bank coverage widened to eleven banks; a trained fallback model (64.7% held-out accuracy) now backs the rule engine",
  "The Gemini-only advisory replaced by an on-device Qwen2.5-1.5B model with a full provider ladder and a real database as the last-resort fallback",
  "A full Salary & Tax module: both regimes, HRA, PF, gratuity, marginal relief",
  "An Analytics Engine with recurring-commitment detection",
  "A guard that discards any chatbot reply containing an unexplained figure",
  "172 automated tests, all passing, plus a live run against real imported data",
], { x: 7.05, y: 2.35, w: 5.55, h: 3.9, fontSize: 12.5, gap: 8, color: WHITE });
footer(s, 5);
s.addNotes("Frame this as growth in depth, not just breadth: it is not only more pages, but a shift from trusting an external API and a rule-only classifier to a system that grounds every figure in real computation and runs its own model locally. The two defects fixed during the live run — described later — are part of this semester's work, not oversights left over from mid-semester.");

// =================================================================== 6. Architecture
s = p.addSlide(); s.background = { color: BG }; title(s, "System Architecture", "Four layers: browser front end, Flask application, on-device inference, SQLite");
fig(s, "01_system_architecture.png", 0.7, 1.6, 8.6, 5.2);
const stack = [["Front end", "Server-rendered HTML · vanilla JS · Chart.js, served from the app itself"],
  ["Flask app", "Eight modules over SQLAlchemy"], ["Inference", "llama.cpp · Qwen2.5-1.5B, Q4_K_M"],
  ["Database", "SQLite · 7 tables"]];
stack.forEach(([h, d], i) => {
  const y = 1.7 + i * 1.15; card(s, 9.5, y, 3.3, 1.0, LIGHT);
  s.addText(h, { x: 9.65, y: y + 0.08, w: 3.0, h: 0.3, fontSize: 13, bold: true, color: BLUED, margin: 0 });
  s.addText(d, { x: 9.65, y: y + 0.4, w: 3.05, h: 0.55, fontSize: 10.5, color: GREY, margin: 0 });
});
footer(s, 6);
s.addNotes("Walk down the diagram from top to bottom. The browser layer is deliberately simple — server-rendered pages rather than a client-side framework, which is why the interface works offline. The Flask layer is the eight modules covered on the next slide. The inference layer is a separate, swappable piece with its own provider ladder. The database is SQLite reached through SQLAlchemy, chosen for a single-user desktop-style deployment rather than a multi-tenant server.");

// =================================================================== 7. The eight modules
s = p.addSlide(); s.background = { color: BG }; title(s, "The Eight Modules");
const mods = [
  ["Authentication & Session", "Login, registration, hashed passwords, a session guard on every route"],
  ["Statement Parser", "parser.py — reads CSV, XLSX and PDF across eleven banks"],
  ["Transaction Classifier", "classifier.py — 17 categories, rules first, rails last"],
  ["Analytics Engine", "analytics.py — summaries, trends, recurring commitments, insights"],
  ["Salary & Tax", "salary.py — CTC breakdown, both regimes, marginal relief"],
  ["Natural-Language Query Engine", "nlq.py — turns a question into a real SQL aggregate"],
  ["AI Advisory", "advisor.py — savings guidance from computed figures"],
  ["RAG Chatbot", "rag.py — retrieval for context, guarded generation for wording"],
];
mods.forEach(([h, d], i) => {
  const col = i % 2, row = Math.floor(i / 2);
  const x = 0.6 + col * 6.3, y = 1.65 + row * 1.32;
  card(s, x, y, 6.0, 1.14);
  s.addText(h, { x: x + 0.25, y: y + 0.1, w: 5.5, h: 0.4, fontSize: 13.5, bold: true, color: BLUED, margin: 0 });
  s.addText(d, { x: x + 0.25, y: y + 0.5, w: 5.5, h: 0.55, fontSize: 11, color: GREY, margin: 0 });
});
footer(s, 7);
s.addNotes("These eight modules sit on top of the database and beneath the front end. Each will get its own slide or slide-pair later where it matters most for the viva narrative — parsing, classification, analytics, salary, and the natural-language chat with its grounding guard. Authentication and Advisory are covered briefly since their defence rests mainly on the test suite and on the grounding discussion respectively.");

// =================================================================== 8. Database
s = p.addSlide(); s.background = { color: BG }; title(s, "Database", "Seven tables, reached through SQLAlchemy, with a stored transaction fingerprint");
fig(s, "04_er_diagram.png", 0.7, 1.6, 7.6, 5.2);
card(s, 8.6, 1.65, 4.2, 5.15);
s.addText("Seven tables", { x: 8.85, y: 1.85, w: 3.7, h: 0.35, fontSize: 14, bold: true, color: BLUED, margin: 0 });
bulletBlock(s, ["users", "transactions", "embeddings", "chat_history", "salary_profiles", "savings_goals", "budgets"],
  { x: 8.9, y: 2.25, w: 3.7, h: 1.9, fontSize: 12.5, gap: 5 });
s.addText("Fingerprint", { x: 8.85, y: 4.25, w: 3.7, h: 0.35, fontSize: 14, bold: true, color: GREEN, margin: 0 });
s.addText("A SHA-1 hash over user, date, amount, type and narration. Stops a re-uploaded statement being imported twice.",
  { x: 8.9, y: 4.62, w: 3.7, h: 1.0, fontSize: 11.5, color: INK, valign: "top", margin: 0 });
s.addText("ensure_schema()", { x: 8.85, y: 5.7, w: 3.7, h: 0.3, fontSize: 12.5, bold: true, color: BLUED, margin: 0 });
s.addText("Adds any missing table or column to an existing database in place, so upgrades never lose data.",
  { x: 8.9, y: 6.0, w: 3.7, h: 0.7, fontSize: 11, color: GREY, margin: 0 });
footer(s, 8);
s.addNotes("The transactions table is the centre of the schema — it carries category, method, source, merchant, confidence and the fingerprint alongside the usual date, amount and description fields. The fingerprint is the mechanism behind duplicate-upload protection, demonstrated later in the live run. ensure_schema() is what allowed the database location fix, discussed in the grounding section, to be made safely.");

// =================================================================== 9. Statement parsing — measured results
s = p.addSlide(); s.background = { color: BG }; title(s, "Statement Parsing", "Measured on the bundled sample statements");
const parseRows = [
  ["sample_statement.csv", "Unknown", "30", "0"],
  ["hdfc_statement.csv", "HDFC", "40", "0 (6 preamble rows)"],
  ["icici_statement.csv", "ICICI", "35", "0 (Amount + Dr/Cr column)"],
  ["axis_statement.csv", "Axis", "30", "1 (opening balance)"],
  ["sample_statement.pdf", "Unknown", "30", "1 (no ruled table)"],
];
s.addTable(
  [[{ text: "File", options: { bold: true, color: WHITE, fill: { color: BLUED } } },
    { text: "Bank detected", options: { bold: true, color: WHITE, fill: { color: BLUED } } },
    { text: "Rows", options: { bold: true, color: WHITE, fill: { color: BLUED } } },
    { text: "Skipped", options: { bold: true, color: WHITE, fill: { color: BLUED } } }],
   ...parseRows.map((r, i) => r.map(c => ({ text: c, options: { fill: { color: i % 2 ? "F2F6FC" : WHITE }, color: INK } })))],
  { x: 0.6, y: 1.75, w: 12.1, h: 2.6, fontSize: 13, autoPage: false, colW: [3.6, 2.8, 1.6, 4.1], border: { type: "solid", color: "CCD6E6", pt: 0.75 } }
);
card(s, 0.6, 4.6, 12.1, 2.05);
s.addText("Direction is resolved in a fixed order:", { x: 0.9, y: 4.78, w: 11.5, h: 0.35, fontSize: 13.5, bold: true, color: BLUED, margin: 0 });
s.addText("Explicit Dr/Cr column  →  Dr/Cr suffix on the value  →  sign of the number  →  movement of the running balance",
  { x: 0.9, y: 5.15, w: 11.5, h: 0.5, fontSize: 13, color: INK, margin: 0 });
s.addText("The Axis sample above carries no explicit marker at all — its direction is resolved entirely from the fourth rule.",
  { x: 0.9, y: 5.7, w: 11.5, h: 0.7, fontSize: 12, italic: true, color: GREY, margin: 0 });
footer(s, 9);
s.addNotes("Every row in this table is a real measurement against the bundled sample statements, not an estimate. Point out that the parser scans the first 25 rows to score a header candidate, which is exactly why the six-row HDFC preamble does not cause any row to be dropped. The Axis example is worth dwelling on, since it demonstrates that the direction-resolution order is not decorative — that statement genuinely needs the fourth rule to be read correctly.");

// =================================================================== 10. Parsing edge cases
s = p.addSlide(); s.background = { color: BG }; title(s, "Parsing Edge Cases That Mattered");
const edges = [
  ["Preamble above the header", "Real SBI and ICICI exports carry account details and blank rows before the transaction table. The parser scores each of the first 25 rows as a header candidate rather than assuming row one."],
  ["No explicit Dr/Cr marker", "Axis-style statements are read by falling through to the movement of the running balance, the last resort in the direction-resolution order."],
  ["Indian amount formats", "1,23,456.00 · Rs. 4,500 · (2,000.50) for a withdrawal · a trailing Dr or Cr — all handled explicitly."],
  ["PDFs with no ruled table", "Falls back to line-by-line regular-expression parsing of the extracted text."],
  ["Password-protected PDFs", "Raises a plain-English message rather than a stack trace."],
  ["Balance and sub-total rows", "Recognised and rejected, counted as skipped rather than imported, so totals stay honest."],
];
edges.forEach(([h, d], i) => {
  const col = i % 2, row = Math.floor(i / 2);
  const x = 0.6 + col * 6.3, y = 1.65 + row * 1.7;
  card(s, x, y, 6.0, 1.5);
  s.addText(h, { x: x + 0.25, y: y + 0.12, w: 5.5, h: 0.4, fontSize: 13.5, bold: true, color: BLUED, margin: 0 });
  s.addText(d, { x: x + 0.25, y: y + 0.52, w: 5.5, h: 0.9, fontSize: 11, color: GREY, margin: 0 });
});
footer(s, 10);
s.addNotes("These are not hypothetical edge cases — each one corresponds to a real bundled sample statement or a real failure mode. If asked what would happen with a bank not in the current list of eleven, the honest answer is that it depends on how close its layout and amount formatting are to what is already handled; genuinely novel formats would need a new alias map entry.");

// =================================================================== 11. Classification and rails-last
s = p.addSlide(); s.background = { color: BG }; title(s, "Classification — the Rails-Last Rule");
fig(s, "11_classifier_flow.png", 0.7, 1.6, 6.3, 5.2);
card(s, 7.2, 1.65, 5.5, 5.15, BLUED);
s.addText("17 categories. Rules first, at confidence 1.0.", { x: 7.45, y: 1.85, w: 5.0, h: 0.6, fontSize: 15, bold: true, color: WHITE, margin: 0 });
bulletBlock(s, [
  "Payment rails — UPI, NEFT, IMPS, RTGS, PhonePe, GPay, Paytm — are tested last, not first.",
  "A UPI payment to Swiggy is filed as Food & Dining; only a payment with no identifiable merchant becomes Transfers.",
  "Whatever the rules cannot place goes to a trained fallback: TF-IDF character n-grams into logistic regression, 746 labelled narrations, held-out accuracy 64.7%.",
  "Below 0.35 confidence, the fallback returns Others rather than guessing.",
  "If scikit-learn is absent, the module still runs on rules alone.",
], { x: 7.45, y: 2.55, w: 5.1, h: 3.9, fontSize: 12.5, color: WHITE, gap: 10 });
footer(s, 11);
s.addNotes("The ordering is the whole point of this slide: testing rail markers last is what keeps a UPI payment to a known merchant correctly categorised, instead of every UPI transaction collapsing into a meaningless Transfers bucket. The 64.7% figure belongs only to the fallback model on deliberately ambiguous narrations — the rules resolve the unambiguous majority before the model is ever consulted, which is covered in more depth two slides from now if asked.");

// =================================================================== 12. PREMIUM/EMI trap
s = p.addSlide(); s.background = { color: BG }; title(s, "The PREMIUM / EMI Trap", "A concrete classifier bug, and its fix");
card(s, 0.6, 1.75, 5.9, 4.7, RED);
s.addText("The bug", { x: 0.9, y: 1.95, w: 5.3, h: 0.4, fontSize: 16, bold: true, color: WHITE, margin: 0 });
s.addText([
  { text: "NACH-LIC PREMIUM-AUTODEBIT\n", options: { fontSize: 15, color: WHITE, fontFace: "Consolas", breakLine: true } },
  { text: "\n", options: { breakLine: true } },
  { text: "A plain substring search for the keyword ", options: { fontSize: 13, color: "FCE4E4" } },
  { text: "EMI ", options: { fontSize: 13, bold: true, color: WHITE } },
  { text: "matched inside the word ", options: { fontSize: 13, color: "FCE4E4" } },
  { text: "PREMIUM", options: { fontSize: 13, bold: true, color: WHITE } },
  { text: ", filing a genuine LIC insurance premium under EMI / Loans instead of Insurance.", options: { fontSize: 13, color: "FCE4E4" } }],
  { x: 0.9, y: 2.45, w: 5.4, h: 3.7, valign: "top", margin: 0 });
card(s, 6.8, 1.75, 5.9, 4.7, GREEN);
s.addText("The fix", { x: 7.1, y: 1.95, w: 5.3, h: 0.4, fontSize: 16, bold: true, color: WHITE, margin: 0 });
s.addText([
  { text: "Keywords shorter than four characters are matched on a word boundary, not as a plain substring.\n\n", options: { fontSize: 14, color: WHITE, breakLine: true } },
  { text: "EMI now matches only the standalone word EMI, and no longer matches as a fragment inside PREMIUM, SEMINAR, or any other longer word.", options: { fontSize: 13.5, color: "E2F6EC" } }],
  { x: 7.1, y: 2.45, w: 5.4, h: 3.7, valign: "top", margin: 0 });
footer(s, 12);
s.addNotes("This is a genuinely useful concrete example for a viva, because it shows a real bug that was found and fixed, not a hypothetical one. It also demonstrates that keyword matching in the classifier is not naive substring matching — the four-character threshold and word-boundary rule exist specifically because of this incident.");

// =================================================================== 13. Analytics and insights
s = p.addSlide(); s.background = { color: BG }; title(s, "Analytics & Insights");
card(s, 0.6, 1.7, 6.7, 4.9);
s.addText("Deterministic insights, always with a real figure", { x: 0.9, y: 1.9, w: 6.1, h: 0.4, fontSize: 14.5, bold: true, color: BLUED, margin: 0 });
bulletBlock(s, [
  "Month-on-month change and the category that drove it",
  "A category taking more than 30% of spend",
  "Weekend versus weekday split",
  "Largest single transaction",
  "Days with no spend at all",
  "Food-delivery count and total",
  "Annualised cost of standing charges",
  "Savings rate against a 20% benchmark",
], { x: 0.95, y: 2.35, w: 6.2, h: 4.1, fontSize: 12.5, gap: 8 });
card(s, 7.6, 1.7, 5.1, 4.9);
s.addText("Category taxonomy — 17 categories", { x: 7.85, y: 1.9, w: 4.6, h: 0.4, fontSize: 13.5, bold: true, color: BLUED, margin: 0 });
s.addChart(p.charts.PIE, [{ name: "Categories", labels: ["Recurring-eligible (6)", "Other categories (11)"], values: [6, 11] }],
  { x: 7.7, y: 2.35, w: 4.7, h: 3.9, chartColors: [BLUE, LIGHT], dataLabelColor: INK, dataLabelFontSize: 11,
    showLegend: true, legendPos: "b", legendFontSize: 10, showValue: true, showPercent: false, dataBorderColor: WHITE, dataBorderWidth: 1 });
footer(s, 13);
s.addNotes("Six of the seventeen categories — Subscriptions, Utilities, Insurance, EMI / Loans, Rent and Investments — are the ones eligible for recurring-commitment detection, shown in the chart. The remaining eleven, including Food & Dining and Groceries, are deliberately excluded from that specific feature, which is the subject of the next slide.");

// =================================================================== 14. Recurring commitments and the cadence bug
s = p.addSlide(); s.background = { color: BG }; title(s, "Recurring Commitments — the Cadence Bug");
card(s, 0.6, 1.7, 5.9, 4.9);
s.addText("The rule", { x: 0.9, y: 1.9, w: 5.3, h: 0.35, fontSize: 15, bold: true, color: BLUED, margin: 0 });
bulletBlock(s, [
  "Restricted to Subscriptions, Utilities, Insurance, EMI / Loans, Rent and Investments",
  "A supermarket visited weekly is a habit, not a standing charge",
  "A merchant qualifies once it appears in 2+ distinct months within 15% of its median amount",
], { x: 0.95, y: 2.3, w: 5.5, h: 2.2, fontSize: 13, gap: 9 });
s.addText("Cadence is decided from the number of distinct months a charge appears in, not the raw day-gap between two charges.",
  { x: 0.95, y: 4.5, w: 5.5, h: 1.0, fontSize: 12.5, italic: true, color: GREY, valign: "top", margin: 0 });
card(s, 6.8, 1.7, 5.9, 4.9, BLUED);
s.addText("The bug it fixed", { x: 7.1, y: 1.9, w: 5.3, h: 0.35, fontSize: 15, bold: true, color: WHITE, margin: 0 });
s.addText([
  { text: "Two statements happened to cover the same period, which read as a weekly rhythm.\n\n", options: { fontSize: 13.5, color: "DCE7FF", breakLine: true } },
  { text: "A genuine Rs.9,500 EMI was inflated to an annualised Rs.4.94 lakh — before the fix, deciding cadence from distinct months instead of raw day-gaps.", options: { fontSize: 13.5, color: WHITE } }],
  { x: 7.1, y: 2.3, w: 5.4, h: 3.9, valign: "top", margin: 0 });
footer(s, 14);
s.addNotes("This is the second concrete, named bug in the deck, alongside the PREMIUM/EMI trap. Nearly a five-times overstatement of a real EMI is a serious error for a personal finance tool to make, which is why the fix — deciding cadence from the count of distinct calendar months rather than the raw gap between two charges — is worth explaining carefully if asked.");

// =================================================================== 15. Salary and tax
s = p.addSlide(); s.background = { color: BG }; title(s, "Salary & Tax", "FY 2025-26 — both regimes, computed from CTC");
fig(s, "13_salary_flow.png", 1.3, 1.55, 5.2, 5.3);
card(s, 6.9, 1.65, 5.8, 5.2);
s.addText("Key statutory percentages", { x: 7.15, y: 1.85, w: 5.3, h: 0.35, fontSize: 14.5, bold: true, color: BLUED, margin: 0 });
bulletBlock(s, [
  "Basic: 40% of CTC  ·  HRA: 50% of basic",
  "PF: 12% of basic each side, capped at the Rs.15,000 wage ceiling when opted out",
  "Gratuity: 4.81% of basic  ·  Gross = CTC − employer PF − gratuity",
  "HRA exemption (old regime only): least of actual HRA, rent − 10% of basic, 50%/40% of basic",
  "Standard deduction: Rs.75,000 new  ·  Rs.50,000 old  ·  Cess: 4%",
  "Section 87A rebate to nil up to Rs.12,00,000 (new) / Rs.5,00,000 (old), with marginal relief just above the new-regime threshold",
  "Professional tax Rs.2,400/year in 8 states",
], { x: 7.2, y: 2.3, w: 5.4, h: 4.4, fontSize: 12, gap: 9 });
footer(s, 15);
s.addNotes("Every percentage on this slide is used in the worked example on the next slide, so keep this one brief and treat it as reference material the audience can look back at. The professional-tax detail is worth having ready since it is state-specific and easy to be asked about directly — the eight states are Tamil Nadu, Karnataka, Maharashtra, West Bengal, Andhra Pradesh, Telangana, Gujarat and Madhya Pradesh.");

// =================================================================== 16. Worked example
s = p.addSlide(); s.background = { color: BG }; title(s, "Worked Example — CTC Rs.18,00,000", "New regime, metro city, rent Rs.25,000/month");
s.addTable(
  [[{ text: "Component", options: { bold: true, color: WHITE, fill: { color: BLUED } } }, { text: "Amount (Rs.)", options: { bold: true, color: WHITE, fill: { color: BLUED } } }],
   ...[["Basic", "7,20,000"], ["HRA", "3,60,000"], ["Special allowance", "5,98,968"], ["Gross pay", "16,78,968"],
       ["Employee PF", "86,400"], ["Gratuity", "34,632"], ["Taxable income", "16,03,968"], ["Slab tax", "1,20,794"],
       ["Cess (4%)", "4,832"], ["Total tax", "1,25,625"], ["Professional tax", "2,400"], ["Net annual pay", "14,64,543"],
       ["Net monthly pay", "1,22,045"]].map((r, i) => r.map(c => ({ text: c, options: { fill: { color: i % 2 ? "F2F6FC" : WHITE }, color: INK } })))],
  { x: 0.6, y: 1.6, w: 6.1, h: 5.3, fontSize: 11.5, autoPage: false, colW: [3.7, 2.4], border: { type: "solid", color: "CCD6E6", pt: 0.75 } }
);
s.addText("Total tax: new regime vs old regime", { x: 7.0, y: 1.6, w: 5.7, h: 0.35, fontSize: 13.5, bold: true, color: BLUED, margin: 0 });
s.addChart(p.charts.BAR, [{ name: "Total tax (Rs.)", labels: ["New Regime", "Old Regime"], values: [125625, 215145] }],
  { x: 7.0, y: 2.0, w: 5.7, h: 3.6, barDir: "col", chartColors: [GREEN, GREY], showValue: true, dataLabelFontSize: 12,
    dataLabelColor: INK, catAxisLabelColor: INK, valAxisLabelColor: GREY, showLegend: false });
card(s, 7.0, 5.75, 5.7, 0.95, BLUED);
s.addText("The new regime is better by Rs.89,520 a year for this profile.", { x: 7.25, y: 5.75, w: 5.2, h: 0.95, fontSize: 13.5, bold: true, color: WHITE, valign: "middle", margin: 0 });
footer(s, 16);
s.addNotes("Every figure in the table is a real output of the salary module for this exact input, not a rounded illustration — be ready to explain any single row. The chart makes the regime comparison concrete: total tax of Rs.1,25,625 under the new regime against Rs.2,15,145 under the old regime, for the identical profile, a difference of Rs.89,520 a year. If asked why the new regime wins here, the answer is that its wider slabs and larger standard deduction outweigh what the old regime's HRA exemption would have saved at this rent level.");

// =================================================================== 17. Marginal relief
s = p.addSlide(); s.background = { color: BG }; title(s, "Marginal Relief Under Section 87A");
card(s, 0.6, 1.7, 12.1, 1.6, BLUED);
s.addText("Without marginal relief, earning one rupee over Rs.12,00,000 taxable income would create tax on the full amount — a cliff-edge that turns a small raise into a net loss. Marginal relief caps the tax at the amount of income actually over the threshold.",
  { x: 0.9, y: 1.85, w: 11.5, h: 1.3, fontSize: 14, color: WHITE, valign: "top", margin: 0 });
s.addTable(
  [[{ text: "CTC", options: { bold: true, color: WHITE, fill: { color: BLUED } } },
    { text: "Taxable income", options: { bold: true, color: WHITE, fill: { color: BLUED } } },
    { text: "Excess over Rs.12,00,000", options: { bold: true, color: WHITE, fill: { color: BLUED } } },
    { text: "Tax charged", options: { bold: true, color: WHITE, fill: { color: BLUED } } },
    { text: "What happened", options: { bold: true, color: WHITE, fill: { color: BLUED } } }],
   [{ text: "Rs.14,00,000" }, { text: "Rs.12,30,864" }, { text: "Rs.30,864" }, { text: "Rs.30,864" }, { text: "Capped exactly at the excess" }],
   [{ text: "Rs.14,50,000" }, { text: "—" }, { text: "Rs.77,502" }, { text: "Rs.71,625" }, { text: "Ordinary slab tax applies — already below the cap" }]],
  { x: 0.6, y: 3.55, w: 12.1, h: 2.0, fontSize: 13, autoPage: false, colW: [2.3, 2.6, 2.7, 2.2, 2.3], border: { type: "solid", color: "CCD6E6", pt: 0.75 } }
);
card(s, 0.6, 5.9, 12.1, 0.9);
s.addText("At Rs.14,00,000 CTC, relief exactly cancels the excess. At Rs.14,50,000, ordinary slab tax is already the smaller number, so relief stops applying.",
  { x: 0.9, y: 5.9, w: 11.5, h: 0.9, fontSize: 12.5, italic: true, color: GREY, valign: "middle", margin: 0 });
footer(s, 17);
s.addNotes("This is the single most technical tax point in the whole system and the one most likely to be probed directly. The key distinction in the table: at the lower CTC, the excess over Rs.12,00,000 is smaller than what ordinary slab tax would charge, so relief caps it down; at the higher CTC, ordinary slab tax has already fallen below the excess amount, so relief no longer changes the result. Both rows were computed by the salary module, not chosen to fit a narrative.");

// =================================================================== 18. NLQ engine
s = p.addSlide(); s.background = { color: BG }; title(s, "Natural-Language Query Engine", "Every rupee figure comes from a real database aggregate");
fig(s, "12_rag_pipeline.png", 0.7, 1.6, 6.5, 5.2);
card(s, 7.4, 1.65, 5.3, 5.15);
s.addText("The pipeline, in order", { x: 7.65, y: 1.85, w: 4.8, h: 0.35, fontSize: 14.5, bold: true, color: BLUED, margin: 0 });
numBlock(s, [
  "parse_query turns the question into a structured query using regular expressions and keyword tables — no model involved",
  "execute runs a real SQLAlchemy aggregate scoped to the signed-in user",
  "Embeddings retrieve supporting transactions for context only — never for a figure",
  "The model is handed the finished sentence and asked only to reword it",
  "A guard discards the reply if it invents or miscomputes anything",
], { x: 7.7, y: 2.3, w: 5.0, h: 4.3, fontSize: 12.5, gap: 10 });
footer(s, 18);
s.addNotes("This slide is the mechanical description of grounding; the next two slides tell the story of why it exists — the actual failure that was observed, and the specific guard rules that resulted from it. Understanding this pipeline in order is essential: parsing and computation happen with zero model involvement, and the model only ever touches a sentence that is already correct.");

// =================================================================== 19. On-device model speed
s = p.addSlide(); s.background = { color: BG }; title(s, "The On-Device Model");
const specs = [["1,066 MB", "Model file size (GGUF, Q4_K_M)"], ["2.7 s", "Time to load"], ["8.8 tok/s", "Generation speed"], ["4096", "Context window (n_ctx)"]];
specs.forEach(([v, l], i) => {
  const x = 0.6 + i * 3.15; card(s, x, 1.8, 2.9, 1.7);
  s.addText(v, { x, y: 1.95, w: 2.9, h: 0.9, fontSize: 32, bold: true, color: BLUED, align: "center", margin: 0 });
  s.addText(l, { x, y: 2.85, w: 2.9, h: 0.55, fontSize: 11.5, color: GREY, align: "center", margin: 0 });
});
card(s, 0.6, 3.75, 12.1, 2.85);
bulletBlock(s, [
  "Qwen2.5-1.5B-Instruct, quantised to Q4_K_M in GGUF format",
  "Runs on llama-cpp-python 0.3.34, installed from a prebuilt CPU wheel only 6.6 MB in size — no compiler needed on the client machine",
  "Thread count equal to the number of CPU cores on the machine it runs on",
  "Measured on the development machine; a faster or slower machine will load and generate at a different speed, but the same figures reported here",
  "Nothing leaves the machine in the default configuration",
], { x: 0.95, y: 3.95, w: 11.5, h: 2.6, fontSize: 14, gap: 11 });
footer(s, 19);
s.addNotes("All four numbers on this slide are direct measurements on the development machine, not vendor claims. If asked why 1.5 billion parameters specifically, the honest answer is a deliberate trade-off between running comfortably on an ordinary machine and having enough language ability to reword a sentence — which is genuinely all it is ever asked to do.");

// =================================================================== 20. Fallback ladder
s = p.addSlide(); s.background = { color: BG }; title(s, "The Provider Fallback Ladder", "An answer is always produced");
fig(s, "14_llm_fallback_chain.png", 0.7, 1.7, 12.0, 3.4);
card(s, 0.6, 5.3, 12.1, 1.5, BLUED);
s.addText("Local model  →  Ollama (if running)  →  Gemini (only with a supplied key)  →  Deterministic rule-based advisor",
  { x: 0.9, y: 5.55, w: 11.5, h: 0.6, fontSize: 15, bold: true, color: WHITE, margin: 0 });
s.addText("Every step in this chain is optional except the last one, and the last one has no external dependency at all.",
  { x: 0.9, y: 6.1, w: 11.5, h: 0.6, fontSize: 12.5, italic: true, color: "DCE7FF", margin: 0 });
footer(s, 20);
s.addNotes("This ladder is used identically by AI Advisory and by the RAG chatbot. The important point is that the final step is not a degraded experience — it is a deterministic, rule-based advisor with no external dependency, which is exactly why the system can guarantee an answer is always produced, with or without internet, with or without a key, with or without the local model even being installed.");

// =================================================================== 21. Grounding — the failure observed
s = p.addSlide(); s.background = { color: BG }; title(s, "Grounding — the Failure Observed", "Why the language model is never trusted with a number");
card(s, 0.6, 1.75, 12.1, 2.3, RED);
s.addText("Asked directly how much was spent on food, given a total and a transaction count, the model attempted to divide one number by the other itself — and emitted LaTeX instead of an answer.",
  { x: 0.9, y: 1.95, w: 11.5, h: 1.9, fontSize: 16, color: WHITE, valign: "top", margin: 0 });
card(s, 0.6, 4.25, 12.1, 2.35);
s.addText("A second, related failure — found during the live run", { x: 0.9, y: 4.45, w: 11.5, h: 0.35, fontSize: 14, bold: true, color: BLUED, margin: 0 });
s.addText("The dashboard advisory was, at one point, quoting savings figures the model had invented, rather than figures the Analytics Engine had actually computed.",
  { x: 0.9, y: 4.85, w: 11.5, h: 1.6, fontSize: 14, color: INK, valign: "top", margin: 0 });
footer(s, 21);
s.addNotes("These are the two real, observed failures that motivated everything on the next slide. The LaTeX incident happened during development and is the more dramatic of the two — it shows the model attempting arithmetic and failing visibly. The advisory incident is arguably more dangerous, because an invented but plausible-looking savings figure would not have been obviously wrong to a user reading the dashboard, which is exactly why a silent output guard was needed rather than relying on the failure being obvious.");

// =================================================================== 22. Grounding — the guard built
s = p.addSlide(); s.background = { color: BG }; title(s, "Grounding — the Guard Built");
card(s, 0.6, 1.7, 6.6, 4.9, BLUED);
s.addText("Every model reply is checked. It is discarded, in favour of the original deterministic sentence, if it:",
  { x: 0.9, y: 1.9, w: 6.0, h: 0.7, fontSize: 13.5, color: WHITE, valign: "top", margin: 0 });
bulletBlock(s, [
  "Quotes a figure that was never computed",
  "Shows arithmetic working",
  "Contains LaTeX",
  "Is written in the first person",
  "Opens with congratulations",
  "Runs past three sentences",
], { x: 0.95, y: 2.65, w: 6.1, h: 3.7, fontSize: 13.5, color: WHITE, gap: 12 });
card(s, 7.4, 1.7, 5.3, 4.9);
s.addText("Multi-row answers bypass the model entirely", { x: 7.65, y: 1.9, w: 4.8, h: 0.7, fontSize: 14.5, bold: true, color: BLUED, margin: 0 });
s.addText("Lists, category breakdowns and period comparisons never reach the model at all — a small model reliably garbles anything with more than one row of numbers, so the deterministic, database-computed text is returned directly, with nothing generated left to check.",
  { x: 7.65, y: 2.75, w: 4.85, h: 3.6, fontSize: 13, color: INK, valign: "top", margin: 0 });
footer(s, 22);
s.addNotes("Each item in the left-hand list traces back to an observed failure mode, not a guess — the LaTeX check exists because of the exact incident on the previous slide. The right-hand point is arguably the stronger guarantee of the two, since routing multi-row answers around the model entirely means there is no generated text to fail a check in the first place.");

// =================================================================== 23. Privacy and offline operation
s = p.addSlide(); s.background = { color: BG }; title(s, "Privacy & Offline Operation");
fig(s, "09_deployment_diagram.png", 0.7, 1.6, 7.2, 5.2);
card(s, 8.1, 1.65, 4.6, 5.15, BLUED);
s.addText("In the default configuration", { x: 8.35, y: 1.85, w: 4.1, h: 0.35, fontSize: 14, bold: true, color: WHITE, margin: 0 });
bulletBlock(s, [
  "Nothing leaves the machine",
  "The language model, embeddings and retrieval all run locally",
  "No internet connection is required for the application to function",
  "Every optional component degrades quietly rather than crashing — without llama.cpp the rule-based advisor still answers, without sentence-transformers retrieval falls back to keyword search",
], { x: 8.35, y: 2.35, w: 4.15, h: 4.3, fontSize: 12.5, color: WHITE, gap: 11 });
footer(s, 23);
s.addNotes("A bank statement is about as sensitive as personal data gets, and this slide is the direct payoff of choosing an on-device model over a cloud API in the first place. The graceful-degradation point matters as much as the privacy point — the application was designed so that a missing optional dependency reduces capability rather than availability.");

// =================================================================== 24. Testing
s = p.addSlide(); s.background = { color: BG }; title(s, "Testing", "172 automated tests, all passing, across five files");
const testStats = [["172", "Tests, all passing"], ["5", "Test files"], ["8", "Modules covered"], ["100%", "Routes require login"]];
testStats.forEach(([v, l], i) => {
  const x = 0.6 + i * 3.15; card(s, x, 1.75, 2.9, 1.5);
  s.addText(v, { x, y: 1.88, w: 2.9, h: 0.8, fontSize: 30, bold: true, color: BLUED, align: "center", margin: 0 });
  s.addText(l, { x, y: 2.65, w: 2.9, h: 0.5, fontSize: 11, color: GREY, align: "center", margin: 0 });
});
card(s, 0.6, 3.55, 12.1, 3.05);
bulletBlock(s, [
  "test_parser.py — every sample layout, header detection, balance-delta direction, Indian amount and date formats",
  "test_classifier.py — category placement, rail-versus-merchant precedence, the PREMIUM/EMI trap",
  "test_salary.py — statutory percentages, regime differences, HRA minimum, PF ceiling, marginal relief across the whole relief band",
  "test_analytics.py — summary arithmetic, recurring-commitment restriction, user isolation, fingerprint behaviour",
  "test_chat.py — exact totals from SQL, and every guard rejection reason",
  "test_routes.py — every page requires login; one account can neither read nor delete another account's transaction",
], { x: 0.95, y: 3.75, w: 11.6, h: 2.7, fontSize: 12, gap: 6 });
footer(s, 24);
s.addNotes("Each file maps onto specific modules covered earlier in the deck, and each test name is a specific, checkable claim — for a viva, naming the file that proves a claim is stronger than describing the behaviour alone. test_routes.py's account-isolation test is worth having ready if asked directly how privacy between users is enforced.");

// =================================================================== 25. Live run evidence
s = p.addSlide(); s.background = { color: BG }; title(s, "The Live Run", "Evidence from the finished build, not a simulation");
card(s, 0.6, 1.7, 12.1, 3.15);
bulletBlock(s, [
  "Registered an account, uploaded two statements",
  "69 transactions imported, with 69 distinct fingerprints",
  "A third upload of an already-loaded statement correctly imported nothing",
  "69 embeddings indexed for the chatbot to use",
  "All eleven pages returned HTTP 200 with no template errors",
  "The chatbot answered \"how much did I spend on groceries in June\" with:",
], { x: 0.95, y: 1.9, w: 11.6, h: 2.5, fontSize: 14, gap: 9 });
card(s, 1.4, 4.15, 10.5, 0.85, GREEN);
s.addText("“In June 2026, you spent Rs.4,960 on groceries.”", { x: 1.6, y: 4.15, w: 10.1, h: 0.85, fontSize: 16, bold: true, italic: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
card(s, 0.6, 5.2, 12.1, 1.6, BLUED);
s.addText("Two defects this run exposed, and fixed:", { x: 0.9, y: 5.35, w: 11.5, h: 0.35, fontSize: 13.5, bold: true, color: WHITE, margin: 0 });
s.addText("The dashboard advisory was quoting invented savings figures; and route tests were writing to the real database because Flask-SQLAlchemy binds its engine at init_app — fixed by making the database location properly configurable.",
  { x: 0.9, y: 5.72, w: 11.5, h: 1.0, fontSize: 12, color: "DCE7FF", valign: "top", margin: 0 });
footer(s, 25);
s.addNotes("Every number on this slide happened on the finished build in one continuous run, not across separate isolated tests. Presenting the two defects found and fixed is deliberate — it demonstrates that the live run was a genuine verification step that changed the code, not a rehearsed demo. Being ready to name both fixes precisely, as printed here, is worth doing before the viva.");

// =================================================================== 26. Limitations
s = p.addSlide(); s.background = { color: BG }; title(s, "Limitations, Stated Honestly");
card(s, 0.6, 1.7, 12.1, 4.9);
bulletBlock(s, [
  "The classifier's fallback model has a held-out accuracy of only 64.7% — honestly measured on a corpus deliberately weighted towards ambiguous narrations, but still a real ceiling on the hardest cases.",
  "Bank coverage is limited to the eleven banks currently recognised; a genuinely novel layout would need a new column alias map before it parses correctly.",
  "The on-device model is only 1.5 billion parameters, and is deliberately never trusted with arithmetic or reasoning of its own — this is a design strength, but it does mean the model's own language ability is modest.",
  "The fallback classifier was trained on 746 labelled narrations — a real but modest corpus size for the hardest, most ambiguous cases it has to handle.",
  "The parser's header-scoring window is fixed at the first 25 rows; a bank whose real-world exports carry an unusually long preamble beyond that would need the window widened.",
  "The live run and automated tests validate the system against the bundled sample statements and a single test account at a time; broader multi-user, multi-bank scale testing was outside this semester's scope.",
], { x: 0.95, y: 1.95, w: 11.6, h: 4.5, fontSize: 14, gap: 14 });
footer(s, 26);
s.addNotes("Stating limitations honestly and specifically, with the same real numbers used throughout the deck, is stronger in a viva than either hiding them or being vague. Each limitation here should be recognisable from an earlier slide, since it is the same figure discussed positively earlier, now examined for what it does not yet cover.");

// =================================================================== 27. Future work
s = p.addSlide(); s.background = { color: BG }; title(s, "Future Work");
card(s, 0.6, 1.7, 12.1, 4.9);
numBlock(s, [
  "Grow and diversify the labelled narration corpus beyond 746 examples, and evaluate a stronger fallback model architecture, to raise the classifier's 64.7% held-out accuracy on ambiguous cases.",
  "Extend bank coverage beyond the current eleven banks with additional column alias maps.",
  "Make the parser's preamble-scoring window adaptive rather than fixed at 25 rows, for banks whose real exports need more.",
  "Extend the live-run style of end-to-end verification to more banks and a wider range of account histories, beyond the single test account exercised this semester.",
  "Continue widening the guard's checklist as new model failure modes are observed, in the same way the current checklist grew directly out of the LaTeX and invented-savings-figure incidents.",
], { x: 0.95, y: 1.95, w: 11.6, h: 4.5, fontSize: 15, gap: 16 });
footer(s, 27);
s.addNotes("These five points follow directly from the limitations on the previous slide — each one names the specific number or behaviour that would need to change, rather than a vague aspiration. If asked what would be done differently with more time, the classifier accuracy point is the strongest single answer, since it is the most honestly reported weak point in the whole system.");

// =================================================================== 28. Conclusion
s = p.addSlide(); s.background = { color: BLUED };
s.addText("Conclusion", { x: 0.9, y: 0.55, w: 11, h: 0.7, fontSize: 32, bold: true, color: WHITE, fontFace: "Georgia", margin: 0 });
bulletBlock(s, [
  "A four-layer architecture — browser, Flask application with eight modules, on-device inference, and SQLite — built to read genuinely messy Indian bank statements",
  "A classifier that resolves cryptic narrations correctly by testing merchant identity before generic payment-rail markers",
  "A chatbot and advisory system where every rupee figure is computed by real SQL, and the language model is never trusted with a number",
  "A salary and tax module that reaches all the way to marginal relief, not just the headline rebate",
  "172 automated tests, all passing, plus a live run against real imported data that exposed and fixed two genuine defects",
  "A system that runs on the user's own machine, with nothing leaving it by default",
], { x: 0.95, y: 1.55, w: 11.4, h: 4.8, fontSize: 15, color: WHITE, gap: 13 });
footer(s, 28);
s.addNotes("Use this slide to draw the whole narrative together in one breath: the problem was genuinely hard because Indian bank data is messy and inconsistent, and the system's central design principle throughout — computation by real code, generation only for wording — is what makes its numbers trustworthy rather than merely plausible.");

// =================================================================== 29. Thank you
s = p.addSlide(); s.background = { color: BLUED };
s.addText("Thank You", { x: 0.9, y: 2.6, w: 11, h: 0.9, fontSize: 44, bold: true, color: WHITE, fontFace: "Georgia", margin: 0 });
s.addText("Questions", { x: 0.9, y: 3.5, w: 11, h: 0.6, fontSize: 22, color: "CADCFC", italic: true, margin: 0 });
s.addText("SmartEdit AI — An Intelligent Personal Finance Web Application for Indian Salaried Users",
  { x: 0.9, y: 5.6, w: 11, h: 0.5, fontSize: 13, color: "9DB8F0", margin: 0 });
s.addText("Shyam Sundar  ·  BITS ZG628T — Dissertation  ·  BITS Pilani (WILP)  ·  2026",
  { x: 0.9, y: 6.1, w: 11, h: 0.4, fontSize: 12, color: "9DB8F0", margin: 0 });
s.addNotes("Invite questions. Keep the demo script and the viva question bank from the knowledge transfer guide within reach, since most follow-up questions will land on grounding, the classifier accuracy figure, marginal relief, or privacy — the four topics with the deepest supporting detail in this deck.");

p.writeFile({ fileName: OUT }).then(f => console.log("WROTE", f));
