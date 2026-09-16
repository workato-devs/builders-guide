# WOW 2026 Builder Guide

`wow-2026.html` is a single self-contained page (inline `<style>` + `<script>`,
no build step). Open it directly in a browser or serve the folder statically —
all assets are relative paths into `src/`.

## For whoever picks this up next

A few things worth doing before this ships:

1. **Double-check the schedule.** The session list in `SESSIONS` (see below)
   was assembled from a mix of a planning PDF and a manual walkthrough — it's
   had several rounds of corrections already, but re-verify every day/time/
   speaker against whatever is the current source of truth before this goes
   live. Times that read `'Starts X:XX PM'` (no end time) are intentional —
   those sessions never had a confirmed end time — but double check that's
   still accurate.
2. **Wire up the Explore section.** Every card at the bottom (Community,
   Events Calendar, Follow Us, Self Serve, Otto) currently links to `#` — see
   the `RESOURCES` array and `renderExplore()` near the bottom of the file.
   They need real URLs. The icon is the same speech-bubble glyph on every
   card right now (`CHAT_ICON_SVG`) — it could likely use distinct icons per
   card once real content/links are decided.
3. **Icons/design help** — loop in Ray (this project's owner) if you need
   new icon assets made for the above, or have other design questions about
   how this page was put together.

## Files

```
wow-2026/
  wow-2026.html               the page
  src/                         images, logos, portraits, mascot art
  breakpoints-and-grid.md      shared Wolf2 breakpoint/grid system (copied in
                                 so this folder is self-contained if zipped)
  sessions.txt                 raw paste of the Dev Lounge planning sheet — reference
                                 only, not read by the page
  WOW Builder Lounge Content
    Ideas - Available Time
    Slots.pdf                  the planning doc sessions.txt was pasted from —
                                 source of truth if the schedule is questioned
```

## How the page is structured

Everything below the hero is rendered from two plain JS arrays near the
bottom of the file — edit the data, not the HTML, to change content:

- **`SESSIONS`** — one combined, chronological "Builder Sessions" agenda
  spanning Tuesday–Thursday. Registered main-track talks (Cvent-linked) and
  informal Dev Lounge meetups (meet-the-devs chats, afterparties, community
  sessions) are interleaved in the same array and the same day-tabbed grid —
  there's no separate section for the two. Each entry has `day`/`date`/
  `start`/`end` (used for sorting and for the "Up Next" / "Happening Now"
  featured card), `timeLabel` (what's displayed — usually derived from
  start/end, but written out by hand so it can say things like `'Starts 5:00
  PM'` for sessions with no confirmed end time), `title`, and a `speakers`
  array (can be empty — e.g. a networking session with no named host).
  Optional fields: `url` (a Cvent registration link — omit it for sessions
  with no link, which hides the "Learn more" line), `topic` (a small
  `// category` eyebrow label, rendered in monospace above the time — pick
  from the existing small taxonomy already in use: Community, Conversation,
  Behind the Scenes, Research, Demos, Networking, Best Practices, Deep Dive
  — rather than inventing a new one-off label per session), `desc` (a short
  abstract).
- **`RESOURCES`** — the "Explore" link-out cards at the bottom (see TODO #2
  above — these need real `href`s, currently all `#`).

### Speakers

Each speaker is either:
- `{ name, role, company, photo }` — headshot from `src/`, or
- `{ name, role, company }` (no `photo`) — renders the Dewy mascot
  (`src/dewy-avatar-placeholder.png`) on a soft tint circle as a stand-in
  avatar until a real headshot is added. `role` is optional; a speaker with
  no role just shows their company.

### Live/upcoming logic

`renderAgenda()` compares each session's start/end against "now" to decide
what's past, what's featured (soonest upcoming or currently live), and
whether the whole event is over. To preview this without waiting for the
real dates:
- add `?now=2026-09-23T15:00:00` to the URL, or
- use the **debug panel** (bottom-left floating box) — it also has a
  "simulate date" dropdown and a container-outline toggle for checking the
  breakpoint grid. It's dev-only; strip the `.debug-panel` div and its script
  hookup (`setupDebugPanel()`) before a final public launch if it shouldn't
  ship.

## Adding or editing a session

Add a new object to `SESSIONS` (or edit an existing one) with `day`/`date`/
`start`/`end`/`timeLabel`/`title`/`speakers`, plus whichever optional fields
apply (`url`, `topic`, `desc`). Drop a headshot into `src/` and reference it
as `photo`, or omit `photo` to use the Dewy placeholder avatar.

## Shared conventions

- Breakpoints/container widths follow the standard Wolf2 system — see
  [`breakpoints-and-grid.md`](breakpoints-and-grid.md).
- Brand palette is defined as CSS variables at the top of `wow-2026.html`
  (`--teal`, `--dark-blue`, `--orange`, etc.) — reuse those tokens rather
  than hardcoding new colors.

