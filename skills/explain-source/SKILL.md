---
name: explain-source
description: Use when someone has to understand a source before acting on it (approve, sign, adopt, take over, decide) — a file, a diff, a document, a paper, a contract, a license — or asks to explain, walk through or break down a source that is long or looks familiar, where a missed part would matter.
---

# explain-source

The explanation is written from a **ledger**: one row for each part of the source, with a quote copied from it and the
lines it sits on. The reader gets a short explanation; the ledger makes it checkable, and it is what a page
(`illustrate`), a cold read and a quiz are later built from.

The source you recognise is the dangerous one. A standard license, a well-known library file, a familiar template:
the text you remember explains well and is not the text in the folder. Measured on a GPL-3 copy with five changed or
added clauses: without a ledger, 5 of 5 explanations named none of them and called the file "the standard GPL";
a walk through "the important parts" named all five in 1 of 5.

## Steps

1. **Read every line**, in parts when the file is long. The number of the last line goes in the first ledger row.
2. **Inventory, before any prose.** Walk the source in its own order and write `ledger.jsonl` in
   `.logbooks/understanding/<slug>/`: a row for each part (a section, a clause, a function, a block), so that the rows
   together run from the first line to the last. One clause, one paragraph or one block is one row, 15 lines at most.
   A part that does not matter is still a row, `skipped`, with its range, as long as it needs to be.
3. **Write `explanation.md` from the rows only**, in the same folder: one line saying what the source is and is for;
   then the `core` rows in the source's order, each a sentence or two ending in its row id and lines, `[p07, 426-431]`;
   then one line naming what was skipped. A point that is your reading, not the source's words, starts "Probably" or
   "It looks like".
4. **Check, last:** `python3 ${CLAUDE_SKILL_DIR}/scripts/check_ledger.py .logbooks/understanding/<slug>` until it
   prints `errors=0`. It finds quotes that are not on their lines, rows that are too wide, stretches of the source no
   row covers and core rows the explanation leaves out. An edit to either file after it means running it again.
5. **Reply** with the explanation, as short as was asked, the folder's path, and the check's last two lines as it
   printed them.

"Keep it short" and "ten minutes" shorten the reply: every `core` row whose `differs` is not `no` stays in it. They
never shorten steps 1, 2 and 4.

## A row

```json
{"id": "p07", "source": "LICENSE.txt", "anchor": "426-431", "quote": "you cure the violation prior to 7 days after", "gloss": "A first violation is forgiven only if fixed within 7 days of the notice.", "kind": "stated", "importance": "core", "differs": "the GPL-3 I remember says 30 days"}
```

| Field | Value |
|---|---|
| `id` | `p01`, `p02`, … in the source's order |
| `source`, `anchor` | the file, and the lines the row covers: `120` or `120-140`, from a numbered read |
| `quote` | text copied from those lines, at most 25 words; the words that carry the point (the number, the party, the condition). May be empty on a `skipped` row |
| `gloss` | the point in plain words |
| `kind` | `stated`: the source says it. `inferred`: your reading |
| `importance` | `core`, `supporting` or `skipped` |
| `differs` | only for a source you recognise: what this copy says that the one you remember does not; `no` when you could recite the original's wording for this part and it matches; else `unsure` |

`core` is what the reader would act on or would get wrong:

- **Code:** what the body does where the name, the docstring or the well-known version says something else; what is
  dropped, cut, retried or written silently; defaults, limits and permissions.
- **Documents, contracts, licenses, papers:** who must do what, by when; every number, sum, period and threshold;
  who decides; exceptions and "notwithstanding"; what the authors say their result does not show.
- **A recognised source:** every row whose `differs` is not `no`, `unsure` included: a duty, a fee, a deadline, an
  exclusion or a power you do not positively remember in the original is a difference until checked. Say on the
  explanation's first line that this copy is not the standard one, and how many places differ.

A number, a period, a sum, a name or a condition in a gloss is the quote's, never one you recall.

## What the check does not show

`errors=0` means each quote is on its lines, the rows reach the end of the source and the explanation cites the core
rows. It does not mean a gloss is true to its quote: read each core row's quote against its gloss once before step 4.
