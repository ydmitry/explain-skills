# explain-skills

Five Claude Code skills for a text that a person reads alone and has to trust: one writes it so that it is easy to skim, one cleans its sentences, two keep it true to its sources, and one tests it on a reader with no context.

**Each skill owns one thing and leaves the rest alone,** so they can run one after another on the same text, and each also works without the others.

| When | Skill | What it does |
|---|---|---|
| While the work runs | `keep-sources` | saves each fact with the words that carry it and the place they stand |
| Writing | `skimmable-markdown` | the structure: small sections, the point first, one thing in bold |
| After writing | `deslop-prose` | the sentences: removes what signals without saying; adds nothing |
| Before showing | `check-sources` | a second reader reports what the sources contradict |
| Before showing | `cold-read` | a reader with no context says the point and what stopped them |

## Install

```
/plugin install explain --marketplace ydmitry/explain-skills
```

Or in two steps, from a shell:

```
claude plugin marketplace add ydmitry/explain-skills
claude plugin install explain@explain-skills
```

The skills are then `/explain:skimmable-markdown`, `/explain:deslop-prose`, `/explain:keep-sources`, `/explain:check-sources` and `/explain:cold-read`. Claude also picks one up by itself when a request fits its description.

To use one without the plugin, copy its folder from `skills/` into `~/.claude/skills/`. **The scripts need Python 3 and nothing else.**

## skimmable-markdown

**The test is that the text is easy to skim with the eyes.** A reader who looks only at the headings, the bold text and the first sentence of each paragraph gets the story, and can tell which part to stop and read.

The skill asks for:

- the answer first, then one idea in each section of at most 300 words, under a heading that says what is inside;
- an argument as a short paragraph, steps as a numbered list, the same facts over several cases as a table;
- paragraphs of at most 60 words that open with their point, and one thing in bold in each section;
- plain words in place of a name made up during the work, a number with what it covers, a claim with the check that showed it;
- for a hand-over: a dated status line, a short summary, and what was ruled out, what is not known and who does what next.

It ships `scripts/skim_check.py`. The check prints what a skimming eye sees and lists what breaks the rules above.

## deslop-prose

**Slop is a sentence that signals instead of saying.** The skill lists fourteen tells, from "it's not just X, it's Y" to "I hope this helps", and says what to do with each.

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

## What was measured

**Little, and none of it on these skills as they are now.** The numbers below come from their earlier forms, on four synthetic working sessions of about 3,300 words each. Claude Haiku wrote them up, and a second model read each write-up with no other context.

| Claim | What was seen | Carries over? |
|---|---|---|
| A cold reader can say what a made-up name stands for | 0.50 names a write-up it could not say with the rule, 1.15 without | The rule was in `explain-context`, a skill since removed. It is now in `skimmable-markdown`; not measured there. |
| Claude runs the form check when it can | in 12 of 12 runs; listed problems went from 7.9 to 0 | Same script, older skill text. |
| A second reader finds planted contradictions | 60 of 60 named, about one false call in two pages | Measured with the prompt that `check-sources` adapts, not with its brief. |
| A count of statements with no source is stable | No: two readings of one text differed as much as planted sentences moved it | This is why "no source" does not block. |
| `skimmable-markdown` makes a text easier to skim | Not measured. Model readers showed no difference; the rules come from one person reading write-ups side by side. | |
| `deslop-prose`, `keep-sources` and `cold-read` | Not measured here. | |

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
