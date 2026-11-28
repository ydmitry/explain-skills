---
name: draw-figures
description: Use while writing a text that states a claim whose structure is the point (a before and after, steps in order, parts of a whole, two things on one scale, a flow between a few parts), when a text holds a `Figure:` line that is not drawn yet, or when asked to draw, diagram, illustrate or visualise something a text says.
---

# draw-figures

A figure is for a claim whose structure is the point: a before and an after, a threshold, a part of a whole, a flow. The reader sees the shape before reading a word of it. Where structure adds nothing, a sentence or a table says it better.

**The text owns every word.** A figure is marked in the text by a line that states its claim. That line is read with the rest of the text, and the drawing adds no word and no number of its own.

## Which claims get a figure

Go through the text claim by claim. **A claim gets a figure only when both tests hold:**

- **Contrast:** you can name the state the claim asserts and a concretely different state it rules out: the before, the failure, the other option. With no second state there is nothing to draw.
- **Structure:** with every label deleted, the drawing would still argue the claim. When only the labels would carry it, write a table or a list.

Results and limits are easy to pass over: a row of a results table can hide a gap or a split, and a stated limit is often a threshold.

**When many claims pass, draw the few the text's point rests on.** A table of results whose rows all pass stays a table: one figure for the row the text leads with says more than six alike.

**A definition of a term gets no figure,** even when a picture of it comes to mind. It says what a word means and asserts nothing about the subject, so it fails the contrast test. The same holds for a list of terms and for a sentence on who owns or keeps something.

A mark that already stands in the text and fails a test is not drawn. Say so in your report: its claim stays a sentence, and the mark comes out of the text.

## The shape follows the claim

**Each kind of claim has a shape, and the brief names it.**

| The claim is about | Shape |
|---|---|
| a before and an after, a regression | `the Gap` |
| steps in order, eight nodes at most | `small flow` |
| a boundary, something kept out | `zones-with-wall` |
| a count out of a total | `n-of-m fill` |
| one share of a whole | `filled track` |
| a whole split into a few parts | `pie` |
| steps that pass between several parts, in order | `swimlane` |
| dates, and a span between them | `line of time` |
| a limit that is crossed or held | `threshold meter` |
| a change over time | `trend line` |
| two versions that must agree | `paired diff` |
| a thing with named parts | `labeled anatomy` |
| two independent axes | `2x2` |
| a position between two poles | `spectrum` |

A claim that fits none of these and still passes both tests is a `one-off metaphor`. Rows and columns of values are a table, never a figure. One figure carries one claim: three claims are three figures.

An arrow is drawn only for a sequence, a cause or a movement. A reader takes an arrow to mean that something acts or flows, so the parts of a thing and two things compared get none.

## The form a reader expects

**Where readers expect a form, use it.** A whole split into a few parts is a pie. Steps that pass between several parts are swimlanes: a lane for each part, time from left to right. Dates are a line of time.

A reader knows how to read these before reading a word. A shape of your own is for a claim that no expected form fits.

**A sequence shows where it starts and reads one way.** The first step stands at the left, or carries the number 1, and position or a number gives the order. An arrow that needs a label to say when it happens, or that bends around a box, hides the order: draw swimlanes, or number the steps.

## The mark

Where the figure goes, write one line as a paragraph of its own:

```
Figure: Before the guard 60% of the runs were covered, after it 95%.
```

- **The line states the claim,** in a sentence or two. "Figure: coverage chart" names the medium and says nothing.
- **It is the caption and the figure's accessible name,** word for word, without Markdown's backticks and stars. `marks` prints it that way.
- **Write the marks while you write the text,** before `check-sources` and `cold-read` read it. They then read each caption as part of the text.

## Draw what is marked

`FIGS` is `python3 ${CLAUDE_SKILL_DIR}/scripts/figures.py`, and `TEXT` is the Markdown file.

