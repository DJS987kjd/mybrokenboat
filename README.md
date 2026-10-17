# My Broken Boat

My Broken Boat ([mybrokenboat.com](https://mybrokenboat.com)) is a static outboard motor troubleshooting site. Each page covers one common symptom in plain English: a short answer, likely causes, safe owner checks, parts and tools, when to call a marine mechanic, and the sources those checks come from.

The articles live in `library/*.md`. `build.py` reads that library and writes a dependency-free static site into `site/` (HTML, CSS, `sitemap.xml`, `robots.txt`, and `llms.txt`). The published pages have no analytics, ads, affiliate links, or third-party scripts.

## Build

Rebuild `site/` from the library:

```bash
python build.py
```

The script removes the existing `site/` directory and writes it again. It uses only the Python standard library.

## Validate

Check the generated pages:

```bash
python validate.py
```

Validation confirms that every page's JSON-LD parses, internal links and sitemap URLs resolve to files, titles and descriptions are unique, and each page includes the mechanic disclaimer, a canonical URL, and an Open Graph title. The command exits with status 0 when those checks pass.

## Deploy

The site deploys on Vercel as prebuilt static files. `vercel.json` sets `outputDirectory` to `site`, with no framework and no build step, so Vercel serves the committed `site/` directory as-is. Run the build and validate commands above, then commit the regenerated `site/` output, before deploying.

## Still to wire up

- Contact form: the contact page has a disabled form in `<section id="contact-form">`. It is not connected to any service. Edit the contact block in `build.py`, then rebuild.
- Newsletter: home and about include a placeholder `<section id="newsletter">`. Edit the `NEWS` string in `build.py`, then rebuild.
- Disclaimer text comes from `library/DISCLAIMER-draft.md` and still needs a review before it is treated as final.
- Symptom groups, question headings, and related links are set in the `Q` table in `build.py`.
