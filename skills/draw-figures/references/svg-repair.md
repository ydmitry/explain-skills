> **Use when** `figures.py check TEXT` prints a `PROBLEM`, `WARN` or `NOTE` line for a figure, a figure fails
> its look in `figures.py preview TEXT`, or the check prints `measured=no` and the measured checklist must
> run by hand. Not a routine-authoring read: the rules each fix points at live in `svg-geometry.md` (S4) and
> `svg-color.md` (S6).
>
> **In this file:** the PATTERN → FIX catalog (match the finding, apply the fix) · the findings read from
> the source, type → fix · S7: Gate 1 what the check reads from each file's source · Gate 1.5 what the check
> measures in a headless browser, tier by tier, and delegated authoring (you run the check again) · Gate 2
> the bounded look at the previews · the ship-blocker gate · the two-tier ship rubric · authoring-build
> discipline · the structured failure object.
>
> **Siblings:** `svg-figures.md` (S0–S3) · `svg-color.md` (S6) · `svg-geometry.md` (S4) ·
> `svg-shapes.md` (catalog + S5) · `svg-refine.md` (S8–S10: taste, when a figure passes the check but
> looks generic).

# Figure repair: the PATTERN → FIX catalog and the render → look → fix loop (S7)

**Read on repair, not routine authoring.** Open this file after a finding of `figures.py check`: the
PATTERN→FIX catalog and the table of findings read from the source match your bug to a known-good fix.
On an explicit genericness concern, open `references/svg-refine.md` (the anti-generic audit). Routine
authoring (brief, shape, geometry, colour) is fully covered by `references/svg-figures.md`,
`references/svg-color.md`, `references/svg-geometry.md` and `references/svg-shapes.md`; you do NOT need
this file to draw a figure the first time.

---

## PATTERN → FIX gotcha catalog

Pattern-match your own bug against the known-good fix. The content is SVG-specific. **Rows that merely
restate an S4/S6 rule are compressed to severity · symptom · grep · pointer**; the **three
marker-mechanics rows** (2, 3, 4) that have no home elsewhere keep their full Incorrect/Correct diff.

**Compressed rows (the rule lives in S4/S6 — this is the pattern-match handle):**

- **1 · HIGH — `viewBox` aspect ≠ drawn extent** (whole figure stretches/squashes). grep: `viewBox="0 0 ([\d.]+) ([\d.]+)"`, then confirm W:H matches your max x:y. Fix: S4 §2 — type the `viewBox` only after the bands are summed.
- **5 · HIGH — `<text>` overflows the viewBox** (SVG text does NOT wrap). grep: a `<text>` `x + len·fontSize·0.5` exceeding viewBox width. Fix: S4 §4 — size the box from char count, or pre-split into `<tspan>` lines.
- **6 · HIGH — fill not matching the semantic legend** (color lies about meaning). grep: a `class="pass"`/`pass` node whose `fill` is not the `--ok` token. Fix: S6 — one valence→token rule drives legend and shape alike.
- **7 · MED — inverted y-sign** (chart upside down; SVG y grows DOWNWARD). grep: a bar/point `y` that increases as the encoded value increases. Fix: S4 §2 — `y = H − barHeight`, invert the output range.
- **8 · HIGH — missing `role`/`aria-label`** (invisible to assistive tech). grep: `<svg` without a following `role="img"` / `aria-label="…"`. Fix: S6 — role + a finding-stating label, never "a diagram".
- **9 · HIGH — edge drawn target→source** (arrowhead on the wrong end; renders fine, argues backwards). grep: for each `marker-end` line, read the claim aloud and confirm `(x2,y2)` is the TARGET's port. Fix: S4 §9 — `x1,y1`=FROM, `x2,y2`=TO, head on `marker-end`.
- **12 · LOW — arrowhead buried in the target's border stroke.** grep: `marker-end` lines whose `x2`/`y2` exactly equals a rect edge coordinate. Fix: S4 §9 — land 2–4px short so the tip kisses the border.
- **13 · HIGH — loop-back edge routed THROUGH the row it returns across** (slices nodes/edges; head hidden under a box). grep: `marker-end` `<path>`s with diagonal segments whose bbox spans multiple node rects. Fix: S4 §9 — elbow through the reserved corridor, its own label (check: `edge-through-node` + `arrowhead-hidden`).
- **14 · MED — "before/baseline" painted in the error red** (asserts a failure the brief never claimed). grep: `--error` on elements whose nearby label says before/baseline/old. Fix: S6 valence table — baseline/before = `var(--muted)`; red stays reserved for actual failure.

