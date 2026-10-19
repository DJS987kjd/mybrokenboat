// Shared helpers for newsletter functions. No dependencies (Node 18+ fetch/crypto).
const crypto = require("crypto");
const SECRET = () => process.env.NEWSLETTER_SECRET || "";
const sign = (email, ts) => crypto.createHmac("sha256", SECRET()).update(`${email}|${ts}`).digest("hex");
const validEmail = (e) => typeof e === "string" && e.length <= 254 && /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(e);
async function resend(path, body) {
  const r = await fetch(`https://api.resend.com${path}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${process.env.RESEND_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return { ok: r.ok, status: r.status, data: await r.json().catch(() => ({})) };
}
module.exports = { sign, validEmail, resend };
