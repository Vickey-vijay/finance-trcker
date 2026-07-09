// SmartEdit AI — KT / Teaching Guide for the client (docx-js)
const fs = require("fs");
const path = require("path");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
        Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
        WidthType, ShadingType, PageNumber, PageBreak } = require("docx");

const DIR = process.env.DIAGRAMS || path.join(__dirname, "diagrams");
const OUT = process.env.OUTFILE || path.join(__dirname, "SmartEditAI_KT_TeachingGuide.docx");
const BLUE = "1A73E8", BLUED = "1457B8", INK = "1F2733", GREY = "6B7787", GREEN = "1AA260";

const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const para = (t) => new Paragraph({ spacing: { after: 130 }, alignment: AlignmentType.JUSTIFIED, children: [new TextRun({ text: t, size: 22 })] });
const bullet = (t, runs) => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 70 }, children: runs || [new TextRun({ text: t, size: 22 })] });
const num = (t) => new Paragraph({ numbering: { reference: "stp", level: 0 }, spacing: { after: 80 }, children: [new TextRun({ text: t, size: 22 })] });
const code = (t) => new Paragraph({ spacing: { after: 60 }, shading: { fill: "F0F4FA", type: ShadingType.CLEAR },
  children: [new TextRun({ text: t, font: "Consolas", size: 19, color: "0B3D91" })] });

function table(headers, rows, widths) {
  const total = widths.reduce((a, b) => a + b, 0);
  const border = { style: BorderStyle.SINGLE, size: 1, color: "CCD6E6" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const head = new TableRow({ tableHeader: true, children: headers.map((h, i) =>
    new TableCell({ borders, width: { size: widths[i], type: WidthType.DXA }, shading: { fill: BLUED, type: ShadingType.CLEAR },
      margins: { top: 60, bottom: 60, left: 110, right: 110 }, children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: "FFFFFF", size: 20 })] })] })) });
  const rws = rows.map((r, ri) => new TableRow({ children: r.map((c, i) =>
    new TableCell({ borders, width: { size: widths[i], type: WidthType.DXA }, shading: { fill: ri % 2 ? "F2F6FC" : "FFFFFF", type: ShadingType.CLEAR },
      margins: { top: 60, bottom: 60, left: 110, right: 110 }, children: [new Paragraph({ children: [new TextRun({ text: c, size: 20 })] })] })) }));
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, rows: [head, ...rws] });
}

const cover = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 900, after: 120 },
    children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(DIR, "logo.png")),
      transformation: { width: 360, height: 132 }, altText: { title: "logo", description: "SmartEdit AI", name: "logo" } })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200, after: 80 },
    children: [new TextRun({ text: "Knowledge Transfer & Teaching Guide", bold: true, size: 40, color: BLUED, font: "Georgia" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 },
    children: [new TextRun({ text: "How SmartEdit AI works — explained simply", size: 24, color: INK })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 500, after: 40 },
    children: [new TextRun({ text: "Prepared for: Shyam Sundar", size: 22, color: INK, bold: true })] }),
  new Paragraph({ alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "June 2026", size: 20, color: GREY })] }),
  new Paragraph({ children: [new PageBreak()] }),
];

const body = [];
body.push(h1("1. What is SmartEdit AI?"));
body.push(para("SmartEdit AI is a website where you can understand your money. You upload your monthly bank statement (a PDF or CSV file) — or type entries yourself — and the app reads every transaction, sorts each one into a category, shows you where your money went, and gives you smart, specific advice on how to save. There is also a chat assistant you can simply ask questions like \"how much did I spend on Amazon?\""));
body.push(para("In one line: Upload your statement → see where every rupee went → get a plan for next month."));

body.push(h1("2. The five screens"));
body.push(para("After you log in, there are five simple tabs on the left. Here is what each one does:"));
body.push(table(["Screen", "What you do there"],
  [["Dashboard", "See this month's income, expenses, savings, a category chart, and AI advice. For a new account it asks you to upload your statement."],
   ["Add Entry", "Manually add a single credit (money in) or debit (money out). Leave the category blank and the app picks it for you."],
   ["View / Database", "The full table of all your transactions. Filter by category or type, change a category, or delete a row."],
   ["Tracker", "Charts showing money in vs out — daily, monthly, and by day of the week."],
   ["AI Chat", "Ask anything about your spending in plain language; the assistant reads your data and answers."]],
  [2200, 7160]));

