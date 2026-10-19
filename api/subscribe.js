// POST /api/subscribe  {email, website(honeypot)}
// Double opt-in: sends a confirmation link; the contact is only added to the
// Resend audience after the link is clicked (see /api/confirm).
const { sign, validEmail, resend } = require("./_lib");
module.exports = async (req, res) => {
  if (req.method !== "POST") return res.status(405).json({ error: "POST only" });
  const b = typeof req.body === "string" ? Object.fromEntries(new URLSearchParams(req.body)) : req.body || {};
  const wantsHtml = !(req.headers["content-type"] || "").includes("json");
  const done = (code, msg) => wantsHtml ? res.redirect(303, code === 200 ? "/newsletter/check-email/" : "/newsletter/?error=1") : res.status(code).json({ message: msg });
  if (b.website) return done(200, "ok"); // honeypot: pretend success for bots
  const email = String(b.email || "").trim().toLowerCase();
  if (!validEmail(email)) return done(400, "Please enter a valid email address.");
  const { RESEND_API_KEY, NEWSLETTER_SECRET, NEWSLETTER_FROM } = process.env;
  if (!RESEND_API_KEY || !NEWSLETTER_SECRET || !NEWSLETTER_FROM) return done(500, "Signup is not configured yet.");
  const ts = Date.now();
  const link = `https://mybrokenboat.com/api/confirm?e=${encodeURIComponent(email)}&t=${ts}&s=${sign(email, ts)}`;
  const r = await resend("/emails", {
    from: NEWSLETTER_FROM, // e.g. "My Broken Boat <newsletter@news.mybrokenboat.com>"
    to: [email],
    subject: "Confirm your My Broken Boat subscription",
    text: `Tap to confirm you want outboard tips from My Broken Boat:\n\n${link}\n\nIf you didn't sign up, ignore this email and you won't hear from us.`,
    html: `<p>Tap to confirm you want outboard tips from My Broken Boat:</p><p><a href="${link}">Confirm my subscription</a></p><p>If you didn't sign up, ignore this email and you won't hear from us.</p>`,
  });
  return r.ok ? done(200, "Check your email to confirm.") : done(502, "Couldn't send the confirmation email. Please try again later.");
};
