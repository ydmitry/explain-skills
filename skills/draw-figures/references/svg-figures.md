> **Use when** a text has a `Figure:` mark to draw. The first of the drawing references: read it before the
> first `<svg>`, from the top down to the heading `## ON DEMAND`, then `svg-color.md` and `svg-geometry.md`
> as their headers say.
>
> **In this file:** S3 the six families of shapes and the table from a brief's shape name to its recipe ·
> S0 the figure file and the skeleton to copy · S2 the brief: write the claim before any geometry ·
> ON DEMAND, read only when it is unclear whether a claim gets a drawn figure: S1 the decision gate.
>
> **Siblings**, in reading order: `svg-color.md` (S6: the tokens, colour by meaning, accessibility) ·
> `svg-geometry.md` (S4: derive every coordinate) · `svg-shapes.md` (the catalog of shapes and the S5
> primitives, one `###` section each) · `svg-repair.md` (S7: what the check reports and its fix, on a
> finding) · `svg-refine.md` (S8–S10: taste, when a figure passes the check and still looks generic).

# Hand-drawn figures: one SVG for one claim

Hand-drawn means placed by hand, every coordinate exact. It never means a sketchy line or a handwriting font: both make a figure harder to read accurately and less believed.

## S3 · The vocabulary: named shapes with honesty filters

Pick the figure from a finite catalog instead of inventing geometry per claim. Every entry carries an **epistemic precondition** (the claim it can honestly hold) and an **anti-prescription** (the misuse that makes it lie), so choosing the shape *is* the first honesty gate. Start from the question the claim answers; the family routes you to the shapes.

### The index: six information-structure families

| Family | The question it answers | Reach for |
|---|---|---|
| **List** | "What are the members of this set, and do they overlap?" | Usually *no geometry*: a list or a table in the text. Only set **overlap** earns a shape → Venn. |
| **Sequence** | "What are the ordered steps?" | One-shot → pipeline / **swimlane**; repeating → **cycle**; attrition → **phase/funnel**. |
| **Compare** | "How do the options differ on shared terms?" | Two binary axes → **2×2 matrix**; one axis → **spectrum**; 2–3 items on a shared scale → **comparison pair**. |
| **Hierarchy** | "What nests in, or rests on, what?" | Abstraction/dependency → **layered stack**; count/foundation tiers → **pyramid**. |
| **Relation** | "How do these connect or influence each other?" | Directed cause → **causal DAG**; set overlap → **Venn**. |
| **Chart** | "What quantity should the reader read off?" | Value across two categorical axes → **heat-grid**; trend / magnitude+direction → sparkline / slopegraph; single proportion → ring gauge. |

**The catalog and its worked geometry live in `svg-shapes.md`.** Once the index names your shape, read that shape's `###` section there and only that section: the honesty filters, and the pre-solved arithmetic for the three that lie most easily (**2×2 matrix**, **Pyramid**, **Spectrum**). `grep -n '^##' references/svg-shapes.md` prints every heading with its line, so one ranged read takes a section. If no entry fits, the claim is probably not spatial: leave it as a sentence, a list or a table, not a decorated list pretending to be a diagram.

### From the brief's shape name to its recipe

The skill's list of shapes names each shaped claim (`SKILL.md`, "Which claims get a figure"), and the brief's `shape:` line holds that name. Map it to the `###` heading of `svg-shapes.md` to read, or, when no catalog entry fits, build the figure straight from S4 geometry:

| Shape name in the brief | `svg-shapes.md` heading to read, or the build path |
|---|---|
| `n-of-m fill` | `Ring / arc gauge from one number` (part-of-whole, "3 of 8") |
| `filled track` | `Filled track (a share of a whole)` |
| `pie` | `Pie (a whole split into a few parts)` |
| `swimlane` | `Swimlane`, with its example |
| `line of time` | `Line of time (dates, and a span between them)` |
| `threshold meter` | `Threshold meter (a value against a limit)` |
| `zones-with-wall` | *no catalog entry: build from S4 and the S6 zone tints* (tint **plus** a boundary at each end) |
| `paired diff` | `Comparison pair` (or the Gap primitive, S5: `Before / after "Gap" primitive`) |
| `the Gap` | `Before / after "Gap" primitive` (S5) |
| `labeled anatomy` | *no catalog entry: build from S4* (parts + direct labels / leader lines) |
| `spectrum` | `Spectrum` |
| `2x2` | `2×2 matrix` |
| `trend line` | `Inline sparkline (semantic)` (or `Slopegraph (before / after on one shared scale)` for before → after) |
| `small flow` | `Swimlane` when lane-partitioned; else *no catalog entry: build from S4 §9* ports and edges + Semantic arrowheads (S5) |
| `one-off metaphor` | *no catalog entry: bespoke by definition, build from S4* |

