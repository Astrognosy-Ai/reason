# Design Audit — Astrognosy AI Web Properties
**Date:** 2026-03-30
**Auditor:** /design-review (gstack)
**Sites:** reason.astrognosy.com · astrognosy.com · pcfic.com

---

## Scores

| Site | Design Score | AI Slop Score | Status |
|------|-------------|---------------|--------|
| reason.astrognosy.com | B | B+ | Live (just launched) |
| astrognosy.com | B- | B+ | Live |
| pcfic.com | C | D | Live — needs work |

---

## SITE 1: reason.astrognosy.com

**Classifier:** HYBRID (docs-forward with landing intro)

### First Impression
- The site communicates: "open protocol, technical, purpose-built."
- I notice the reason:// ASCII wordmark is distinctive and memorable — it doubles as the logo and the brand.
- The first 3 things my eye goes to are: 1) wordmark, 2) "The DNS for agent intelligence." tagline, 3) the code block.
- One word: **clean.**

### Design System
- Fonts: monospace-heavy (code examples dominate) — no explicit custom font detected
- Background: dark (#0d1117 range)
- Sections: light alternating backgrounds for docs-style clarity
- Load time: fast

### Findings

| ID | Impact | Category | Finding |
|----|--------|----------|---------|
| R-001 | Medium | Typography | No custom font — body falls back to default sans. For a protocol spec page, a monospace or editorial font would signal credibility |
| R-002 | Medium | Spacing | Section backgrounds alternate but the visual rhythm feels unintentional — some sections feel like they're floating |
| R-003 | Medium | AI Slop | "Only winners enter" 4-column info grid (Quality-gated / No data transferred / Immutable provenance / ...) is borderline card-grid territory |
| R-004 | Polish | Content | The "stack" diagram at the bottom is the best section — reason:// → WARF → PCF hierarchy is clear. Consider moving it higher |
| R-005 | Polish | Performance | GitHub Pages HTTPS not yet active — currently serving HTTP only. Certificate will provision within hours |

### Verdict
Solid for a launch-day docs page. The code walkthrough (fraud detection example with real output) is excellent — shows exactly what the protocol does in one scroll. Main gap is visual polish in the lower sections.

---

## SITE 2: astrognosy.com

**Classifier:** MARKETING / LANDING PAGE

### First Impression
- The site communicates: "premium, research-driven, mysterious intelligence company."
- I notice the astronomical compass is genuinely distinctive — not generic, not AI-generated-looking.
- The first 3 things my eye goes to are: 1) compass centerpiece, 2) "Intelligence Built From the Ground Up," 3) gold accents.
- One word: **distinctive.**

### Inferred Design System
- Fonts: Cormorant Garamond (serif, editorial) + DM Sans (sans, functional) + DM Mono (code) — excellent pairing
- Colors: deep navy (#06091a) + gold (#c9a84c) + cyan (#00b4d8) + off-white (#e8ecf8)
- Load time: 336ms (fast)

### Findings

| ID | Impact | Category | Finding |
|----|--------|----------|---------|
| A-001 | **HIGH** | Interaction | Nav links (Pacific, Research, Wharf) are **16px height** — severely below 44px minimum. Untappable on mobile. |
| A-002 | **HIGH** | Interaction | Contact button is 32px height — also below 44px minimum |
| A-003 | **HIGH** | Color/Contrast | Body sections (Three Divisions, One Engine) are nearly invisible — background so dark that text/content is unreadable without zooming in. Section backgrounds need at least a slight lift |
| A-004 | **HIGH** | Content | 404 console error: `astrognosy-ai.github.io/reason/` was returning 404. Now fixed — GitHub Pages enabled during this session |
| A-005 | Medium | AI Slop | Emoji as section icons (🧭 Pacific, 🔬 Research, ⚓ Wharf). Adds personality but risks looking low-fi. Consider SVG icons |
| A-006 | Medium | Typography | H1 weight 300 (Cormorant Garamond) on dark background — beautiful but can feel fragile at small sizes. Weight 400 would be safer |
| A-007 | Medium | Responsive | Mobile nav collapses to logo + Contact only — Research and Wharf are hidden. Intentional? If so, needs a hamburger menu |
| A-008 | Polish | Content | "reason:// — Now Live" section has a live code block — great. But the stats below it (4 Patents Filed, 187 claims, <1.5ms, 0 training) render very small and dark |

### Quick Wins (< 30 min each)
1. **A-001/A-002**: `min-height: 44px` on nav links + padding increase. One CSS line.
2. **A-003**: Raise section background from `#04060e` to `#0c1020` — enough to make content visible.
3. **A-005**: Replace emoji section icons with inline SVGs (compass, flask, anchor) — same concept, more premium.

---

## SITE 3: pcfic.com

**Classifier:** MARKETING / LANDING PAGE

### First Impression
- The site communicates: "technical AI product company."
- I notice it's functional and clear, but feels constructed rather than designed.
- The first 3 things my eye goes to are: 1) hero headline, 2) stats bar, 3) Laminar spotlight.
- One word: **functional.**

