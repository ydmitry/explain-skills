> **Use when** a figure is drawn: read §2 to §4 (from the geometry-constants header to char-width box
> sizing) and §9 (ports and edges) after `svg-color.md`, before the first coordinate: every box, label
> and arrowed edge is derived here; the other §§ when a finding names them. The drawing agent of
> `figure-agent.md` reads it whole. Re-read one § when `figures.py check` names it (S4 §N).
> `grep -n '^##' references/svg-geometry.md` prints every heading with its line, so one ranged read
> takes a section.
>
> **In this file (S4):** §1 top-left anchoring · §2 the constants header, bands first, `H` last, container
> rects · §3 the grid · §4 char-width box sizing + minimum type size · §5 the containment check ·
> §6 z-order · §7 non-scaling-stroke · §8 text anchors, tspans, halos · §9 ports, edges, the edge
> manifest.
>
> **Siblings:** `svg-figures.md` (S0–S3, read first) · `svg-color.md` (S6) · `svg-shapes.md`
> (catalog and the S5 Gap and arrowhead primitives these examples assume) · `svg-repair.md` (S7:
> what the check reports, PATTERN → FIX) · `svg-refine.md` (S8–S10).

# Figure geometry (S4)

## S4 · Coordinate & geometry discipline (derive, don't eyeball)

You cannot see what you draw, and two safety nets you rely on elsewhere are gone inside an SVG `viewBox`: SVG `<text>` does **not** wrap, and the overflow rules that let a page's text reflow (`min-width:0` / `overflow-wrap` / scroll containers) do **not** apply to anything inside a fixed-coordinate frame. A label that is one character too long doesn't wrap or scroll: it spills past the viewBox and gets clipped, silently. So geometry has to be *derived*, not guessed. Get the numbers right up front and the render-look-fix loop (S7) becomes a safety net instead of a debugger.

This covers the inside of each figure.

### 1. One anchor convention: author from top-left, convert to cx/cy at emit-time

The single most common hand-SVG bug is mixing corner-anchored `<rect>`s with center-anchored `<circle>`s, then doing relative math that's silently off by a radius. The discipline is about the **authoring vocabulary**, not the emitted attribute: lay out *every* box-shaped primitive by its **top-left corner** `x,y` plus `width`/`height`, then convert to `cx`/`cy`/`rx`/`ry` only when you emit. No negative coordinates. One set of relations then holds for everything: `center = x + w/2`, `right edge = x + w`, `bottom = y + h`, and a dot and a rect dropped at the same `x,y` line up by construction.

A circle becomes a box you convert at the last moment:

```js
// dot authored from top-left x,y with diameter d — cx/cy/r computed, never typed
const dot = (x, y, d, fill) =>
  `<circle cx="${x + d / 2}" cy="${y + d / 2}" r="${d / 2}" fill="${fill}"/>`;
// now a dot and a rect at the same x,y line up by construction
```

**The ban is the default for every box-shaped primitive.** Author rects, label boxes, pills, and
node frames top-left; never type a `cx`/`cy`/`r`/`rx`/`ry` for them.
The exception is narrow: it covers ONLY primitives whose geometry is intrinsically radial or plotted:
a ring/arc gauge (`svg-shapes.md`, "Ring / arc gauge from one number") that is a `<circle r=>` driven
by `stroke-dasharray` and *cannot* be expressed without `r`, and the sparkline, slopegraph, 2×2, and
spectrum dots, which are points at a computed `cx,cy`. Even then, `cx,cy` must be **emitted from a top-left bounding box**, never
eyeballed: the gauge's `cx,cy` is the center of its top-left box, and each dot's `cx,cy` comes from
a `map()`-ed data value. (`<marker>`s and `<symbol>`s define their own `viewBox`, so their internal
`cx,cy` are local and exempt as well.) The rule bans *typing* a center — not the geometry of circles
that are real circles. Every circle in svg-figures.md S3, svg-shapes.md S5 and svg-color.md S6
carries a one-line note tying its `cx,cy` back to a top-left frame, so the rule and its examples
stop disagreeing.

### 2. Geometry-constants header + derive-don't-type