**Edge direction** (`small flow`, `causal DAG`, `swimlane`): FROM is the subject of the source sentence's verb; a store (cache, database, queue) is never FROM unless the source says it calls something; "reads X, writes Y" is two edges from one actor, not a chain.

---

## S0 · The figure file

This reference does one thing: **hand-draw a small, semantically coloured, accessible SVG for a single claim.** A graph tool draws nodes and edges; this draws *the idea itself*. Before you draw one, read this file down to its ON DEMAND tail, then `svg-color.md` and `svg-geometry.md` as their headers say, and your shape's `###` section of `svg-shapes.md`.

### The canonical unit

Every figure is one file, `fig-N.svg`, in the text's figures folder: one `<svg>` for the Nth `Figure:` mark of the text. The mark's sentence is the caption, and it stays in the text. Copy this skeleton and replace the geometry inside:

```xml
<!-- viewBox, no width/height; role="img"; the aria-label IS the mark's sentence, word for word;
     the id is the figure's id, and every other id starts with it -->
<svg xmlns="http://www.w3.org/2000/svg" id="fig-1" viewBox="0 0 720 200" role="img"
     aria-label="A kebab-case skill name with a real description passes the frontmatter check, while an underscored name with a TODO description is rejected before it can register.">
  <!-- edges: good.B → pass.T | bad.B → fail.T -->
  <defs>
    <!-- colours come ONLY from the tokens (S6); every selector starts with the figure's own id,
         so two figures on one page can both have a .card and never touch each other -->
    <style>
      #fig-1 .mono  { font-family: var(--font-mono); font-size: 12px; }
      #fig-1 .head  { font-size: 12px; font-weight: 700; letter-spacing: .04em; }
      #fig-1 .card  { fill: var(--bg); stroke: var(--border); }
      #fig-1 .ok-i  { fill: var(--ok-ink); }
      #fig-1 .err-i { fill: var(--error-ink); }
      #fig-1 .ok-z  { fill: var(--ok-zone); stroke: var(--ok-line); }
      #fig-1 .err-z { fill: var(--error-zone); stroke: var(--error-line); }
    </style>
    <marker id="fig-1-ok" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0 0 L10 5 L0 10 z" style="fill:var(--ok)"/>
    </marker>
    <marker id="fig-1-bad" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0 0 L10 5 L0 10 z" style="fill:var(--error)"/>
    </marker>
  </defs>

  <!-- dashed divider: decoration layer, drawn FIRST so it sits under the labels -->
  <line x1="360" y1="14" x2="360" y2="186" style="stroke:var(--muted-line)" stroke-dasharray="4 4"/>
  <text class="head ok-i"  x="20"  y="28">PASSES</text>
  <text class="head err-i" x="380" y="28">REJECTED</text>

  <!-- LEFT / pass -->
  <g transform="translate(20,44)">
    <rect class="card" data-name="good" width="320" height="56" rx="8"/>
    <text class="mono" x="14" y="24">name: fact-sheet-search</text>
    <text class="mono" x="14" y="44">description: Search the…</text>
  </g>
  <!-- arrow centred under the pass pill: pill spans x 20–94, centre = 20+37 = 57 -->
  <line x1="57" y1="100" x2="57" y2="124" style="stroke:var(--ok)" stroke-width="1.5" marker-end="url(#fig-1-ok)"/>
  <g transform="translate(20,126)">
    <rect class="ok-z" data-name="pass" width="74" height="24" rx="12"/>
    <path d="M12 12 l4 5 7-9" fill="none" style="stroke:var(--ok)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
    <text class="ok-i" x="30" y="17" font-size="12" font-weight="700">pass</text>
  </g>

  <!-- RIGHT / fail: mirror geometry, the failing valence, an X glyph as the second channel -->
  <g transform="translate(380,44)">
    <rect class="card" data-name="bad" width="320" height="56" rx="8"/>
    <text class="mono err-i" x="14" y="24">name: Fact_Sheet_Search</text>
    <text class="mono err-i" x="14" y="44">description: TODO</text>
  </g>
  <!-- arrow centred under the fail pill: pill spans x 380–450, centre = 380+35 = 415 -->
  <line x1="415" y1="100" x2="415" y2="124" style="stroke:var(--error)" stroke-width="1.5" marker-end="url(#fig-1-bad)"/>
  <g transform="translate(380,126)">
    <rect class="err-z" data-name="fail" width="70" height="24" rx="12"/>
    <path d="M11 8 l8 8 m0 -8 l-8 8" fill="none" style="stroke:var(--error)" stroke-width="2.4" stroke-linecap="round"/>
    <text class="err-i" x="27" y="17" font-size="12" font-weight="700">fail</text>
  </g>
</svg>
```