**Full-diff rows — marker/text mechanics with no S4/S6 home:**

**2 · HIGH — `<marker>` missing `refX`/`orient` (head detaches from the line / never rotates).**
```xml
<!-- Incorrect -->
<marker id="fig-1-arr" markerWidth="7" markerHeight="7"><path d="M0 0L10 5L0 10z"/></marker>
<!-- Correct: anchor the tip at refX, rotate to follow the path -->
<marker id="fig-1-arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7"
        orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" style="fill:var(--ok)"/></marker>
```
grep: `<marker` lines lacking `refX=` or `orient=`.

**3 · MED — `marker-mid` on a `<line>` (mid markers never appear).**
```xml
<!-- Incorrect: <line> has only start/end, no mid vertices -->
<line x1="20" y1="40" x2="200" y2="40" marker-mid="url(#fig-1-dot)"/>
<!-- Correct: marker-mid fires on interior <path> vertices -->
<path d="M20 40 L110 40 L200 40" fill="none" style="stroke:var(--info)" marker-mid="url(#fig-1-dot)"/>
```
grep: `<line[^>]*marker-mid`.

**4 · MED — `markerUnits="strokeWidth"` shrinks heads on thin lines (arrowhead vanishes on a 1px stroke).**
```xml
<!-- Incorrect: head scales with a 1px stroke → ~1px head -->
<marker id="fig-1-arr" markerUnits="strokeWidth" markerWidth="7" markerHeight="7">…</marker>
<!-- Correct: fixed pixel head regardless of stroke -->
<marker id="fig-1-arr" markerUnits="userSpaceOnUse" markerWidth="7" markerHeight="7">…</marker>
```
grep: `markerUnits="strokeWidth"`.

**10 · MED — `<tspan>` without its own `x` (line 2 indents to the end of line 1).**
```xml
<!-- Incorrect -->
<text x="84" y="52" text-anchor="middle">Frontmatter<tspan dy="16">passes the bar</tspan></text>
```
grep: `<tspan` carrying `dy=` but no `x=`. Fix: repeat `x` on every continuation line (S4 §8).

**11 · MED — `dominant-baseline` vertical centering (shifts per renderer and in print).**
```xml
<!-- Incorrect -->
<text x="84" y="56" dominant-baseline="central">queued</text>
```
grep: `dominant-baseline=` / `alignment-baseline=` — should not appear at all. Fix: `y` at the box
centerline + `dy=".35em"` (S4 §8).

---

## Findings read from the source: type → fix

`python3 ${CLAUDE_SKILL_DIR}/scripts/figures.py check TEXT` prints one line per finding:
`PROBLEM fig-N: <type> <detail>`, `WARN fig-N: <type> <detail>` or `NOTE fig-N: <type> <detail>`, then
`measured=yes` or `measured=no`, `warnings=N`, and last `problems=N`. A PROBLEM blocks, a WARN is fixed or
its reason is given, a NOTE is advice. The findings below are read from each file's source on every run,
with or without playwright, and each one is a PROBLEM. The measured findings and their thresholds are in
Gate 1.5 below; the catalog above matches them to a fix.

