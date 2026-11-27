> **Use when** a figure is drawn: read it down to the heading "House bans apply inside the figure" right after
> `svg-figures.md`, before the first `fill` or `stroke`; the rest (house bans, recolouring by class, ids,
> accessibility, contrast) when a finding of the check names it. The drawing agent of `figure-agent.md` reads it
> whole.
>
> **In this file:** the ground a figure stands on · S6: the tokens are the palette, the accent rule, the derived
> shades, house bans inside the figure, `currentColor` and recolouring by class, ids that start with the
> figure's id, accessibility (the label states the finding), never colour alone, contrast floors.
>
> **Siblings:** `svg-figures.md` (S0–S3, read first) · `svg-geometry.md` (S4, read next) · `svg-shapes.md`
> (the catalog and the S5 primitives) · `svg-repair.md` (S7 and PATTERN → FIX, on a finding) · `svg-refine.md`
> (S8–S10).

# Figure colour, tokens and accessibility (S6)

## The ground a figure stands on

A figure draws no background and no frame. **Its ground is `--surface`,** in both places it is shown: `figures.py place` writes a block of tokens into the file that paints that ground behind a standalone figure, and a page that shows the figure inline puts it on a panel of the same colour.

So everything you draw is judged against `--surface`. A card, a node or an empty track that should stand out from the ground is filled with `var(--bg)` and outlined with `var(--border)`.

A panel that only groups other shapes takes no fill (`fill: none`, an outline at most): a filled panel under `--bg` cards hides them, and the check reports it as `zone-invisible`. A zone that an arrow enters is a tint with `fill-opacity`, as below: an opaque box with a label in it counts as a node, and the check reports an edge that crosses it as `edge-through-node`.

---

## S6 · Semantic colour tokens + SVG accessibility + DRY structure

One rule governs the figures of a text: **colour means something, and the tokens already own it.** Green is *positive*, red is *negative*, not "a nice green". If every `<svg>` picks its own hexes, the eighth one drifts off the legend, the reader stops trusting the encoding, and the figure breaks on a dark screen. This section maps valence onto the tokens, recolours a whole figure from one switch, and keeps the markup accessible and free of collisions across many figures.

### The tokens ARE the palette: a figure defines none of its own

The tokens are listed in `assets/tokens.css`, with a value for a light and for a dark screen:

| Token | What it is |
|---|---|
| `--surface` | the ground behind the figure |
| `--bg` | the fill of a card, node or empty track on that ground |
| `--border` | hairlines, dividers, outlines of neutral shapes |
| `--text`, `--text-dim`, `--muted` | label ink, secondary ink, the neutral mark |
| `--ok`, `--warn`, `--error`, `--info` | the four valence hues |
| `--accent`, `--accent-fg` | the one accent, and legible text on a fill of it |
| `--font-body`, `--font-mono` | the two font stacks |

**A figure declares no `--bg`, no `--text`, and no `@media (prefers-color-scheme)` of its own.** `place` writes the one token block into the file, and a page defines the same names; a second definition inside the figure would fight both. Read the tokens; never restate them. The check reports a typed colour as `raw-color` and a media query as `at-rule`.

Tag each thing a figure shows with a valence in the brief, *before* drawing, and bind it to the token:

| Valence in the brief | Token | Notes |
|---|---|---|
| positive · pass · added | `var(--ok)` | the pass hue: keep it for verdicts only |
| negative · fail · removed | `var(--error)` | |
| risk · partial | `var(--warn)` | a mark only on a light screen: see the contrast floors below |
| baseline · not yet run · the state before | `var(--muted)` | with `var(--border)` hairlines and `var(--bg)` tracks |
| secondary register · emphasis | `var(--info)` | see the accent rule |
| an edge that carries no verdict: a step to the next step, a request, a pointer | `var(--muted)` shaft and head | `var(--border)` is too faint for an edge (under 3:1): it is for dividers and outlines |

**The accent rule:** inside a figure, keep the valence hues (`--ok` / `--warn` / `--error`) for verdicts only, so green always means pass or positive. For emphasis that carries no verdict (standalone pointer glyphs, a highlighted series, plotted dots, never the markers of meaning-carrying edges, whose heads match their shafts per S5) use `var(--info)` or `var(--muted)` ink, never a valence hue: an emphasis mark coloured like a verdict reads as a verdict you did not intend. And the valence table binds in both directions: a *baseline* or *before* state is `var(--muted)`, never `var(--error)`. Painting the "before" bar red asserts a failure the brief never claimed.

**Write a token in a class or in `style=`,** as every example in these references does. Chromium also resolves `var()` in a presentation attribute (`fill="var(--ok)"`, tried on Chromium 148); other renderers were not tried.

### Derive shades, don't pick them

You need four *renditions* of each base: a pale zone fill, a legible border, dark text, the solid mark. Hand-picking 16 hexes is how drift starts. The token block derives them with `color-mix()`: toward `--surface` for the tints, toward `--text` for the darker ink of the same hue. Because they are built from the base tokens, they turn with the screen: zones and inks flip between light and dark for free.

