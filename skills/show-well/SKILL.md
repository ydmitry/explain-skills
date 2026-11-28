---
name: show-well
description: Runs explain-well to its end with the page always made - the text is written, checked and read, its figures are drawn, and it is shown as one HTML page. Called by the user only.
argument-hint: "[what to show, or the file to finish]"
disable-model-invocation: true
---

# show-well

One command for something to be shown as a page with figures. What was asked for: $ARGUMENTS

**This is `explain-well` with the figures and the page never left out.** Read `${CLAUDE_SKILL_DIR}/../explain-well/SKILL.md` to the end and follow it: its order, where to start, what to do after a read, what to skip. Only what differs is here.

## What to show

**The subject is the thing the user points at, and nothing wider.** "This", "that" or "your last message" means that one message or file, not the whole session around it. When the words fit two subjects, ask once before writing.

## What differs from explain-well

| Step | In `explain-well` | Here |
|---|---|---|
| 2 | `draw-figures` may mark a claim | Go through the claims with `draw-figures` and mark each one it says to draw. A text where it finds none gets none: do not mark a claim to have a picture |
| 5 | Runs when the text has a `Figure:` line | The same, and a line that `draw-figures` says not to draw is removed, not left undrawn |
| 6 | Only when a page is asked for | Always. A `WARN` line of `page_check.py` is fixed, or listed as open |

**A short text still gets its page.** Under about 300 words write it with `skimmable-writing` alone, as `explain-well` says, then run steps 5 and 6.

## Showing it

1. Open the page for the user: in the browser on their machine, and sent as a file when they follow from another device.
2. Report after it, in place of the text: the page's whole path first, then the three things `explain-well` lists. Add the number of figures drawn, and say so when there are none.