Every word in it (`PASSES`, `REJECTED`, `name:`, `TODO`, `pass`, `fail`) stands in the text it was drawn for or in its brief. `figures.py check` lists a word or a number that stands in neither.

### What the file holds and what it leaves out

| In the file you write | Left to `figures.py place` or the page |
|---|---|
| `xmlns`, `id="fig-N"`, a `viewBox`, `role="img"`, the `aria-label` | `width` and `height` (set from the `viewBox`: one unit is one CSS pixel) |
| one `<style>` whose every selector starts with `#fig-N` | the token block: the palette for a light and a dark screen |
| shapes that read `var(--token)`, ids that start with `fig-N-` | the frame: a `--surface` ground behind the figure |
| the edge manifest comment, when there are arrowed edges | the caption: the mark's sentence, in the text |

- **Text has a default.** A `<text>` with no class is set in `--font-body` and filled with `--text`: the token block gives a standalone file that default, and a page gives it too. Set only what differs.
- **The ground is `--surface`.** Draw no background rectangle. A card or a node that should stand out from the ground is filled with `--bg`.
- **No `<script>`, no `<foreignObject>`, no gradient, no link to another file or a web address.** A figure shown as an image runs none of them, and the check refuses each.
- **Valid XML.** The file is read alone, so `&` is `&amp;` and `<` is `&lt;` in a label, and every tag closes.

### A mark that draws a number carries the number

**Whatever encodes a value by its size says which value,** in an attribute the reader never sees. The check then compares the drawing with its numbers: a bar out of proportion is `value-mismatch`, and a number that stands in neither the text nor the brief is `value-not-in-text`.

| The mark | Write | The check compares |
|---|---|---|
| bars on one scale | `data-value="620"` on each `<rect>`; all of one thickness, starting from zero | each length with its value, against the longest bar |
| a limit across those bars, or across a share's track | `data-value="500"` on the `<line>` | its distance from where the bars, or the track, start |
| a share of a whole | `data-value="350" data-of="500"` on the fill `<rect>`, drawn over a track that starts with it | the fill's length with the track's |
| a ring filled to a share | `data-value="72" data-of="100"` on the `<circle>` with the `stroke-dasharray` | the dash with the full circle |
| a row of cells | `data-value="9" data-of="12"` on the `<g>`, and `data-on=""` on each cell that counts | the number of cells, and of cells with `data-on` |

Bars on a second, different scale in the same figure get `data-scale="name"`, the same name on each of them. A point on a line, a slope and an area carry no `data-value`: the check does not measure them, and the look at the picture does.

### The defining move

What makes this more than a generic diagram:

- **One bespoke figure per claim, not a node graph.** The shapes *are* the subject (a file, a check row, a verdict pill), drawn for this one idea. If you reach for boxes and arrows of generic nodes, the claim is probably a list or a small flow (S10).
- **Semantic fills carry the meaning, through the tokens.** Green (`var(--ok)`, ink `var(--ok-ink)`) = pass, red (`var(--error)`, ink `var(--error-ink)`) = fail, neutral ink for everything else. Colour is never decorative and never the *only* channel: the verdict is doubled with a check mark against an X glyph (S6).
- **A dashed before/after divider** splits the state the claim asserts from the state it rules out. It is decoration, so it is drawn before the labelled groups and sits underneath them.

### viewBox and restraint

