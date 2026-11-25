# explain-skills

Two Claude Code skills for texts a person reads alone: one writes up a working session, one makes any longer text
easy to skim.

`explain-context` is for the end of a working session, when someone else needs what it found or decided: a
hand-over, findings for a lead, a decision to sign off. It produces a Markdown write-up in many small sections that
is easy to skim.

`skimmable` is for any text over about 300 words (a report, a README, a design note, a long answer). It holds the
rules on form only: small sections, the point first, one thing in bold, the form that fits the content.

## Install

```
/plugin install explain --marketplace ydmitry/explain-skills
```

Or in two steps, from a shell:

```
claude plugin marketplace add ydmitry/explain-skills
claude plugin install explain@explain-skills
```

The skills are then `/explain:explain-context` and `/explain:skimmable`. Claude also picks one up by itself when a
request fits its description.

To use one without the plugin, copy its folder from `skills/` into `~/.claude/skills/`.

## explain-context

**The test is that the write-up is easy to skim with the eyes.** A reader who looks only at the headings, the bold
text and the first sentence of each paragraph gets the story, and can tell which section to stop and read.

The skill asks for:

- a status line and a short summary first;
- one small section for each job the write-up has (100 to 300 words);
- the form the content has: an argument as a short paragraph, steps as a numbered list, repeated measurements as a
  table, separate items as bullets;
- one thing in bold in each section, and paragraphs of at most 60 words.

It ships a check, `scripts/skim_check.py`. The check prints what a skimming eye sees and lists what breaks the rules
above. Claude runs it on the file and fixes what it lists.

### What was measured

Four synthetic sessions of about 3,300 words each, written up by Claude Haiku. A second model read each write-up
with no other context and answered 16 questions about details.

| Write-up | Words | Detail questions right | Gist from the first 150 words |
|---|---|---|---|
| No skill | 1,205 | 65% | 32% |
| No skill, asked for 2,000 words | 2,013 | 75% | 26% |
| `explain-context` | 1,568 | 75% | 39% |
| The session transcript itself | 3,300 | 88% | 0% |

In 12 further runs where Claude could run the check, it ran it every time. The write-ups went from 7.9 listed
problems to 0, with the same length and the same score on the detail questions.

What the numbers do not show: whether a person finds the write-up pleasant to read. A model reader cannot judge that.
The rules on form come from one person reading the write-ups side by side.

## skimmable

**The same test, for any text: it is easy to skim with the eyes.** The rules are about form; what the text says, and
how much of it, comes from the task, and a rewrite keeps every fact.

The skill asks for:

- the answer first, then one idea in each section of at most 300 words, under a heading that says what is inside;
- an argument as a short paragraph, steps as a numbered list, the same facts over several cases as a table;
- paragraphs of at most 60 words that open with their point, and one thing in bold in each section;
- no headings at all under about 300 words.

It ships the same check, `scripts/skim_check.py`.

### What was measured

Less than for `explain-context`. On the four synthetic sessions, model readers and judges showed no difference
between `skimmable` write-ups and no-skill ones: in the names a cold reader cannot say, in side-stories let in, and
in statements the session contradicts. Whether the text is easier for a person to skim was not measured; the rules
come from one person reading write-ups side by side.

## License

MIT
