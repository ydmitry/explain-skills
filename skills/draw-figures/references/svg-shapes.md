> **Use when** the S3 index of `svg-figures.md` or its table "From the brief's shape name to its recipe"
> names your shape or primitive, the S5 Gap and Semantic arrowheads included. Read per heading, never
> whole: find the `###` heading (the table quotes it word for word) and read that section only.
>
> **In this file**, in order. The catalog, `## The catalog: eleven named shapes`: 2×2 matrix · 3–8 step
> cycle · Comparison pair · Phase / funnel · Layered stack · Causal DAG · Venn · Spectrum · Pyramid ·
> Heat-grid · Swimlane. The primitives, `## Copy-paste solved-arithmetic primitives (the math
> pre-solved)`, which opens with the house rules and the gutter slots: S5 · Near-universal primitives:
> the Gap + Semantic arrowheads · Before / after "Gap" primitive · Semantic arrowheads · Threshold meter (a
> value against a limit) · Filled track (a share of a whole) · Ring / arc
> gauge from one number · Inline sparkline (semantic) · Slopegraph (before / after on one shared scale)
> · Grouped-bar value labels · Texture / hatch fill as a second channel.
> `grep -n '^##' references/svg-shapes.md` prints every heading with its line, so a ranged read takes
> one section.
>
> **Siblings:** `svg-figures.md` (S3 the shapes and the table from a shape name to its recipe, S0 the
> figure file, S2 the brief, S1 the decision gate; read first) · `svg-color.md` (S6: the tokens, colour
> by meaning, accessibility) · `svg-geometry.md` (S4: derive every coordinate) · `svg-repair.md` (S7:
> what the check reports and its fix, on a finding) · `svg-refine.md` (S8–S10: taste, when a figure
> passes the check and still looks generic).

# Concept-illustration shape catalog + solved-arithmetic primitives

> **Valence tokens.** Figures below that carry a pass/fail reading use `--ok-*`
> (pale zone / hairline line / readable ink). They are tokens like the rest (`assets/tokens.css`,
> S6): the zone and the line are mixed toward `--surface`, the ink toward `--text`. A figure defines
> none of them: `figures.py place` writes the token block into the file.

**Read per-shape, not whole.** After the index (`svg-figures.md` S3) or its table "From the brief's
shape name to its recipe" names your shape, read that section and only that section: the table quotes
the heading word for word, and the grep in the header gives its line.
The whole file is several times what a single shape needs.

Cross-references: `S0`–`S3` point to sections in `references/svg-figures.md` (the core file), `S4`
to `references/svg-geometry.md`, `S6` to `references/svg-color.md`, `S7` to
`references/svg-repair.md`; the Gap primitive and Semantic arrowheads (S5) live in this file. `S8`–`S10`
(taste) are in `references/svg-refine.md`, the PATTERN→FIX catalog in
`references/svg-repair.md`. A graph too large to draw is routed in S1, Gate 2.

---

## The catalog: eleven named shapes

Pick the illustration from this finite catalog instead of inventing geometry per concept. Every
entry carries an **epistemic precondition** (the claim/data shape it can honestly hold) and an
**anti-prescription** (the misuse that turns the picture into a lie). Choosing the shape *is* the
first honesty gate — before any coordinate is placed, the precondition tells you whether the shape
can carry your claim, and the anti-prescription tells you when it would be lying.

Each entry: what it **argues**, when it is **honest**, the **lie** it becomes when misused, and what
to **build** it with. Every shape here is hand-drawn while it is small. When it is not, split the
claim into the claims it holds or give it as a table or a list (S1, Gate 2: a graph of nine or more
nodes is rarely one claim); a `mermaid` block belongs only in a text that stays Markdown (`SKILL.md`,
"A graph in a text that stays Markdown"). The geometry recipes are inline below.

**Three shapes — 2×2 matrix, Pyramid, Spectrum — lie most easily** because their meaning lives in
*proportion and position*, not labels; their arithmetic is pre-solved under their headings below.
All worked recipes are flat-fill, token-driven (colours from the tokens, `assets/tokens.css`, per S6,
so they follow a light and a dark screen), one calm emphasis hue (`var(--info)`) over neutrals,
`role="img"` with an `aria-label` that is the mark's sentence and states the finding, and respect the
bans of S6 (no font but `var(--font-body)` or `var(--font-mono)`, so a typed font family is a finding;
no violet/fuchsia/indigo).

### 2×2 matrix
- *Argues:* two independent binary dimensions carve the field into four genuinely different kinds.
- *Honest when:* items are scored on two axes that vary **independently**, and all four cells are populated.
- *Lie:* if the axes correlate, items pile on one diagonal and two cells stay empty — you've drawn a line with extra ink. Use a spectrum or a ranked list.
- *Build with:* the recipe below.

The poster child for the empty-diagonal lie. Four equal cells, axes crossing at the centre, the
focal quadrant carrying the accent. If your real data only lands in two diagonal cells, this recipe
will *show you* it should have been a spectrum.

