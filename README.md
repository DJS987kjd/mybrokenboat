# My Broken Boat: static site (Outboard Help)

Build: `python3 build.py` (no dependencies; reads library/*.md, rebuilds site/ from scratch)
Validate: `python3 validate.py` (JSON-LD parses, internal links and sitemap resolve, unique titles/descriptions, disclaimer/canonical/OG on every page)
Output: `site/` is a plain static folder; Cloudflare Pages build command can be empty, output dir `site`.

LIVE on mybrokenboat.com (Cloudflare). No analytics, no affiliate links, no third-party scripts yet.

## Placeholders to wire up (David to choose)
- Contact form: `site/contact/` → `<section id="contact-form">` (marked PLACEHOLDER; inputs are disabled).
  Free options: a Cloudflare Pages Function (`functions/contact.js`) that emails or stores to KV/D1; Formspree free tier (~50 submissions/mo); a plain `mailto:` link to a free inbox.
- Newsletter: `<section id="newsletter">` on home and about.
  Free options: Buttondown free tier (up to 100 subscribers), MailerLite free tier (up to ~1,000 subscribers), Kit (ConvertKit) free tier.
- Edit the placeholder copy in `build.py` (`NEWS` and the contact page block), then rebuild.

## Before deploying
- Disclaimer text comes from library/DISCLAIMER-draft.md and still needs David's sign-off (consider a lawyer review).
- Library content hasn't had a human technical review yet.
- Question H1s, symptom groups and related links are set in the `Q` table in build.py.
- Optional: add an og:image (none yet), favicon, and a contact email address.

## Newsletter (Resend, double opt-in)
- `api/subscribe.js` (POST) emails a signed confirmation link. `api/confirm.js` adds the contact to the Resend audience only after the link is clicked.
- Vercel env vars: `RESEND_API_KEY` (secret), `RESEND_AUDIENCE_ID`, `NEWSLETTER_SECRET` (random 32+ chars), `NEWSLETTER_FROM` (e.g. `My Broken Boat <newsletter@news.mybrokenboat.com>`, on a Resend-verified domain).
- Pages: /newsletter/, /newsletter/check-email/, /newsletter/confirmed/. Drafts are in `newsletter/`.
