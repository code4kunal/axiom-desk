// Every string the landing shell can show lives here, so the copy test sees all of it.
import { WEIGHTS_A, WEIGHTS_B } from "./hero/weights.ts";

export const sections = [
  { id: "season", label: "Season" },
  { id: "one-desk", label: "Desk" },
  { id: "sectors", label: "Sectors" },
  { id: "charts", label: "Charts" },
  { id: "options", label: "Options" },
  { id: "strategies", label: "Strategies" },
  { id: "baskets", label: "Baskets" },
  { id: "agent", label: "Agent" },
] as const;

export const shell = {
  skip: "Skip to content",
  navLabel: "Sections",
  indexTrigger: "Index",
  disclaimer: "Research tool. Not investment advice. No performance is promised.",
  footerIndexLabel: "Section index",
  footerCaption: "AXIOM · EN-IN · ILLUSTRATIVE SCREENS ONLY",
  theme: "Theme",
  themeChoices: { system: "System", dark: "Dark", light: "Light" },
  close: "Close",
  privacy: "Privacy",
  terms: "Terms",
};

export const notFound = {
  title: "Page not found",
  caption: "STATUS 404 · NO PAGE AT THIS ADDRESS",
  heading: "No reading at this address.",
  body: "There is no page here. The address may have changed, or it never existed.",
  home: "Go to the start",
  hint: "Or pick a section from the index above.",
};

// Desk sign-in. Keys of signInErrors are the fixed codes the API puts in /sign-in?error=.
const failed = { label: "SIGN-IN FAILED", message: "Sign-in did not complete.", next: "Try again. If it keeps failing, tell your desk admin." };

export const signInErrors = {
  mfa_required: {
    label: "SECOND FACTOR NEEDED",
    message: "Your sign-in did not use multi-factor authentication.",
    next: "Sign in again and complete the second step at your provider.",
  },
  unknown_user: {
    label: "NOT ON THIS DESK",
    message: "Your account signed in, but it is not set up on this desk.",
    next: "Ask your desk admin to add you, then sign in again.",
  },
  expired: { label: "SIGN-IN EXPIRED", message: "That sign-in expired or was already used.", next: "Start again with Sign in." },
  cancelled: { label: "SIGN-IN CANCELLED", message: "You cancelled sign-in at your provider.", next: "Sign in again when you are ready." },
  provider_unavailable: {
    label: "PROVIDER UNREACHABLE",
    message: "We could not reach your sign-in provider.",
    next: "Wait a minute and try again. If it keeps failing, tell your desk admin.",
  },
  failed,
};

export const signIn = {
  title: "Sign in | Axiom Desk",
  errorTitle: "Sign-in problem | Axiom Desk",
  caption: "AXIOM DESK",
  heading: "Sign in",
  body: "Use your desk account. You will be sent to your sign-in provider and brought back here.",
  action: "Sign in",
  hint: "Trouble signing in? Ask your desk admin.",
};

export const desk = {
  title: "Desk | Axiom",
  caption: "SIGNED IN",
  tenantLabel: "BROKER",
  body: "The desk is being built. Nothing to open yet.",
  signOut: "Sign out",
  unreachable: {
    title: "Desk unavailable | Axiom",
    caption: "DESK SERVICE",
    heading: "The desk is not responding",
    label: "SERVICE UNREACHABLE",
    message: "We could not reach the desk service.",
    next: "Reload to try again. If it keeps failing, tell your desk admin.",
    reload: "Reload",
  },
};

const pending = { stamp: "PENDING", notice: "Text pending legal review.", back: "Back to the start" };

export const privacy = {
  ...pending,
  title: "Privacy notice",
  caption: "PRIVACY NOTICE · DRAFT",
  body: [
    "This page will carry Axiom’s privacy notice once counsel has reviewed it. Until then nothing here is a statement of practice.",
    "What this site does today: it keeps one setting in your browser, your theme choice. It has no forms and sends nothing you type.",
  ],
};

export const terms = {
  ...pending,
  title: "Terms of use",
  caption: "TERMS OF USE · DRAFT",
  body: [
    "This page will carry the terms for using this site once counsel has reviewed them. Until then the footer line stands: research tool, not investment advice, no performance is promised.",
  ],
};

const statement = "Markets have seasons. Axiom reads the season, reweights the basket, and shows its evidence.";
const subline = "A research desk for Indian investors. It drafts every trade; a person confirms it.";
const hedgeCard = "HEDGE DRAFT · INDEX PROTECTION · ILLUSTRATIVE · Cover that softens a fall. Nothing is placed until a person confirms it.";

export const meta = {
  title: "Axiom",
  description: subline,
  ogTitle: "Axiom",
  ogDescription: statement,
};

