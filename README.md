# explain-skills

Two Claude Code skills for explaining something to a person who was not there and reads alone.

| Skill | Use it when | What it produces |
|---|---|---|
| `explain-context` | A working session ended and someone else needs what it found or decided: a hand-over, findings for a lead, a decision to sign off. | A Markdown write-up in many small sections that is easy to skim. |
| `explain-source` | Someone has to understand a file, a diff, a paper, a contract or a license before acting on it, and the source is long or looks familiar. | A short explanation backed by a ledger that covers every part of the source. |

## Install

```
/plugin install explain --marketplace ydmitry/explain-skills
```

Or in two steps, from a shell:

```
claude plugin marketplace add ydmitry/explain-skills
claude plugin install explain@explain-skills
```

The skills are then `/explain:explain-context` and `/explain:explain-source`. Claude also picks them up by itself when
a request fits their description.

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

## explain-source

A model that recognises a source tends to explain it from memory. In the test, a license text looked like GPL-3 but
had five changed or added clauses. Without a skill, Claude Haiku named none of them in five runs.

The skill makes Claude read the source in order and keep a ledger: one row for each part, with a quote copied from it
and the lines it sits on. A script, `scripts/check_ledger.py`, checks that the rows cover the whole source. The explanation is written
from the ledger.

| | No skill | `explain-source` |
|---|---|---|
| Changed clauses named, of 25 (5 clauses, 5 runs) | 0 | 22 |

The cost is real: a run took 2 to 4 minutes and 6 to 10 times the tokens of a plain answer. On short sources that
Claude does not recognise, the plain answer was already complete, so the skill is for the long and the familiar.

## License

MIT
