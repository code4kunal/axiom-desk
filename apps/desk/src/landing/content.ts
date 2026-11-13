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
  { id: "footer", label: "Footer" },
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
  privacy: "Privacy",
  terms: "Terms",
};

export const notFound = {
  title: "Page not found",
  caption: "STATUS 404 · NO PAGE AT THIS ADDRESS",
  heading: "No reading at this address.",
  body: "The page you asked for is not on the instrument. The address may have changed, or it never existed.",
  home: "Go to the start",
  hint: "Or pick a section from the index above.",
};

const pending = { stamp: "PENDING", notice: "Text pending legal review.", back: "Back to the start" };

export const privacy = {
  ...pending,
  title: "Privacy notice",
  caption: "PRIVACY NOTICE · DRAFT",
  body: [
    "This page will carry Axiom's privacy notice once counsel has reviewed it. Until then nothing here is a statement of practice.",
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