```css
/* in assets/tokens.css, the same three lines for --error, --warn, --muted and --info */
--ok-zone: color-mix(in srgb, var(--ok) 12%, var(--surface));  /* pale fill of a zone   */
--ok-line: color-mix(in srgb, var(--ok) 42%, var(--surface));  /* its hairline border   */
--ok-ink:  color-mix(in srgb, var(--ok) 38%, var(--text));     /* readable text         */
```

Three corollaries that keep it calm:

- **Borders by construction.** A fill's stroke and its text are the *same hue, darker* (`--ok-line` / `--ok-ink` above), never a new colour. This is what makes a shape read as "one object" instead of a sticker.
- **Tint zones with opacity, not a new hue.** A shaded background region is the valence fill at low `fill-opacity`, so it stays on-hue:

```xml
<rect x="16" y="16" width="288" height="72" rx="8" fill-opacity="0.10"
      style="fill:var(--ok); stroke:var(--ok-line)"/>
```

- **Attenuate ONCE, and a claim-carrying zone must survive the squint test.** `fill-opacity` applies to the RAW valence colour (`var(--ok)`, `var(--error)`), never to an already mixed `--*-zone` token: `fill: var(--error-zone)` **plus** `fill-opacity="0.16"` composes 12% × 16%, about 2 RGB units from the ground, a zone that exists in the source and not in the pixels (the check reports it as `zone-invisible`). And when the zone's *extent* IS the claim (a stale window, an outage span, a rollback boundary), tint alone is the floor, not the target: give it the tint **plus** a visible boundary at each end (dashed rules or a bracket) **plus** a direct label. If the zone disappears in a greyscale squint, the figure has no claim.

### House bans apply inside the figure

- **No typed font.** A `<text>` with no class is already set in `var(--font-body)`; value and code text takes a class with `font-family: var(--font-mono)`. Never a family by name: the check reports it as `typed-font`.
- **No violet, fuchsia or indigo in any slot,** and no colour that is not a token.
- **No gradient** (`<linearGradient>`, `<radialGradient>`): flat fills only. Encode a value with the *shade* tokens above.

The token set keeps you on one calm accent and four valence hues, so there is no reason to reach past them.

### `currentColor` + class recolour (one switch, whole figure)

Draw geometry with `class=` (or `fill="currentColor"`), and define what those classes mean *once* in the figure's `<style>`, each selector starting with the figure's id. A single class then recolours the entire figure, with no edits to single paths.

```xml
<svg xmlns="http://www.w3.org/2000/svg" id="fig-3" viewBox="0 0 320 132" role="img"
     aria-label="Coverage rose from 60% to 95% once the frontmatter guard ran.">
  <defs>
    <style>
      #fig-3 .lbl   { font-size: 12px; }
      #fig-3 .mono  { font-family: var(--font-mono); font-size: 12px; }
      #fig-3 .after { fill: var(--ok); }
      #fig-3 .before{ fill: var(--muted); }
      #fig-3 .track { fill: var(--bg); stroke: var(--border); }
      #fig-3 .ink-ok   { fill: var(--ok-ink); }
      #fig-3 .ink-mute { fill: var(--muted-ink); }
    </style>
  </defs>

  <!-- before: 60% of a 280-wide track -->
  <!-- label text uses an ink token (4.5:1 and more); the solid ok token is for the FILL only.
       Two hyphens in a row never stand inside a comment: the file stops being XML -->
  <rect class="track"  x="20" y="28" width="280" height="16" rx="8"/>
  <rect class="before" x="20" y="28" width="168" height="16" rx="8"/>
  <text class="lbl ink-mute" x="20" y="22">before · 60%</text>

  <!-- after: 95% of the same track -->
  <rect class="track" x="20" y="76" width="280" height="16" rx="8"/>
  <rect class="after" x="20" y="76" width="266" height="16" rx="8"/>
  <text class="lbl ink-ok" x="20" y="70">after · 95%</text>
</svg>
```

The bar widths are worked from the track: `60% × 280 = 168`, `95% × 280 = 266`.

**DRY across the figures of a text:** keep `<g>` ids descriptive and *stable* across edits (so a targeted recolour is deterministic), minimise decimal precision (`x="168"` not `x="167.9994"`), and define any mark you draw twice as a `<symbol>` referenced by `<use>` rather than copying its paths.

### Ids start with the figure's id: the silent collision

When two inline SVGs in one document define `<marker id="arr">`, **the ids collide silently**: every `url(#arr)` reference resolves to the *first* matching definition in the document, so the second figure's arrowheads quietly adopt the first one's colour. The browser gives no warning. So every id inside `fig-N.svg` starts with `fig-N-` (markers, patterns, clips, symbols), and a mark drawn twice is defined once:

