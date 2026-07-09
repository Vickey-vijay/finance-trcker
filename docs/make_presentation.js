// SmartEdit AI — Mid-Semester Presentation (pptxgenjs)
const pptxgen = require("pptxgenjs");
const path = require("path");

const DIR = process.env.DIAGRAMS || path.join(__dirname, "diagrams");
const OUT = process.env.OUTFILE || path.join(__dirname, "SmartEditAI_MidSem_Presentation.pptx");

const BLUE = "1A73E8", BLUED = "1457B8", INK = "1F2733", GREY = "6B7787",
      LIGHT = "E8F0FE", GREEN = "1AA260", WHITE = "FFFFFF", BG = "F6F9FC";

const p = new pptxgen();
p.layout = "LAYOUT_WIDE";            // 13.3 x 7.5
p.author = "Shyam Sundar";
p.title = "SmartEdit AI — Mid-Semester Review";
const W = 13.3, H = 7.5;
const shadow = () => ({ type: "outer", color: "1457B8", blur: 8, offset: 2, angle: 135, opacity: 0.12 });

function footer(s, n) {
  s.addText("SmartEdit AI  ·  Mid-Semester Review", { x: 0.5, y: H - 0.45, w: 8, h: 0.3, fontSize: 9, color: GREY });
  s.addText(`${n} / 10`, { x: W - 1.3, y: H - 0.45, w: 0.8, h: 0.3, fontSize: 9, color: GREY, align: "right" });
}
function title(s, t, sub) {
  s.addText(t, { x: 0.5, y: 0.4, w: W - 1, h: 0.6, fontSize: 30, bold: true, color: BLUED, fontFace: "Georgia", margin: 0 });
  if (sub) s.addText(sub, { x: 0.5, y: 1.05, w: W - 1, h: 0.4, fontSize: 14, color: GREY, italic: true, margin: 0 });
}
function card(s, x, y, w, h, fill) {
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill || WHITE }, line: { color: LIGHT, width: 1 }, rectRadius: 0.08, shadow: shadow() });
}

// ----------------------------------------------------------- Slide 1 — Title
let s = p.addSlide(); s.background = { color: BLUED };
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.9, y: 2.5, w: 1.5, h: 1.5, fill: { color: WHITE }, rectRadius: 0.2 });
[0.55, 0.95, 1.35].forEach((hh, i) =>
  s.addShape(p.shapes.RECTANGLE, { x: 1.2 + i * 0.33, y: 3.5 - hh, w: 0.22, h: hh, fill: { color: BLUE } }));
s.addText("SmartEdit AI", { x: 2.7, y: 2.55, w: 9.5, h: 1.0, fontSize: 52, bold: true, color: WHITE, fontFace: "Georgia", margin: 0 });
s.addText("An Intelligent Personal Finance Web App for Indian Salaried Users",
  { x: 2.72, y: 3.6, w: 9.5, h: 0.6, fontSize: 18, color: "CADCFC", margin: 0 });
s.addText("Mid-Semester Project Review", { x: 2.72, y: 4.2, w: 9, h: 0.4, fontSize: 14, color: "9DB8F0", italic: true, margin: 0 });
s.addText([
  { text: "Student: Shyam Sundar", options: { breakLine: true } },
  { text: "Research Area: NLP · Personal Finance · AI Advisory · Behavioral Finance", options: { breakLine: true } },
  { text: "June 2026" }],
  { x: 0.9, y: 5.7, w: 11, h: 1.1, fontSize: 13, color: "CADCFC" });

// ----------------------------------------------------------- Slide 2 — Agenda
s = p.addSlide(); s.background = { color: BG }; title(s, "Agenda");
const agenda = ["The Problem", "Objectives & Scope", "System Architecture", "Methodology — Parsing & NLP",
  "AI Advisory & RAG Chatbot", "Application Walkthrough", "Progress & Demo", "Plan to Completion"];
