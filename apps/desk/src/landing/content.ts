// Every string the landing shell can show lives here, so the copy test sees all of it.

export const sections = [
  { id: "season", label: "Season" },
  { id: "problem", label: "Problem" },
  { id: "charts", label: "Charts" },
  { id: "options", label: "Options" },
  { id: "hedge", label: "Hedge" },
  { id: "agent", label: "Agent" },
  { id: "evidence", label: "Evidence" },
  { id: "brokers", label: "Brokers" },
] as const;

export const shell = {
  skip: "Skip to content",
  navLabel: "Sections",
  indexTrigger: "Index",
  disclaimer: "Research tool. Not investment advice. No performance is promised.",
  footerIndexLabel: "Section index",
  footerCaption: "AXIOM · EN-IN · ILLUSTRATIVE FIGURES ONLY",
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
const subline = "A research instrument for Indian investors. It drafts; a human confirms every order.";
const hedgeCard = "HEDGE DRAFT · INDEX PROTECTION · ILLUSTRATIVE · a human confirms every order";

export const meta = {
  title: "Axiom",
  description: subline,
  ogTitle: "Axiom",
  ogDescription: statement,
};

export const hero = {
  statement,
  subline,
  primary: "See how it reads a market",
  brokers: "For brokers",
  // Stacked plates 0 / 40 / 70 / 100; the last plate's caption is the hedge card.
  plates: [
    { caption: "REGIME EXPANSION · CONF 0.74 · N 212 · ILLUSTRATIVE", state: "EXPANSION", tone: "monsoon" },
    { caption: "EARLY DETERIORATION · CONF 0.68 · N 212 · ILLUSTRATIVE", state: "EARLY DETERIORATION", tone: "geru" },
    { caption: "EQUITY 61 → 42 · GILTS 18 → 29 · GOLD 9 → 17 · ILLUSTRATIVE" },
  ],
  hedgeCard,
  // The regime reading in the ring's hole: 0 at dock 0, 1 from dock 40 on. Covered by the rail's ILLUSTRATIVE.
  hole: [
    { word: "Expansion", conf: "CONF 0.74 · N 212", tone: "monsoon" },
    { word: "Early deterioration", conf: "CONF 0.68 · N 212", tone: "geru" },
  ],
  // Basket legend under the ring; numbers cut from before to after at dock 70.
  legend: {
    labels: ["Equity", "Gilts", "Gold", "Cash", "Intl"],
    before: ["61", "18", "9", "7", "5"],
    after: ["42", "29", "17", "7", "5"],
    note: "ILLUSTRATIVE",
  },
};

export const problem = {
  heading: "Equity-only tools go quiet when the season turns.",
  lede: "By the time they flag the turn, prices have already fallen.",
};

export const charts = {
  heading: "Every pattern on the chart tells you how often it has worked before, or says it can’t tell yet.",
  caption: "BASE RATE · SAMPLE SIZE · UP TO 8 SYNCED CHARTS",
  clip: { label: "CLIP PLACEHOLDER", shape: "landscape" },
};

export const options = {
  heading: "Every options price comes from one consistent model, so the numbers agree everywhere.",
  caption: "ONE ARBITRAGE-FREE SURFACE · SSVI",
  clip: { label: "CLIP PLACEHOLDER", shape: "portrait" },
};

export const hedge = {
  heading: "When regime confidence shifts, Axiom drafts the hedge.",
  lede: "It never places an order; a human confirms each one.",
  card: hedgeCard,
  // The same example figures as the evidence specimen: one number everywhere.
  grid: [
    { label: "TRIGGER", value: "EARLY DETERIORATION" },
    { label: "BASE RATE", value: "0.58" },
    { label: "N", value: "212" },
    { label: "OOS", value: "0.54" },
    { label: "GRADE", value: "CNF" },
  ],
};

export const agent = {
  heading: "Ask what changed since yesterday’s close.",
  lede: "The agent answers with citations to the same numbers the screens show.",
  caption: "CITATIONS · SAME NUMBERS AS THE SCREENS",
  clip: { label: "CLIP PLACEHOLDER", shape: "portrait" },
};

export const evidence = {
  heading: "Every claim shows its base rate, sample size and out-of-sample result.",
  lede: "When it can’t show all three, it says so: insufficient evidence.",
  specimen: "BASE RATE 0.58 · N 212 · OOS 0.54 · AS OF 2026-11-13 · ILLUSTRATIVE",
  grades: [
    { stamp: "CNF", meaning: "out-of-sample confirmed" },
    { stamp: "RAC", meaning: "in-sample only" },
    { stamp: "WL", meaning: "insufficient evidence" },
  ],
};

export const brokers = {
  heading: "White-label Axiom for your clients.",
  lede: "Your SEBI-registered analysts author every basket and call.",
  action: "Talk to the desk",
  // Reserved placeholder until the real desk address exists; the launch check fails on it.
  contact: "desk@axiom.invalid",
  subject: "Axiom for brokers",
  publicLine: "Investing with a broker? Ask them for Axiom.",
  dialogLede: "Write to the desk at this address.",
  copy: "Copy address",
  copied: "Copied",
  copiedStatus: "Address copied",
  copyFailed: "Select and copy",
  mail: "Write an email",
};