```xml
<svg xmlns="http://www.w3.org/2000/svg" id="fig-4" viewBox="0 0 200 60" role="img"
     aria-label="Step A flows into step B.">
  <defs>
    <marker id="fig-4-arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0 0 L10 5 L0 10 Z" style="fill:var(--muted)"/>
    </marker>
    <symbol id="fig-4-node" viewBox="0 0 60 28">
      <rect x="1" y="1" width="58" height="26" rx="6"
            style="fill:var(--bg); stroke:var(--muted)"/>
    </symbol>
  </defs>
  <!-- width/height MUST match the symbol's viewBox; without them <use> defaults to
       100% of the viewport and the node balloons to fill the canvas -->
  <use href="#fig-4-node" x="8"   y="16" width="60" height="28"/>
  <use href="#fig-4-node" x="132" y="16" width="60" height="28"/>
  <line x1="76" y1="30" x2="132" y2="30" style="stroke:var(--muted)"
        marker-end="url(#fig-4-arrow)"/>
</svg>
```

The check reports an id without the prefix as `unscoped-id`, a repeated id as `duplicate-id`, and a selector that does not start with `#fig-N` as `unscoped-style`. The same collision is why: a `.card` rule of one figure would restyle the `.card` of every other figure on the page.

### Accessibility: the label states the *finding*, not the medium

The root carries `role="img"` and an `aria-label` that asserts the **takeaway**: *"Coverage rose from 60% to 95% once the guard ran"*, never *"a diagram"* or *"chart"*. In this skill the label is the mark's sentence word for word, so the caption a reader sees and the name a screen reader says are one sentence, read by the same readers as the rest of the text. Use `aria-label` alone: no `<title>`, no `<desc>`, no `aria-labelledby`.

**Exact numbers belong in the text.** A figure shows a shape; a reader who wants the values exactly, or cannot see the figure, finds them in the sentences around the mark, or in a table there when there are many.

### Never colour alone

About 8% of men cannot separate your red from your green, and the text may be printed in greyscale. **Never let hue be the only channel:** double every state with shape, dash, or a direct label. Pass against fail is a check glyph against a cross, *and* green against red, *and* the word. A "not yet run" region is a hatch fill, not just a paler colour. Define the hatch as a tileable `<pattern>` (a redundant, print-safe second channel; the full set is in `svg-shapes.md`, "Texture / hatch fill as a second channel"):

```xml
<defs>
  <pattern id="fig-5-hatch" patternUnits="userSpaceOnUse" width="6" height="6"
           patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="6" style="stroke:var(--muted)" stroke-width="1.4"/>
  </pattern>
</defs>
<rect x="16" y="16" width="120" height="40" rx="6"
      fill="url(#fig-5-hatch)" style="stroke:var(--muted)"/>
<!-- pair with a dashed border on the negative side: stroke-dasharray="4 3" -->
```

**Contrast floors:** marks that are not text (a bar, a dot, an arrowhead carrying meaning) need **3:1** against their ground; any `<text>` needs **4.5:1**. The ratios below are computed from the values in `assets/tokens.css`, against the ground `--surface`.

| Case | Light screen | Dark screen | Rule |
|---|---|---|---|
| A solid valence token as a **`<text>` fill** | `--warn` 3.6:1 (fails 4.5), `--ok` 4.6:1 (no headroom), `--error` 5.0:1, `--info` 5.4:1 | 4.9:1 to 6.8:1 | Label text uses the inks (`--ok-ink`, `--error-ink`, `--warn-ink`, `--muted-ink`, `--info-ink`): 9.8:1 and more on the ground, 8.6:1 and more on their own zone, on both screens. Keep the solid token for a short bold label at most, and never `--warn`. |
| **Text on a solid fill** | `var(--bg)` text on `--ok` 4.9:1, on `--error` 5.3:1, on `--info` 5.7:1, on `--warn` 3.9:1 (fails) | 5.2:1 to 7.4:1 | On `--accent` use `var(--accent-fg)`. On `--ok`, `--error` and `--info` fills `var(--bg)` reads on both screens. On a `--warn` fill set no text at all: use a `--warn-zone` tint with `--warn-ink` text. |
| `--warn` as a **mark** (bar, dot, arrowhead) | 3.6:1, close to the 3:1 floor | 6.8:1 | Valid as a bar or dot, never the only channel: pair it with the hatch or a label, per "Never colour alone". |
| Solid `--ok` / `--error` / `--info` / `--muted` **marks** | 4.6:1 to 5.6:1 | 4.9:1 to 5.7:1 | They clear 3:1 as fills. The failures above are about *text*, not bar fills. |
| A `--*-zone` tint against the ground | 1.14:1 to 1.18:1 | 1.14:1 to 1.20:1 | A tint is visible and nothing more. When the zone's extent is the claim, add the boundary and the label (see "Attenuate ONCE" above). |

If you change a value in `assets/tokens.css`, compute these again: the table holds for the values that are there now.
