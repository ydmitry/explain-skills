---
name: explain-well
description: Runs the whole explain set, in order, on one text someone will rely on - keep-sources, skimmable-writing, deslop-prose, check-sources, cold-read, then draw-figures for the figures the text marks and render-page when a page is asked for. Called by the user only.
argument-hint: "[what to write, or the file to finish]"
disable-model-invocation: true
---

# explain-well

One command for a text someone will rely on: a report, findings, a write-up, a README. What was asked for: $ARGUMENTS

**This skill owns the order, when a step is skipped and when to stop, and nothing else.** The rules of each step are in that step's skill. Load the skill when you reach its step and follow it. Nothing of it is repeated here.

## The order

| Step | When | Skill | Done when |
|---|---|---|---|
| 1 | While the work runs | `keep-sources` | `sources.py check` prints `errors=0` |
| 2 | Writing | `skimmable-writing`, and `draw-figures` for which claims get a `Figure:` line | `skim_check.py` prints `problems=0` |
| 3 | After writing | `deslop-prose` | `prose_check.py check` prints `errors=0`, and the check of step 2 still prints `problems=0` |
| 4 | Before showing | `check-sources` and `cold-read`: two fresh readers of the same final text | the last line of `check_sources.py quotes` shows `counted=0`, and none of the four conditions of `cold-read` holds |
| 5 | After the readers, when the text has a `Figure:` line | `draw-figures` | `figures.py check` prints `problems=0`, and each picture was looked at |
| 6 | Last, only when a page is asked for | `render-page` | `page_check.py` prints `problems=0` |

**Every edit comes before the readers.** They read the text as it will be shown, `Figure:` lines included, so the two can be dispatched at the same time. Steps 5 and 6 add no sentence: a figure's labels come from the text, and the page is the text.

## Where to start

- **Nothing is written yet:** start at step 1, and keep rows from the first fact on.
- **The work is done and no record was kept:** start at step 2. Do not rebuild a record from memory. In step 4 give `check-sources` the files, the transcript or the notes the text was written from, and say in the report that no record was kept.
- **A draft exists:** start at step 2, as a rewrite that keeps every fact.

## After a read

1. Fix what blocks: a counted contradiction from `check-sources`, or a condition of `cold-read` that holds.
2. Run the form check of step 2 and the scan of `deslop-prose` again on the changed text. Do not run its `check` again: it compares with the copy from before the sentence pass, and a fix for a reader adds what that pass may not.
3. Dispatch a new reader for each read that blocked. Dispatch a new `check-sources` reader as well whenever a fix added or changed a statement of fact.
4. **Two reads at most for each reader,** four in all. Stop then, whatever the second read says.

A fix made after the last read has been read by no one. List it as open.

## What to skip

- **A text under about 300 words, or one nobody will rely on:** this command is too much. Write it with `skimmable-writing` alone.
- **No sources at all,** as for an opinion or a plan from scratch: skip step 1 and `check-sources`, and say so.
- **No tool that starts a subagent:** the writer is the reader, which is weaker. Say so.

## The report

Show the text, then three things:

- **The line each step printed,** copied from its output. A step with no line is reported as not run.
- **What the readers found,** and what was changed for it.
- **What is still open:** a blocking finding left after the second read, a fix no reader has seen, a statement with no source.
