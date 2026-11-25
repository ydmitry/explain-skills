---
name: skimmable
description: Use when writing or rewriting a text of more than about 300 words that a person will read on their own (a report, a README, a design note, an explanation, a long answer), or when asked to make a text easier to read or to skim.
---

# skimmable

A reader skims before they read. They look at the headings, the bold text and the first sentence of each paragraph,
and from that they decide what to read in full. They stop at the first part that asks too much of them.

**The test: it is easy to skim with the eyes.** Someone who looks only at the headings, the bold text and the first
sentence of each paragraph gets the story, and can tell which part to stop and read.

These rules are about form. What the text says, and how much of it, comes from the task. A rewrite keeps every fact.

## Sections

- **The answer comes first:** the first lines say what the text is and its main point.
- **One idea in each section,** said by its heading. A section that makes two points is two sections, each under
  its own heading.
- **Many small sections beat a few large ones.** A section is at most 300 words; a short one is fine.
- **A section can be read alone:** it names what it talks about again and leans on no earlier section.
- **Headings say what is inside,** in the words the reader would search for.

## The form follows the content

A text that is all bullets reads as a list of facts, not an explanation. Each piece takes the form of what it is:

- **An argument or an explanation** (what happens, why, what follows) is a short paragraph of connected sentences. The
  words that connect ("so", "because", "but", "which means") are the explanation; a bullet drops them.
- **Steps or a chain of causes** are a numbered list.
- **The same facts over several cases** (options, flags, runs, versions) are a table.
- **Separate items of one kind** (open points, limits, requirements) are bullets.

Sentences stay short, about a dozen words.

## What stands out

A section of plain paragraphs gives the eye nothing to land on. So:

- **A paragraph is at most 60 words.** A longer one is two paragraphs, or its parallel parts become a list.
- **A paragraph's first sentence says its point;** the rest supports it.
- **One thing in bold in each section:** the conclusion, the number or the condition that matters most there.
- **Bold labels only where a section holds several separate items** of the same kind (four reasons, three checks):
  each item then opens with a label of one to three words. An ordinary paragraph has no label; it opens with its
  point.
- No more bold than that: a label on every paragraph, or a section that is mostly bold, is as hard to read as none.
- A list of more than eight items is grouped under labels or becomes a table.

## Short texts

Under about 300 words there are no headings and nothing to split. The point comes first, paragraphs stay short, and
at most one thing is bold.

## Writing up work for someone who was not there

A hand-over, findings for a lead, a decision to sign off: the reader has only this text.

- **Open with a status line:** one or two sentences, dated as of the last data. Where the matter stands: settled,
  open, or waiting on what.
- **Then a summary:** five to eight bullets, one fact each, in the order a reader would ask. The last one is the next
  step: who does what, and by when.
- **Thorough beats short.** Leave out nothing the reader may need to act or to trust the conclusion; for a few hours
  of work that is 1,500 to 2,500 words. Only the story of how the work went is left out.

## Words

A term the reader may not know is explained where it first appears; there is no glossary. Names the reader will
search for or type (a flag, a file, a command) are in backticks.

## Check

When the text is a file, check it: `python3 ${CLAUDE_SKILL_DIR}/scripts/skim_check.py FILE --skim`. It prints what a
skimming eye sees and lists paragraphs over 60 words, sections over 300, sections with nothing in bold or too much of
it, and long runs of bullets. Fix what it lists, then read the skim view alone: if it does not tell the story, the
headings and first sentences need rewriting.