// The basket split in percentages (the user asked for numbers here, not words standing in for them).
const ASSETS = ["Equity", "Gilts", "Gold", "Cash", "Global"];
const pct = (w: number) => `${w}%`;
// Only the assets that move: "EQUITY 61% → 42% · GILTS 18% → 29% · GOLD 9% → 17%".
const moved = ASSETS.flatMap((a, k) =>
  WEIGHTS_A[k] === WEIGHTS_B[k] ? [] : [`${a.toUpperCase()} ${pct(WEIGHTS_A[k]!)} → ${pct(WEIGHTS_B[k]!)}`],
).join(" · ");

export const hero = {
  statement,
  subline,
  primary: "See how it reads a market",
  brokers: "For brokers",
  // Stacked plates 0 / 40 / 70 / 100; the last plate's caption is the hedge card. Season names follow
  // the regime engine (R39): Risk-on, Early deterioration (said here as "early warning"), Risk-off, Recovery.
  plates: [
    { caption: "SEASON · RISK-ON · ILLUSTRATIVE", state: "RISK-ON", tone: "monsoon" },
    { caption: "SEASON · EARLY WARNING · ILLUSTRATIVE", state: "EARLY WARNING", tone: "geru" },
    { caption: `${moved} · ILLUSTRATIVE` },
  ],
  hedgeCard,
  // One plain sentence per dock (0, 40, 70, 100), above each mono caption, so the pin reads as a story.
  steps: [
    { label: "STEP 1 OF 4", say: "Risk-on. Most sectors are rising, so the basket leans on equity." },
    { label: "STEP 2 OF 4", say: "Early warning. Fewer sectors are rising, and Axiom flags the change." },
    { label: "STEP 3 OF 4", say: "Axiom moves money out of equity and into gilts and gold." },
    { label: "STEP 4 OF 4", say: "It drafts a hedge. Nothing is placed until a person confirms it." },
  ],
  // The ring's hole, one per dock (0, 40, 70, 100): the equity share, the slice that moves. The season is in
  // the step line and caption beside it; repeating it here wrapped to three lines in the narrow plates.
  hole: [
    { word: pct(WEIGHTS_A[0]!), note: "EQUITY", tone: "monsoon" },
    { word: pct(WEIGHTS_A[0]!), note: "EQUITY", tone: "geru" },
    { word: pct(WEIGHTS_B[0]!), note: "EQUITY", tone: "geru" },
    { word: pct(WEIGHTS_B[0]!), note: "EQUITY", tone: "geru" },
  ],
  // Basket legend under the ring, from the weights the ring draws; it cuts from before to after at dock 70.
  legend: {
    labels: ASSETS,
    before: WEIGHTS_A.map(pct),
    after: WEIGHTS_B.map(pct),
  },
};

// 02: the whole desk on one sheet; each item links to the story that shows it.
export const oneDesk = {
  heading: "One desk instead of four tools.",
  lede: "Most investors keep a charting site, a screener, an options tool and a spreadsheet open at once. Axiom puts the whole job in one place.",
  items: [
    { name: "Sector rotation", say: "See which sectors are leading and which are fading.", href: "#sectors" },
    { name: "Smart-money flows", say: "Who is moving money: foreign investors, funds and company owners.", href: "#sectors" },
    { name: "Macro tracker", say: "Global and Indian macro, next to the sectors it moves.", href: "#sectors" },
    { name: "Morning view", say: "One screen before the open: the season, the sectors, what changed.", href: "#sectors" },
    { name: "Live chart signals", say: "Signals on the chart as they happen, each with its track record.", href: "#charts" },
    { name: "Screener", say: "Finds stock trades with a suggested entry and exit.", href: "#charts" },
    { name: "Daily watchlist", say: "A short list picked for you each morning.", href: "#charts" },
    { name: "Option chain", say: "A deep, live chain with flows and open interest.", href: "#options" },
    { name: "Volatility premium", say: "Ranks option trades by how much premium they carry.", href: "#options" },
    { name: "Strategies and backtests", say: "Build a strategy and test it on past markets.", href: "#strategies" },
    { name: "Multi-asset baskets", say: "Equity, gilts, gold, cash and global assets in one basket.", href: "#baskets" },
    { name: "Hedges", say: "Drafted when the season turns. You confirm.", href: "#baskets" },
    { name: "AI agent", say: "Ask for a screen or an option trade in plain words.", href: "#agent" },
  ],
  proof: "Every signal says how often it has worked before. When there is not enough history, it says so.",
};