| Type | Fix |
|---|---|
| `not-drawn` | A mark has no file: draw `fig-N.svg` for it from the skeleton in `svg-figures.md` (S0). |
| `extra-file` | A `fig-N.svg` has no mark: remove the file or restore the mark. |
| `mark-not-alone` | Give the `Figure:` line a paragraph of its own, with an empty line above and below it. |
| `mark-too-short` | Write the claim into the mark as one sentence of four words or more, never the medium ("Figure: coverage chart"). |
| `not-xml` | Write `&amp;` for `&` and `&lt;` for `<` in a label, close every tag, and keep two hyphens in a row out of a comment (write a token's name there without its `--`). |
| `no-xmlns` | Add `xmlns="http://www.w3.org/2000/svg"` to the root `<svg>`. |
| `no-viewbox` | Give the root a `viewBox` of four numbers, `0 0 W H`. |
| `too-wide` | Draw in a `viewBox` 720 wide or less: resize, re-band or split the figure. |
| `wide-for-phone` (WARN) | Draw the figure 400 units wide or less, with its bands stacked. In a text that is not read on a phone the warning stays: say so in your report. |
| `typed-size` | Remove `width` and `height` from the root: only `figures.py place` writes them, from the `viewBox`. |
| `a11y-missing` | Add `role="img"` and an `aria-label` holding the mark's sentence to the root. |
| `label-differs` | Copy the mark's sentence into the `aria-label`, or change the mark in the text and then the brief and the label. |
| `id-differs` | Set the root's `id` to `fig-N`, the number of its mark. |
| `unscoped-id` | Start the id with `fig-N-`, and change every `url(#…)` and `href="#…"` that points at it. |
| `duplicate-id` | Give each of the two its own name that starts with `fig-N-`, and point each reference at the one it means. |
| `unresolved-ref` | Point the `url(#id)` or `href="#id"` at an id the file defines, or define that id in the file's `<defs>`. |
| `unscoped-style` | Start the selector with `#fig-N` (`#fig-2 .card { ... }`). |
| `at-rule` | Remove the `@media`, `@import` or other at-rule: the tokens already follow a light and a dark screen, and `place` writes their block. |
| `raw-color` | Read a token of `svg-color.md` (S6) instead: `var(--ok)`, `var(--text)`, a token `color-mix()`. |
| `typed-font` | Use `var(--font-body)` or `var(--font-mono)`; a `<text>` with no class is set in `var(--font-body)` already. |
| `banned-element` | Remove the `<script>`, `<foreignObject>`, gradient, animation element or `<image>`, and draw the meaning with plain shapes that read tokens. |
| `external-ref` | Remove the link to the other file or web address: a figure is one file. |
| `nan-coord` | Recompute the coordinate from its named constants (S4). |
| `negative-size` | Draw from the top-left corner with a positive width, height or radius (S4). |
| `text-too-small` | Raise the font size to 12 units or more (S4 §4). |
| `brief-missing` | Run `figures.py brief TEXT`, then fill each block (S2). |
| `brief-block-missing` | Add a `## fig-N` block for the mark, with `claim:`, `shape:`, `data:` and `constraints:` (S2). |
| `brief-claim-differs` | Copy the mark's sentence into `claim:`; to change the claim, change the mark in the text first. |
| `brief-incomplete` | Fill `shape:` with a name from the S3 table, and `data:` with every label, value and unit the figure shows (S2). |
| `new-words`, `new-numbers` | Use the text's own word or number. One taken from a source the text points at goes on the brief's `data:` line, with its place in parentheses (S2). If the figure truly needs a word neither has, add it to the text. |
| `value-not-drawn` | Draw the value. If it will not fit, the layout is wrong (resize, re-band, split the figure); never drop it from `data:` (S2). |

---

## S7 · Opportunistic render → look → fix loop (gates + ship rubric)

A bespoke SVG can be perfectly legal XML and still be unreadable: shapes assembled from separately-typed coordinates leave gaps, clip the viewBox, or point an arrowhead the wrong way — and **the model that wrote it cannot see any of that from the source**. Run two named gates in order, cheapest first:

- **Gate 1 — "parses / legal":** deterministic, no render, false-positive-free. Catches reference and coordinate bugs that vision is slow and unreliable at. `figures.py check TEXT` reads it from each file's source, and it always runs.
- **Gate 2 — "renders readable":** the expensive look, reserved for taste. `figures.py preview TEXT` writes a picture of each figure; read them against a closed defect table, fix, re-run the check, preview again. Bounded to <=2 rounds.

This extends steps 5 and 6 of `SKILL.md`, "Draw what is marked", into a structured loop. Coordinate-discipline and primitive recipes live in S4–S5 (Gap + arrowheads) and `references/svg-shapes.md`; this section is the verification half.

### Gate 1 — Deterministic geometry/a11y preflight (no render)

Lint only what is **knowable from the source** so the check is false-positive-free, then spend the vision round on aesthetics alone. `figures.py check TEXT` reads this tier from each file's source on every run, with or without playwright; its findings and their fixes are in the table "Findings read from the source" above. The items below that it does not report stay a checklist you run by hand, and so do the measured ones when the check prints `measured=no`.

- [ ] Every coordinate sits inside the declared `viewBox` (nothing clipped) — account for `stroke-width`/`marker` overhang at edges.
- [ ] Every `url(#id)` (marker, clip, pattern) resolves to an id actually defined in `<defs>`.
- [ ] All ids are unique across the **whole document**: figures shown inline in one page share it, so duplicate ids across figures silently collide and later refs resolve to the FIRST def. Prefix per figure (`fig-1-`, `fig-2-`).
- [ ] Root `<svg>` has `role="img"` and an `aria-label` that states the **finding**, not the medium: the mark's sentence, word for word.
- [ ] No `NaN`, no negative coordinates, no zero/negative `width`/`height`.
- [ ] No two semantic `<rect>`s overlap (legend swatches, before/after panels).
- [ ] Every `<text>` estimated bbox (S4 width estimate) sits >=2px inside the viewBox.
- [ ] Every `<text>` bbox clears every other `<text>` and every meaning-carrying line by >=4px; near an edge, switch to right/left `text-anchor` or shorten the label; never route a data line through its own label.
- [ ] `viewBox` aspect ratio matches the drawn extent (see PATTERN->FIX row 1).
- [ ] Every arrowed edge, read aloud as "FROM → TO", matches the drawing: `x2,y2` (the `marker-end`
      end) is the named TARGET's port, landing 2–4px short of its border (S4 §9; rows 9 and 12).
- [ ] Every figure with arrowed edges carries the S4 §9 edge-manifest comment
      (`<!-- edges: FROM.port → TO.port | … -->`) with mechanically resolvable names (node `id` /
      `data-name` / exact label text), and each drawn edge diffs clean against it —
      reversed/mis-routed arrows render fine and pass every geometric check; only this diff
      catches them. The measured check (Gate 1.5) automates the diff when playwright is installed.
- [ ] Every `<tspan>` after the first sets its own `x`; no `dominant-baseline`/`alignment-baseline`
      anywhere — vertical centering is `y` at the centerline + `dy=".35em"` (S4 §8; rows 10 and 11).
- [ ] No theme-dependent raw hex in any fill/stroke — every color is a `var(--…)` token, a token
      `color-mix()`, or a `<defs><style>` class built from them (S6). Grep: `fill="#`, `stroke="#`,
      `fill:#`, `stroke:#`.
- [ ] Minimum type size, computed at source (S4 §4): `font-size × (rendered width / viewBox width)
      ≥ 9.5px`. A page shows a figure down to four fifths of its size, so that is ≥ 12 user units.
- [ ] **Data-line tick.** Every item on the brief's `data:` line (S2) points at a drawn element. An
      unticked item is a ship-blocker, not a simplification — never deleted to fit.
- [ ] **Caption audit.** Every visual device the mark's sentence (the caption and the aria-label)
      names — *the shaded band*, *the hatched stages*, *the boundary*, *the cycle* — has a drawn
      referent you can point at. A caption noun with no element behind it is a figure contradicting
      its own description.
- [ ] No container slack: every card/panel edge sits ≤ 2×PAD beyond its farthest child (S4 §2),
      and sibling node boxes keep ≥ 24u gutters — no two node borders touch (S4 §9).
- [ ] Every loop-back/return edge has `marker-end`, its own label, and an elbow route through a
      corridor — it crosses no node interior and no other edge (S4 §9).

**Rule of thumb:** every id you write carries the figure's prefix, `fig-N-`. Grep the finished files for `id="` and confirm no bare, repeatable name (`arrow`, `clip`, `hatch`) appears in any of them.

### Gate 1.5 — Measured geometry lint (`figures.py check`, with playwright)

The checklist above estimates; this gate **measures**. When the `playwright` package can be imported,
`figures.py check TEXT` loads each figure file in a headless browser, computes true rendered boxes
(glyph metrics, letter-spacing and font-weight included), then reports, in viewBox user units:

| Tier | Check | Threshold |
|---|---|---|
| **PROBLEM** | `outside-viewbox` — rendered box escapes the `<svg>` box (⇒ clipped) | > 1.5 u |
| **PROBLEM** | `text-collision` with negative gap — glyph boxes intersect | sep < 0 |
| **PROBLEM** | `text-too-small` — *rendered* px at four fifths of the drawn size, the smallest a page shows | < 9.5 px (under 12 units) |
| **PROBLEM** | `manifest-edge-mismatch` — an `<!-- edges: -->` entry with no drawn `marker-end` edge landing on its declared TO port from its declared FROM side: a reversed, mis-routed, or missing arrow. The only deterministic catch for the class that renders fine and passes every geometric check | end ≤ 9 u of TO side, start ≤ 20 u of FROM side |
| **PROBLEM** | `manifest-entry-unparsable` — an entry off the exact `NAME.port → NAME.port` grammar silently disables the mismatch check for that edge | — |
| **PROBLEM** | `edge-through-node` — an arrowed edge transits the interior of an opaque labeled node box that is not a 2–4px landing: the loop-back that "slices through" (S4 §9) | run > 14 u through (> 18 u when it stops inside) |
| **WARN** | `text-collision` near-touch (cross-parent) | 0 ≤ sep < 3 u |
| **WARN** | `split-label` — a colliding pair that is really ONE logical label split across same-parent siblings (stacked lines at normal leading, or value+unit on one baseline): merge into tspans (S4 §8). Reclassed out of the PROBLEM tier — em-boxes of stacked 12px lines measure gap < 0 while the ink never touches | stacked: sep > −4 u; inline: sep ≥ 0 |
| **WARN** | `arrowhead-hidden` — a `marker-end` endpoint inside an opaque shape painted after the edge: the decoration-under-nodes z-order (S4 §6) makes the head invisible | ≥ 1 u inside |
| **WARN** | `node-gap` — two manifest-resolved node boxes touch or sit < 6 u apart: ports degenerate, no routing corridor (S4 §9 "nodes never touch"; the gutter to draw is 24 u) | gap < 6 u |
| **WARN** | `zone-invisible` — a wide zone/band rect whose composited fill differs from its backdrop by < 8 RGB per channel with no visible stroke (bands: even with one): the claim-carrying zone doesn't exist in the pixels (S6 "attenuate once") | Δ < 8 |
| **WARN** | `edge-not-in-manifest` — a drawn arrowed edge matching no manifest entry (invented edge); report names it by nearest labels ("gamma → beta"). Legend/key swatches (a `g.legend` group, or short labeled swatch lines) are excluded — a key entry is not topology | — |
| **WARN** | `manifest-missing` — figure has arrowed edges but no S4 §9 manifest; `manifest-name-unresolved` / `manifest-name-ambiguous` — manifest present but not checkable | — |
| **WARN** | `text-overflows-container` — a label whose center sits inside a rect escapes its border (box sized smaller than its label); smallest containing rect wins, so a pill straddling a card edge doesn't false-fire | > 2 u |
| **WARN** | `line-through-text` — a stroked line/path crosses through a label's glyph box with both endpoints outside it (a leader line *terminating* at its label is fine); halo'd labels (S4 §8 `paint-order: stroke`) are exempt | — |
| **WARN** | `dead-canvas` — content fills < 70% of the frame on an axis, or an empty vertical run > 30% | — |
| **NOTE** | `arrow-buried` — `marker-end` endpoint deep inside a foreground rect (S4 §9 says land 2–4px short) | > 3 u inside |
| **NOTE** | `arrow-into-void` — endpoint far from every 2D shape/label (axis arrows are the known-intentional case) | > 8 u |
| **NOTE** | `text-vs-marker` — a label box intersecting a small dot/tick | overlap > 0 |

The manifest diff resolves names by element `id`, then `data-name`, then a `<text>` whose exact
content equals the name (case-insensitive; in the labeled-box idiom the smallest shape containing
that label's center becomes the node box). Matching is one-to-one against side *segments*, not
midpoints, so S4 §3 corridor offsets (±8px along a side) and curved `<path>` edges match fine.

The measured tier costs no tokens. Each of its PROBLEM lines counts in `problems=N`, and the check is
done at `problems=0`.

**Semantics in the ship flow:** PROBLEM lines are **ship-blockers**; a WARN needs a stated reason or a
fix; a NOTE gets a look (both arrow NOTEs have known-intentional cases, which is why they aren't
problems). **Whenever playwright can be imported, the check runs this tier itself; when it cannot,
your report says that the geometry was not measured.** Fix noise with authoring rules, not check
exemptions: the check reports everything; the S4 §8 one-label rule is what makes intentional
adjacency invisible to it. **Re-run the check after every fix, and re-enter the repair loop on any
NEW finding at any tier, not only PROBLEMs**: a repair that shortened a flying arrow can create a
fresh `dead-canvas`, and it ships when the loop re-gates only on the PROBLEM tier.

**Delegated authoring (the drawing agent of `figure-agent.md`): its self-check is a claim, not
evidence.** A drawing agent can report its figures as passing while the check, run again, reports
findings, even on the exact element it describes having "arithmetically fixed". So the drawing agent
runs `figures.py check TEXT` itself, and when its files come back you run the check again and feed the
findings back to it as the repair prompt; PROBLEM lines block ship regardless of the agent's stated
verification. Scope the drawing agent to catalog shapes with straight/elbow edges — rings, freehand
curves, and radial layouts fail at this tier even with explicit instructions; those get a stronger
model or a regenerate, not a repair loop (§ two-tier ship rubric: below B → regenerate, don't patch
at the same tier).

> **DEGRADE GRACEFULLY.** No playwright → the check prints `NOTE measured checks did not run: ...` and
> `measured=no`. What it reads from the source, the Gate 1 checklist above and the S4 §5 arithmetic
> containment check remain the contract, and your report says that the geometry was not measured.
> Install playwright only where your instructions allow installing packages; never make it a
> *required* dependency, the same rule as Gate 2.

**Look for a line you cannot see.** No finding reports a divider or a scale rail drawn in `--border` that vanishes on a dark screen: when the claim leans on the line, draw it in `--muted-line` (S6).

### Gate 2 — Opportunistic bounded vision loop

Run `figures.py preview TEXT`: it writes a PNG of each figure for a light and a dark screen (without playwright, an HTML file to open in a browser). Look at each picture once against its claim and **read the pixels**. Then **score what you SEE, not what you know the code does**, against this CLOSED defect table:

| Defect | What it looks like in the pixels |
|---|---|
| overflow | a shape or stroke runs past the viewBox edge / out of its panel |
| overlap | two semantic shapes or labels collide and obscure each other |
| text-truncated | a `<text>` is clipped or runs off — SVG text does NOT wrap |
| blank | an element is invisible (wrong fill, zero size, off-canvas) |
| element-outside-viewBox | a marker/label drawn beyond `0 0 W H`, cropped away |
| arrow-direction | an arrowhead points the wrong way for the relation it asserts |
| fill-vs-legend | a fill's color doesn't match what the legend/caption claims it means |

Loop: preview -> score every row -> fix the named defects -> **re-run the check, then preview again**. Cap at **<=2 rounds**; if defects remain after round 2, escalate (see structured failure object). Re-running the check and the preview after each fix is mandatory, since an un-rendered "fix" is a guess. Act on any NEW finding the check prints, at any tier.

> **DEGRADE GRACEFULLY.** No picture to look at (no playwright, and no browser to open the file `preview` writes) -> fall back to textual self-critique plus the Gate 1 preflight, and say in your report that vision was unavailable. NEVER make a headless browser a *required* dependency: the loop is opportunistic by rule.

### Ship-blocker GATE

**Do not ship a bespoke SVG that was never visually inspected** (unless your report explicitly notes vision was unavailable). Rationale, stated plainly so it survives: *LLMs cannot see what they generate; shapes built from separate coordinates produce gaps and clips the model cannot detect without rendering.* This converts "you should verify" into a blocking pass/fail step — treat render-count == 0 as not-done.

### Two-tier ship rubric (works headless)

The tiers line up with the two gates above: **Tier 1 is Gate 1** (parse/legal: what the check reads from the source), and the rubric below grades **Tier 2** (layout-integrity booleans, judged from the preview) and **Tier 3** (quality, judged from taste). Produce this as a pasteable artifact even when no browser is available — both tiers degrade to source self-critique.

- **Tier 2 — layout-integrity booleans.** Record `true` when an issue **IS found**: `overflow`, `overlap`, `text_truncated`, `blank`, `element_outside_viewbox`. Any `true` is a hard stop — fix before scoring Tier 3.
- **Tier 3 — 1–5 quality scores:** `spacing`, `legibility`, `color_semantics` (fills match the legend), `alignment`. Average them, map to a letter: 4.5+ = A, 3.5+ = B, 2.5+ = C, below = D/F.
- **Ship bar:** ship at **A or B**; **regenerate below B**. **Any critical dimension at its floor (a `1`)** — legibility or color_semantics — = **do-not-ship**, regardless of the average. (The scale is 1–5, so the floor is `1`, not `0`; a single floored critical dimension hard-stops the ship even when the mean lands in A/B.)

### Authoring-build discipline (prevents defects upstream)

- **Incremental scaffold-then-render.** Draw the skeleton/anchor shapes, render, then add **one labeled element at a time**, re-rendering — so the breaking coordinate is isolated at its source instead of in a finished tangle.
- **Repair by edit, never by redraw.** Fix a figure with edits to the elements a finding names, a few at a time. When one finding repeats across most labels (`text-too-small` on every text), the cause is one number, so change that once. Do not write a whole figure again to change sizes or positions: every coordinate is typed anew, and each is a new chance of a slip.
- **Loop budget: two looks.** A figure earns one or two rounds of look and fix (Gate 2). If it still fails after the second, escalate (structured failure object) instead of looping again.

### Structured failure object (defect -> self-repair retry)

When a gate fails, emit a machine-actionable object so the defect becomes a bounded self-repair retry rather than a vague "review it":

```json
{
  "error": "arrow-direction: pass arrowhead points from result back toward the check",
  "troubleshooting_matches": [
    { "symptom": "<line ...marker-end... > with reversed x1/x2",
      "correct_example": "swap endpoints OR use orient=\"auto-start-reverse\" and marker-start" }
  ],
  "suggested_fix": "set marker-end on the line whose x2,y2 is the result node",
  "round": 1
}
```

Bounded retry then escalate: match the `error` against the PATTERN→FIX rows (top of this file), apply the `correct_example`, re-run the check and preview again. After **2** rounds with the defect unresolved, stop auto-repairing and surface the object plus the last preview for human judgment — do not silently ship.
