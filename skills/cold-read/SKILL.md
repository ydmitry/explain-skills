---
name: cold-read
description: Use when a document someone will read without the chat (a page, README, spec, PR description, one-pager, hand-over, verdict) is about to be shown or handed off, or when asked for a cold read or whether a reader with no context gets the point.
---

# cold-read

A reader with no context reads the document alone, says its one point in two sentences and where it found it, and
lists what stopped it. "Can you understand this?" is a question a patient reader always passes; "say the point, where
you found it, what you had to guess" is not.

A review asks whether the document is right; a cold read asks whether a reader without the chat gets its point.
illustrate's cold-read audit is the author's checklist while building a page; this is the test afterwards, by a reader.
A page drafted in Markdown is read as the draft, before it is rendered: fixing it there is cheaper.

## The read

Once per document, the reader (a fresh subagent, or you: see below) takes the role of the least-informed person the
document is for (the role given, else the one the document or its brief, the task it was written for, names, else an
engineer new to the team). The role knows its job, not this work. Then:

1. Read only the first screen: the title and 25 lines after it (a page: the visible text before its first section;
   a footnote, small print or a closed block is not on it). Write `first screen:`.
2. Read the rest. Open nothing it names (code, logs, links) and check no fact: the real reader cannot.
3. Write the other lines, and nothing else.

```
first screen: <the point as the first screen gives it, or none>
point: <the document's one point, in two sentences of your own, from the document alone>
guessed: <each word of your point: line whose meaning neither the document nor your role gives, or none>
found: <the heading or line where the point became clear>
do: <what the document asks its reader to do or decide next, or none>
gap: <term|context|why|buried|next> — <heading or line> — <what stopped you; what would fix it>
cut: <a passage that can go without losing the point>
```

Gaps: `term` a name, acronym, ID or label not explained where first used; `context` what only the author's chat, run
or files supply ("as discussed", a role name, a path the reader cannot open); `why` a claim, step or number with no
reason on the page, or broader than the page shows; `buried` the point sits late, low or under detail that does not
serve it; `next` the next step is unclear, split or has no owner. At most 10 gaps and 3 cuts, those on the point's
path first.

## What blocks

A read blocks when any of these holds; every gap is otherwise minor:
1. `point:` misses or contradicts what the document is for (the author's intended point; in a run, its goal).
2. `first screen:` does not hold the point.
3. `guessed:` is not none.
4. The document exists for a decision or an action, and `do:` is none.

## With a subagent tool

0. Read last: make every other edit and check first. The read is of the text as it will be shown.
1. Write the point you intended, in one sentence; keep it from the reader.
2. Dispatch a fresh subagent with this prompt and nothing from the chat: `You are a cold reader: <the
   role, e.g. a product manager on the team, who was not in this work>. You are the reader; dispatch no one. Read
   <absolute path> and follow "The read" in ${CLAUDE_SKILL_DIR}/SKILL.md. Reply with its lines only.`
3. Compare its `point:` with your sentence; apply What blocks. Fix every blocking gap, and a minor one when its fix is a
   line, by adding (the point on the first screen, a gloss, a reason, the next step); cut only what a `cut:` names.
4. After a blocking read and your fixes, one more read by a new subagent. Two reads at most; then show the document
   with three lines: what the reader got, what you changed, what is still open.
5. Keep each reader's reply whole where whoever judges your work can open it: in the notes directory when your
   instructions give one (`cold-read-1.md`, `cold-read-2.md`, the document's path on top), else in your reply. A judge
   cannot open your subagent's session, and a summary of its lines is not the read.

An edit after a read, other than a fix that read asked for, leaves the shown text unread: read again, by a new
subagent, before showing it.

## Without a subagent tool

You are the reader. Open the document before the brief, the diff, the code or any notes, and do The read; then read
what the document is for and apply What blocks. You cannot unread a goal your input gave you: every word of `point:`
comes from the document, and one you know only from your input goes in `guessed:`.

## Judging a run's result

When your reply ends in `done:`, `why:` and `note:` lines (you judge a run's result against its Definition of done),
the read is yours, of the document as it now stands. The author's reads are not your evidence: one may predate the
last edit, and its reader may have known the brief. With a subagent tool, dispatch a new subagent for it (the prompt
in "With a subagent tool", step 2); without one, you are the reader. Your read's lines go in the observation above
your `done:` line. If the Definition of done asks for a cold read, a blocking read makes it `done: no`, with
`why: cold read: <which of the four holds, and where>`. Otherwise every gap is a note, never a reason for no:
`note: cold read: <kind> — <where> — <what>`, blocking ones first.

## With the other skills

This skill owns one question: does a reader with no context get the point. `check-sources` asks the other one, whether
the text says what its sources say. Both read the text as it will be shown, after `skimmable-markdown` and
`deslop-prose`. Each works without the others.
