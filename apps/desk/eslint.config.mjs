import next from "eslint-config-next";

const config = [
  { ignores: [".next/**", "next-env.d.ts", "playwright-report/**", "test-results/**"] },
  ...next,
];

export default config;