Declare named constants once at the top, then compute every coordinate from them. The model never invents two conflicting magic numbers, and the drawing stays editable — bump `GAP` and everything re-flows.

```js
const W = 720, H = 240, PAD = 24, GAP = 16, STROKE = 1.5;
const COL = (W - 2 * PAD - GAP) / 2;          // two equal columns
const colX = i => PAD + i * (COL + GAP);       // x of column i
const rowY = (top, i, step) => top + i * step; // y of row i

const constrain = (n, lo, hi) => Math.max(lo, Math.min(hi, n));
const map = (v, inMin, inMax, outMin, outMax) =>
  outMin + ((v - inMin) * (outMax - outMin)) / (inMax - inMin);

// Pixel y grows DOWN, data grows UP — invert the output range so the
// bar top sits at PAD and the baseline at H-PAD. Forget this and your
// chart is upside down with no error.
const yScale = v => constrain(map(v, 0, 100, H - PAD, PAD), PAD, H - PAD);
```

Siblings are `colX(0)`, `colX(1)`; a stacked group's total height is `icon + GAP + label`. Emit the SVG from these (template string) or paste the computed literals — either way the numbers trace back to the header.

**Bands first, `H` last.** Lay the figure out as named horizontal bands in the constants header —
`TITLE_H`, `FIG_H`, `CAP_H`, `FOOT_H` — and *compute* the frame:
`H = PAD + TITLE_H + FIG_H + CAP_H + FOOT_H + PAD`. Type the `viewBox` attribute only after the
bands are summed, never first. A frame typed first and "filled in" fails in both directions:
content grows and the typed `H` doesn't (a late-added footnote lands outside the frame and is
clipped), or `H` is typed generously and never reconciled (a third or more of the frame ships
empty; the check (S7) reports this as `dead-canvas`).

The same rule binds every **container rect** inside the frame, not just the viewBox: a card or
panel's `width`/`height` is `last_child_edge + PAD`, recomputed as the LAST authoring step after
all children land. A container whose bottom or right edge sits more than `2×PAD` beyond its
farthest child is a defect, not breathing room: the content floats in the upper-left of an
oversized panel. Round literals ("height=260 feels safe") are how the slack gets in; derive, don't
round up.

### 3. Plan the grid before assigning any coordinate

Before the first `x`, sketch the grid on paper: how many columns, how many rows, where the divider sits. Then:

- **Snap** every `x/y/w/h` to one base unit (here `PAD/GAP = 24/16`). Off-grid pixels read as misalignment.
- **Same-role elements share an axis.** Both "PASS" pills sit at the same `y`; both column headers share a baseline. If two things mean the same kind of thing, one of their coordinates is identical — `colX(i)`, not two typed numbers.
- **Reserve ~80px routing corridors** between rows for connectors and arrowheads so a `<line>` + marker never collides with the box below it.

### 4. Char-width box sizing, computed up front

Because `<text>` won't wrap, size every label box from its character count *before* drawing it.
Width estimate **by style, not one constant**: sentence-case 400-weight ≈ `len × fontSize × 0.5`;
monospace ≈ `× 0.6`; **600–700-weight CAPS with letter-spacing ≈ `× 0.7`**. That last one is the
label style of headers, group labels, and badges, precisely where collisions happen (the 0.5
coefficient undershoots it by ~30–40%, the usual cause of near-collisions in these labels). When an
estimate lands within 10% of its budget, treat it as over
budget — and fix it by **re-layout, never by deletion**: widen the box, move the label to a
clearer slot, or drop the font size within the S7 legibility floor. NEVER delete or truncate a
token that the brief's `data:` line lists to make text fit: a unit ("ms", "s"), a value, a named
event, a sublabel word. Removing an item of the brief to pass containment converts a layout warn
into a fidelity failure, which is strictly worse: a figure that "fixes" overflow by dropping the
axis unit, a named event or sublabel words fails on exactly the content it deleted. These
coefficients get the first draft close; the check (S7) measures the truth afterwards (when
`playwright` is not installed the check measures nothing and says so).

These coefficients are estimates for an average sans. The fonts of `--font-body` differ by machine, and a wide one runs near `0.6` for sentence-case text: leave a tenth of slack in a box that holds a sentence, and trust the measured check (`text-overflows-container`) over the estimate.

