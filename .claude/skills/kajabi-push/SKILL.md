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

Open it in the Kajabi editor and copy the theme ID from the URL
`/admin/themes/<theme_id>/settings/edit` into `PAGES`.

## Auth failures

`kajabi.py` exits with "Kajabi session expired" on a 401/403. The session
is Kajabi's own browser login and lasts about a day; there is no API key
for this endpoint, so a fresh login is unavoidable. Make it one paste:

1. Ask the user to open the Kajabi admin, devtools -> Network, pick any
   request to app.kajabi.com of type **Fetch/XHR** (opening a theme editor
   page produces one), right-click -> Copy -> Copy as cURL, and paste it.
2. Save the pasted text to the scratchpad and run
   `python3 kajabi.py creds <file>`. It pulls out the authorization,
   x-csrf-token, and cookie values and rewrites `.kajabi/env`.
3. If it prints "still missing", the paste was a page navigation
   (Document type, e.g. the `/auth/auth0/callback` redirect), which carries
   no authorization or x-csrf-token header. Ask for a Fetch/XHR one.

Never print, echo, or commit the pasted values; `.kajabi/env` is
gitignored. Remind the user the pasted session now sits in chat history
and is worth logging out of when done.
