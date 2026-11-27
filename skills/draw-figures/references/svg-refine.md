> **Use when** a figure fails the swap test (looks generic), when it is unclear whether a claim needs
> geometry or stays text (S9), or for a data-ink taste question (S8). Never needed to draw a figure the
> first time, and not the repair read: the findings of `figures.py check` go to `svg-repair.md`.
>
> **In this file:** S8 data-ink taste · S9 what stays text around the figures, and the test that tells it
> from a figure · S10 anti-generic audit and draw-step economy. `grep -n '^##' references/svg-refine.md`
> prints every heading with its line.
>
> **Siblings:** `svg-figures.md` (S0–S3) · `svg-color.md` (S6) · `svg-geometry.md` (S4) ·
> `svg-shapes.md` (catalog + S5) · `svg-repair.md` (S7 + PATTERN → FIX).

# Concept-illustration taste & anti-generic audit

> **Valence tokens.** Figures below that carry a pass/fail reading use `--ok-*` and `--error-*`
> (pale zone / hairline line / readable ink). They are in the tokens (`assets/tokens.css`), mixed
> from the base colours as `svg-color.md` S6 · "Derive shades, don't pick them" describes. A figure
> defines none of them: `figures.py place` writes the token block into the file, and a page defines
> the same names.

Cross-references: `S0`–`S3` are in `references/svg-figures.md` (core), `S4` in
`references/svg-geometry.md`, `S6` in `references/svg-color.md`, `S7` and the PATTERN→FIX catalog
in `references/svg-repair.md`; the shape catalog and the S5 primitives (Gap, Semantic arrowheads,
ring / sparkline / slopegraph / grouped-bar / texture) are in `references/svg-shapes.md`.

---

## S8 · Data-ink taste that transfers (Tufte / perceptual)

These are encoding and restraint rules, not new shapes. They raise the data-ink ratio and perceptual honesty, and catch slop the banned-hue/font lists can't enumerate. Geometry math lives in S4; the check's findings and their fixes in S7; the caption-is-the-claim rule in S2. This is the taste layer for the look at each figure's preview (`SKILL.md`, "Draw what is marked", step 6). It does **not** re-derive the sparkline recipe: that is `Inline sparkline (semantic)` in `svg-shapes.md`, so borrow it for the marks themselves.

### 1. Refine by subtraction, not addition

The default polish instinct is to *add* — a border to "contain" things, a legend to "explain" them, a gridline to "anchor" them. Resist it. Run one pass over every **non-data** element and ask: **"if I delete this, does the drawing lose information?"** Delete if the answer is no.

- **Always removable:** gridlines, separate legends (direct-label instead), decorative borders/frames, drop shadows, background fills behind marks, redundant axis ticks.
- **Maybe:** axis lines (a faint baseline often suffices), container rectangles around free-floating labels.
- **Never:** the data marks themselves, and the one annotation that states the finding (§4).

When the instinct is to ADD a shape, **STOP** and instead make the elements already on the canvas more cohesive — align them to a shared axis, tighten spacing, unify a stroke weight (see S4 grid discipline). A new box is rarely the fix.

**Default to free-floating text and lines; draw a box only around a genuine component** (a real container, a node that owns sub-parts, a shape whose outline carries meaning). Target: **under ~30% of the text in the figure sits inside a box.** A figure of uniform rounded rectangles is the tell that this pass was skipped.

Carry the literal question into the look at each preview as a subtractive clause: *"For each non-data mark: delete-test it. When I want to add, make existing marks cohesive instead."*

### 2. Perceptual encoding hierarchy (Cleveland–McGill)

When a value must be *read* off the figure, the visual channel you pick determines how accurately a human decodes it. Ordered most-accurate to least:

> **position > length > angle > area > color**

The actionable consequence for concept-viz: **bars (position/length) > pie (angle) > bubble (area)** for the same comparison. Prefer a bar or a dot-on-a-shared-baseline over a pie or a cloud of circles whenever the reader is meant to compare magnitudes. Reserve area and color for *secondary* or categorical encodings, never the primary quantitative read.

**If size must carry a value, scale by AREA, not radius.** The eye reads a disk's area; setting `r ∝ value` makes a 4× value look ~16× bigger — a silent lie. Use `r ∝ √value`:

```js
// area-proportional bubble: area ∝ value  ⇒  r = Rmax * sqrt(v / vMax)
const R_MAX = 28;                              // px radius of the largest bubble
const bubbleR = (v, vMax) => R_MAX * Math.sqrt(v / vMax);
// 25 vs 100 → r = 14 vs 28 (2× radius, 4× area) — honest
```

```xml
<svg xmlns="http://www.w3.org/2000/svg" id="fig-1" viewBox="0 0 220 100" role="img"
     aria-label="Team B handled 100 cases, 4× Team A's 25; bubble areas are proportional, not radii.">
  <!-- cx/cy derived from a top-left box per S4; areas (not radii) encode the count.
       The value label must clear the LARGEST bubble's bottom edge — derive it, don't eyeball:
       baseline y = cy + R_MAX + gap = 40 + 28 + 20 = 88, and the viewBox height (100) contains it.
       (A hard-coded y=72 in an 80-tall box overlaps the r=28 circle, whose bottom is at 68.) -->
  <circle cx="34"  cy="40" r="14" style="fill:var(--muted)"/><text x="34"  y="88" font-size="12"
    text-anchor="middle" style="fill:var(--muted);font-family:var(--font-mono)">25</text>
  <circle cx="150" cy="40" r="28" style="fill:var(--info)"/><text x="150" y="88" font-size="12"
    text-anchor="middle" style="fill:var(--muted);font-family:var(--font-mono)">100</text>
</svg>
```

### 3. Gray-first, smallest-effective-difference

Default **every** mark to a neutral gray. Add hue only to the mark whose color *carries meaning*, and then use the **smallest difference that still separates** — dark-gray vs mid-gray beats red vs blue when the contrast is merely "these are two series." Loud, saturated, full-spectrum palettes are the unmistakable AI-slop tell.

- **De-emphasize secondary data by ghosting with opacity, never by introducing a new hue.** Past/baseline/context marks drop to `opacity="0.35"`; the load-bearing mark stays at full strength in the one accent.
- **One calm emphasis hue over neutrals** — `var(--info)` for non-semantic emphasis (S6 accent rule) — plus the semantic pair (`var(--ok)` = pass, `var(--error)` = fail). Never violet/fuchsia/indigo in any slot.
- **Verify the figure still reads in grayscale.** If two marks become indistinguishable when you imagine the color removed, the difference was doing the encoding — add a second non-color channel (dash, label, or a hatch fill per the Texture primitive) rather than a louder hue. (8% of men are red-green colorblind; grayscale is the cheap proxy test.)

```xml
<svg xmlns="http://www.w3.org/2000/svg" id="fig-2" viewBox="0 0 260 70" role="img"
     aria-label="This release's latency holds flat where last release spiked; the prior run is ghosted for context.">
  <!-- context series: ghosted gray, no new hue -->
  <polyline points="6,52 50,20 94,40 138,18 182,44 226,30 254,46" fill="none"
            style="stroke:var(--muted)" stroke-width="1.5" opacity="0.35"/>
  <!-- load-bearing series: the one emphasis hue, full strength -->
  <polyline points="6,40 50,42 94,39 138,41 182,40 226,42 254,40" fill="none"
            style="stroke:var(--info)" stroke-width="2"/>
</svg>
```

### 4. Annotate the insight (direct-label, don't legend)

A figure carries **one claim** (need three claims → three figures — see S2). Mark the single load-bearing element *on the visual* with a short arrow or label so the eye lands on it without hunting:

