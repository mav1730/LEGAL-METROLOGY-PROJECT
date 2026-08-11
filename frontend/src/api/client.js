const BASE = "/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: {
      ...(options.body && !(options.body instanceof FormData)
        ? { "Content-Type": "application/json" }
        : {}),
      ...options.headers,
    },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok && data.ok !== true) {
    const err = new Error(data.error || `HTTP ${res.status}`);
    err.data = data;
    err.status = res.status;
    throw err;
  }
  return data;
}

export const api = {
  health: () => request("/health"),
  stats: () => request("/stats"),
  samples: () => request("/samples"),
  rules: () => request("/rules"),
  products: () => request("/products"),
  product: (id) => request(`/products/${id}`),
  scanUrl: (url, html = "") =>
    request("/scan/url", {
      method: "POST",
      body: JSON.stringify({ url, html: html || undefined }),
    }),
  scanText: (payload) =>
    request("/scan/text", { method: "POST", body: JSON.stringify(payload) }),
  scanSample: (sample_id) =>
    request("/scan/sample", {
      method: "POST",
      body: JSON.stringify({ sample_id }),
    }),
  scanImage: (file) => {
    const fd = new FormData();
    fd.append("image", file);
    return request("/scan/image", { method: "POST", body: fd });
  },
  reviewFinding: (id, action, comment = "") =>
    request(`/findings/${id}/review`, {
      method: "POST",
      body: JSON.stringify({ action, comment }),
    }),
  reviewProduct: (id, status, comment = "") =>
    request(`/products/${id}/review`, {
      method: "POST",
      body: JSON.stringify({ status, comment }),
    }),
  report: (id, format = "json") =>
    request(`/products/${id}/report`, {
      method: "POST",
      body: JSON.stringify({ format }),
    }),
};
