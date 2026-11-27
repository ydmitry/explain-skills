# explain-skills

Five Claude Code skills for a text that a person reads alone and has to trust: one writes it so that it is easy to skim, one cleans its sentences, two keep it true to its sources, and one tests it on a reader with no context.

**Each skill owns one thing and leaves the rest alone,** so they can run one after another on the same text, and each also works without the others.

| When | Skill | What it does |
|---|---|---|
| While the work runs | `keep-sources` | saves each fact with the words that carry it and the place they stand |
| Writing | `skimmable-writing` | the structure: small sections, the point first, one thing in bold |
| After writing | `deslop-prose` | the sentences: removes what signals without saying; adds nothing |
| Before showing | `check-sources` | a second reader reports what the sources contradict |
| Before showing | `cold-read` | a reader with no context says the point and what stopped them |

A sixth, `explain-well`, owns no part of the text: it is a command that runs the five in this order.

## Install

```
/plugin install explain --marketplace ydmitry/explain-skills
```

Or in two steps, from a shell:

```
claude plugin marketplace add ydmitry/explain-skills
claude plugin install explain@explain-skills
```

The skills are then `/explain:skimmable-writing`, `/explain:deslop-prose`, `/explain:keep-sources`, `/explain:check-sources` and `/explain:cold-read`. Claude also picks one up by itself when a request fits its description. `/explain:explain-well` runs them all in order, and only you can call it.

To use one without the plugin, copy its folder from `skills/` into `~/.claude/skills/`. **The scripts need Python 3 and nothing else.**

## skimmable-writing

**The test is that the text is easy to skim with the eyes.** A reader who looks only at the headings, the bold text and the first sentence of each paragraph gets the story, and can tell which part to stop and read.

The skill asks for:

- the answer first, then one idea in each section of at most 300 words, under a heading that says what is inside;
- an argument as a short paragraph, steps as a numbered list, the same facts over several cases as a table;
- paragraphs of at most 60 words that open with their point, and one thing in bold in each section;
- plain words in place of a name made up during the work, a number with what it covers, a claim with the check that showed it, a fact from a file or a page with a pointer to it;
- for a hand-over: a dated status line, a short summary, and what was ruled out, what is not known and who does what next.

It ships `scripts/skim_check.py`. The check prints what a skimming eye sees and lists what breaks the rules above. It also notes, as a count and not a problem, when three or more headings open with the same word.

Until 2026-11-26 this skill was named `skimmable-markdown`.

## deslop-prose

**Slop is a sentence that signals instead of saying.** The skill lists fourteen tells, from "it's not just X, it's Y" to "I hope this helps", and says what to do with each.

A reference file gives, for each tell, a case where the same turn of phrase stays. It also says what to compare by eye after the rewrite: a lost "not", "only if" or "may".

The pass rewords sentences and nothing else. Headings, lists, tables, bold and code stay as they are, every number, code name and link is kept, and none is added.

It ships `scripts/prose_check.py`:

- `scan` lists the lines that hold a known tell. It is a finder, not a grade.
- `check` compares the file with a copy from before the pass and exits 0 only when the limits above held.

## keep-sources

**A fact is saved when it is met, not recalled when it is written.** In a long chat the context gets summarised, and the page a number came from is no longer in front of the model.

One folder holds the record: a row for each fact, with the quoted words, the file and lines they stand on, and the fact in plain words. A page, a command's output or a message is saved as a snapshot first, and quoted from the copy.

It ships `scripts/sources.py`. `add` refuses a quote that is not in its source word for word, and a number in the plain-words reading that the quote does not hold. `check` looks every quote up again.

A snapshot can hold private data. The folder is working material and is not meant to be committed or published.

## check-sources

**The writer's own check passes what the writer believes.** So a fresh subagent that did not write the text reads it against the sources and reports two kinds of statement: contradicted, and no source.

It ships `scripts/check_sources.py`:

- `brief` writes the reader's instructions: where the text and the sources are, the kept rows, and the numbers and dates of the text that stand in no source.
- `quotes` looks the reader's copied words up. A contradiction counts only when its words are really in the text and in a source, and the command exits 0 when none counts.

A counted contradiction blocks. A statement with no source does not: the writer adds the source, marks the statement as a reading, or cuts it.

## cold-read

**"Can you understand this?" is a question a patient reader always passes.** So a fresh subagent, in the role of the least-informed person the text is for, says the text's one point in two sentences, where it found it, and what it had to guess.

The read blocks on four things: the point is missed, the first screen does not hold it, a word of the point had to be guessed, or a text written for a decision names no next step. Everything else the reader lists is a minor gap.

It has no script. A review asks whether the text is right; this asks whether a reader without the chat gets its point.

## explain-well

**One command that runs the five skills in order on a text someone will rely on.** It holds the order, when a step is skipped and when to stop, and it repeats no rule of the other skills.