**Minimum type size, computed at source.** The floor (rendered < 9.5 px) is checkable before any
render: `rendered px = font-size × (rendered width / viewBox width)`. One viewBox unit is one CSS
pixel at full size, a viewBox is at most 720 wide, and a page shows a figure at 100% of its size
down to 80% before the figure scrolls sideways. So label text of 12 units stays readable at the
smallest size (12 × 0.8 = 9.6 px), and the check reports text under 12 units as `text-too-small`: it measures each figure at that smallest size.
Fix by enlarging the font or shrinking the viewBox; never by hoping the figure is shown at full
size. (Small axis ticks, such as 0..300 ticks at 9 units, are where this is most often missed.)

```js
const PER_CHAR = 7;      // ~0.55 * 13px mono
const LINE_H = 18, BOX_PAD = 14, MIN_W = 120;
const boxW = (lines) =>
  Math.max(MIN_W, Math.max(...lines.map(s => s.length)) * PER_CHAR + 2 * BOX_PAD);
const boxH = (lines) => lines.length * LINE_H + 2 * BOX_PAD;
// center text inside the box: x = boxX + boxW/2 with text-anchor="middle"
```

This is the inside-the-viewBox counterpart to a page's overflow rules: those let DOM text *reflow* when it's too wide; here nothing reflows, so you must make the box wide enough at author time. Size correctly and overflow defects rarely occur.

### 5. Containment check (pre-ship)

Before you report, verify by arithmetic, not by eye: every `x+w ≤ W - PAD` and `y+h ≤ H - PAD` and every `x,y ≥ PAD`; no glyph extends past its box (`textLen ≤ boxW - 2*BOX_PAD`); no two same-row boxes overlap (`colX(0)+COL ≤ colX(1)`). Nothing outside the viewBox, no clipped glyph, no colliding labels. This is what demotes the vision loop to a backstop.

### 6. Decoration z-order: connectors under node text

SVG paints in document order — there is no `z-index`. Put dividers, connectors, and zone fills in their **own `<g>` placed BEFORE the items group**, so decoration renders *under* the nodes and their text. Group labels with their shapes so a targeted edit moves both.

```xml
<svg xmlns="http://www.w3.org/2000/svg" id="fig-1" viewBox="0 0 720 240" role="img"
     aria-label="The kebab-case skill name passes the frontmatter check; the underscored TODO stub fails.">
  <!-- decoration FIRST: dashed divider + zone tints render underneath.
       vector-effect is non-inherited and only applies to graphics elements, so it
       must live on the <line>, NOT the <g> — on a container it is a silent no-op. -->
  <g class="decor">
    <line x1="360" y1="24" x2="360" y2="216" style="stroke:var(--border)" stroke-dasharray="4 4"
          vector-effect="non-scaling-stroke"/>
  </g>
  <!-- items SECOND: boxes + text paint on top of the divider -->
  <g class="items">
    <rect x="24" y="40" width="312" height="92" rx="10" style="fill:var(--bg); stroke:var(--border)"/>
    <text x="38" y="64" font-size="13"
          style="font-family:var(--font-mono); fill:var(--ok-ink)">name: fact-sheet-search</text>
  </g>
</svg>
```

### 7. non-scaling-stroke (+ pathLength) for a figure shown smaller than drawn

A page shows a figure at 100% of its size down to 80% before the figure scrolls sideways, and plain strokes scale with it: a 1.5px hairline thins to 1.2px at 80%. Set `vector-effect="non-scaling-stroke"` so stroke width stays constant under any transform. For dashes that must stay proportional regardless of path length, set `pathLength="1"` and express the dash array as fractions of 1, so the dash math no longer depends on the measured geometry:

```xml
<!-- half-on/half-off dashes, identical at any size -->
<path d="M24 120 H696" fill="none" style="stroke:var(--info)" stroke-width="1.5"
      vector-effect="non-scaling-stroke" pathLength="1" stroke-dasharray="0.04 0.04"/>
```

One calm emphasis hue (`var(--info)`) over neutrals (`var(--muted)` / `var(--border)`), semantic fills from the tokens only (`var(--ok)` = pass, `var(--error)` = fail, S6). The `aria-label` states the *finding*, not the medium: it is the mark's sentence, word for word (S0).

