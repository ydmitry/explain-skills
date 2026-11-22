---
name: explain-context
description: Use when asked to write up, explain, summarise or hand over what a working session found or decided, for a person who was not in it and will read alone (a hand-over, findings for a lead or a manager, a decision for whoever signs it off, "write up what we found").
---

# explain-context

The reader was not there and reads alone. They know their job; they do not know this session. They read one section
at a time and stop at the first one that asks too much of them. So the write-up is thorough, in many small sections,
each easy by itself, and each written in the form its content has.

**The test: it is easy to skim with the eyes.** Someone who looks only at the headings, the bold text and the first
sentence of each paragraph gets the story, and can tell which section to stop and read.

(The owner's read of four versions of one session: a 2,000-word write-up in twelve sections read best. An 840-word one
that packed six answers into its first paragraph stopped the reading. A 1,300-word one that was 98% bullets was
"obsessed with lists, boring to read": its evidence section listed facts where the better one explained them.)

## Shape

1. **A status line first:** one or two sentences, dated as of the session's last data, not today. Where the matter stands: settled, open, or waiting
   on what. Report the session's position; take none of your own.
2. **A summary section:** five to eight bullets, one fact each, in the order a reader would ask: what happened, why,
   what was done, what is next.
3. **Then one section for each job the write-up has,** named in the words this kind of document uses. An incident:
   impact, timeline, cause, evidence, ruled out, changes made, open items, caveats. An experiment: what was tested,
   result, what the result covers, problems found, what it means for the decision, open questions. A decision: the
   requirement, the options, the comparison, where it stands, what it waits on. Choose the sections the subject needs;
   ten or twelve is normal.

## Each section

- **One job,** said by its heading. A reader who opens only this section can follow it: it names what it talks about
  again and leans on no earlier section.
- **Small:** 100 to 300 words. A longer one is split in two.
- **A number carries what it covers** where it is given: the period, the group, what was left out.
- **A claim carries the check that showed it** and what the check returned.

## The form follows the content

A write-up that is all bullets reads as a list of facts, not an explanation. Each piece takes the form of what it is:

- **An argument** (what was seen, what it shows, how far to trust it) is a short paragraph of connected sentences:
  "The 504s cluster in the 5-minute marks, about 770 each, with 0 to 3 in
  other minutes. Within the minute they fall in seconds 02 to 09, which fits a lock held for about 9 s." Several such items in one section each get a bold label ("**Minute pattern.**").
  The words
  that connect ("which fits", "so", "because", "but") are the explanation; a bullet drops them.
- **Steps or a chain of causes** are a numbered list.
- **The same measurement over several cases** (runs, options, groups) is a table.
- **Separate items of one kind** (open items, things ruled out) are bullets.

Sentences stay short, about a dozen words.

## What stands out

A section of plain paragraphs gives the eye nothing to land on. So:

- **A paragraph is at most 60 words.** A longer one is two paragraphs, or its parallel parts become a list.
- **A paragraph's first sentence says its point;** the rest supports it.
- **One thing in bold in each section:** the conclusion, the number or the condition that matters most there. A
  reader who reads only the headings and the bold gets the point of every section.
- **Bold labels only where a section holds several separate items** of the same kind (four pieces of evidence, three
  checks): each item then opens with a label of one to three words. An ordinary paragraph has no label; it opens
  with its point.
- No more bold than that: a label on every paragraph, or a section that is mostly bold, is as hard to read as none.

When the write-up is a file, check it: `python3 ${CLAUDE_SKILL_DIR}/scripts/skim_check.py FILE --skim`. It prints
what a skimming eye sees and lists paragraphs over 60 words, sections over 300, sections with nothing in bold or
too much of it, and long runs of bullets. Fix what it lists, then read the skim view alone: if it does not tell the story, the headings
and first sentences need rewriting.

## What goes in

Thorough beats short: for a session of a few hours, 1,500 to 2,500 words. Everything the reader may need to act or to trust the conclusion, each in the section where they would look for it:
what was ruled out and why; what changed from first belief to last ("first thought X; the replay showed Y"); what is
not known; what would change the conclusion; who owns the next step and by when; settings, dates and limits needed to
carry it out.

## Words

A name made up in the session ("run 7", "the B-path", a nickname for a theory) is replaced by plain words for what it
stands for. Names the reader will search for (a flag, a ticket, a commit, a file) stay, in backticks. A term is
explained where it first appears; there is no glossary section.

## Left out

How the session itself went: the order things were tried in, tool trouble, side-stories.