agenda.forEach((t, i) => {
  const col = i % 2, row = Math.floor(i / 2);
  const x = 0.6 + col * 6.3, y = 1.7 + row * 1.25;
  card(s, x, y, 6.0, 1.0);
  s.addShape(p.shapes.OVAL, { x: x + 0.25, y: y + 0.25, w: 0.5, h: 0.5, fill: { color: BLUE } });
  s.addText(String(i + 1), { x: x + 0.25, y: y + 0.25, w: 0.5, h: 0.5, fontSize: 18, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
  s.addText(t, { x: x + 0.95, y: y, w: 4.9, h: 1.0, fontSize: 16, bold: true, color: INK, valign: "middle", margin: 0 });
});
footer(s, 2);

// ----------------------------------------------------------- Slide 3 — Problem
s = p.addSlide(); s.background = { color: BG }; title(s, "The Problem", "Where did the money go?");
card(s, 0.6, 1.7, 5.6, 4.8, BLUED);
s.addText([
  { text: "End of month.\n", options: { fontSize: 18, bold: true, color: WHITE, breakLine: true } },
  { text: "Rs.12,400 left in the account. You remember the rent and a few grocery runs. The rest — Swiggy, random UPI transfers, a forgotten subscription — is a blur.\n\n", options: { fontSize: 14, color: "DCE7FF", breakLine: true } },
  { text: "The statement is right there as a PDF. But 80 rows of ", options: { fontSize: 14, color: "DCE7FF" } },
  { text: "‘POS-4521-RELIANCE’", options: { fontSize: 14, color: WHITE, italic: true } },
  { text: " and ", options: { fontSize: 14, color: "DCE7FF" } },
  { text: "‘UPI-SWIGGY-OKAXIS’", options: { fontSize: 14, color: WHITE, italic: true } },
  { text: " tell you nothing useful.", options: { fontSize: 14, color: "DCE7FF" } }],
  { x: 0.95, y: 2.0, w: 4.9, h: 4.2, valign: "top", margin: 0 });
s.addText("3 gaps no existing app solves together for Indian users:", { x: 6.5, y: 1.7, w: 6.2, h: 0.4, fontSize: 15, bold: true, color: BLUED, margin: 0 });
const gaps = [
  ["No Indian PDF support", "SBI, HDFC, ICICI, Axis all use different layouts. Apps rely on SMS parsing (now blocked) or manual entry."],
  ["Advice is just arithmetic", "“You spent 30% more on food” is a chart, not guidance. It never says what to change."],
  ["No plan from real data", "No app reads your statement and builds a realistic next-month budget from how you actually spend."]];
gaps.forEach(([h, d], i) => {
  const y = 2.25 + i * 1.42; card(s, 6.5, y, 6.3, 1.25);
  s.addText(`${i + 1}`, { x: 6.7, y: y + 0.2, w: 0.55, h: 0.55, fontSize: 20, bold: true, color: WHITE, align: "center", valign: "middle", fill: { color: BLUE }, margin: 0 });
  s.addShape(p.shapes.OVAL, { x: 6.7, y: y + 0.2, w: 0.55, h: 0.55, fill: { color: BLUE } });
  s.addText(`${i + 1}`, { x: 6.7, y: y + 0.2, w: 0.55, h: 0.55, fontSize: 20, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
  s.addText(h, { x: 7.45, y: y + 0.12, w: 5.2, h: 0.4, fontSize: 14, bold: true, color: INK, margin: 0 });
  s.addText(d, { x: 7.45, y: y + 0.5, w: 5.25, h: 0.7, fontSize: 11.5, color: GREY, margin: 0 });
});
footer(s, 3);

// ----------------------------------------------------------- Slide 4 — Objectives & Scope
s = p.addSlide(); s.background = { color: BG }; title(s, "Objectives & Scope");
card(s, 0.6, 1.7, 6.1, 4.9);
s.addText("Objectives", { x: 0.9, y: 1.9, w: 5.5, h: 0.4, fontSize: 17, bold: true, color: BLUED, margin: 0 });
s.addText([
  "Parse Indian bank statement PDFs/CSVs (SBI, HDFC, ICICI, Axis)",
  "Classify cryptic UPI/NEFT/NACH/POS descriptions into categories",
  "Dashboard: income, expense, savings rate, category trends",
  "AI advisory grounded in the user’s actual transactions",
  "RAG chatbot to answer free-form questions on spending",
  "Privacy-first: local LLM (Ollama) in the final version"
].map((t, i, a) => ({ text: t, options: { bullet: true, breakLine: true, fontSize: 13, color: INK, paraSpaceAfter: 8 } })),
  { x: 0.95, y: 2.35, w: 5.6, h: 4.1, valign: "top" });
card(s, 6.9, 1.7, 5.9, 4.9);
s.addText("Scope", { x: 7.2, y: 1.9, w: 5.3, h: 0.4, fontSize: 17, bold: true, color: GREEN, margin: 0 });
s.addText([
  { text: "IN SCOPE\n", options: { fontSize: 12, bold: true, color: GREEN, breakLine: true } },
  { text: "Web app · PDF/CSV parsing · manual entry · classification · analytics · AI advisory · RAG chat · Indian salary (PF/HRA/TDS) model\n\n", options: { fontSize: 12.5, color: INK, breakLine: true, paraSpaceAfter: 6 } },
  { text: "OUT OF SCOPE (v1)\n", options: { fontSize: 12, bold: true, color: GREY, breakLine: true } },
  { text: "Investment portfolio tracking · real-time bank API linking · multi-currency · native mobile app", options: { fontSize: 12.5, color: GREY } }],
  { x: 7.2, y: 2.35, w: 5.4, h: 4.1, valign: "top", margin: 0 });
footer(s, 4);

// ----------------------------------------------------------- Slide 5 — Architecture
s = p.addSlide(); s.background = { color: BG }; title(s, "System Architecture", "Six modules over Flask + SQLite, with a swappable AI provider");
s.addImage({ path: path.join(DIR, "01_system_architecture.png"), x: 0.7, y: 1.6, w: 9.4, h: 5.2, sizing: { type: "contain", w: 9.4, h: 5.2 } });
const stack = [["Frontend", "HTML · CSS · Chart.js"], ["Backend", "Flask · SQLAlchemy"], ["Database", "SQLite"], ["Parsing", "pdfplumber · pandas"], ["AI", "Gemini → Ollama"], ["RAG", "MiniLM + cosine"]];
stack.forEach(([h, d], i) => {
  const y = 1.7 + i * 0.84; card(s, 10.4, y, 2.5, 0.74, LIGHT);
  s.addText(h, { x: 10.55, y: y + 0.06, w: 2.2, h: 0.3, fontSize: 12, bold: true, color: BLUED, margin: 0 });
  s.addText(d, { x: 10.55, y: y + 0.36, w: 2.25, h: 0.32, fontSize: 9.5, color: GREY, margin: 0 });
});
footer(s, 5);

// ----------------------------------------------------------- Slide 6 — Methodology
s = p.addSlide(); s.background = { color: BG }; title(s, "Methodology — Parsing & NLP Classification");
card(s, 0.6, 1.7, 6.1, 4.9);
s.addText("1 · PDF / CSV Parsing", { x: 0.9, y: 1.9, w: 5.5, h: 0.4, fontSize: 16, bold: true, color: BLUED, margin: 0 });
s.addText([
  "pdfplumber extracts tables page-by-page; pandas reads CSV",
  "Auto-maps Date / Narration / Debit / Credit columns",
  "Handles mixed date formats & ₹1,23,456 separators",
  "Normalises every row → (date, description, amount, type)"
].map(t => ({ text: t, options: { bullet: true, breakLine: true, fontSize: 13, color: INK, paraSpaceAfter: 7 } })),
  { x: 0.95, y: 2.4, w: 5.6, h: 4.0, valign: "top" });
card(s, 6.9, 1.7, 5.9, 4.9);
s.addText("2 · Transaction Classification", { x: 7.2, y: 1.9, w: 5.4, h: 0.4, fontSize: 16, bold: true, color: BLUED, margin: 0 });
s.addText([
  "India-aware rule engine over the raw description",
  "SWIGGY → Food · LIC → Insurance · NETFLIX → Subscriptions",
  "Detects UPI / NEFT / NACH / POS / IMPS method markers",
  "17 categories; unknown → Others, user can re-categorise"
].map(t => ({ text: t, options: { bullet: true, breakLine: true, fontSize: 13, color: INK, paraSpaceAfter: 7 } })),
  { x: 7.2, y: 2.4, w: 5.4, h: 2.3, valign: "top" });
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 7.2, y: 5.05, w: 5.3, h: 1.4, fill: { color: LIGHT }, rectRadius: 0.06 });
s.addText([
  { text: "Example\n", options: { fontSize: 11, bold: true, color: BLUED, breakLine: true } },
  { text: "“UPI-SWIGGY-OKAXIS-XXXX1234”  →  Food & Dining  (method: UPI)", options: { fontSize: 12, color: INK } }],
  { x: 7.4, y: 5.2, w: 4.95, h: 1.1, valign: "top", margin: 0 });
footer(s, 6);

// ----------------------------------------------------------- Slide 7 — AI Advisory & RAG
s = p.addSlide(); s.background = { color: BG }; title(s, "AI Advisory & RAG Chatbot");
card(s, 0.6, 1.65, 5.7, 5.0, BLUED);
s.addText("AI Savings Advisory", { x: 0.9, y: 1.85, w: 5.1, h: 0.4, fontSize: 16, bold: true, color: WHITE, margin: 0 });
s.addText([
  { text: "Chain-of-thought prompt over the categorised monthly summary produces specific, rupee-level advice — not generic tips.\n\n", options: { fontSize: 13, color: "DCE7FF", breakLine: true } },
  { text: "“Your Swiggy + Zomato spend is Rs.1,348. Capping to 3 orders/week saves about Rs.800 next month.”\n\n", options: { fontSize: 13, italic: true, color: WHITE, breakLine: true } },
  { text: "Provider: Gemini now → Ollama (local) later. Deterministic fallback if offline — the demo never breaks.", options: { fontSize: 12, color: "CADCFC" } }],
  { x: 0.95, y: 2.35, w: 5.0, h: 4.1, valign: "top", margin: 0 });
s.addText("RAG Chatbot (retrieval pipeline)", { x: 6.6, y: 1.65, w: 6.2, h: 0.4, fontSize: 16, bold: true, color: BLUED, margin: 0 });
const steps = [["Embed", "Question → vector (MiniLM, 384-d)"], ["Search", "Cosine similarity vs stored transaction vectors"],
  ["Aggregate", "Exact SQL totals so numbers are never hallucinated"], ["Generate", "Top-K + totals → LLM → grounded answer"]];
steps.forEach(([h, d], i) => {
  const y = 2.15 + i * 1.07; card(s, 6.6, y, 6.2, 0.92);
  s.addShape(p.shapes.OVAL, { x: 6.78, y: y + 0.2, w: 0.5, h: 0.5, fill: { color: GREEN } });
  s.addText(String(i + 1), { x: 6.78, y: y + 0.2, w: 0.5, h: 0.5, fontSize: 16, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
  s.addText(h, { x: 7.45, y: y + 0.1, w: 5.2, h: 0.35, fontSize: 13.5, bold: true, color: INK, margin: 0 });
  s.addText(d, { x: 7.45, y: y + 0.44, w: 5.25, h: 0.4, fontSize: 11, color: GREY, margin: 0 });
});
footer(s, 7);

// ----------------------------------------------------------- Slide 8 — Walkthrough (use case)
s = p.addSlide(); s.background = { color: BG }; title(s, "Application Walkthrough", "Five clean screens: Dashboard · Add · View · Tracker · Chat");
s.addImage({ path: path.join(DIR, "02_use_case.png"), x: 0.7, y: 1.7, w: 12.0, h: 5.0, sizing: { type: "contain", w: 12.0, h: 5.0 } });
footer(s, 8);

// ----------------------------------------------------------- Slide 9 — Progress
s = p.addSlide(); s.background = { color: BG }; title(s, "Progress & Demo");
const stats = [["100%", "Core app working", BLUE], ["17", "Spend categories", GREEN], ["30+", "Txns parsed in demo", BLUED], ["6", "Backend modules", BLUE]];
stats.forEach(([v, l, c], i) => {
  const x = 0.6 + i * 3.15; card(s, x, 1.7, 2.9, 1.6);
  s.addText(v, { x: x, y: 1.85, w: 2.9, h: 0.85, fontSize: 40, bold: true, color: c, align: "center", margin: 0 });
  s.addText(l, { x: x, y: 2.7, w: 2.9, h: 0.5, fontSize: 12, color: GREY, align: "center", margin: 0 });
});
card(s, 0.6, 3.55, 12.2, 3.0);
s.addText("Done so far", { x: 0.9, y: 3.7, w: 5.5, h: 0.35, fontSize: 15, bold: true, color: GREEN, margin: 0 });
s.addText([
  "Auth, dashboard, add-entry, view/database, tracker, chat",
  "PDF/CSV parser + India-aware classifier (verified end-to-end)",
  "AI advisory + RAG chatbot with offline fallback",
  "Clean white/blue UI; SQLite persistence"
].map(t => ({ text: t, options: { bullet: true, breakLine: true, fontSize: 12.5, color: INK, paraSpaceAfter: 6 } })),
  { x: 0.95, y: 4.1, w: 5.9, h: 2.3, valign: "top" });
s.addText("Demo flow", { x: 6.9, y: 3.7, w: 5.5, h: 0.35, fontSize: 15, bold: true, color: BLUED, margin: 0 });
s.addText([
  "Register → land on empty dashboard",
  "Upload one month statement (CSV/PDF)",
  "Transactions auto-categorised → dashboard fills",
  "Ask chatbot: “how much on Amazon?” → exact total"
].map((t, i) => ({ text: t, options: { bullet: { type: "number" }, breakLine: true, fontSize: 12.5, color: INK, paraSpaceAfter: 6 } })),
  { x: 7.2, y: 4.1, w: 5.5, h: 2.3, valign: "top" });
footer(s, 9);

// ----------------------------------------------------------- Slide 10 — Plan / Thank you
s = p.addSlide(); s.background = { color: BLUED };
s.addText("Plan to Completion", { x: 0.9, y: 0.55, w: 11, h: 0.6, fontSize: 28, bold: true, color: WHITE, fontFace: "Georgia", margin: 0 });
const plan = [["Now – Wk 2", "Add more bank PDF formats; refine parser edge cases"],
  ["Wk 3 – 4", "Lightweight ML classifier for ambiguous descriptions"],
  ["Wk 5 – 6", "Indian salary (CTC/PF/TDS) module + savings goals"],
  ["Wk 7 – 8", "Swap Gemini → Ollama (local), evaluate advisory quality"]];
plan.forEach(([w, d], i) => {
  const y = 1.5 + i * 1.0;
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.9, y, w: 2.6, h: 0.8, fill: { color: BLUE }, rectRadius: 0.06 });
  s.addText(w, { x: 0.9, y, w: 2.6, h: 0.8, fontSize: 13, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 3.7, y, w: 8.7, h: 0.8, fill: { color: "21407A" }, rectRadius: 0.06 });
  s.addText(d, { x: 3.95, y, w: 8.3, h: 0.8, fontSize: 13, color: "DCE7FF", valign: "middle", margin: 0 });
});
s.addText("Thank you", { x: 0.9, y: 5.9, w: 11, h: 0.6, fontSize: 26, bold: true, color: WHITE, fontFace: "Georgia", margin: 0 });
s.addText("Upload your statement. See where every rupee went. Plan better.", { x: 0.92, y: 6.55, w: 11, h: 0.4, fontSize: 14, italic: true, color: "CADCFC", margin: 0 });

p.writeFile({ fileName: OUT }).then(f => console.log("WROTE", f));
