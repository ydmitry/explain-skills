# keep-sources: save a fact when you meet it

`keep-sources` is a skill for Claude Code: a folder of instructions, with one script, for work whose result someone will rely on. This page is for someone deciding whether to install it.

- **In one sentence:** each fact the final text may state is saved when it is read, as a row with the words that carry it and the line they stand on, and the script refuses a row whose quote is not in the source.
- **What is shown:** the skill was not measured. A clean check shows that each quote stands in its source, not that the text is true.
- **To install:** `/plugin install explain --marketplace ydmitry/explain-skills` adds this skill and four others to Claude Code: `skimmable-writing`, `deslop-prose`, `check-sources` and `cold-read`. Each works without the others.

## What it is for

The fact recalled at the end of a long chat is not the fact read at its start. The context gets summarised, a number drifts, and the page it came from is no longer in front of the model.

**So a fact is saved when it is met, not recalled when it is written.** The text is later written from the rows, and `check-sources`, another skill of the plugin, reads it against them.

![A long chat, from left to right. The source is in view only while it is read, and the summary that follows keeps a retelling. The row written at that moment reaches the text and the check unchanged.](figures/keep-sources/fig-1.svg)

Figure: A long chat, from left to right. The source is in view only while it is read, and the summary that follows keeps a retelling. The row written at that moment reaches the text and the check unchanged.

## What a row holds

**One folder holds the record of one piece of work:** the file `ledger.jsonl`, with one row for each fact, and `snapshots/`, copies of sources that will not stay. The folder sits beside where the text will be written, as `sources/<short-name>/`.

![A real row and the file it came from. The script looks the quote up in the file, which fixes its line. The reading in plain words may hold only numbers that the quote holds, unless the row carries a calculation, given with --calc.](figures/keep-sources/fig-2.svg)

Figure: A real row and the file it came from. The script looks the quote up in the file, which fixes its line. The reading in plain words may hold only numbers that the quote holds, unless the row carries a calculation, given with `--calc`.

A page, a command's output or a message is saved as a snapshot first and quoted from the copy. When a tool gave its own summary of a page and not the page, that summary is what gets saved, and the row says so.

## What the script refuses

**The script refuses a quote that is not in the source word for word, and a number in the reading that the quote does not hold.** It compares numbers only. Whether a name or a cause in the reading is true to the quote is left to a second reader.

![Three attempts to save the same fact from service.yaml. The first copies the quote from the file and becomes row s01. The second retypes the quote, and the third recalls another number: both are refused.](figures/keep-sources/fig-3.svg)

Figure: Three attempts to save the same fact from `service.yaml`. The first copies the quote from the file and becomes row `s01`. The second retypes the quote, and the third recalls another number: both are refused.

## How to call it

Claude picks the skill up at the start of such work, or you call it as `/explain:keep-sources`. Claude then adds a row each time it reads a fact the text may state, while the source is in front of it. The script records and checks.

| Command | When | What it prints |
|---|---|---|
| `sources.py snap FOLDER NAME` | a source will not stay: a page, an output, a message. The text comes from standard input, `--file` or `--text` | the path of the saved copy |
| `sources.py add FOLDER --source FILE --quote "..." --says "..."` | a fact was read that the text may state | the row's id and its line in the source |
| `sources.py list FOLDER` | before the text states a number, a date or a name, and after the context was summarised | the rows, one line each |
| `sources.py drop FOLDER ID --why "..."` | a fact turned out wrong, or its source changed | the row stays in the file, marked as dropped |
| `sources.py check FOLDER` | before the text is handed over | one line for each problem, then `errors=N` |

**The check looks every quote up again.** Here a source was edited after its row was written:

```
$ sources.py check sources/incident
rows=2
errors=0

(someone edits service.yaml: max_attempts is now 6)

$ sources.py check sources/incident
ERROR s01: the quote is no longer in …/job/service.yaml (the file changed, or the row was written by hand); read the source again and add a new row, then drop this one
rows=2
errors=1
```

## Where it stops

**A clean check means each quote stands in its source and no number crept into the reading.** It does not show three things:

- that the reading is true to its quote;
- that the source is right;
- that the text states only facts that have a row.

A second reader settles the first and the last: `check-sources`.

The skill was not measured, and neither was what it costs: each row is one more command while reading. In one trial on 2026-11-25 Claude Haiku kept 12 rows for one job, and the check printed `errors=0`.

A snapshot can hold private data: command output, a page behind a login, a message. The folder is working material and is not meant to be committed or published.

## What it needs, and its place in the set

**This skill owns the record of where each fact came from.** The script needs Python 3 and nothing else. The set is the five skills of the plugin, and each works alone.