The two readers run after every other edit, each at most twice. The report then shows the line each step printed, what the readers found, and what is still open. Claude never starts it on its own: you call it as `/explain:explain-well`.

It is not measured.

## What was measured

**Three checks ran on the skills as they are, on 2026-11-25. `keep-sources` and the main claim are not measured.** The texts are write-ups of four synthetic working sessions of about 3,300 words each. Claude Haiku wrote them, and a second model read them with no other context.

| Claim | What was seen | Measured on |
|---|---|---|
| `skimmable-writing` leaves fewer made-up names that a cold reader cannot say | 0.55 names a write-up against 1.48 with no skill, 40 write-ups each. It gets there by using fewer names, 2.1 against 4.5. | the skill as it is |
| The `check-sources` reader finds false sentences planted in a text | 52 of 60 named, and no false call on those texts. 21 came back as contradicted, 31 as no source. | the skill's own brief, with the text inline and a reader without tools |
| One reply of that reader lists everything | No. It lists a handful. With five false sentences planted in a text it dropped most of what it had reported before, and the count of reported statements rose by 1.75 where the bar asked for 1.78. | the same |
| `deslop-prose` beats a one-line instruction | Not shown: there was no room. Told in one sentence to remove filler, Claude Haiku removed 7.85 of 8 planted sentences and broke no limit, so the comparison was not run. | planted whole sentences only |

## Checks that need no human reader

**Eight checks on 2026-11-26 and 2026-11-27 show no gain from `skimmable-writing` over no skill.** They ran on 80 saved write-ups of the same four sessions: 40 made with no skill, and 40 made with the skill as it stood on 2026-11-25.

A model judge counts as proven only after it moved the right way on damage that a script had planted.

| Question | What was seen | Grader |
|---|---|---|
| Does the skill keep one idea a section better? | No room: with no skill only 5 of 20 write-ups had a section flagged, and the bar for room was 7. | a model judge, proven |
| Does a model prefer the skill's write-up? | No: of 14 pairs it picked each side 3 times and gave no pick 8 times. It picked the text shown first in 27 of 40 calls. | a model asked in both orders, proven |
| Does the skill put key points nearer the top? | Not measured. The score failed two proofs, the second by 0.02 against its bar. | a model judge, not proven |
| Does the `cold-read` reader see planted damage? | Not shown, for any of three conditions. | the skill's reader on Claude Haiku, with the text inline |
| Does that reader block fewer write-ups made with the skill? | No gap shown: it blocked 19 of 20 made with the skill and 18 of 20 made without. | the same reader, not proven |

## What two counts by script found

**No write-up links to its sources, and pages written with the set open most headings with the same word.** A count describes and is not a grade.

| Question | What was seen |
|---|---|
| Does a text point to its sources? | None of the 80 write-ups holds a link. A text written with the whole set, from a record of 71 sourced facts, pointed to none of them. |
| Do the headings open with the same word? | On six of seven pages written with the set, 43% to 71% of them do. In the 80 write-ups the share is 15% with no skill and 18% with it. |
| Do the sections look less alike with the skill? | Not shown. |

Two things were changed on 2026-11-27 after these counts. `skimmable-writing` now asks for a pointer to the source of a fact, and `skim_check.py` notes headings that open with the same word. No writer has been tested with the note.

## The pointer rule, tried on a writer

**With the rule, 15 of 20 write-ups point to a line of a file that their session shows, against 5 of 20 without it.** Claude Haiku wrote both sets on 2026-11-27 from the same four sessions. The two skill texts are the skill before and after commit `cf5d538`, which added the rule and a paragraph on the heading note.

A script looked each pointer up in the transcript the write-up was written from. Of the 83 pointers made with the rule it could not place 2, and both are right on reading. Where a transcript showed no line of any file, the writers made none up.

The writer had a transcript and no files, so this does not show what a writer with tools does. It also does not show that the line a pointer names says what the sentence says.

## What was not measured, or only on earlier forms

**Whether a person finds the text easier to skim was never measured.** The form rules come from one person reading write-ups side by side.

| Claim | What was seen | Measured on |
|---|---|---|
| Claude runs the form check when it can | In 12 of 12 runs; listed problems went from 7.9 to 0. | the same script, an older skill text |
| A count of statements with no source is stable | No: two readings of one text differed as much as planted sentences moved it. This is why "no source" does not block. | an earlier prompt |
| `keep-sources` | Not measured here. | |

A model reader cannot judge whether a text is pleasant to read. Treat the form rules as one person's taste, written down.

## One more step, kept elsewhere

**`illustrate` turns the checked text into one HTML page with figures.** It runs last and is not in this repository.

## Where the patterns come from

The tells in `deslop-prose` follow Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) and the [humanizer](https://github.com/blader/humanizer) skill (MIT), reworded and cut down to sentences. Its formatting rules are left out on purpose: here the structure belongs to the writer.

## Tests

```
cd tests && python3 -m unittest discover -s .
```

## License

MIT
