---
name: kajabi-push
description: Edit a Kajabi landing page's HTML and push it live. Use when the user asks to change, update, remove, or add anything on a Kajabi page (for-teams, etc.) or says "push to kajabi".
---

# Kajabi page update

Pages are plain HTML files in the repo root, one per page, mirrored to the
Custom Code block of a Kajabi landing page by `kajabi.py`. Page names and
IDs live in the `PAGES` dict in `kajabi.py`.

## Steps

1. Pull first so you edit the live version, not a stale copy:
   `python3 kajabi.py pull <page> <page>.html`
2. Edit `<page>.html` with sed/Edit. Delete whole blocks by their
   `<!-- ─── NAME ─── -->` comment markers. Leave orphaned CSS alone unless asked.
3. Push: `python3 kajabi.py push <page> <page>.html`
4. Commit the HTML file.

## Adding a page

Open it in the Kajabi editor and copy the IDs from the URL
`/admin/themes/<theme_id>/settings/edit?file_id=<file_id>` into `PAGES`.

## Auth failures

401 means the token in `.kajabi/env` expired (about one day). Ask the user
for a fresh `authorization`, `x-csrf-token`, and `cookie` header from any
app.kajabi.com request in devtools, and update the three vars in that file.
Never commit `.kajabi/env`.
