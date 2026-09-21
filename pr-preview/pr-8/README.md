# WOW 2026 Builder Guide

A Jekyll site (converted from an earlier static single-file page). `index.html`
is the page template; content lives in `_data/*.json` and is injected at build
time via Liquid (`{{ site.data.sessions | jsonify }}`), not hand-edited inline.
Deploys to GitHub Pages via `.github/workflows/pages.yml`; PRs get a preview
build via `.github/workflows/pr-preview.yml`.

## Running it locally

```bash
bundle install   # first time only, installs the jekyll gem (see Gemfile)
bundle exec jekyll serve
```

Then open **http://localhost:4000/builders-guide/** — note the `/builders-guide/`
path is required locally too, since `_config.yml` sets `baseurl: "/builders-guide"`
to match how GitHub Pages serves this repo (`workato-devs.github.io/builders-guide`).
Jekyll watches files and rebuilds automatically; refresh the browser after
editing (`--livereload` can be added to the serve command for auto-refresh).

`jekyll.environment` is `development` under `jekyll serve` by default, which is
what keeps the debug panel (bottom-left floating box — breakpoint readout, date
simulator, container-outline toggle) visible locally. Production builds
(`JEKYLL_ENV=production bundle exec jekyll build`, which is what the Pages
workflow runs) hide it automatically — see the `{% if jekyll.environment !=
"production" %}` guards in `index.html`.

## For whoever picks this up next

A few things worth doing before this ships:

1. **Double-check the schedule.** The session list in `_data/sessions.json`
   was assembled from a mix of a planning PDF and a manual walkthrough — it's
   had several rounds of corrections already, but re-verify every day/time/
   speaker against whatever is the current source of truth before this goes
   live. Times that read `"Starts X:XX PM"` (no end time) are intentional —
   those sessions never had a confirmed end time — but double check that's
   still accurate.
2. **Wire up the Explore section.** Every card at the bottom (Community,
   Events Calendar, Follow Us, Self Serve, Otto) currently has `"url": ""` in
   `_data/resources.json`. They need real URLs. The icon is the same
   speech-bubble glyph on every card right now — it could likely use distinct
   icons per card once real content/links are decided.
3. **Icons/design help** — loop in Ray (this project's owner) if you need
   new icon assets made for the above, or have other design questions about
   how this page was put together.

## Files

```
builders-guide/
  index.html                  the page template (styles + JS + Liquid data injection)
  _data/
    sessions.json              the Builder Sessions agenda (see below)
    resources.json              the "Explore" link-out cards
  _config.yml                  Jekyll config (title, baseurl, url)
  Gemfile                       pins the jekyll gem version
  favicon.png
  src/                         images, logos, portraits, mascot art
  breakpoints-and-grid.md      shared Wolf2 breakpoint/grid system
  .github/workflows/
    pages.yml                   builds + deploys to GitHub Pages on push
    pr-preview.yml               builds a preview for pull requests
```

## How the page is structured

- **`_data/sessions.json`** — one combined, chronological "Builder Sessions"
  agenda spanning Tuesday–Thursday. Registered main-track talks and informal
  Dev Lounge meetups (meet-the-devs chats, afterparties, community sessions)
  are interleaved in the same array and the same day-tabbed grid — there's no
  separate section for the two. Each entry has `day`/`date`/`start`/`end`
  (used for sorting and for the "Up Next" / "Happening Now" featured card),
  `timeLabel` (what's displayed — usually derived from start/end, but written
  out by hand so it can say things like `"Starts 5:00 PM"` for sessions with
  no confirmed end time), `title`, and a `speakers` array (can be empty — e.g.
  a networking session with no named host). Optional-in-spirit fields (still
  present as empty strings/arrays when unused, since this is now a fixed JSON
  shape rather than free-form JS objects): `url` (a Cvent registration link —
  empty hides the "Learn more" line), `topic` (a small `// category` eyebrow
  label, rendered in monospace above the time — pick from the existing small
  taxonomy already in use: Community, Conversation, Behind the Scenes,
  Research, Demos, Networking, Best Practices, Deep Dive — rather than
  inventing a new one-off label per session), `desc` (a short abstract).
- **`_data/resources.json`** — the "Explore" link-out cards at the bottom
  (see TODO #2 above — these need real `url`s, currently all empty).

### Speakers

Each speaker object has `name`, `role`, `company`, `photo`. `role` can be an
empty string (renders as just the company). `photo` can be an empty string —
that renders the Dewy mascot (`src/dewy-avatar-placeholder.png`) on a soft
tint circle as a stand-in avatar until a real headshot is added.

### Live/upcoming logic

The page's JS compares each session's start/end against "now" to decide
what's past, what's featured (soonest upcoming or currently live), and
whether the whole event is over. To preview this without waiting for the
real dates:
- add `?now=2026-09-23T15:00:00` to the URL, or
- use the **debug panel** (see "Running it locally" above for when it's
  visible) — it also has a "simulate date" dropdown and a container-outline
  toggle for checking the breakpoint grid.

## Adding or editing a session

Add an object to `_data/sessions.json` (or edit an existing one) with
`day`/`date`/`start`/`end`/`timeLabel`/`title`/`speakers`, plus whichever of
`url`/`topic`/`desc` apply (empty string if unused, to keep the JSON shape
consistent). Drop a headshot into `src/` and reference it as a speaker's
`photo`, or leave `photo` empty to use the Dewy placeholder avatar.

## Shared conventions

- Breakpoints/container widths follow the standard Wolf2 system — see
  [`breakpoints-and-grid.md`](breakpoints-and-grid.md).
- Brand palette is defined as CSS variables at the top of `index.html`
  (`--teal`, `--dark-blue`, `--orange`, etc.) — reuse those tokens rather
  than hardcoding new colors.