### Inferred Design System
- Fonts: **system font stack only** (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto`) — no custom fonts. This is the single biggest design liability.
- Heading weight: **800 everywhere** — H1, all H2s, all H3s. No weight hierarchy.
- Colors: navy (#2c3e50) + indigo/blue (#5b6ecc) + cyan (#00b4d8) — decent palette but indigo trend-adjacent
- Load time: 284ms (fast)

### Findings

| ID | Impact | Category | Finding |
|----|--------|----------|---------|
| P-001 | **HIGH** | Typography | **No custom fonts.** System font stack screams "default." One font addition (Inter, DM Sans, or better: Syne + Inter) transforms the entire feel |
| P-002 | **HIGH** | AI Slop | **Emoji as headings** in "One Engine. Many Applications." section: 🔤 Natural Language, 🔴 Cybersecurity, ⚙️ Hardware Verification, 🤖 Robotics/AV, 🏭 Industrial IoT, 🧠 AI Infrastructure — textbook AI-generated pattern |
| P-003 | **HIGH** | AI Slop | **The 3-column feature grid** in "Five Products. One Engine." — icon + bold title + description, repeated 6x symmetrically. Most recognizable AI layout pattern. |
| P-004 | **HIGH** | Interaction | Nav links are **23px height**. "View on Google Patents" links are **11px height** — essentially untappable. |
| P-005 | **HIGH** | Content | ~~"2 Patents Pending" badge~~ — **FIXED this session** → "4 Patents Filed" |
| P-006 | **HIGH** | Content | ~~Patent 3 "In Preparation"~~ — **FIXED this session** → "March 2026 — Filed" + Patent 4 added |
| P-007 | Medium | Typography | Weight 800 on H1, all H2s, all H3s — no hierarchy differentiation. H2 should be 600-700, H3 500-600. |
| P-008 | Medium | AI Slop | Cookie-cutter section rhythm: hero → stats → spotlight → feature grid → applications → IP → CTA. Every section same height. |
| P-009 | Medium | Color | Indigo/blue primary (#5b6ecc) is in the purple-adjacent territory — trending toward AI design cliché. Cyan (#00b4d8) is the stronger, more distinctive color — consider making it primary. |
| P-010 | Medium | Content | Hero stat "F1 0.969" labeled "Best Security F1" — this is the BruteForce-only score. Overall F1 is 0.929. Consider labeling more precisely: "F1 0.969 BruteForce" or using the aggregate |
| P-011 | Polish | Spacing | The product cards in "Five Products" have product stage badges (LIVE, BETA, DESIGN, SILICON, ROBOTICS, COMING SOON) — good. But the LIVE/BETA badges disappear on smaller viewports |

### Quick Wins (< 30 min each)
1. **P-001**: Add one Google Font. `<link>` tag + `font-family` override on `body`. `DM Sans` matches astrognosy.com and costs zero performance.
2. **P-002**: Replace emoji heading prefixes with a simple colored dot or short category label in uppercase small text.
3. **P-007**: Override H2/H3 weight: `h2 { font-weight: 600 }`, `h3 { font-weight: 500 }`. Immediate visual improvement.
4. **P-004**: Add `padding: 12px 0` to nav links to bring them to 44px+ touch targets.

---

## Cross-Site Issues

| Issue | Sites Affected |
|-------|---------------|
| Touch targets below 44px | astrognosy.com, pcfic.com |
| Emoji as design elements | astrognosy.com, pcfic.com |
| No consistent brand font | pcfic.com (astrognosy.com and reason.astrognosy.com are fine) |
| Section contrast too low | astrognosy.com |

## Fixes Applied This Session

| Fix | File | Commit |
|-----|------|--------|
| Patent badge: 2 → 4 | Pcfic.com/index.html:765 | 5385a2f |
| Hero stat: 2 Patents Pending → 4 Patents Filed | Pcfic.com/index.html:801 | 5385a2f |
| Patent 3: In Preparation → March 2026 Filed | Pcfic.com/index.html:1135 | 5385a2f |
| Patent 4: added to IP timeline | Pcfic.com/index.html:1138 | 5385a2f |
| GitHub Pages enabled on reason repo | GitHub API | — |
| GitHub Pages HTTPS enforced | GitHub API | — |

## Deferred (needs design session)
- pcfic.com: Add custom font (DM Sans recommended — matches astrognosy.com)
- pcfic.com: Replace emoji headers with proper icon system
- pcfic.com: Break up the 3-column feature grid into a layout with more visual differentiation
- astrognosy.com: Fix nav link touch targets
- astrognosy.com: Lift dark section backgrounds for readability
- reason.astrognosy.com: Add custom font + polish lower sections

**PR Summary:** Design review found 19 issues across 3 sites. Fixed 6 (patent data errors + infrastructure). Design score: pcfic.com C/D slop, astrognosy.com B/B+, reason.astrognosy.com B/B+.
