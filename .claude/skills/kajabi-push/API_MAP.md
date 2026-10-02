# Kajabi API map

Explored 2026-10-02 against site `2148415899` (brian-jenney.mykajabi.com, served
as parsity.io). "Verified" means called for real; "observed" means seen in the admin
HTML or JS but not called. Landing-page writes were verified on 2026-10-02 against a
throwaway clone, then used on the live page. All other writes are untested.

## Which API for what

| Job | Use | Auth lifetime |
|---|---|---|
| Edit a page's HTML (Custom Code block) | Internal: `/admin/themes/{id}/settings` | Browser session, ~1 day |
| Rename a page, set its URL slug, publish or unpublish, SEO fields | Internal form: `/admin/landing_pages/{id}` | Browser session |
| Duplicate or import a page | Internal: `/clone`, `/import` | Browser session |
| Contacts, tags, offer grants, notes, form submits, webhooks, purchase actions | Official API `api.kajabi.com/v1` | OAuth client credentials, refreshable |
| Read offers, products, courses, orders, transactions | Official API (GET only) | Same |
| Email broadcasts and sequences, offer or product editing | No API of either kind found. Official Kajabi MCP is the next thing to try | n/a |

## 1. Official public API (verified from the OpenAPI spec)

- Base `https://api.kajabi.com/v1`, spec at `https://developers.kajabi.com/openapi.yaml` (OAS 3.1.1, 60 paths), docs index `https://developers.kajabi.com/llms.txt`.
- Auth: `POST /v1/oauth/token` with `client_id`, `client_secret`, `grant_type=client_credentials`. Returns an access token and a refresh token. Create the key in Admin > Settings > Security > User API Keys. This is the fix for the daily cookie expiry, for the resources it covers.
- Plan: the help center says the API is included on Pro and sold as a $25/month add-on otherwise. This account shows a Growth plan. Unconfirmed: the help article itself 404ed, so ask support@kajabi.com.
- Rate limits are not documented. Pagination is `page[number]`/`page[size]`; filters are `filter[attr_eq|cont|gt|...]`.

| Resource | Methods |
|---|---|
| `/contacts`, `/contacts/{id}` | GET, POST, PATCH, DELETE |
| `/contacts/{id}/relationships/tags` | GET, POST, PATCH, DELETE |
| `/contacts/{id}/relationships/offers`, `/customers/{id}/relationships/offers` | GET, POST, PATCH, DELETE (grant or revoke) |
| `/contact_notes` | GET, POST, PATCH, DELETE |
| `/hooks` | GET, POST, DELETE (no update). Events: purchase, payment_succeeded, order_created, form_submission, tag_added, tag_removed |
| `/forms/{id}/submit` | POST |
| `/purchases/{id}/deactivate`, `/reactivate`, `/cancel_subscription` | POST |
| `/landing_pages`, `/website_pages` | GET only: title, url, publish_at, timestamps. No HTML, no settings |
| `/offers`, `/products`, `/courses`, `/forms`, `/form_submissions`, `/contact_tags`, `/custom_fields`, `/customers`, `/orders`, `/order_items`, `/transactions`, `/kajabi_payments_payouts`, `/blog_posts`, `/podcasts`, `/sites`, `/me` | GET only |

No endpoints exist for themes, page content, email, or site settings.

## 2. Internal admin endpoints (session auth: authorization, x-csrf-token, cookie)

Same headers `kajabi.py` already sends. Undocumented, so they can change without notice.

### Page code and theme
- Verified: `GET /admin/themes/{theme_id}/settings` returns JSON (`theme`, `file`, `files`, `user`, `linkPaths`). `linkPaths.editAdminLandingPageUrl` gives the landing page ID for a theme, which is how to map theme to page.
- Verified: `PUT` on the same path writes a page's code (this is what `kajabi.py push` does).
- Observed in the editor JS, untested: `/admin/themes/:id/settings/edit/add_section`, `.../sections/:sectionId`, `.../sections/:sectionId/add_block`, `.../blocks/:blockId`, `.../global/:settingId`.
- Observed: `POST /admin/themes/{id}/snapshots` with `theme_upload_storage_key` (theme file upload).

### Landing page settings (Rails forms, form-encoded)
All of these take `Content-Type: application/x-www-form-urlencoded` plus the usual
`x-csrf-token` and cookie headers (the form `authenticity_token` is not needed). A
success is a 302; read the `Location` header rather than following it.

- Verified: `GET /admin/landing_pages/{landing_page_id}/edit` is HTML and shows the current values.
- Verified: `POST /admin/landing_pages/{id}` with `_method=patch` updates only the fields you send. Slug-only (`landing_page[path]=...`) left title, SEO and publish state untouched, and the new slug served publicly at once. The old slug returns 404, with no redirect. Other fields: `landing_page[title]`, `[page_title]`, `[page_description]`, `[page_image]`, `[hide_from_search_engines]`.
- Verified: `landing_page[publishing_option]` takes `published` or `draft`. `draft` made the public URL 404.
- Verified: `POST /admin/landing_pages/{id}/clone` returns 302 to `/admin/theme_pending/{new_theme_id}`. The new page is published at once, titled "<old title> 1" with slug "<old slug>-1". Find the new landing page ID by diffing the page list before and after.
- Verified: `POST /admin/landing_pages/{id}` with `_method=delete` removes a page (302 to the page list).
- Observed, untested: `POST /admin/sites/{site_id}/landing_pages/import` with `theme[original_zip]`; `GET /admin/landing_pages/{id}/stats` (HTML).

### Site and media (JSON, verified GET)
- `/admin/sites/{site_id}`: site settings object (title, support email, home_landing_page_id, SEO defaults, and more).
- `/admin/sites/{site_id}/forms`, `/products`, `/assessments`: `[{id, text}]` picker lists.
- `/admin/sites/{site_id}/recent_images`, `/videos`: media library items (JSON:API shape).
- `/api/admin/sites/{site_id}/kj_embed/widget_types`: embed widget catalog.
- `/admin/sites/{site_id}/offers` and `/landing_pages` return `[]` as JSON; they appear to need query parameters. The HTML versions hold the real lists (24 landing pages).

### HTML-only sections (406 for JSON, scrapable)
affiliates, analytics, automation_rules, blog_posts, communities, contacts (500 for JSON), coupons, courses, email_campaigns, events, invoices, navbars, newsletters, payments, pipelines, podcasts, products, reports, settings, universal_inbox, website_designs, website_pages. The sidebar of `/admin/sites/{site_id}/dashboard` is the full route list. Anything that only exists here means scraping HTML and posting forms.

## IDs

| Thing | ID |
|---|---|
| Site | 2148415899 |
| agentic-engineering-101 | theme 2167731896, landing page 2152304400 |

## Current state (as of 2026-10-02)

The workshop page is live at `https://www.parsity.io/agentic-engineering-101`. The slug was fixed today; the earlier slug `ai-for-web-developers-ai-dev-slug-1` now returns 404. Still left over from the clone: the Kajabi title is "AI for Web Developers (ai-dev slug) 1" and the SEO page title is "AI for Web Developers". Both are one PATCH away.

## Suggested next steps

1. Fix the title and SEO page title with the landing-page PATCH.
2. Confirm API access with Kajabi support. If it is available, move contact, tag and webhook work to the official API.
3. Test the official Kajabi MCP for page, offer and email drafting, which neither API covers.
4. Add `kajabi.py pages` (list pages with id, slug, status) and `kajabi.py meta` (slug, title, publish) on top of the endpoints above, so the verified requests are not rewritten each time.
