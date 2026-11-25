---
name: check-sources
description: Use when a text that states facts (a report, findings, a write-up, a README, an answer with numbers) is about to be shown or handed off and what it was written from is at hand (a keep-sources folder, files, a transcript, notes, a diff), or when asked whether a text says what its sources say.
---

# check-sources

The writer's own check passes what the writer believes. So **a second reader,** one who did not write the text, reads it against the sources and reports each statement the sources contradict.

A review asks whether the work is right. This asks something narrower: does the text say what its sources say?

## What it needs

- **The text as a file.**
- **The sources:** a `keep-sources` folder (`--sources FOLDER`), the files the text was written from (`--source FILE`, as many as there are), or both. A transcript, notes, a diff and data all count.

With no source at hand there is nothing to read against. Say so and do not run the check.

## The check

Read last: make every other edit first, `deslop-prose` included. The check is of the text as it will be shown.

1. **Write the brief:** `python3 ${CLAUDE_SKILL_DIR}/scripts/check_sources.py brief TEXT --sources FOLDER --source FILE`. It prints the brief's path. A line that starts `STALE` names a kept row whose quote is no longer in its source: read that source again before going on.
2. **Dispatch a fresh subagent** with this prompt and nothing from the chat: `You check a text against its sources. You are the reader; dispatch no one. Read <the brief's path> and do exactly what it says. Reply with the blocks it asks for and nothing else.`
3. **Save the reply whole** as a file beside the text or in the sources folder (`check-reply-1.md`).
4. **Look the reader's words up:** `python3 ${CLAUDE_SKILL_DIR}/scripts/check_sources.py quotes REPLY TEXT --sources FOLDER --source FILE`. A `contradicted` block counts only when its copied words are really in the text and in a source. It prints one line for each block and exits 0 when none counts.

## What blocks, and the fix

**A counted `contradicted` line blocks.** The text takes what the source says. When you believe the source is the one that is wrong or out of date, do not overrule it in silence: add the newer source, and let the text say which one it follows.

**A `no source` line does not block.** For each one, do one of three things: add its source, mark the statement as your reading ("Probably", "It looks like"), or cut it.

After a fix to a counted line, write a new brief and have a new subagent read once more. Two reads at most. Then show the text with three lines: what the reader found, what you changed, what is still open.

## Without a subagent tool

You are the reader, and you wrote the text, so **this read is weaker.** Write the brief, then read the sources before the text and go statement by statement. Write your blocks to a file and run `quotes` on it. Say in your report that the reader was the writer.

## What it cannot show

- **A source that is wrong.** The reader compares; it does not know better than the source.
- **A source nobody saved.** A fact with no source shows up as `no source`, never as contradicted.
- **Support far away.** One reader reads a long source once and can miss a passage. That is why `no source` does not block. In a test of the prompt this brief is adapted from, a count of unsupported statements moved as much between two readings of one text as it did when false sentences were planted. Contradictions held: that reader named 60 of 60 planted ones.

## With the other skills

This skill owns one question: does the text say what its sources say. `keep-sources` builds the folder it reads best from. `cold-read` asks the other question, whether a reader with no context gets the point. Each works without the others.