- Use **`viewBox="0 0 W H"`, never a typed `width`/`height`**: one unit is one CSS pixel at full size, so 12-unit text is 12px text. The integer coordinate space keeps geometry deterministic (S4). A page shows a figure at that size or smaller, never larger.
- **Width 720 at most.** That is the width of a page's text column. A figure that needs less is drawn narrower. **On a phone a figure wider than about 400 units does not show whole:** a page shrinks it to four fifths and then scrolls it sideways in its frame. The check warns of such a figure (`wide-for-phone`), and the page check warns when a figure is cut off on a 390 px screen. A text that will be read on a phone gets figures 400 wide or less, with their bands stacked; say the width on the brief's `canvas:` line.
- **Token-driven, one calm emphasis over neutrals.** The only saturated hues are the semantic ones, and emphasis that carries no verdict uses `var(--info)` (see the S6 accent rule). No violet or fuchsia in any slot.
- **Static.** No SMIL (`<animate>`), no motion, no interaction.

### One grammar for all the figures of a text

A text with several figures stays cheap to read only when they share a grammar. So for a text with **three or more figures**: fix ONE contrast frame, one meaning for each colour, and one or two canvas widths, and use them in every figure, so the reader learns the grammar once. The brief's header holds these choices (`canvas:`, `palette:`). Anchor every figure to the concrete material it abstracts (a value, an excerpt, a file path that the text gives): a figure you cannot anchor stays a sentence.

---

## S2 · The brief: plan the claim before any SVG

A figure earns its weight only when its **structure carries meaning**. The failure mode: a model opens an `<svg>`, emits coordinates, and produces a decorated list, boxes that label text instead of arguing anything. The fix is a gate of two phases: no coordinates until the claim is written down.

### Phase 1: write the brief. Phase 2: make the SVG satisfy it.

Treat the brief as a **contract the drawing is checked against**, not as planning you keep in your head. `figures.py brief TEXT` writes `brief.md` beside the figure files, with a block for each mark and the mark's sentence as its `claim:`. Fill the rest of each block, and only then draw:

```markdown
## fig-3
claim: A field that quietly becomes optional is caught as drift.
shape: the Gap (before / after)
data: pass: `confirm: boolean`, matches the snapshot; drift: `confirm?: boolean`, was required (docs/snapshots.md:41)
constraints: pass on the left, drift on the right; the changed character is the one marked element
```

- **`claim:` is the mark's sentence.** The script copies it, and the check compares it with the mark and with the figure's `aria-label`. To change it, change the mark in the text.
- **`shape:`** is a name from the table in S3.
- **`data:` is load-bearing.** It lists every label, value and unit the figure shows, copied and never retyped from memory, with where each stands in parentheses: a line of the text, or a row of a `keep-sources` folder. What stands in parentheses is a pointer only: the check takes no label and no number from it, and does not look it up. A brief without a concrete example ("60% → 95%", `confirm?: boolean`) lets you draw a plausible diagram of nothing. Every number outside the parentheses counts as a value the figure must show, so write "the top row", not "row 1", when you describe the layout there.
- **`constraints:`** says what must and must not be shown: which side is which, which element is marked, what stays out.

**The data line is the list the check ticks.** Every number on it must be drawn, and every number and word drawn must stand in the text or in the block. A value you leave out "to reduce clutter" is a fidelity failure the reader cannot detect, which makes it worse than clutter. If an item really will not fit, the layout is wrong (resize, re-band, split the figure): the item is not optional.

**Decompose the unit from the arrangement.** Plan the *repeating cell* ("one test = a pass box with a green check, a fail box with a red cross") apart from the *arrangement* ("cells split left and right by a dashed divider"). Conflating them is how you end up with a uniform grid of identical cards: the cell got designed and the arrangement defaulted to "tile it".

### Pick the metaphor from the relationship, before any geometry

Before you choose shapes, name the **relationship or behaviour** in the idea and look up its metaphor. Geometry is the *last* decision, derived from the relationship, not the first.

