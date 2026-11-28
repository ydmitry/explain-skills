---
name: render-page
description: Use when a finished Markdown text is to be shown as an HTML page - asked for a page, an HTML version, something to open in a browser or to read on a phone - or when a text with drawn `Figure:` lines needs its figures shown in place.
---

# render-page

A page is the text, shown: the same words in the same order, with its figures in place. It is made by a script, so the page cannot say something the text does not.

**The text stays the source.** To change the page, change the text and render again. Never edit the page.

## Before rendering

**Render a text that is finished.** Every sentence was written, cleaned and read as Markdown; a page is the last step and adds no reading of its own.

- A `Figure:` line needs its figure drawn first: that is `draw-figures`. The renderer refuses a mark with no figure file.
- A `mermaid` block is refused. A page shows drawn figures only, so give the graph a `Figure:` line and draw it, or keep the text as Markdown.

## Render and check

`TEXT` is the Markdown file.

1. **`python3 ${CLAUDE_SKILL_DIR}/scripts/render.py TEXT`** writes the page beside the text, with the same name and `.html`. `-o PAGE` writes it elsewhere. A text with no `# ` title needs `--title "..."`.
2. **`python3 ${CLAUDE_SKILL_DIR}/scripts/page_check.py PAGE TEXT`** until it prints `problems=0`. Fix a line that starts `WARN` too, or say why it stays.
3. **Open the page** and look at it once, at a phone's width as well as a wide one, when you have a way to look.

When the renderer prints `ERROR line N`, it wrote no page. Fix that line of the text: the message says how.

## What the page holds

| On the page | Where it comes from |
|---|---|
| the title and the text | the Markdown, word for word |
| each figure, with its caption | `fig-N.svg` and the mark's sentence |
| a list of the sections | the `## ` headings |
| a switch named Skim | dims everything but headings, bold text and first sentences |
| a switch for a light or a dark screen | follows the system until the reader picks |

**The list of sections and the two switches are the only words the page adds.** It is one file, it carries its pictures inside it, and it asks the network for nothing.

## What the renderer reads

Headings, paragraphs, bold, italic, struck text, code, links, lists that nest, tables, fenced code, quotes, rules and local pictures.

**What it cannot show it refuses, with the line:** raw HTML, a footnote, a picture from the web, an indented code block. It never drops a line silently.

## What a clean check shows

`problems=0` means four things:

- **The page is the render of the text as it is now.** Nobody edited it, and neither the text nor a figure changed since.
- **The words a reader sees are the words of the text,** in order. The check reads them from the page and from the Markdown separately.
- **The page asks the network for nothing,** and holds one figure for each mark.
- **Measured in a headless browser:** nothing is wider than the screen at 320, 360 and 768 pixels, and no label of a figure is drawn under 9.5 pixels on a phone.

The measured part needs the `playwright` package. Without it the check prints `measured=no`: say in your report that the page's width was not measured.

**It does not show that the page looks right.** Step 3 does.

## A wide figure on a phone

**A figure is shown at the size it was drawn, never larger.** On a narrow screen it shrinks to four fifths of that size and then scrolls sideways inside its own frame, so its labels stay readable and the page itself never scrolls sideways.

A figure about 400 units wide or less shows whole on a phone. **The check warns of a figure that is cut off on a 390 px screen:** a line `WARN figure-cut-off` and a count in `warnings=N`. Have it redrawn narrower with `draw-figures`, or say in your report that the page is not read on a phone.

## The look of the page

**The colours and fonts are the tokens in `assets/tokens.css`,** the same file `draw-figures` holds, so a figure and the page around it turn dark together. The layout is `assets/page.html`.

To give pages another look, change those two files and keep the token names. Then run the plugin's tests: one of them fails when the two skills' token files differ.

## With the other skills

**This skill owns the page and no word of it.** `skimmable-writing` owns the text's structure, `draw-figures` owns the figures, and `check-sources` and `cold-read` read the Markdown before it is rendered: fixing a sentence there is cheaper. Each works without the others.
