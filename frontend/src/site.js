/** Flask origin. The Vite dev server proxies /api only, so DemoMart stays on port 5000. */
export function backendOrigin() {
  if (import.meta.env.DEV) return "http://127.0.0.1:5000";
  if (typeof window === "undefined") return "http://127.0.0.1:5000";
  return window.location.origin;
}
