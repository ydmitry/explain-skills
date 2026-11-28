---
name: skimmable-writing
description: Use when writing or rewriting a Markdown text of more than about 300 words that a person will read on their own (a report, a README, a design note, an explanation, a long answer, a hand-over or write-up of what a working session found or decided), or when asked to make a text easier to read or to skim.
---

# skimmable-writing

A reader skims before they read. They look at the headings, the bold text and the first sentence of each paragraph, and from that they decide what to read in full. They stop at the first part that asks too much of them.

**The test: it is easy to skim with the eyes.** Someone who looks only at the headings, the bold text and the first sentence of each paragraph gets the story, and can tell which part to stop and read.

Most of these rules are about form. How much the text says comes from the task, and a rewrite keeps every fact. The rules on words, numbers and claims are here because a skimming reader lands in the middle of the text: each part has to make sense where it stands.

## Sections

- **The answer comes first:** the first lines say what the text is and its main point.
- **One idea in each section,** said by its heading. A section that makes two points is two sections, each under its own heading.
- **Many small sections beat a few large ones.** A section is at most 300 words; a short one is fine.
- **A section can be read alone:** it names what it talks about again and leans on no earlier section.
- **Headings say what is inside,** in the words the reader would search for.

## The form follows the content

A text that is all bullets reads as a list of facts, not an explanation. Each piece takes the form of what it is:

- **An argument or an explanation** (what happens, why, what follows) is a short paragraph of connected sentences. The words that connect ("so", "because", "but", "which means") are the explanation; a bullet drops them.
- **Steps or a chain of causes** are a numbered list.
- **The same facts over several cases** (options, flags, runs, versions) are a table.
- **Separate items of one kind** (open points, limits, requirements) are bullets.

A sentence keeps the words that belong together close: the subject near its verb, the verb near what it acts on. A long sentence is never split at "because", "so" or "but": that word is the explanation.

## What stands out

A section of plain paragraphs gives the eye nothing to land on. So:

- **A paragraph is at most 60 words.** A longer one is two paragraphs, or its parallel parts become a list.
- **A paragraph's first sentence says its point;** the rest supports it.
- **One thing in bold in each section:** the conclusion, the number or the condition that matters most there.
- **Bold labels only where a section holds several separate items** of the same kind (four reasons, three checks): each item then opens with a label of one to three words. An ordinary paragraph has no label; it opens with its point.
- No more bold than that: a label on every paragraph, or a section that is mostly bold, is as hard to read as none.
- A long list is grouped under labels or becomes a table when its items fall into kinds a reader would look for, whatever the count.

## Words

**A name made up during the work is replaced by plain words for what it stands for.** "Run 7", "the B-path", a nickname for a theory: the reader was not there when the name was given.

Names the reader will search for or type (a flag, a ticket, a commit, a file, a command) stay, in backticks. A term the reader may not know is explained where it first appears, in a clause or a sentence of its own after the claim and never wedged into the middle of one; there is no glossary.

## Numbers, claims and sources

- **A number carries what it covers** where it is given: the period, the group, what was left out.
- **A claim carries the check that showed it** and what the check returned.
- **A fact from a file or a page carries a pointer to it,** where the fact is stated: a link, or the path with the line (`src/billing/retry.py:12`), copied from where you read it or from its `keep-sources` row. A reader who doubts the fact can then follow it.
- **A fact the conclusion rests on shows its source's words:** a short quote, copied letter for letter, beside the pointer. A line of code, a clause of a contract, a sentence of a message: about 25 words at most, in quotation marks or as a quoted block. Quote only what you have open in front of you; a quote from memory is worse than none.

## Short texts

Under about 300 words there are no headings and nothing to split. The point comes first, paragraphs stay short, and at most one thing is bold.

## Writing up work for someone who was not there

A hand-over, findings for a lead, a decision to sign off: the reader has only this text.

- **Open with a status line:** one or two sentences, dated as of the last data, not today. Where the matter stands: settled, open, or waiting on what. Report where the work stands and take no position of your own.
- **Then a summary:** five to eight bullets, one fact each, in the order a reader would ask. The last one is the next step: who does what, and by when.
- **As long as what the reader lacks needs, and no longer.** Leave out nothing the reader may need to act or to trust the conclusion, and add nothing beyond that.
- **What goes in,** each in the section where the reader would look for it: what was ruled out and why, what changed from the first belief to the last, what is not known, what would change the conclusion, and the settings, dates and limits needed to carry it out.
- **What stays out:** how the work itself went. The order things were tried in, tool trouble, side-stories.

## Check

When the text is a file, check it: `python3 ${CLAUDE_SKILL_DIR}/scripts/skim_check.py FILE --skim`. It prints what a skimming eye sees and lists paragraphs over 60 words, sections over 300, and sections with nothing in bold or too much of it. The check reads each line as one paragraph, so **write each paragraph on one line.**

The limits of 60 words, 300 words and one thing in bold are house style, chosen so that a script can count them. Published studies support short and sparse; none tests these numbers.

Fix what it lists, then read the skim view alone: if it does not tell the story, the headings and first sentences need rewriting.

A line that starts `NOTE` is a count and not a problem. One counts a run of more than eight bullets: group them when they fall into kinds, else leave them.

The other note appears when three or more headings, and two fifths of them all, open with the same word ("What it reads", "What it prints"). Reword the headings where that word says nothing about the section.

## With the other skills

**This skill owns the structure:** sections, headings, lists, tables and what is in bold. `deslop-prose` rewords sentences afterwards and leaves the structure alone; run the check again after it. `check-sources` and `cold-read` read the finished text. Each works without the others.