```xml
<svg xmlns="http://www.w3.org/2000/svg" id="fig-1" viewBox="0 0 320 300" role="img"
     aria-label="Initiatives plotted by impact (vertical) against effort (horizontal): the two quick wins sit top-left, high impact for low effort; the high-effort low-impact quadrant is a time sink.">
  <style>
    #fig-1 .q-cell{fill:var(--bg);stroke:var(--border);stroke-width:1}
    #fig-1 .q-win {fill:var(--ok-zone);stroke:var(--ok-line)}
    #fig-1 .q-axis{stroke:var(--muted);stroke-width:1.5}
    #fig-1 .q-name{font:600 12px var(--font-body);fill:var(--text)}
    #fig-1 .q-ttl {font:600 12px var(--font-body);fill:var(--muted);letter-spacing:.5px}
    #fig-1 .q-dot {fill:var(--info)}  /* plotted items = emphasis, not a verdict → --info, not the green */
  </style>
  <!-- quadrants: 120x120 each, focal cell first so it carries the accent -->
  <rect class="q-cell q-win" x="64"  y="20"  width="120" height="120"/>
  <rect class="q-cell"       x="184" y="20"  width="120" height="120"/>
  <rect class="q-cell"       x="64"  y="140" width="120" height="120"/>
  <rect class="q-cell"       x="184" y="140" width="120" height="120"/>
  <!-- axes through the centre (184,140) -->
  <line class="q-axis" x1="64"  y1="140" x2="304" y2="140"/>
  <line class="q-axis" x1="184" y1="20"  x2="184" y2="260"/>
  <!-- quadrant meanings, anchored at cell centres -->
  <text class="q-name" x="124" y="84"  text-anchor="middle">Quick wins</text>
  <text class="q-name" x="244" y="84"  text-anchor="middle">Big bets</text>
  <text class="q-name" x="124" y="204" text-anchor="middle">Fill-ins</text>
  <text class="q-name" x="244" y="204" text-anchor="middle">Time sinks</text>
  <!-- two real items populate the focal quadrant;
       cx/cy are plotted points derived from a top-left box per S4 (S4 §1 plotted-point exception) -->
  <circle class="q-dot" cx="110" cy="60" r="4"/>
  <circle class="q-dot" cx="150" cy="104" r="4"/>
  <!-- axis titles encode direction in words, no extra arrowheads -->
  <text class="q-ttl" x="40"  y="140" text-anchor="middle"
        transform="rotate(-90 40 140)">IMPACT: low &#8594; high</text>
  <text class="q-ttl" x="184" y="288" text-anchor="middle">EFFORT: low &#8594; high</text>
</svg>
```

### 3–8 step cycle
- *Argues:* a process repeats; the last step feeds the first, with no start or end.
- *Honest when:* 3–8 stages that genuinely loop back.
- *Lie:* a one-shot run bent into a ring. If it starts and stops, it's a sequence/pipeline. Past ~8 nodes the ring is unreadable — split it.
- *Build with:* a ring of nodes + curved arrowheads (Semantic arrowheads, S5 in this file). A true graph rather than a loop is a small flow at eight nodes or fewer (S4 §9); at nine or more, split it into the claims it holds or give it as a nested list (S1, Gate 2).

### Comparison pair
- *Argues:* A and B differ measurably on the **same** dimensions.
- *Honest when:* two (at most three) alternatives scored on one shared baseline/axis set.
- *Lie:* scoring each side on different axes (apples vs oranges), or padding the favored column to look fuller. Share the baseline.
- *Build with:* the Slopegraph primitive below, or the before-after "Gap" primitive (S5, this file); when the two sides are prose rather than values, a table in the text.

### Phase / funnel
- *Argues:* a population attrits through ordered stages, each a subset of the last.
- *Honest when:* counts decrease monotonically and each stage nests inside the prior; **width ∝ count**.
- *Lie:* funnel widths for non-nested or non-decreasing quantities — if stage 3 > stage 2 the taper is cosmetic fiction. Width must encode the count, not the slide layout.
- *Build with:* stacked area-proportional trapezoids (see the Pyramid recipe). A branching flow is hand-drawn while it is small; otherwise split it into the claims it holds or give it as a table (S1, Gate 2).

