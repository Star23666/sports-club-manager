// ── Admin Dashboard Runtime Config ───────────────────
// Edit these values to match your deployment.
const ConstSitting = {
    base_url: "/admin/api",
    app_title: "Club Admin",             // Browser tab title
};
// Client frontend URL for embedded find-account / reset-password pages.
window.__FIND_URL__ = window.__FIND_URL__ || "http://localhost:8080";