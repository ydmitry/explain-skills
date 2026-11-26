---
name: deslop-prose
description: Use after writing, as the last pass over the sentences of a text before it is checked and shown, or when prose reads as machine-written or padded (stock AI words, "not X but Y", staged openers, one-line closers, forced threes, inflated claims, chat leftovers), or when asked to deslop, de-AI, humanize or tighten a text.
---

# deslop-prose

Slop is a sentence that signals instead of saying. The reader's eye stops on it and gets nothing, and after a few such stops they trust the rest less.

**Each sentence that stays gives the reader something they did not have.**

## What this pass may change

Only the wording of sentences, in paragraphs, list items and table cells. **It removes and rewords. It adds no fact, no example and no opinion.**

It leaves as they are: the headings, the number of list items and table rows, what is in bold, code and inline code, links, and every number, name, date and quote. The words inside bold may be reworded; the bold stays. Structure belongs to whoever wrote the text, or to `skimmable-writing`.

A sentence that holds a fact keeps the fact. Only a sentence with no fact in it is cut whole.

## Tells that stage the point

These signal that something matters without saying it. **One sighting is enough to act.**

| Tell | Looks like | Do |
|---|---|---|
| A contrast nobody asked for | "It's not just a cache, it's a strategy." "This isn't about speed." | State the positive half. Keep the contrast only when the reader really holds the first belief. |
| A run-up | "Let's dive in." "Here's the thing." "It's worth noting that" "The hard part is" | Delete it and open with the point. |
| A closer that repeats | "That's the real win." "Overall, caching matters." A last line that names what the example just showed. | Cut it. A last sentence stays when it adds a fact or a consequence. |
| A saying that sounds deep | "At its core" "The real question is" "Trust is the currency of teams" | Say the specific claim. |
| Arguing with no one | "To be clear" "Some might say" "A tempting approach would be" | Remove the defence. Keep an objection the reader would raise. |
| Threes by habit | "fast, simple and reliable" Three parallel examples. | Keep the items that each say something, often one or two. A real list of three stays. |
| A dash for every join | "The fix — shipped Tuesday — works" | Choose the comma, colon or full stop that says how the parts relate. |
| Stacked hedges | "could potentially" "it might arguably" | One hedge, and only where the doubt is real. |

## Tells that inflate, and leftovers

The fact underneath is usually sound. **Keep the fact and remove the dressing.**

| Tell | Looks like | Do |
|---|---|---|
| Stock words | delve, pivotal, crucial, seamless, leverage, landscape, testament, showcase, foster, additionally, moreover | Use the plain word or drop it. |
| Inflated weight | "plays a key role" "marks a pivotal moment" "stands as" "serves as" | Say what it is or does: "is", "has", the fact. |
| An -ing phrase bolted on | ", highlighting the importance of..." ", ensuring reliability" | Cut it, or make it a sentence with its own fact. |
| Borrowed authority | "experts say" "studies show" "it is widely believed" | Name who said it when the text already has that. Otherwise make it the text's own claim, or cut it. |
| Chat leftovers | "Great question!" "I hope this helps" "Let me know if" "As of my last update" | Delete. |
| The text about itself | "This section covers" "As mentioned above" | Delete. The reader can see it. |

## When to leave it

- **Not prose of this text:** a quotation, a title, a name, code, or a passage that discusses the phrase.
- **A technical sense:** a robust estimator, a key in a map, a landscape page.
- **Weak alone:** one dash, one hedge or one "associated with" in a text that shows no other tell.
- **A person's voice:** informal text a person wrote is not slop. Lowercase, fragments and anger stay.

A text with no tell goes back unchanged. Say so.

For each tell, `${CLAUDE_SKILL_DIR}/references/keep-cases.md` gives one edit and one case where the same turn of phrase stays, and five weaker tells. Read it before cutting a sentence whole, and when a listed line may be carrying information.

## The pass on a file

1. **Keep a copy:** `python3 ${CLAUDE_SKILL_DIR}/scripts/prose_check.py start FILE`.
2. **List the known tells:** `python3 ${CLAUDE_SKILL_DIR}/scripts/prose_check.py scan FILE`. It finds words, not slop: a listed line may be fine.
3. **Read the whole text once** for what the scan cannot see: threes, closers that repeat, a paragraph that says nothing new.
4. **Rewrite sentence by sentence.** State the point directly. Swapping a listed word for its synonym leaves the same empty sentence.
5. **Check the limits:** `python3 ${CLAUDE_SKILL_DIR}/scripts/prose_check.py check FILE` until it prints `errors=0`. It compares with the copy: same headings, lists, tables, bold and code, every number, code name and link kept, none added. When a number stood only in a sentence that had to go, pass `--gone "3"`.
6. **Read the rewrite against the copy for meaning.** The check cannot see a lost "not", "only if" or "may", or an opinion that lost its owner. What to compare is in the last section of `${CLAUDE_SKILL_DIR}/references/keep-cases.md`.
7. **Scan again.** A line still listed stays only for a reason under "When to leave it".

When the text was written with `skimmable-writing`, run its check again afterwards.

Then report three things: the tells found, the ones left and why, and the words before and after.

## Pasted text

With no file, do the same in the reply without the scripts. Return the rewritten text, then one line for each fact-bearing sentence you cut or merged.

## With the other skills

This skill owns the wording of sentences and nothing else. It runs after `skimmable-writing`, which owns the structure, and before `check-sources` and `cold-read`, which read the text as it will be shown. Each works without the others.