| Relationship in the idea | Metaphor | Minimal structure |
|---|---|---|
| one → many | fan-out | one source, lines diverging to many targets |
| many → one | convergence | many lines merging into one target |
| A vs B | shared baseline | two marks measured on one common axis |
| before / after | **the Gap** | two states split by a dashed divider |
| cycle / feedback | ring | arcs sweeping around a circle, arrowed |
| input → transform → output | assembly line | left-to-right stages joined by arrows |
| separates into phases | break | stacked bands with deliberate gutters between them |
| fuzzy / overlapping sets | overlapping clouds | soft translucent regions that intersect |
| part of a whole / coverage | filled track / gauge | a value filling a fixed track |
| a whole split into a few parts | pie | slices of one disc, each with its number |

**Hard rule: each major concept of a text uses a DIFFERENT metaphor.** A text where every figure is the same row of cards has thrown away the one thing a drawn figure buys: that the *shape itself* is information. If three claims all want "the Gap", two of them are probably the same claim, or two of them should stay sentences.

A `shape: the Gap` brief renders as two states on a shared baseline, split by a dashed divider, with one arrow that crosses the gap to assert the movement. The load-bearing part of such a figure (the marker is the one of the S5 Semantic arrowheads, `svg-shapes.md`, in the colour of its shaft):

```xml
<svg xmlns="http://www.w3.org/2000/svg" id="fig-2" viewBox="0 0 720 220" role="img"
     aria-label="Test coverage rose from 60% before the fix to 95% after it.">
  <defs>
    <marker id="fig-2-rise" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0 0 L10 5 L0 10 z" style="fill:var(--muted)"/>
    </marker>
  </defs>
  <line x1="360" y1="36" x2="360" y2="184" style="stroke:var(--muted-line)" stroke-dasharray="4 4"/><!-- the Gap -->
  <rect x="130" y="98" width="70" height="72"  rx="4" data-value="60" style="fill:var(--muted)"/><!-- before: 60% -->
  <rect x="520" y="56" width="70" height="114" rx="4" data-value="95" style="fill:var(--ok)"/><!-- after: 95% -->
  <line x1="210" y1="92" x2="512" y2="60" style="stroke:var(--muted)" marker-end="url(#fig-2-rise)"/><!-- the movement -->
</svg>
```

Semantic fills only (`var(--muted)` for the state before, `var(--ok)` for the better state after), the marker has the `refX`/`orient` it needs, every coordinate sits inside the `720×220` viewBox, and the `aria-label` asserts the finding, not "a bar chart". For the *geometry* of these primitives (top-left anchoring, deriving every `x`/`y` from named constants, the gauge arithmetic) see S4; this section governs only *what* to draw and *why*.

### Two gates that kill chartjunk before a single coordinate

Apply both while the brief is still prose:

- **Isomorphism test.** Mentally delete *all* text from the figure. Does the structure alone still convey the idea? In the snippet above, two bars on a shared baseline with a rising arrow still say "it went up" with every label stripped. If deleting the text destroys the meaning, the geometry was decorative: **fix the layout, not the labels.** Bigger fonts and better wording cannot rescue a diagram whose structure says nothing.
- **Pre-flight test.** Ask: *if I removed the geometry entirely, would the reader lose information?* If the answer is no, **remove the mark and write a list or a table instead.** An SVG that survives being flattened to bullet points was never carrying its weight.

### The mark asserts the finding; one figure, one claim

The mark's sentence states the **claim**, not the medium or the variables: "A field that quietly becomes optional is caught as drift", never "diagram of snapshot validation" or "coverage over time". Mark the single load-bearing element directly (the rising arrow above), cap callouts at one to three, and prefer direct labels over a separate legend.

**One figure carries exactly one claim.** Three claims are three marks, three blocks of the brief and three metaphors, never one busy diagram. If you cannot state the claim in one sentence, you are drawing more than one picture.

---

## ON DEMAND: the long form of the decision (read below only when it is unclear whether a claim gets a drawn figure)

Everything past this line decides *whether* a claim gets a hand-drawn figure, not how to draw it. The two tests in `SKILL.md` already make that call for most claims, and a mark in the text means the call was made, so a routine read stops here.

## S1 · When to hand-draw and when to route away (the decision gate)

A hand-drawn SVG is the most expensive figure to get right and the easiest to get silently wrong: the model places coordinates it cannot see. Run every claim through this gate *before* drawing a single `<rect>`. The gate picks **which** claims get drawn, not whether the text gets any: route graphs and tables away, then draw every claim that passes, one figure per claim, sharing one contrast frame and one palette across the set.

### Gate 1: scale (the hard ceiling)

