// GET /api/confirm?e=&t=&s=  -> adds the confirmed contact to the Resend audience.
const crypto = require("crypto");
const { sign, validEmail, resend } = require("./_lib");
const WEEK = 7 * 24 * 3600 * 1000;
module.exports = async (req, res) => {
  const q = req.query || {};
  const e = String(q.e || ""), t = String(q.t || ""), s = String(q.s || "");
  const ts = Number(t), good = sign(e, ts);
  const sigOk = s.length === good.length && crypto.timingSafeEqual(Buffer.from(s), Buffer.from(good));
  if (!validEmail(e) || !sigOk || !(Date.now() - ts < WEEK)) return res.redirect(303, "/newsletter/?error=link");
  const r = await resend(`/audiences/${process.env.RESEND_AUDIENCE_ID}/contacts`, { email: e, unsubscribed: false });
  // 409/422 "already exists" is fine: treat as confirmed.
  return res.redirect(303, r.ok || r.status === 409 || r.status === 422 ? "/newsletter/confirmed/" : "/newsletter/?error=1");
};