### Layered stack
- *Argues:* upper layers rest on, and depend on, the layers below.
- *Honest when:* a true abstraction/dependency stack — each layer sits on the one beneath it.
- *Lie:* stacking unrelated peers (that's a list, drawn sideways), or implying a bottom layer supports the rest when it doesn't.
- *Build with:* a vertical run of full-width `<rect>`s, semantic fills (S6).

### Causal DAG
- *Argues:* causes flow to effects along directed, acyclic edges.
- *Honest when:* directed influence/dependency with **no feedback loops**; an arrow reads "leads to".
- *Lie:* a cycle inside a "DAG" (it's a state machine / feedback loop then); or arrows implying causation you only have correlation for.
- *Build with:* this is a node/edge graph. At eight nodes or fewer, hand-draw it as a small flow (S4 §9 ports and edges + Semantic arrowheads, S5 in this file); at nine or more, split it into the claims it holds or give it as a nested list (S1, Gate 2).

### Venn
- *Argues:* sets share members; the overlap region is the shared subset.
- *Honest when:* 2–3 sets whose intersection is meaningful and **non-empty**.
- *Lie:* Venn-ing sets that can't overlap (an empty intersection is just two separate circles), or using overlap to imply sequence or causation.
- *Build with:* two or three circles drawn by hand, every centre and radius derived from S4 constants: circle-overlap geometry is fiddly and error-prone when placed by eye. Sets that do not fit as circles are split into the claims they hold or given as a table or a list.

### Spectrum
- *Argues:* items sit at positions along one continuous axis between two poles.
- *Honest when:* a single ordinal/continuous dimension with meaningful endpoints; **position encodes value**.
- *Lie:* placing items at evenly spaced ticks when the underlying values aren't evenly spaced — position must encode magnitude, not reading order.
- *Build with:* the recipe below.

One axis, two poles, items at their **true** positions. Map a value `v` on a `[0, 10]` scale to
`x = 40 + (v/10)·240`. Uneven values must produce uneven gaps; that gap *is* the finding.

```xml
<svg xmlns="http://www.w3.org/2000/svg" id="fig-1" viewBox="0 0 320 90" role="img"
     aria-label="Three tools on a single manual-to-autonomous axis by their actual autonomy score: the two manual tools cluster at the left, the autonomous one sits far right; the gaps are real, not evenly spaced.">
  <style>
    #fig-1 .s-axis{stroke:var(--muted);stroke-width:2}
    #fig-1 .s-dot {fill:var(--info)}
    #fig-1 .s-lab {font:600 12px var(--font-body);fill:var(--text)}
    #fig-1 .s-pole{font:12px var(--font-body);fill:var(--muted)}
  </style>
  <line class="s-axis" x1="40" y1="44" x2="280" y2="44"/>
  <!-- plotted points: v=1.5 -> x76, v=4 -> x136, v=8.5 -> x244;
       cx/cy derived from a top-left box per S4 (S4 §1 plotted-point exception) -->
  <circle class="s-dot" cx="76"  cy="44" r="4"/>
  <circle class="s-dot" cx="136" cy="44" r="4"/>
  <circle class="s-dot" cx="244" cy="44" r="4"/>
  <text class="s-lab" x="76"  y="30" text-anchor="middle">grep</text>
  <text class="s-lab" x="136" y="30" text-anchor="middle">linter</text>
  <text class="s-lab" x="244" y="30" text-anchor="middle">agent</text>
  <text class="s-pole" x="40"  y="72" text-anchor="start">Manual</text>
  <text class="s-pole" x="280" y="72" text-anchor="end">Autonomous</text>
</svg>
```

### Pyramid
- *Argues:* each tier is supported by the larger tier beneath it.
- *Honest when:* nested levels where lower = more numerous/foundational, and band **area ∝ count**.
- *Lie:* equal-height bands for unequal counts (or any non-nested data) — then the area encodes nothing and you've drawn a colored list with a slope.
- *Build with:* the area-proportional band recipe below.

Honest only when band **area** is proportional to count. For a triangle of height `H` and apex at
the top, the area above a horizontal cut scales as `(d/H)²`, so a cut holding cumulative area
fraction `f` sits at `d = H·√f`. With counts 5 / 25 / 70 (cumulative 0.05 / 0.30 / 1.00) and
`H = 180`, the cuts land at `√0.05·180 ≈ 40` and `√0.30·180 ≈ 99` below the apex. Half-width at
depth `d` is `120·d/180`. Those numbers are baked into the polygons below — the bands' areas are
5 : 25 : 70 by construction, not by eye.

```xml
<svg xmlns="http://www.w3.org/2000/svg" id="fig-1" viewBox="0 0 320 240" role="img"
     aria-label="An honest org pyramid: tier AREAS are proportional to headcount (5 leaders, 25 managers, 70 individual contributors), so the wide base correctly dominates the picture.">
  <style>
    /* neutral ramp derived from one token — no hand-picked grays */
    #fig-1 .p-t1{fill:color-mix(in srgb, var(--muted) 28%, var(--surface));stroke:var(--muted);stroke-width:1}
    #fig-1 .p-t2{fill:color-mix(in srgb, var(--muted) 52%, var(--surface));stroke:var(--muted);stroke-width:1}
    #fig-1 .p-t3{fill:color-mix(in srgb, var(--muted) 78%, var(--surface));stroke:var(--muted);stroke-width:1}
    #fig-1 .p-lab {font:600 12px var(--font-body);fill:var(--text)}
    #fig-1 .p-lead{stroke:var(--muted);stroke-width:1}
  </style>
  <!-- apex (160,20); base from (40,200) to (280,200) -->
  <polygon class="p-t1" points="160,20 187,60 133,60"/>
  <polygon class="p-t2" points="133,60 187,60 226,119 94,119"/>
  <polygon class="p-t3" points="94,119 226,119 280,200 40,200"/>
  <!-- direct labels: in-band where it fits, leader line for the tiny apex -->
  <line  class="p-lead" x1="174" y1="40" x2="206" y2="40"/>
  <text  class="p-lab"  x="210" y="44" text-anchor="start">Leaders &#183; 5</text>
  <text  class="p-lab"  x="160" y="94"  text-anchor="middle">Managers &#183; 25</text>
  <text  class="p-lab"  x="160" y="164" text-anchor="middle">Contributors &#183; 70</text>
</svg>
```

### Heat-grid
- *Argues:* one quantity varies across two categorical axes; intensity shows where it concentrates.
- *Honest when:* every cell is the **same** measure on one comparable scale, encoded by a single sequential ramp.
- *Lie:* a rainbow or diverging ramp for sequential data (S8, `references/svg-refine.md`), or cells carrying incomparable units side by side.
- *Build with:* a grid of `<rect>`s, fill-opacity ∝ value over one accent, row/column labels.

### Swimlane
- *Argues:* process steps belong to distinct actors; the handoffs are the lane crossings.
- *Honest when:* a sequence partitioned by responsible party, where crossing a lane is a real handoff.
- *Lie:* lanes when everything happens in one lane (it's just a sequence), or lane assignments that are arbitrary rather than ownership.
- *Build with:* horizontal lane `<rect>`s + step nodes + arrowheads (Semantic arrowheads, S5 in this file). Lanes that hold nine or more steps are split into the claims they hold or given as a nested list (S1, Gate 2).

**Rule of thumb:** if the shape's precondition doesn't hold for your data, the shape is the wrong
choice, not a labelling problem you can write around. Switch shapes (or drop to a sentence, a list
or a table in the text), then let the check and the look at the preview (S7, `svg-repair.md`) catch
what the math didn't.

---

## Copy-paste solved-arithmetic primitives (the math pre-solved)

These are small bespoke visuals reduced to drop-in recipes: no library, no build step, and the
**arithmetic already worked out** so the model emits coordinates instead of guessing arc flags or
inverting a y-axis. Each one is token-driven (light and dark for free, per S6), flat-filled (no
gradient), semantically coloured, and drawn as the figure file of S0 (`svg-figures.md`, "The canonical
unit"): copy that skeleton and change only the geometry inside it. The caption is the mark's sentence,
in the text, and the same sentence is the `aria-label`. (The before-after **Gap primitive** and the
**Semantic arrowheads** primitive come first, under S5 below: they are near-universal.)

Shared house rules for everything below:
- **`role="img"` + an `aria-label` that is the mark's sentence and asserts the takeaway**, never "a chart". Double every colour with a label, dash, or shape: hue alone fails for ~8% of readers and in greyscale print.
- **Semantic fills from the tokens (`assets/tokens.css`, S6), never raw hexes**: pass `var(--ok)` (zone/line/ink renditions per S6); fail `var(--error)`; risk `var(--warn)`; baseline `var(--muted)`; tracks `var(--bg)`; hairlines `var(--border)`; non-semantic emphasis `var(--info)`: keep the valence hues for verdicts only, so green always means pass (S6 accent rule). Put token colours in `style="…"` (small figures) or in-`<defs>` classes (repeated marks), each selector starting with `#fig-N`. No violet/fuchsia, no gradient.
- **Start every id with the figure's own id** (`fig-N-`, for example `fig-2-arrow`). Duplicate ids across SVGs on one page silently collide and `url(#id)` resolves to the *first* match.
- Name no font family in `<text>`: use `var(--font-mono)` for code and numbers and let labels take the default, `var(--font-body)`. A typed font family is a finding.

**Gutter slots (label allocation for dense figures).** When labels outnumber the space next to
their marks (ledger brackets, timeline ticks, phase bands), don't nudge — reserve a gutter band
above and/or below the figure band and *allocate slots*: sort the labeled marks by `x`, assign
labels to slots left-to-right (alternating above/below when one band is full), and connect
mark→label with a short leader line (the Pyramid above shows the leader idiom). Slot pitch = widest
label estimate (S4 §4 coefficients) + `GAP`, so collisions are impossible by construction:

```js
const SLOT_W = Math.max(...labels.map(s => s.length)) * PER_CHAR + GAP;  // one pitch fits the widest
const slotX  = i => PAD + i * SLOT_W;                                    // slot i, left-to-right
const band   = i => (i % 2 === 0 ? GUTTER_TOP_Y : GUTTER_BOT_Y);         // alternate when crowded
// leader: <line x1="${markX}" y1="${axisY}" x2="${slotX(i) + SLOT_W/2}" y2="${band(i)}" …/>
```

Without slots, the labels of events that share one point (three events at `t=0` on a timeline) pile
onto one cluster, overprinting the markers and each other: the exact shape this primitive eliminates.

### S5 · Near-universal primitives: the Gap + Semantic arrowheads

The before-after **Gap** and the **Semantic arrowheads** primitives come first: nearly every text with figures reaches for one or both. The rest of the solved-arithmetic catalog (**threshold meter, filled track, ring / arc gauge, inline sparkline, slopegraph, grouped-bar value labels, texture / hatch fill**) follows them, and the **gutter-slot** label-allocation recipe precedes them; grep the primitive's `###` heading. Both primitives below share the usual house rules: token-driven fills (S6, never raw hexes), the figure file of S0, `role="img"` + an `aria-label` that is the mark's sentence and states the finding, and ids that start with `fig-N-` so `url(#id)` never collides.

---
### Before / after "Gap" primitive

The dashed-divider metaphor: two semantically filled blocks split by a dashed `<line>`, with the **gap itself annotated** so the whitespace carries the delta. Annotate it only with a number the text states: a delta the text does not give is a composed label. Use this when the point is the change between two states; when the two sides are prose rather than a magnitude, give them as a table in the text.

This is the one primitive worked **straight from the S4 constants header** — derive, then emit, so the literals below trace back to named constants instead of being typed:

```js
// S4 §2 geometry-constants header, instantiated for this figure:
const W = 320, H = 120, PAD = 16, GAP = 48;
const COL  = (W - 2 * PAD - GAP) / 2;     // 120 — each block
const colX = i => PAD + i * (COL + GAP);  // → 16, 184  (the two translate() x's below)
const mid  = colX(0) + COL + GAP / 2;     // 160 — the dashed divider, centered in the gap
// S4 §4: "60%" at 22px is about 3 × 22 × 0.6 = 40 wide, well inside the 120-wide block, so neither numeral clips.
```

```xml
<!-- block x's (16, 184) and divider x (160) are emitted from colX()/mid above, not typed -->
<svg xmlns="http://www.w3.org/2000/svg" id="fig-1" viewBox="0 0 320 120" role="img"
     aria-label="Coverage went from 60% before to 92% after — a 32-point gain.">
  <!-- before: the neutral block (S6: a state before is muted, never the error red, unless the text calls it a failure) -->
  <g transform="translate(16,28)">
    <rect width="120" height="64" rx="8" style="fill:var(--muted-zone); stroke:var(--muted-line)"/>
    <!-- numeral and its word are ONE label: one <text>, the word a tspan with its own x (S4 §8) -->
    <text x="60" y="30" text-anchor="middle" font-size="22" font-weight="700"
          style="fill:var(--muted-ink);font-variant-numeric:tabular-nums">60%<tspan
          x="60" dy="20" font-size="12" font-weight="400">before</tspan></text>
  </g>
  <!-- the gap: dashed divider + delta label -->
  <line x1="160" y1="20" x2="160" y2="100" style="stroke:var(--muted-line)" stroke-dasharray="4 4"/>
  <text x="160" y="16" text-anchor="middle" font-size="12" font-weight="700" style="fill:var(--ok-ink)">+32 pts</text>
  <!-- after: ok-tinted block -->
  <g transform="translate(184,28)">
    <rect width="120" height="64" rx="8" style="fill:var(--ok-zone); stroke:var(--ok-line)"/>
    <!-- numeral and its word are ONE label: one <text>, the word a tspan with its own x (S4 §8) -->
    <text x="60" y="30" text-anchor="middle" font-size="22" font-weight="700"
          style="fill:var(--ok-ink);font-variant-numeric:tabular-nums">92%<tspan
          x="60" dy="20" font-size="12" font-weight="400">after</tspan></text>
  </g>
</svg>
```

---

### Semantic arrowheads

Two routes. A small `<defs>` **marker vocabulary** — arrow / dot / diamond — applied with `marker-end`, where the *shape encodes the relation* (filled arrow = causes/flows-to, dot = endpoint/attaches, diamond = aggregates/composes):

```xml
<defs>
  <marker id="fig-1-arrow" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0 0 L10 5 L0 10 z" style="fill:var(--muted)"/>
  </marker>
  <marker id="fig-1-dot" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6">
    <circle cx="5" cy="5" r="4" style="fill:var(--muted)"/>
  </marker>
  <marker id="fig-1-diamond" viewBox="0 0 10 10" refX="5" refY="5"
          markerWidth="9" markerHeight="9" orient="auto">
    <path d="M5 0 L10 5 L5 10 L0 5 z" style="fill:var(--muted)"/>
  </marker>
</defs>
<line x1="20" y1="20" x2="120" y2="20" style="stroke:var(--muted)" stroke-width="1.5" marker-end="url(#fig-1-arrow)"/>
```

Or, for **maximum portability** (no `<marker>`, no font dependency, renders identically anywhere it's pasted), draw the head as an inline `<path>` at the line's end. **Open vs filled is itself semantic** — open = weak/optional link, filled = hard/required:

```xml
<!-- line ending at (120,20), pointing right -->
<line x1="20" y1="20" x2="120" y2="20" style="stroke:var(--muted)" stroke-width="1.5"/>
<path d="M120 20 L112 16 L112 24 Z" style="fill:var(--muted)"/>                          <!-- filled -->
<path d="M112 16 L120 20 L112 24" fill="none" style="stroke:var(--muted)" stroke-width="1.5"/> <!-- open -->
```

The examples above draw the neutral edge, `var(--muted)` (S6). **The head is the SAME colour as its shaft: a marker is never an emphasis slot.** Define one
marker per edge colour (the S0 pattern: `fig-1-ok` green, `fig-1-bad` red) or use
`fill="context-stroke"` inside the marker so one definition inherits every edge's stroke. A blue
head on a grey or green edge reads as a third, unexplained encoding; the usual cause is a single
`--info` marker reused across semantically different edges. The S6 accent rule's `--info` slot covers
*standalone pointer glyphs*, never the markers of meaning-carrying edges.

Marker `refX`/`orient`/`markerUnits` pitfalls (heads vanishing on thin lines, `marker-mid` not firing on `<line>`) are catalogued in the PATTERN→FIX catalog (**`references/svg-repair.md`**) — reach for the self-contained `<path>` head whenever portability matters more than reuse.

---

### Threshold meter (a value against a limit)

Tracks on **one scale** with the limit drawn across them as a rule: the claim is on which side of the rule each value ends. Map a value to `x = X0 + v / MAX × TRACK`; the rule sits at the limit's own `x`, so the distance from a bar's end to the rule is the margin, drawn to scale. Colour says the verdict and the rule says it again: a bar that crosses is the failing tone, one that stops short the passing tone.

```xml
<!-- scale 0..700 ms on a 320-wide track from x=40: 620 → 323.4, 410 → 227.4, the limit 500 → 268.6 -->
<svg xmlns="http://www.w3.org/2000/svg" id="fig-1" viewBox="0 0 400 140" role="img"
     aria-label="Before the change the p95 was 620 ms, over the limit of 500 ms, and after it 410 ms, under the limit.">
  <defs>
    <style>
      #fig-1 .lbl   { font-size: 13px; }
      #fig-1 .track { fill: var(--bg); stroke: var(--muted-line); }
      #fig-1 .rule  { stroke: var(--muted); stroke-width: 1.5; stroke-dasharray: 4 4; }
    </style>
  </defs>
  <text class="lbl" x="40" y="28">before · 620 ms</text>
  <rect class="track" x="40" y="36" width="320" height="14" rx="3"/>
  <rect x="40" y="36" width="283.4" height="14" rx="3" data-value="620" style="fill:var(--error)"/>
  <text class="lbl" x="40" y="80">after · 410 ms</text>
  <rect class="track" x="40" y="88" width="320" height="14" rx="3"/>
  <rect x="40" y="88" width="187.4" height="14" rx="3" data-value="410" style="fill:var(--ok)"/>
  <!-- the limit: one rule through both tracks, its label under it -->
  <line class="rule" x1="268.6" y1="30" x2="268.6" y2="110" data-value="500"/>
  <text class="lbl" x="268.6" y="128" text-anchor="middle" style="fill:var(--muted-ink)">limit 500 ms</text>
</svg>
```

Each bar and the rule carry their number as `data-value`, so the check compares the three lengths with the three numbers (S0). The scale starts at zero (S8 §5: a cut baseline exaggerates the margin). With one value only, draw one track; with a limit that must be reached, not kept under, the tones swap and the geometry stays.

### Filled track (a share of a whole)

One track for the whole and one fill for the share: `fill width = share / whole × TRACK`. Length is read more exactly than an arc, so prefer it to the ring when the figure has room for a line of text above the bar.

```xml
<!-- 350 of 500 on a 320-wide track: 350 / 500 × 320 = 224 -->
<svg xmlns="http://www.w3.org/2000/svg" id="fig-1" viewBox="0 0 400 76" role="img"
     aria-label="350 GB of the disk's 500 GB is used.">
  <text x="40" y="28" font-size="13">350 of 500 GB used</text>
  <rect x="40" y="38" width="320" height="16" rx="3" style="fill:var(--bg); stroke:var(--muted-line)"/>
  <rect x="40" y="38" width="224" height="16" rx="3" data-value="350" data-of="500" style="fill:var(--info)"/>
</svg>
```

The fill is `--info`, not a verdict hue: a share is neither good nor bad until the text says so. Several shares of different wholes get one track each, all of one length, stacked.

### Ring / arc gauge from one number

One `<circle fill="none">` with `stroke-dasharray` set to `[shown, total]`. The dash math is the whole trick: the visible stroke length equals `pct × circumference`, so the model never reasons about angles or arc flags.

**Legitimate vs. slop — read with S8 §5 (`references/svg-refine.md`).** This earns its place *only* as a single **part-of-whole** proportion ("72% covered", "3 of 8"), where the **filled arc length** encodes the value. It is **not** the dashboard speedometer the S8 §5 anti-pattern table rejects: that one spends a half-circle of ink on a lone scalar with no comparison and leans on *angle*, the weak channel. Ring = a proportion read off arc length; speedometer = a naked number on a dial — ship the first, never the second.

```
C = 2 × π × r       // r = 52  →  C = 326.73
shown = pct × C     // pct = 0.72  →  235.24
dasharray = "235.24 326.73"
rotate(-90 cx cy)   // move the start from 3 o'clock to 12 o'clock
```

```xml
<svg xmlns="http://www.w3.org/2000/svg" id="fig-1" viewBox="0 0 120 120" role="img"
     aria-label="Eval coverage is 72%, up from the 60% baseline.">
  <!-- circle-as-arc: cx,cy is the center of a top-left 104×104 box (S4 §1 stated exception) -->
  <!-- track: full ring, neutral -->
  <circle cx="60" cy="60" r="52" fill="none" style="stroke:var(--border)" stroke-width="12"/>
  <!-- value: 72% of C=326.73 → 235.24 shown. linecap="butt" so the visible arc
       length equals pct·C exactly — round caps would add stroke-width to the arc. -->
  <circle cx="60" cy="60" r="52" fill="none" style="stroke:var(--ok)" stroke-width="12"
          data-value="72" data-of="100" stroke-linecap="butt" stroke-dasharray="235.24 326.73"
          transform="rotate(-90 60 60)"/>
  <text x="60" y="60" text-anchor="middle" font-size="26" font-weight="700"
        style="fill:var(--text);font-variant-numeric:tabular-nums">72%<tspan
        x="60" dy="20" font-size="12" font-weight="400" style="fill:var(--muted)">coverage</tspan></text>
</svg>
```

**Round-cap caveat (honesty):** `stroke-linecap="round"` adds a semicircular cap of radius `stroke-width/2` at each end — here ~12px ≈ +3.7% of `C`, so a stated 72% renders as ~76%. For an exact proportional read keep `stroke-linecap="butt"` (as above). If you want round caps for looks, compensate by subtracting the stroke width from the shown dash: `shown = pct·C − strokeWidth` (235.24 − 12 = 223.24 → `stroke-dasharray="223.24 326.73"`).

**Skip the circumference entirely** by setting `pathLength="100"` on the circle — then `stroke-dasharray="72 100"` reads as a literal percent and `r` can change without recomputing anything.

**Quarter-arc wedge** (a filled sector, when you want a slice not a ring). Build it `M center L startEdge A r r 0 0 1 endEdge Z`; both arc flags are `0 1` for any sweep ≤ 180° going clockwise, so they never need thought. Place an arc label at the **sector centroid radius `d = 4r·sin(θ/2)/(3θ)`** along the wedge's bisector. (The familiar `4r/(3π)` is the *semicircle* centroid; using it on a narrower sector pulls the label too far toward the center. For a quarter, θ = π/2, so `d = 0.6·r`.)

```xml
<!-- top→right quarter of a circle, center (60,60) = top-left box (8,8) + r=52 (S4 §1 arc exception) -->
<svg xmlns="http://www.w3.org/2000/svg" id="fig-1" viewBox="0 0 120 120" role="img"
     aria-label="One quarter of runs are still pending.">
  <path d="M60 60 L60 8 A 52 52 0 0 1 112 60 Z" style="fill:var(--info)"/>
  <!-- bisector −45°, d = 0.6·52 ≈ 31.2 → (60 + 31.2·cos45, 60 − 31.2·sin45) ≈ (82, 38) -->
  <!-- on-fill text: the bg token reads on an info fill in both themes (S6 contrast floors) -->
  <text x="82" y="38" text-anchor="middle" font-size="12" style="fill:var(--bg)">25%</text>
</svg>
```

**When the empty state is the claim ("0 of 20"), the `--border` track is too faint to carry it** (about 1.2:1 against the ground): draw the empty track in `var(--muted-line)` or prefer a row of cells, where an empty cell has an outline of its own.

Numbers that go with the gauge's centre number belong in the text, as a sentence or a table, rather than rebuilt as numerals in SVG.

### Inline sparkline (semantic)

The bare polyline is placed with the point-scaling math below. What this section adds is the **semantic layer**: exactly three `r=1.5` dots naming the min, max, and current value, the only three points a reader acts on. The same scaling places the dots, so the dot coordinates trace back to it.

```
x_i = i/(n−1) × w                        // point-scaling
y_i = (h−2) − (v−min)/range × (h−4)      // −2/−4 keeps the stroke off the edges; y inverted
```

```xml
<!-- data [8,5,11,7,14,9,6,12]  n=8  min=5  max=14  range=9  w=100  h=30 -->
<svg xmlns="http://www.w3.org/2000/svg" id="fig-1" viewBox="0 0 100 30" role="img"
     aria-label="Pass rate trended up to 12, peaking at 14, from a low of 5.">
  <polyline fill="none" style="stroke:var(--muted)" stroke-width="1.5"
            stroke-linecap="round" stroke-linejoin="round"
            points="0,19.33 14.29,28 28.57,10.67 42.86,22.22 57.14,2 71.43,16.44 85.71,25.11 100,7.78"/>
  <!-- three dots: cx,cy are x_i,y_i above (S4 §1 plotted-point exception), pulled in by r so they clear the viewBox edge -->
  <circle cx="14.29" cy="28"   r="1.5" style="fill:var(--error)"/> <!-- min   -->
  <circle cx="57.14" cy="2"    r="1.5" style="fill:var(--ok)"/> <!-- max   -->
  <circle cx="98.5"  cy="7.78" r="1.5" style="fill:var(--text)"/> <!-- endpoint: x pulled to 98.5 so the marker clears the right edge -->
</svg>
```

The dots are the entire color budget — keep the line neutral gray so the three markers carry the meaning.

### Slopegraph (before / after on one shared scale)

Two label columns, **one shared scale**, one `<line>` per category from start→end. No axes, no gridlines — the slope *is* the chart, encoding magnitude and direction at once. Highlight the one or two load-bearing categories with the accent; ghost the rest in gray.

```
y(v) = top + (max−v)/(max−min) × (bottom−top)   // here 0–100 → y∈[20,180]: y = 180 − 1.6·v
```

```xml
<svg xmlns="http://www.w3.org/2000/svg" id="fig-1" viewBox="0 0 360 200" role="img"
     aria-label="After the fix, coverage jumped 60→92 while latency, flake rate and cost barely moved.">
  <text x="120" y="14" text-anchor="middle" font-size="12" font-weight="700" style="fill:var(--muted)">BEFORE</text>
  <text x="240" y="14" text-anchor="middle" font-size="12" font-weight="700" style="fill:var(--muted)">AFTER</text>

  <!-- ghosted categories: one hue, dropped opacity (S8 §3) — never a second color -->
  <g style="stroke:var(--muted); fill:var(--muted)" opacity="0.5" stroke-width="1.5" font-size="12">
    <line x1="120" y1="52"  x2="240" y2="92"/>   <!-- latency 80→55 -->
    <line x1="120" y1="132" x2="240" y2="160.8"/><!-- flake   30→12 -->
    <line x1="120" y1="108" x2="240" y2="112.8"/><!-- cost    45→42 -->
    <text x="112" y="55"  text-anchor="end">latency 80</text>
    <text x="112" y="135" text-anchor="end">flake 30</text>
    <text x="112" y="111" text-anchor="end">cost 45</text>
    <text x="248" y="95">55</text><text x="248" y="163.8">12</text><text x="248" y="115.8">42</text>
  </g>

  <!-- highlighted category: coverage 60→92, y = 84 → 32.8; rose = positive → the ok token -->
  <line x1="120" y1="84" x2="240" y2="32.8" style="stroke:var(--ok)" stroke-width="2.5"/>
  <!-- endpoint dots: cx,cy are the line ends, y from y(v) above (S4 §1 plotted-point exception) -->
  <circle cx="120" cy="84" r="2.5" style="fill:var(--ok)"/><circle cx="240" cy="32.8" r="2.5" style="fill:var(--ok)"/>
  <text x="112" y="87"   text-anchor="end" font-size="12" font-weight="700" style="fill:var(--ok-ink)">coverage 60</text>
  <text x="248" y="35.8" font-size="12" font-weight="700" style="fill:var(--ok-ink)">92</text>
</svg>
```

### Grouped-bar value labels

The value label above a bar is usually the claim itself, and it collides exactly where the claim
lives, on the shortest bar of a hostile scale (a "6 ms" label pushed off its tiny bar into the
neighbouring "41 ms"). The recipe is mechanical:

- **Each label anchors to ITS OWN bar center**: `x = bar.x + bar.w/2`, `text-anchor="middle"`,
  `y = bar.y - 6`. Never nudge a label sideways off its bar — a sideways label orphans the bar it
  belongs to and collides with the neighbor's.
- **Value and unit are ONE `<text>`** — `26 ms`, optionally a smaller-`font-size` `<tspan>` for
  the unit sharing the same baseline (S4 §8). Sibling `<text>` fragments ("6" + "ms") are two
  independent guesses about spacing; the check reports them as `split-label`.
- **When two labels in one group would come within 4px horizontally, stagger them vertically** by
  one line-height — the taller bar's label one step higher — instead of shifting either sideways.
- **A bar shorter than one line-height still gets its label ABOVE the bar**, never inside it,
  never beside it.

```js
// label y for bar i: base slot above the bar; +LINE_H stagger when crowded
const labY = (bar, crowded) => bar.y - 6 - (crowded ? LINE_H : 0);
```

### Texture / hatch fill as a second channel

Define a tileable `<pattern patternUnits="userSpaceOnUse">` and reference it with `fill="url(#id)"` so state is encoded **redundantly with color** — solid green = pass, gray crosshatch = not-yet-run. The texture survives grayscale print and color-blindness, where the hue alone would collapse.

```xml
<svg xmlns="http://www.w3.org/2000/svg" id="fig-1" viewBox="0 0 240 60" role="img"
     aria-label="Three checks pass; two have not run yet.">
  <defs>
    <pattern id="fig-1-cross" width="6" height="6" patternUnits="userSpaceOnUse">
      <rect width="6" height="6" style="fill:var(--bg)"/>
      <!-- both / and \ strokes → a true crosshatch (matches the name and the prose) -->
      <path d="M0 0 L6 6 M-1 5 L1 7 M5 -1 L7 1 M6 0 L0 6 M7 5 L5 7 M1 -1 L-1 1"
            style="stroke:var(--muted)" stroke-width="1"/>
    </pattern>
  </defs>
  <!-- pass: solid + checkmark -->
  <rect x="8"  y="14" width="100" height="32" rx="8" style="fill:var(--ok-zone); stroke:var(--ok-line)"/>
  <path d="M22 30 l5 6 9-12" fill="none" style="stroke:var(--ok)" stroke-width="2.4"
        stroke-linecap="round" stroke-linejoin="round"/>
  <text x="46" y="35" font-size="12" font-weight="700" style="fill:var(--ok-ink)">pass ×3</text>
  <!-- not-yet-run: crosshatch + dashed border -->
  <rect x="132" y="14" width="100" height="32" rx="8" fill="url(#fig-1-cross)"
        style="stroke:var(--border)" stroke-dasharray="3 3"/>
  <text x="150" y="35" font-size="12" font-weight="700" style="fill:var(--muted)">pending ×2</text>
</svg>
```

For a diagonal single-hatch instead of a crosshatch, keep one stroke per tile and add `patternTransform="rotate(45)"`. Keep the tile small (4–8px) so it reads as texture, not stripes.