export const sectors = {
  heading: "See which sectors have the wind behind them.",
  lede: "Volume shows what everyone sees. Axiom watches who is moving the money: foreign investors (FIIs), mutual funds and company owners. It reads the economy at home and abroad alongside, and each morning shows which sectors are gaining, leading or fading.",
  caption: "SECTOR ROTATION · SMART-MONEY FLOWS · MACRO · MORNING VIEW",
  clip: { label: "ILLUSTRATIVE", shape: "landscape" },
  // The four seasons of the regime engine, in the order a cycle runs.
  cycle: [
    { name: "Risk-on", say: "Most sectors rise." },
    { name: "Early warning", say: "Fewer sectors join in." },
    { name: "Risk-off", say: "Most sectors fall." },
    { name: "Recovery", say: "Leaders start to rise again." },
  ],
  scene: {
    title: "SECTOR ROTATION",
    leading: "LEADING",
    fading: "FADING",
    before: ["Banks", "IT", "Autos", "Metals", "Pharma", "FMCG"],
    after: ["Pharma", "FMCG", "Banks", "Autos", "IT", "Metals"],
  },
};

export const charts = {
  heading: "Charts that tell you how often a signal has worked.",
  lede: "Your charts move together. Signals appear as they happen, the screener finds stock trades with an entry and an exit, and a short watchlist is ready each morning.",
  caption: "LIVE SIGNALS · SCREENER · DAILY WATCHLIST",
  clip: { label: "ILLUSTRATIVE", shape: "landscape" },
  // Tags the clip pins on two of its panes: one signal with a record, one it cannot vouch for.
  scene: { title: "SYNCED CHARTS", known: "HAS A TRACK RECORD", unknown: "NOT ENOUGH HISTORY" },
};

export const options = {
  heading: "A deep option chain, and option trades ranked for you.",
  lede: "See every option as prices move. Axiom ranks option trades by how much extra price they carry over the moves the market is likely to make. Traders call this the volatility premium, or VRP.",
  caption: "OPTION CHAIN · TRADES RANKED BY PREMIUM · ONE PRICE EVERYWHERE",
  clip: { label: "ILLUSTRATIVE", shape: "portrait" },
  // Strategy types, not instruments: the clip ranks kinds of trade, it does not recommend one.
  scene: {
    title: "TRADES RANKED BY PREMIUM",
    rows: [
      { trade: "Short strangle", grade: "Rich" },
      { trade: "Iron condor", grade: "Rich" },
      { trade: "Calendar spread", grade: "Fair" },
      { trade: "Covered call", grade: "Fair" },
      { trade: "Long straddle", grade: "Thin" },
    ],
    key: "Rich: options cost more than the likely move. Thin: they cost less.",
  },
};

export const strategies = {
  heading: "Test a strategy on past markets before you use it.",
  lede: "Build it on screen or in Python. The backtest counts costs and checks the result on years it never saw.",
  caption: "STRATEGY BUILDER · BACKTESTS · PYTHON LAB",
  clip: { label: "ILLUSTRATIVE", shape: "portrait" },
  scene: {
    title: "BACKTEST",
    unseen: "UNSEEN YEARS",
    note: "Built on these years, then checked on years it never saw. Falls show up too.",
    checks: ["Costs counted", "Checked on unseen years", "Same rules as live"],
  },
};

export const baskets = {
  heading: "Spread your money across more than stocks.",
  lede: "A basket holds equity, gilts, gold, cash and global assets. When the season turns, Axiom drafts the change and a hedge. A person confirms every order.",
  caption: "MULTI-ASSET BASKETS · HEDGE DRAFTS",
  before: "RISK-ON BASKET",
  after: "EARLY-WARNING BASKET",
};

export const agent = {
  heading: "Ask in plain words. It shows its sources.",
  lede: "Ask for a screen, an option trade or what changed overnight. The agent answers from the same readings the screens show, and links to each one.",
  caption: "PLAIN QUESTIONS · CITED ANSWERS",
  clip: { label: "ILLUSTRATIVE", shape: "portrait" },
  scene: {
    question: "What changed since yesterday’s close?",
    answer: [
      { text: "The season moved from risk-on to early warning.", cite: "1" },
      { text: "Fewer sectors are rising. Banks and IT are fading.", cite: "2" },
      { text: "The basket draft moves money from equity into gilts and gold.", cite: "3" },
    ],
    sources: ["SEASON READING", "SECTOR ROTATION", "BASKET DRAFT"],
    footnote: "It drafts. A person confirms every order.",
  },
};

export const brokers = {
  heading: "Offer Axiom to your clients under your own name.",
  lede: "Your SEBI-registered analysts write every basket and call your clients see.",
  action: "Talk to the desk",
  // Reserved placeholder until the real desk address exists; the launch check fails on it.
  contact: "desk@axiom.invalid",
  subject: "Axiom for brokers",
  publicLine: "Investing with a broker? Ask them for Axiom.",
  dialogLede: "For brokers licensing Axiom to their clients. Investing on your own? Ask your broker instead.",
  copy: "Copy address",
  copied: "Copied",
  copiedStatus: "Address copied",
  copyFailed: "Address selected. Copy it with your keyboard or menu.",
  mail: "Write an email",
};