1. **`FIGS marks TEXT`** lists the marks and the file each one gets: `figures/<name of the text>/fig-1.svg` beside the text, numbered in the order of the marks.
2. **`FIGS brief TEXT`** writes `brief.md` into that folder, with a block for each mark. Fill each block: the shape, the data, what must and must not be shown.
3. **Read before the first `<svg>`:** `references/svg-figures.md` down to its ON DEMAND heading, then `references/svg-color.md` and `references/svg-geometry.md` as their headers say, and the section of `references/svg-shapes.md` that the table in `svg-figures.md` names for the shape. For a shape with no section there, the geometry file is the recipe.
4. **Draw each figure as its own file,** from the skeleton in `svg-figures.md`.
5. **`FIGS check TEXT`** until it prints `problems=0`. `references/svg-repair.md` has the fix for each finding. Fix a line that starts `WARN` too, or say why it stays.
6. **`FIGS preview TEXT`** writes a picture of each figure, for a light and a dark screen, and prints where: a temporary folder, or the one given with `--out`. Look at each one once against its claim. When a figure passes the check and still looks like any other, read `references/svg-refine.md`.
7. **`FIGS place TEXT`** finishes the files and writes an image line above each mark.

## Where the labels come from

**A label is copied, never composed.** Every word and number inside a figure stands in the text, or in the figure's block of the brief with the place it was taken from: a line of a file, or a row of a `keep-sources` folder.

The check lists a word or a number that stands in neither.

In the brief, what stands in parentheses is the pointer to the place: it allows no label, and the check does not look it up. Take the text's word for it. If the figure needs a word the text lacks, the text is missing it: add it there, where a reader will read it.

## A figure is scanned, not read

**A figure does not win by saying more. It wins by what a reader takes in at a look.**

- **A label is a few words:** seven at most, and about twenty on the whole figure. The check lists a longer label and a fuller figure as a `WARN`.
- **What needs a sentence stays in the text** beside the figure, where the mark's line already says it.
- **A part of the idea that the plain shapes do not show gets something that shows it:** a crossed line where nothing passes, a second bar for the plan, a place outside the group. A drawn hint scans faster than a phrase.

The two numbers are house style. They come from the figures that were picked in a blind look at drawn figures, not from a study.

## The file

- **One file for one figure:** `fig-N.svg`, for the Nth mark of the text.
- **It names no colour.** Fills and strokes read tokens such as `var(--ok)` and `var(--text)`, so the figure follows a light and a dark screen. `place` writes the palette into the file.
- **Its `aria-label` is the mark's sentence.** When you change the mark, change the label and the brief with it; the check compares the three.
- **A mark that draws a number carries it:** `data-value="620"` on a bar, with `data-of` for a share of a whole. The check then compares the drawing with its numbers.
- **Its ids and its style rules start with its own id,** so several figures can stand inline in one page.

`place` leaves a file that shows correctly wherever a browser draws it: on GitHub, in an editor's preview, in a page. Where an image is needed, as in a chat message or an issue tracker, use the pictures that `preview` writes.

## What a clean check does not show

`problems=0` means each mark has a figure with its sentence as the label, no colour is typed, no label holds a new word or number, every mark that carries its number is drawn in proportion to it, and nothing measured collides or leaves the canvas.

**It does not show that the figure argues its claim.** Only the look at the picture in step 6 does.

Without the `playwright` package the check measures nothing and says so. Then say in your report that the geometry was not measured.

## One agent draws them all

**With four or more figures, one subagent can draw them all from the brief** while you go on with other work. `references/figure-agent.md` has its prompt and what it returns. The brief is then the whole hand-over, so fill it for a reader who has not seen the chat.

## A graph in a text that stays Markdown

**A graph of boxes and arrows can go into the text as a `mermaid` block,** when the text will be read as Markdown and speed matters more than looks. GitHub and most editors draw it. It needs no mark, no file and no check.

Boxes and arrows fit a flow or a sequence. For a comparison or a quantity they are the wrong form: mark a figure, or write a table.

Keep it under about fifteen nodes, take every label from the text, and set no colours. `render-page` refuses such a block: a page shows drawn figures only.

## With the other skills

**This skill owns the figures: which claims get one, and the drawing.** The words stay with the text: `skimmable-writing` owns its structure, the two readers read the marks with it, and `render-page` puts the figures into a page. Each works without the others.
