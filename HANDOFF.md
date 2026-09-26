# Handoff — delete this file once you're done with it

Context for whoever (or whichever agent) picks this up next, from a cloud session
that just finished the ai-dev redesign. Everything below is already merged to `main`.

## What shipped

- **`ai-dev.html`** — redesigned from the old six-week-cohort / self-paced split
  into a single $1,997 mentor-led offer (six 1:1 sessions with a senior engineer,
  human-reviewed feedback, certification + Claude certification pathway, job leads
  with no guarantee). CTA is "Book a short call" throughout. **Live on Kajabi.**
  FAQ was rebuilt around real objections pulled from the "Top 10%: Agentic
  Engineering Interest List" Typeform (form id `EDuBEz4U`), generalized into
  categories (trust in AI output, "meat proxy" anxiety, no repeatable system,
  team misalignment on what "good" looks like) rather than quoted verbatim —
  the user was explicit that quoting respondents' actual words would be a
  privacy problem.

- **`agentic-engineering-101.html`** — new page, built but **not yet pushed to
  Kajabi**. One Saturday (Dec 12, 2026), $495, no-call direct signup, positioned
  as "learn to actually use the AI coding tools you already have," gated against
  people wanting to build a "software factory" or become a "meat proxy."

## Open items, in priority order

1. **`agentic-engineering-101.html` has no real payment link.** CTA buttons
   currently point at the Typeform interest-list form (`EDuBEz4U`), which only
   collects name/email — it does not take payment. The user wants "sign up and
   pay, no call" for this $495 product. Need a real Stripe checkout link (same
   pattern as `buy.stripe.com/dRm14o0hu5nJ6oGf11djO0J` used on `agent-weekend.html`),
   then swap it into every CTA on the page (there are several: hero, buy section,
   final CTA).

2. **`agentic-engineering-101.html` isn't live on Kajabi yet.** To push it:
   create the page in the Kajabi editor first, grab its theme ID from the
   `/admin/themes/<theme_id>/settings/edit` URL, add it to the `PAGES` dict in
   `kajabi.py`, then use the `kajabi-push` skill (or `python3 kajabi.py push
   agentic-engineering-101 agentic-engineering-101.html` directly). Auth lives
   in `.kajabi/env` (gitignored) — token expires in ~1 day, refresh from
   devtools on any `app.kajabi.com` request if you get a 401.

3. **Rotate the Kajabi session credential.** The bearer token / CSRF token /
   cookies currently in `.kajabi/env` were pasted into a chat transcript
   earlier in this project's history. They still work as of this handoff, but
   they've been visible outside the browser session they came from — worth
   logging out/in on Kajabi to invalidate them once nothing depends on the old
   session anymore.

## Ad creative — ready for Paper

Five ad concepts were finalized for the $1,997 mentor-led program only (a
"save your software" / codebase-rescue ad angle was floated but the user said
"we're not set up for that right now" — don't build that offer or its ads
unless asked). Style reference: Cause of a Kind's Meta ads (black background,
white text, blunt problem → concrete quantified fix, no stock photography).
All five share the same payoff line so the ad always states plainly what's
taught (RAG + agents, mentor, 6 sessions, $1,997) — the user was explicit that
a clever hook with a vague payoff pulls in the wrong buyers.

1. **Language angle** — "No one cares what language you know anymore.
   Developers who are getting hired know 2 skills: RAG and agents. We teach
   both, with a mentor, in 6 sessions. $1,997."
2. **Meat-proxy angle** — "Using Claude isn't the same as knowing how to build
   a RAG pipeline or a production agent. We teach both, with a mentor, in 6
   sessions. $1,997." (Post hook: "You've been copy-pasting between five
   Claude tabs for a year. That doesn't make you the AI person on your team.
   It makes you a very fast intern.")
3. **Trust-in-output angle** — "We teach the two things companies are
   actually hiring for: production RAG pipelines and AI agents. With a
   mentor, in 6 sessions, $1,997." (Post hook: "You review every line the
   model writes because you don't trust it. That's not a skill issue. It's a
   systems issue.")
4. **Category-claim angle** — "AI engineer is the new full-stack engineer.
   The developers getting hired know 2 things: RAG and agents. We teach
   both, with a mentor, in 6 sessions. $1,997."
5. **Straightforward angle** — "Companies are hiring for production RAG
   pipelines and AI agents right now. We teach both, with a mentor, in 6
   sessions. $1,997." (Post hook: "Companies are hiring for RAG and agent
   skills right now. Almost no developers actually have them.")

**Next step:** the user wants to build the actual ad card images using Paper
(paper.design)'s MCP server. That server only runs via `stdio` through Paper
Desktop running locally — it can't be reached from a cloud session, which is
why this got punted to a local session in the first place. From a local
session: open Paper Desktop, connect it to Claude per
https://paper.design/docs/mcp, and hand it these five concepts as prompts for
the frames (black background, white text, small wordmark corner — see the
Cause of a Kind screenshot the user shared for the exact visual target).
