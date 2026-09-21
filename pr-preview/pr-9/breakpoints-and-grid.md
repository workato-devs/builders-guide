# Breakpoints & Grid System

Source of truth: values audited off the real production workato.com site (via breakpoint-visualizer.html), not invented. Every page listed below implements the same 4-tier snapping system so header, sub-nav, and content container can never drift out of alignment with each other.

## The tiers

- Desktop: viewport 1440px and up, container max-width 1438px
- Responsive: viewport 1150-1439px, container max-width 1140px
- Compact: viewport 960-1149px, container max-width 946px
- Tablet/Mobile: viewport under 960px, container is fluid (100%, full width with padding)

Container side padding is 24px at every tier - that part stays constant, it's only the max-width that snaps.

Note the container never actually reaches full viewport width until under 960px. Above that it always snaps to one of three fixed widths (1438, 1140, or 946), matching how the real site behaves - it jumps between fixed widths rather than scaling fluidly.

## Implementation pattern

The whole system is one CSS custom property, --max-w, redefined inside @media blocks targeting :root. Every element that needs to align to the grid (page container, header, sub-nav) just reads var(--max-w) - nothing else needs to change per breakpoint.

Root declaration:
--max-w: 1438px (this is the desktop default)

Media query overrides, placed right after :root closes:
- @media (max-width: 1439px) sets --max-w to 1140px (Responsive tier)
- @media (max-width: 1149px) sets --max-w to 946px (Compact tier)
- @media (max-width: 959px) sets --max-w to 100% (Tablet/Mobile, fluid)

Then every layout element reads the same variable:
.container gets max-width: var(--max-w), margin: 0 auto, padding: 0 24px
.wk-header-inner gets the same max-width/margin/padding, plus its own layout properties
.dev-subnav nav gets the same max-width/margin/padding, plus its own layout properties

Why this fixed the original bug: before this, the header (.wk-header-inner) was hardcoded to 1280px with 28px padding, while .container used a separate --max-w variable set to 1200px with 32px padding, and the wireframe had a third width (960px) for its own content. Header, sub-nav, and content edges didn't line up, and it varied page to page. Routing every one of them through the same var(--max-w) makes that structurally impossible now - change the value once and everything that reads it moves together.

## Where it lives today

Each file currently defines its own copy of the :root/@media block described above. It is not yet extracted into a shared stylesheet the way colors are - see Known gaps below.

Files that have the system:
- community.html
- developers.html
- developers-3b.html
- developers-v4.html
- workato-salesforce-community.html
- community-lp-wireframe.html
- wow-2026/wow-2026.html (container follows the system; a nested `.layout` max-width of 1040px keeps the single-column agenda + resources sidebar legible instead of stretching to the full 1438px container)

Files that don't:
- otto-teaser.html - standalone microsite, uses its own fixed .wrap at max-width 1080px. Not part of the shared ecosystem chrome (no wk-header or dev-subnav), so it was intentionally left out.

## Adding this to a new page

1. Add the --max-w: 1438px declaration to the page's :root block.
2. Add the three @media overrides immediately after :root closes.
3. Point .container (and .wk-header-inner / .dev-subnav nav if the page has them) at max-width: var(--max-w) and padding: 0 24px instead of any hardcoded width or padding.

## Known gaps

- Not shared across files yet. Colors were extracted to shared/wolf2-colors.css so a brand color change is a one-line edit. The breakpoint system hasn't had the same treatment yet - updating a tier value today still means editing the @media block in each of the 6 files listed above. A shared/wolf2-grid.css file would close this gap the same way.
- otto-teaser.html intentionally uses its own fixed 1080px width and isn't part of this system.
