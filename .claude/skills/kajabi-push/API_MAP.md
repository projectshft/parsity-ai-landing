# Kajabi API map

Explored 2026-10-02 against site `2148415899` (brian-jenney.mykajabi.com, served
as parsity.io). Only GET requests were made. "Verified" means a real 200 response;
"observed" means seen in the admin HTML or JS but not called. Every write below is
untested.

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
- Verified: `GET /admin/landing_pages/{landing_page_id}/edit` is HTML and shows the current values.
- Observed: `POST /admin/landing_pages/{id}` with `_method=patch` and any of `landing_page[title]`, `[path]` (URL slug), `[page_title]`, `[page_description]`, `[page_image]`, `[publishing_option]` (current value is `published`), `[hide_from_search_engines]`.
- Observed: `POST /admin/landing_pages/{id}/clone` (link uses `data-method="post"`). This is how to create a new page.
- Observed: `POST /admin/sites/{site_id}/landing_pages/import` with `theme[original_zip]`.
- Observed: `GET /admin/landing_pages/{id}/stats` (HTML).
- Likely works with the `x-csrf-token` header instead of a form `authenticity_token`, since the theme PUT does. Untested.

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

## Current state worth fixing (as of 2026-10-02)

The workshop page is published at `https://www.parsity.io/ai-for-web-developers-ai-dev-slug-1` with the new copy. Its Kajabi title is still "AI for Web Developers (ai-dev slug) 1" and its SEO page title is "AI for Web Developers". `/agentic-engineering-101` returns 404. The landing-page PATCH above would fix all three. Not done: it writes to a live page.

## Suggested next steps

1. Fix the slug, title and SEO fields via the landing-page PATCH, after testing it on a throwaway clone.
2. Confirm API access with Kajabi support. If it is available, move contact, tag and webhook work to the official API.
3. Test the official Kajabi MCP for page, offer and email drafting, which neither API covers.
4. Add `kajabi.py pages` (list pages with id, slug, status) and `kajabi.py meta` (slug, title, publish) on top of the endpoints above.