- **Cap callouts at 1–3.** More than three and none of them is "the" point.
- **Prefer direct labeling over a separate legend.** A legend forces a saccade-and-match round trip; a label sitting on the mark is read in place. Drop the legend (it's removable per §1) and write the word next to the thing.
- The caption/`aria-label` states the **finding** ("Coverage rose 60→95% after the fix"), not the variables ("coverage over time") — this is the S2 headline-is-the-argument rule, doubled into the accessible name.

Reuse the Semantic-arrowheads vocabulary (`svg-shapes.md` S5) for the pointer (note `refX`/`orient`, and `markerUnits="userSpaceOnUse"` so the head doesn't shrink on a thin stroke — PATTERN→FIX rows 2 and 4):

```xml
<svg xmlns="http://www.w3.org/2000/svg" id="fig-3" viewBox="0 0 300 96" role="img"
     aria-label="Coverage jumped to 95% at the fix; the final point is the one that matters.">
  <defs>
    <marker id="fig-3-pt" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7"
            markerUnits="userSpaceOnUse" orient="auto"><path d="M0 0L10 5L0 10z" style="fill:var(--muted)"/></marker>
  </defs>
  <polyline points="12,78 70,70 128,66 186,40 244,16" fill="none" style="stroke:var(--info)" stroke-width="2"/>
  <circle cx="244" cy="16" r="3.5" style="fill:var(--ok)"/>
  <!-- single direct annotation, not a legend -->
  <line x1="208" y1="14" x2="234" y2="16" style="stroke:var(--muted)" stroke-width="1" marker-end="url(#fig-3-pt)"/>
  <text x="206" y="12" text-anchor="end" font-size="12"
        style="fill:var(--ok-ink);font-family:var(--font-mono)">95% after fix</text>
</svg>
```

### 5. Concept-viz anti-pattern table (renderer-agnostic)

Each row transfers to hand-authored SVG regardless of renderer. Two rows are **honesty** rules, not taste — breaking them misrepresents the data.

| Anti-pattern | Why it fails | One-line fix |
|---|---|---|
| Gauge / speedometer (a lone scalar, no comparison) | Burns a half-circle of ink on one number; angle is a weak channel (§2) | Big number + a sparkline + a comparison value |
| Gradient fill on a mark | Implies a value ramp that isn't in the data; pure decoration | Solid semantic fill |
| 3D bars / pie, drop shadows | Perspective distorts the length/area being compared | Flat 2D |
| Rainbow ramp for ordinal data | Hue isn't ordered — readers can't rank the colors **(HONESTY)** | Gray + single accent, or a sequential single-hue ramp |
| Decorative border / frame | Adds ink, zero information (§1) | Remove it |
| Marker on every data point | Dots become noise; the eye can't find the signal | Mark only min / max / endpoint (see `Inline sparkline (semantic)` in `svg-shapes.md`) |
| Rotated (45°/vertical) axis labels | Forces a head-tilt; truncates unpredictably | Flip the chart so labels are horizontal, or abbreviate |
| Truncated / non-zero baseline | Exaggerates differences by cropping the axis **(HONESTY)** | Start the value axis at zero, or disclose the break explicitly |

The gauge row targets the **dashboard speedometer** — one naked number on a dial. It is *not* the part-of-whole ring/arc gauge in `references/svg-shapes.md`: that one encodes a genuine proportion ("3 of 8") in **arc length**, not angle, and earns its place. Ring = a proportion read off length; speedometer = a scalar on an angle — keep the first, drop the second.

These extend the hard bans for figures (no gradient; no violet, fuchsia or indigo; fonts only through `var(--font-body)` and `var(--font-mono)`) from a banned-list into a failure *catalog*: when a figure feels off, match it against a row and apply the fix. The two HONESTY rows are non-negotiable — a truncated baseline or a rainbow-ordinal ramp ships a figure that argues something the numbers don't support.

---

## S9 · What stays text around the figures

A text is mostly *not* figures. The figures are islands; the connective tissue is the text itself: its sentences, lists and tables. The text carries every fact whose meaning is **not spatial**, and that frees the figures to carry the facts that are.

### Decide text vs. a drawn figure with the education test

Run the S2 isomorphism/education test *before* you write a `Figure:` mark: mentally delete all the geometry and keep only the words. If you lost nothing, the geometry was decoration, and the text is the **correct** answer, not a consolation prize. Counts, pass/fail statuses, term definitions, a flat list of categories, "N of M done": none of these has a shape. Give them as a sentence, a list or a table in the text and move on. Reserve a drawn figure for relationships that *are* the picture: a before→after flow, a coverage arc, a convergence, a hatched "not-yet-run" zone. Five honest numbers in a table beat a five-slice donut every time.

What stays text picks one claim and asserts it in its own words (headline-is-the-argument): write `0 failures · type-check clean`, not `failure count`. The reader should learn the takeaway from the words and confirm it in the numeral.

The two tests that make this call claim by claim are in `SKILL.md`, "Which claims get a figure"; S1 in `svg-figures.md` has the long form.

---

## S10 · Anti-generic philosophy & draw-step economy

The bans for figures (no gradient; no violet, fuchsia or indigo in any slot; fonts only through `var(--font-body)` and `var(--font-mono)`) kill the *loudest* tells, not the quiet ones: the looks an LLM drifts into because they feel tasteful. This section names those looks for self-audit, gives a diff test for "would I draw this for any brief?", makes every decorative device earn its place, and caps deliberation on the draw step. It governs *judgment* around the figure file; the geometry lives in S4, semantic colour in S6, verification in S7.

### The looks a figure drifts into

A figure reads the tokens, so it cannot pick a ground, a typeface or a hue of its own: the loud tells are closed off. What is left is layout and shape, and three defaults that feel tasteful and say nothing:

- **Everything centred.** Every label `text-anchor="middle"`, every block on the middle axis. Centring is a default, not a decision. Left-align, or go asymmetric, unless the symmetry encodes something (a genuine before/after mirror does: see the S0 divider).
- **One `rx` on every rect.** The same radius on every card, pill and frame flattens the hierarchy. Vary it or drop it: sharp corners for a fixed frame, soft for a state pill, and let the difference *mean* something.
- **A row of equal boxes joined by arrows,** whatever the claim. When the boxes could be swapped without changing the picture, the shape is carrying nothing (S3: pick the shape from the claim).

**Audit the cluster, not one ingredient.** Each of these is fine alone; the figure reads generic when they arrive together and the structure does no work. Break one: the fastest break is to give the second register a **working semantic job** (S6): if green = pass and red = fail already, let `var(--info)` carry a third real state instead of garnishing.

### Generate-default-then-diff genericness test

Originality is checkable, not a vibe. Operationalize the swap test as a diff against your own autopilot:

1. **Mentally re-run a *similar* brief**: "the default figure I'd draw for any pass/fail check."
2. **Diff this illustration against that default.** Any part that matches the autopilot — the centered layout, the blanket radius, the lone accent arrow, the boxes-and-arrows reflex — is a candidate for revision.
3. **Revise the matching part and state what changed and why**, in one line, tied to *this* content. If you cannot name a content-driven reason, the change was decoration; revert it.

A worked diff (state it this tersely):

```text
default  → two centered cards, identical 8px radius, one accent arrow between them
this one → left card sharp-framed (the fixed contract), right card soft (the variable input);
           arrow is the failing→passing transition, so it's the ONE semantic-colored element.
why      → radius now encodes fixed-vs-variable; color is reserved for the verdict, not chrome.
```

This is the swap test, "would I draw this for any brief?", given a procedure and an output (the stated diff), so it can't be skipped with a nod.

### Structure-is-information rule

Every structural or decorative device — numbered markers, eyebrow labels, section dividers, chips, semantic fills, varied radius — is allowed **only if it encodes something true about the content**:

- **Number a list only if it is genuinely an ordered sequence.** Steps that must happen in order earn `1·2·3`; a set of peers gets bullets. Numbering peers lies about precedence.
- **A divider is allowed only if it separates two real registers** (before/after, fixed/variable). A divider that just "breaks up the figure" is chartjunk: delete it (S8's subtraction pass).
- **A chip's color is a claim.** Green chip = the thing actually passed. If it doesn't carry a state, it's a sticker.
- **A second accent must do a second job.** One calm accent over neutrals is the rule; a second hue is permitted only when it carries a distinct semantic register, never for variety.

This is the planning-side twin of S2's isomorphism test ("delete all text — does structure still convey the idea?") and S6's "color is never decorative." If a device survives those gates it stays; otherwise it goes. The test: *remove the device — does the reader lose information?* No → it was decoration.

### Anti-rumination directive for the draw step

Once the brief (S2), shape (S3), and coordinate frame (S4) are fixed, the actual *drawing* deserves almost no deliberation. Cap it:

- **Commit to one concrete layout on first impulse.** Do not debate orientation or alternatives.
- **Do not compute coordinates in prose loops** ("700 is too wide, tighten to 680, hmm 664…"). You already have the geometry-constants header from S4 — derive from it and emit.
- **Do not narrate process** ("now I'll finalize the arrowheads…"). Emit the elements directly. Planning tokens spent here are output tokens lost.

**IMPORTANT divergence from an auto-layout tool's "never re-check coordinates."** That rule is correct *only because such a tool auto-layouts*: a solver guarantees the geometry. We hand-author, so we **keep the check and the look at the preview** (S7; `SKILL.md`, "Draw what is marked", steps 5 and 6): draw decisively, then verify once. The economy is at the *authoring* step (don't ruminate while placing shapes), not at the *verification* step (always look at the result). Decisive draw + bounded verify, never timid draw + no verify.
