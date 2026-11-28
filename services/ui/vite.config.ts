import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// The app always calls /api on its own origin. In the image nginx forwards it to API_URL; in development
// `API_URL=http://... npm run dev` does the same.
const api = process.env.API_URL;

export default defineConfig({
  plugins: [react()],
  server: { proxy: api ? { "/api": { target: api, rewrite: (path) => path.replace(/^\/api/, "") } } : undefined },
  test: { environment: "jsdom" },
});