### 8. Text alignment: place anchors, not strings

The renderer aligns text around its **anchor point** — control that; never "center" a left-anchored
string by padding its `x` with guessed pixels (the single most common misalignment).

- **Pick `text-anchor` by role, then share the anchor coordinate.** Centered label →
  `text-anchor="middle"` at the box center (`x + w/2`). A column of row labels →
  `text-anchor="end"`, all on ONE anchor line declared in the constants header
  (`const LBL_X = colX(1) - 8`); the values beside them → `text-anchor="start"` at their own shared
  `x`. This is §3's same-role-same-axis rule applied to text: same role ⇒ same anchor coordinate.
- **Vertical centering is baseline arithmetic, not `dominant-baseline`.** `dominant-baseline` /
  `alignment-baseline` shift differently across renderers and print rasterizers — don't rely on
  them. Center single-line text with `y = boxY + boxH/2` plus `dy=".35em"` — the cap-height
  correction that visually centers any sans at any size, and stays *computable* for the §4/§5
  containment estimates (a renderer-computed shift isn't):

```xml
<!-- label dead-center in a 120×32 box at (24,40): y = 40 + 16, dy corrects the baseline -->
<rect x="24" y="40" width="120" height="32" rx="6" style="fill:var(--bg); stroke:var(--border)"/>
<text x="84" y="56" dy=".35em" text-anchor="middle" font-size="12" style="fill:var(--text)">queued</text>
```

- **Multi-line text: re-set `x` on every `<tspan>`.** A `<tspan dy="16">` continues from where the
  previous line *ended* — without its own `x`, line 2 starts indented at line 1's right edge. Line
  spacing: `dy = fontSize × 1.3`.

```xml
<text x="84" y="52" text-anchor="middle" font-size="12">Frontmatter
  <tspan x="84" dy="16">passes the bar</tspan></text>  <!-- x repeated, or line 2 drifts right -->
```

- **One logical label = one `<text>` node.** A composite label — node name + tag ("A" + "v2.1"),
  numeral + unit ("26" + "ms"), any stacked two-liner — is ONE `<text>` with `<tspan>`s (tspans may
  carry their own `font-size`/`fill` for mixed styles), never sibling `<text>` nodes nudged
  together. Two reasons: siblings drift apart under edits because their spacing is two independent
  guesses; and the check (S7) treats separate `<text>` nodes as separate labels: merged labels make
  every remaining collision report a real defect.
- **Halo, don't dodge, when contact is unavoidable.** A label that must sit on or beside a
  meaning-carrying line gets a background-colored halo:
  `paint-order: stroke; stroke: var(--surface); stroke-width: 3px;` on the `<text>`. The
  cartography trick keeps the label readable through the crossing. Corridors (§3) remain the first
  choice; the halo is the sanctioned fallback — and a halo'd label touching a line is not a defect.
- **Mixed sizes align on the baseline, not the top.** A 26px numeral and its 11px unit share the
  same `y` — baselines align typographically; tops never do.
- **Number columns:** `text-anchor="end"` on one shared right edge +
  `style="font-variant-numeric:tabular-nums"` — digits align with zero per-row nudging.

### 9. Ports and edges: arrows that cannot detach or reverse

Wrong-way arrows and heads floating off their boxes share one root cause: edge endpoints typed as
fresh literals instead of derived from the boxes they claim to touch. Kill the class, not the
instance:

- **Nodes are data; ports are derived; edges may reference ONLY ports.**

```js
const box = (x, y, w, h) => ({ x, y, w, h,
  L: [x, y + h / 2], R: [x + w, y + h / 2],     // left / right ports
  T: [x + w / 2, y], B: [x + w / 2, y + h] });  // top / bottom ports
const A = box(24, 40, 120, 48), Bx = box(280, 40, 120, 48);
// horizontal edge A → B, tip landing 3px short of B's border:
// <line x1="${A.R[0]}" y1="${A.R[1]}" x2="${Bx.L[0] - 3}" y2="${Bx.L[1]}" marker-end="url(#…)"/>
```

  Move a box and its arrows follow — detachment becomes impossible by construction.
- **One direction convention: source→target, head on `marker-end`.** `x1,y1` is always FROM,
  `x2,y2` always TO, the head always `marker-end`. Never draw target→source and patch with
  `marker-start`. "Does this arrow point the right way" then becomes a *words* check, not a
  geometry check: read the claim ("check → verdict"), confirm `x2,y2` is the verdict's port.
- **Land 2–4px short of the target.** With the S5 marker (`refX="9"`, ~7px head) the tip sits at
  the line's end — stop the line 3px before the port along the approach axis so the head kisses
  the border instead of burying into it.
- **Elbow edges: H/V segments; the final segment aims INTO the port.** For grid-aligned boxes route
  `M ax ay H midX V by H bx` — never a diagonal into a corner. `orient="auto"` rotates the head to
  the *final* segment, so finish horizontal into an `L`/`R` port and vertical into a `T`/`B` port
  and the head points exactly where the edge enters. Two edges sharing a corridor (§3): offset
  their mid-segments ±8px so they don't overlap.
- **A loop-back / return edge is an edge, not decoration.** The re-entry arc, the retry path, the
  cycle-closing edge (the element most often drawn wrong) obeys the same
  port discipline as a forward edge: it starts at a derived FROM port, its FINAL segment aims INTO
  the TO port, it lands 2–4px short, it carries `marker-end`, and it carries its own label ("fix
  commit", "retry"). Route it as an elbow through a reserved corridor (§3) — around the outside of
  the node row, never diagonally across other nodes or edges. If you cannot derive every point of
  a curve from ports and corridor constants, draw the elbow instead: a freehand arc that "sweeps
  back" is how re-entry arrows end up slicing through node interiors with their heads buried under
  a box (the check reports both: `edge-through-node` as a `PROBLEM`, `arrowhead-hidden` as a
  `WARN`).
- **Nodes never touch.** Sibling node boxes keep a gutter of at least 24u (§3 corridors). Two boxes
  sharing a border make their facing ports the SAME line: an edge starting there "belongs" to both
  nodes, the manifest diff can no longer tell them apart, and any edge between them has zero
  routing room (check: `node-gap`). If two boxes are conceptually fused, draw ONE box with two
  labels inside it.
- **Edge manifest: verbalize the topology as an auditable artifact, then diff it.** Every figure
  with arrowed edges carries a manifest comment, the first child of the `<svg>`, listing each edge
  as `FROM.port → TO.port`: `<!-- edges: check.R → verdict.L | input.B → transform.T -->`. Write it
  when you fill the brief, before any coordinate. The grammar is EXACTLY `NAME.port → NAME.port`
  entries joined by `|`, ports L/R/T/B, with no parenthetical annotations, no adjectives, no prose:
  an entry the check cannot parse silently disables the only test that catches reversed and
  mis-routed arrows on that edge, so the check reports an unparsable entry as a `PROBLEM`.
  Legend/key swatch arrows are not
  topology — keep them inside a `<g class="legend">` and leave them out of the manifest. Names must
  resolve mechanically, in this order: an element `id` inside the `<svg>`, then a `data-name`, then
  a `<text>` whose exact content is the name. Every id starts with `fig-N-`, so name each node rect
  with a `data-name` matching its manifest name, as the S0 skeleton does, or give it a label whose
  exact text is the name. The audit is then a mechanical diff: each `marker-end` edge must land on
  the named TO-port's side (± the 2–4px landing gap) having started at the FROM side.
  `figures.py check` (S7) runs this diff automatically when the manifest is present, and flags
  figures that have arrows but no manifest. This catches reversed and mis-routed arrows, which
  *render* perfectly and are invisible to every geometric check: a cycle edge drawn to the wrong
  node is exactly this class, and one of the worst fidelity failures a figure can have. When
  authoring is delegated (subagents, workflows), the manifest is load-bearing: it is the only
  artifact a verifier can check the drawing against without re-deriving the intent.
- **Mirrors are functions.** For symmetric before/after layouts derive the right side —
  `const mirror = b => box(W - b.x - b.w, b.y, b.w, b.h)` — retyping mirrored coordinates by hand
  is how the after-side ends up 6px off.