body.push(h1("3. How it works behind the scenes (in simple words)"));
body.push(h2("3.1 Reading your statement"));
body.push(para("When you upload a PDF or CSV, the app opens the file and pulls out each transaction row — the date, the description, and the amount. Indian banks (SBI, HDFC, ICICI, Axis) all format statements differently, so the app is built to understand their different column styles automatically."));
body.push(h2("3.2 Sorting transactions into categories"));
body.push(para("Bank descriptions are cryptic — things like 'UPI-SWIGGY-OKAXIS-XXXX'. The app recognises keywords and files each transaction under the right category. For example:"));
body.push(bullet("SWIGGY / ZOMATO → Food & Dining"));
body.push(bullet("LIC / PREMIUM → Insurance"));
body.push(bullet("NETFLIX / SPOTIFY → Subscriptions"));
body.push(bullet("AMAZON / FLIPKART → Shopping"));
body.push(para("If it isn't sure, it puts the transaction under 'Others' and you can correct it on the View screen with one click."));
body.push(h2("3.3 The AI advice"));
body.push(para("Once your data is in, the app summarises your spending and asks the AI model to suggest specific savings — with real rupee figures, not vague tips. For example: \"Your food delivery spend is Rs.1,348; capping to 3 orders a week saves about Rs.800 next month.\""));
body.push(h2("3.4 The chat assistant (RAG)"));
body.push(para("When you ask a question, the assistant finds the transactions most related to your question and also calculates exact totals from the database, then writes a clear answer. Because it uses your real numbers, the answers are accurate."));
body.push(img_safe());

body.push(new Paragraph({ children: [new PageBreak()] }));
body.push(h1("4. How YOU use it day to day"));
body.push(num("Open the app and log in (or register the first time)."));
body.push(num("On the Dashboard, upload one month of your bank statement (PDF or CSV)."));
body.push(num("Wait a moment — the app reads and sorts every transaction automatically."));
body.push(num("Look at the Dashboard: income, expenses, savings, and the category chart fill in."));
body.push(num("Go to View / Database to check the transactions; fix any category if needed."));
body.push(num("Open Tracker to see your daily and monthly money flow."));
body.push(num("Use AI Chat to ask questions or ask how to save more."));
body.push(num("Add any cash spends the bank didn't capture using Add Entry."));
body.push(para("Tip: Upload at least one full month so the app has enough to analyse. You can upload more months anytime to build history."));

body.push(h1("5. How to add or edit entries yourself"));
body.push(para("You are fully in control of your data:"));
body.push(bullet("Add: Add Entry tab → choose Credit or Debit → type the amount and a short description → Save. The category is detected automatically (or pick one)."));
body.push(bullet("Re-categorise: View / Database tab → use the dropdown in the Category column → choose the right category. It updates instantly."));
body.push(bullet("Delete: View / Database tab → click the ✕ button on a row → confirm."));

body.push(h1("6. Running the app (for setup)"));
body.push(para("The app is a Python project. To start it on a computer:"));
body.push(code("cd SmartEditAI"));
body.push(code("python -m venv .venv  &&  .venv\\Scripts\\activate   (Windows)"));
body.push(code("pip install -r requirements.txt"));
body.push(code("copy .env.example .env      (then add your free Gemini key)"));
body.push(code("python app.py"));
body.push(para("Then open http://localhost:5000 in a browser. Use the file sample_data/sample_statement.csv to try it immediately."));

body.push(h1("7. About the AI model"));
body.push(para("Right now the app uses the Gemini API (a free key from Google). It is set up so that later we can switch to a fully local model with Ollama — meaning your financial data never leaves your computer. Changing it is a single setting (LLM_PROVIDER) in the .env file; nothing else changes. If there is ever no internet or no key, the app still works using a built-in offline advisor and search, so a demo never fails."));
body.push(table(["Setting", "Meaning"],
  [["LLM_PROVIDER=gemini", "Use the Gemini API (needs a free key)"],
   ["LLM_PROVIDER=ollama", "Use a local model on your own machine (private)"],
   ["LLM_PROVIDER=fallback", "Work fully offline with built-in logic"]],
  [3200, 6160]));

body.push(h1("8. Key terms (quick glossary)"));
body.push(table(["Term", "Simple meaning"],
  [["PDF/CSV parsing", "Reading transactions out of your statement file automatically"],
   ["Category", "The bucket a transaction goes into (Food, Travel, EMI, etc.)"],
   ["Credit / Debit", "Money coming in / money going out"],
   ["Savings rate", "What share of your income you kept this month"],
   ["RAG", "A method where the AI first looks up your real data, then answers"],
   ["Embedding", "Turning text into numbers so similar things can be matched"],
   ["Ollama", "A tool to run an AI model privately on your own computer"]],
  [2600, 6760]));

body.push(new Paragraph({ spacing: { before: 240 }, alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: "You're all set. Upload a statement, explore the tabs, and ask the assistant anything.", italics: true, size: 22, color: GREEN })] }));

function img_safe() {
  try {
    return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 160, after: 200 },
      children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(DIR, "07_data_flow.png")),
        transformation: { width: 560, height: 233 }, altText: { title: "flow", description: "How data flows", name: "flow" } })] });
  } catch (e) { return new Paragraph({ children: [new TextRun("")] }); }
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Calibri", size: 22, color: INK } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 30, bold: true, color: BLUED, font: "Georgia" }, paragraph: { spacing: { before: 280, after: 150 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: BLUE }, paragraph: { spacing: { before: 180, after: 110 }, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 600, hanging: 280 } } } }] },
    { reference: "stp", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 600, hanging: 320 } } } }] },
  ] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "SmartEdit AI — Teaching Guide", size: 16, color: GREY })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Page ", size: 16, color: GREY }), new TextRun({ children: [PageNumber.CURRENT], size: 16, color: GREY })] })] }) },
    children: [...cover, ...body],
  }],
});

Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log("WROTE", OUT, buf.length); });
