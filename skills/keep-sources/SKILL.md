---
name: keep-sources
description: Use while the work runs, from its start, when its result is one someone will rely on (research, an investigation, a review, a comparison, a write-up) and its facts will come from files, web pages, command output or what people said; when asked to keep, save or track sources; or when a long chat is about to state numbers, dates, names or quotes it met earlier.
---

# keep-sources

The fact you recall at the end of a long chat is not the fact you read at its start. The context gets summarised, a number drifts, and the page it came from is no longer in front of you.

**So each fact the final text may state is saved when you meet it,** with the words that carry it and the place they stand. The text is later written from these rows, and `check-sources` reads it against them.

## The folder

**One folder for one piece of work:** `sources/<short-name>/` beside where the text will be written, or any folder you can write to when the work has no project folder. Tell the user its path once. Below it is `FOLDER`.

It holds `ledger.jsonl`, one row for each fact, and `snapshots/`, copies of sources that will not stay.

## When to add a row

Add a row when you read something the final text may state as a fact: a number, a date, a name, a limit, a decision, a cause, who said what. **Add it then,** before the next step, while the source is in front of you.

No row for every line you read, and none for what any reader of the subject already knows.

## A source that stays: a file

```
python3 ${CLAUDE_SKILL_DIR}/scripts/sources.py add FOLDER --source src/billing/retry.py --quote "MAX_RETRIES = 5" --says "A failed charge is retried 5 times."
```

- **`--quote` is copied from the file,** 40 words at most: the words that carry the number, the name or the condition. The script finds them in the file and records the lines. It refuses a quote that is not there word for word.
- **`--says` is the fact in plain words.** A number in it is the quote's, never one you recall: the script refuses a number the quote does not hold.
- **`--calc "600 s is 10 minutes"`** goes with a number that follows by arithmetic, or that stands in the quote as a word.

## A source that will not stay: a page, an output, a message

Save it first, then quote from the saved copy.

```
curl -s https://example.com/pricing | python3 ${CLAUDE_SKILL_DIR}/scripts/sources.py snap FOLDER pricing-page --origin "https://example.com/pricing"
make test 2>&1 | python3 ${CLAUDE_SKILL_DIR}/scripts/sources.py snap FOLDER test-run-1 --origin "make test, before the fix"
python3 ${CLAUDE_SKILL_DIR}/scripts/sources.py snap FOLDER lead-on-deadline --origin "the user, in this chat" --text "We cannot ship after the 14th."
python3 ${CLAUDE_SKILL_DIR}/scripts/sources.py add FOLDER --source FOLDER/snapshots/test-run-1.txt --quote "3 failed, 212 passed" --says "Before the fix 3 of 215 tests failed." --calc "3 + 212 = 215"
```

**Save what you actually read.** When a tool gave you its own summary of a page and not the page, save that summary and say so in `--origin` ("a fetch tool's summary of https://..."). The row then shows the fact is second-hand.

A snapshot is a record: the script will not overwrite one with other text. A second run of a command gets a new name.

## Use the rows

- **Write from the rows.** Before the text states a number, a date or a name, run `python3 ${CLAUDE_SKILL_DIR}/scripts/sources.py list FOLDER` and take it from there.
- **After the context was summarised,** run `list` before anything else. The summary is a retelling; the rows are the record.
- **When a fact turns out wrong, or its source changed,** run `drop FOLDER s04 --why "the config was edited"` and add the new row. A dropped row stays in the file.
- **Before the text is handed over,** run `check FOLDER` until it prints `errors=0`. It looks every quote up again.

## What a clean check does not show

`errors=0` means each quote stands in its source and no number crept into `says`. It does not show that `says` is **true to its quote,** that the source is right, or that the text states only facts that have a row. A second reader settles the first and the last: `check-sources`.

## Private material

A snapshot can hold what should not leave the machine: command output, a page behind a login, a message. **The folder is working material.** Do not commit, publish or attach it unless the user asks.

## With the other skills

**This skill owns the record of where each fact came from.** `check-sources` reads the finished text against it, and the rule in `skimmable-writing` that a claim carries its check is easy to meet from a row. Each works without the others.
