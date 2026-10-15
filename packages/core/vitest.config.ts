import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    dir: "../..",
    include: ["packages/core/test/**/*.test.ts", "languages/*/tests/**/*.test.ts"],
    globals: false,
  },
});
