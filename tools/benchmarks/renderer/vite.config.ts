import { createReadStream } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { defineConfig } from "vite";

const wasmDir = join(dirname(createRequire(import.meta.url).resolve("scichart/package.json")), "_wasm");

export default defineConfig({
  server: { port: 5199, strictPort: true },
  plugins: [
    {
      name: "scichart-wasm",
      configureServer(server) {
        server.middlewares.use("/scichart-wasm", (req, res) => {
          const file = (req.url ?? "").replace(/^\//, "").split("?")[0]!;
          if (!/^[\w.-]+\.wasm$/.test(file)) {
            res.statusCode = 404;
            res.end();
            return;
          }
          res.setHeader("Content-Type", "application/wasm");
          createReadStream(join(wasmDir, file))
            .on("error", () => {
              res.statusCode = 404;
              res.end();
            })
            .pipe(res);
        });
      },
    },
  ],
});