A figure that explains one claim almost never needs a thousand elements. If yours does, you are drawing data, not a concept: give the numbers as a table, split the claim into smaller ones, or leave the chart to a tool made for data. Hand-draw only under **about 1000 elements**.

### Gate 2: is it really a table, a list or a large graph? (route away)

Classify the claim's *shape* first.

- **Rows × columns of values or statuses** → a table in the text. A table is accessible, can be copied, and never clips.
- **A count, a status, a definition, a single number** → a sentence, with the number in bold when it is the point of its section. If deleting the geometry loses nothing, the geometry was decoration.
- **A node-and-edge graph of nine or more nodes** is rarely one claim. Split it into the claims it holds and draw those, or give it as a nested list. In a text that stays Markdown, a `mermaid` block draws a large graph quickly (`SKILL.md`, "A graph in a text that stays Markdown"); a page shows no Mermaid.
- **The same flow at eight nodes or fewer** → hand-draw it (the small flow, pipeline and swimlane vocabulary in S3 and `svg-shapes.md` S5): it always renders and needs nothing from the network.

### Gate 3: hand-draw only for meaning a table cannot carry

Reach for a drawn figure only when it must carry a meaning a table or a generic chart **cannot express**: a fill that encodes a valence (green = passing, red = failing), a deliberate *Gap* (a dashed divider whose whitespace **is** the claim), a partial fill that means "3 of 8", a threshold with its limit drawn, a trend, a position between two poles, a labelled anatomy, a one-off metaphor specific to this idea.

The test is isomorphism: *mentally delete every label. If the structure alone still argues the point, the geometry is load-bearing and earns a drawn figure. If only the labels carried meaning, write a table or a list instead.*

Here is the positive case: a before/after split where the dashed Gap and the fills do the arguing, not the text.

```xml
<svg xmlns="http://www.w3.org/2000/svg" id="fig-1" viewBox="0 0 320 120" role="img"
     aria-label="Before the fix 3 of 8 checks passed; after the fix all 8 pass.">
  <!-- the Gap: this dashed divider is the claim, not decoration -->
  <line x1="160" y1="12" x2="160" y2="108" style="stroke:var(--muted-line)" stroke-dasharray="4 4"/>
  <text x="80"  y="24" text-anchor="middle" font-size="12" style="fill:var(--muted)">Before</text>
  <text x="240" y="24" text-anchor="middle" font-size="12" style="fill:var(--muted)">After</text>
  <!-- before: track + 3/8 partial fill -> 3/8 * 112 = 42 -->
  <rect x="24" y="40" width="112" height="20" rx="4" style="fill:var(--bg); stroke:var(--border)"/>
  <rect x="24" y="40" width="42"  height="20" rx="4" style="fill:var(--error)"/>
  <text x="80" y="80" text-anchor="middle" font-size="12">3 / 8 pass</text>
  <!-- after: full fill, valence = passing -->
  <rect x="184" y="40" width="112" height="20" rx="4" style="fill:var(--ok)"/>
  <text x="240" y="80" text-anchor="middle" font-size="12">8 / 8 pass</text>
</svg>
```

A graph of nodes cannot say that: it has no "partial fill that means 3 of 8, coloured by valence, split by a meaningful gap". That is the line where hand-drawing pays for itself.

### Decision table

| The claim's shape is… | Give it as… | Where |
|---|---|---|
| a process flow, decision, hierarchy, sequence or lifecycle of nine or more nodes | the smaller claims it holds, or a nested list; a `mermaid` block in a text that stays Markdown | `SKILL.md` |
| the same shapes at eight nodes or fewer | **a drawn figure**: small flow / pipeline / swimlane | S3 here + `svg-shapes.md` (S5) |
| rows × columns of values or statuses | a table in the text | the text |
| a count, a status, one number | a sentence | the text |
| a meaning a table cannot carry: valence fills, the Gap, partial fills, a threshold, a trend, custom geometry | **a drawn figure** | this reference |

### One figure carries one claim

A drawn figure argues exactly one thing. If an idea has three claims ("coverage rose", "and latency held", "and cost fell"), that is three figures, not one crowded diagram. The claim is the mark's sentence and the `aria-label`; plan it in the brief before any geometry: the gate decides *whether* to draw and *what shape*, the claim decides *what the drawing must show*.
