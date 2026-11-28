# explain-skills

Seven Claude Code skills for a text that a person reads alone and has to trust.

Five work on the words: one writes the text so that it is easy to skim, one cleans its sentences, two keep it true to its sources, and one tests it on a reader with no context. Two show it: one draws a figure for a claim whose structure is the point, and one renders the text as a page.

**Each skill owns one thing and leaves the rest alone,** so they can run one after another on the same text, and each also works without the others.

| When | Skill | What it does |
|---|---|---|
| While the work runs | `keep-sources` | saves each fact with the words that carry it and the place they stand |
| Writing | `skimmable-writing` | the structure: small sections, the point first, one thing in bold |
| After writing | `deslop-prose` | the sentences: removes what signals without saying; adds nothing |
| Before showing | `check-sources` | a second reader reports what the sources contradict |
| Before showing | `cold-read` | a reader with no context says the point and what stopped them |
| After the readers | `draw-figures` | draws each figure the text marks, with labels taken from the text |
| Last, for a page | `render-page` | turns the text into one HTML page that says what the text says |

An eighth, `explain-well`, owns no part of the text: it is a command that runs the seven in this order. A ninth, `show-well`, is the same command with the figures and the page always made.

## Install

```
/plugin install explain --marketplace ydmitry/explain-skills
```

Or in two steps, from a shell:

```
claude plugin marketplace add ydmitry/explain-skills
claude plugin install explain@explain-skills
```

The skills are then `/explain:skimmable-writing`, `/explain:deslop-prose`, `/explain:keep-sources`, `/explain:check-sources`, `/explain:cold-read`, `/explain:draw-figures` and `/explain:render-page`. Claude also picks one up by itself when a request fits its description. `/explain:explain-well` runs them all in order, and only you can call it. `/explain:show-well` does the same and always ends with the page.

To use one without the plugin, copy its folder from `skills/` into `~/.claude/skills/`. **The scripts need Python 3 and nothing else.** Two of them, in `draw-figures` and `render-page`, also measure in a headless browser when the `playwright` package is installed, and say so when it is not.

## skimmable-writing

**The test is that the text is easy to skim with the eyes.** A reader who looks only at the headings, the bold text and the first sentence of each paragraph gets the story, and can tell which part to stop and read.

The skill asks for:

- the answer first, then one idea in each section of at most 300 words, under a heading that says what is inside;
- an argument as a short paragraph, steps as a numbered list, the same facts over several cases as a table;
- paragraphs of at most 60 words that open with their point, and one thing in bold in each section;
- plain words in place of a name made up during the work, a number with what it covers, a claim with the check that showed it, a fact from a file or a page with a pointer to it;
- for a hand-over: a dated status line, a short summary, and what was ruled out, what is not known and who does what next.

It ships `scripts/skim_check.py`. The check prints what a skimming eye sees and lists what breaks the rules above. It also notes, as a count and not a problem, when three or more headings open with the same word.

**The numbers are house style, not findings.** A script needs something to count, so the rules say 60 words, 300 words and one thing in bold. Published studies support the direction and test none of these numbers.

In one study, students recalled underlined sentences better when only those were underlined; with half of the other sentences underlined as well, recall was no better than with no underlining ([Lorch, Lorch and Klusewitz 1995](https://scholars.uky.edu/en/publications/effects-of-typographical-cues-on-reading-and-recall-of-text/), read as the abstract).

Until 2026-11-26 this skill was named `skimmable-markdown`.

## deslop-prose

**Slop is a sentence that signals instead of saying.** The skill lists fourteen tells, from "it's not just X, it's Y" to "I hope this helps", and says what to do with each.

A reference file gives, for each tell, a case where the same turn of phrase stays. It also says what to compare by eye after the rewrite: a lost "not", "only if" or "may".

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
- `shown` looks up every quote the text shows its reader, in quotation marks or a quoted block, and lists the ones no source holds letter for letter. It needs no reader.
- `quotes` looks the reader's copied words up. A contradiction counts only when its words are really in the text and in a source, and the command exits 0 when none counts.

A counted contradiction blocks. A statement with no source does not: the writer adds the source, marks the statement as a reading, or cuts it.

## cold-read

**"Can you understand this?" is a question a patient reader always passes.** So fresh subagents read it, in the role of the least-informed person the text is for. A model cannot forget what it knows, so it reads like an expert from outside: where it gets stuck a person will too, and a pass proves little.

The author's report to you says so in a line of its own.

One gets only the first screen and says what point it gives. A second reads the whole text and says its one point in two sentences, where it found it, and what it had to guess.

The read blocks on four things: the point is missed, the first screen does not hold it, a word of the point had to be guessed, or a text written for a decision names no next step. Everything else the reader lists is a minor gap.

It has no script. A review asks whether the text is right; this asks whether a reader without the chat gets its point.

## draw-figures

**A figure is for a claim whose structure is the point, and the text owns every word of it.** A line `Figure:` with one sentence marks the figure in the text. The two readers read that sentence with the rest, and it becomes the caption.

The skill says which claims get a figure: there must be a second state to contrast, and the drawing must still argue the claim with its labels deleted. It names a shape for each kind of claim, and its references hold the drawing rules: geometry derived from constants, colour by meaning, and a catalog of shapes.

A figure is one SVG file that names no colour. It reads tokens, so it follows a light and a dark screen.

It ships `scripts/figures.py`:

- `brief` writes a plan with a block for each mark: the shape, and every label and value with the place it was taken from.
- `check` lists a typed colour, a label that is not the mark's sentence, and a word or a number that stands neither in the text nor in the plan. With `playwright` it also measures: labels that collide, a box that leaves the canvas, an arrow that lands on nothing.
- `preview` writes a picture of each figure, and `place` finishes the files and writes an image line into the text.

## render-page

**The page is the text, shown: the same words in the same order, made by a script.** To change the page you change the text and render again.

`scripts/render.py` turns the Markdown into one HTML file that carries its figures and pictures inside it and asks the network for nothing. What it cannot show it refuses with the line: raw HTML, a `mermaid` block, a picture from the web.

The page adds a list of its sections and two switches. One follows a light or a dark screen. The other dims everything but headings, bold text and first sentences, which is the skim view of `skimmable-writing` on the page itself.

`scripts/page_check.py` confirms that the page is the render of the text as it is now and that its words are the text's words. With `playwright` it also confirms that nothing is wider than a phone's screen.

## explain-well

**One command that runs the seven skills in order on a text someone will rely on.** It holds the order, when a step is skipped and when to stop, and it repeats no rule of the other skills.

The two readers run after every other edit, each at most twice. The report then shows the line each step printed, what the readers found, and what is still open. Claude never starts it on its own: you call it as `/explain:explain-well`.

It is not measured.

## show-well

**`explain-well` that always ends with a page.** It looks for the claims worth a figure, draws them, renders the text as a page and opens it. You call it as `/explain:show-well`, with what to show.

Its subject is the one thing you point at: "show me that" means the last message, not the whole session.

It is not measured.

## What was measured

**Three checks ran on the skills as they are, on 2026-11-25. `keep-sources` and the main claim are not measured.** The texts are write-ups of four synthetic working sessions of about 3,300 words each. Claude Haiku wrote them, and a second model read them with no other context.

| Claim | What was seen | Measured on |
|---|---|---|
| `skimmable-writing` leaves fewer made-up names that a cold reader cannot say | 0.55 names a write-up against 1.48 with no skill, 40 write-ups each. It gets there by using fewer names, 2.1 against 4.5. | the skill as it is |
| The `check-sources` reader finds false sentences planted in a text | 52 of 60 named, and no false call on those texts. 21 came back as contradicted, 31 as no source. | the skill's own brief, with the text inline and a reader without tools |
| One reply of that reader lists everything | No. It lists a handful. With five false sentences planted in a text it dropped most of what it had reported before, and the count of reported statements rose by 1.75 where the bar asked for 1.78. | the same |
| `deslop-prose` beats a one-line instruction | Not shown: there was no room. Told in one sentence to remove filler, Claude Haiku removed 7.85 of 8 planted sentences and broke no limit, so the comparison was not run. | planted whole sentences only |

## Checks that need no human reader

**Ten checks on 2026-11-26 and 2026-11-27 show no gain from `skimmable-writing` over no skill.** They ran on 80 saved write-ups of the same four sessions: 40 made with no skill, and 40 made with the skill as it stood on 2026-11-25.

A model judge counts as proven only after it moved the right way on damage that a script had planted.

| Question | What was seen | Grader |
|---|---|---|
| Does the skill keep one idea a section better? | No room: with no skill only 5 of 20 write-ups had a section flagged, and the bar for room was 7. | a model judge, proven |
| Does a model prefer the skill's write-up? | No: of 14 pairs it picked each side 3 times and gave no pick 8 times. It picked the text shown first in 27 of 40 calls. | a model asked in both orders, proven |
| Does the skill put key points nearer the top? | Not decided, and no gain: the first 300 words of headings, bold text and first sentences state 4.20 of 12 key points with the skill and 4.75 without, on 20 write-ups each. The gap is about the size of chance and comes from one session. | a model judge, proven at the third try |
| Does the `cold-read` reader see planted damage? | Not shown, for any of three conditions. | the skill's reader on Claude Haiku, with the text inline |
| Does that reader block fewer write-ups made with the skill? | No gap shown: it blocked 19 of 20 made with the skill and 18 of 20 made without. | the same reader, not proven |

## What two counts by script found

**No write-up links to its sources, and pages written with the set open most headings with the same word.** A count describes and is not a grade.

| Question | What was seen |
|---|---|
| Does a text point to its sources? | None of the 80 write-ups holds a link. A text written with the whole set, from a record of 71 sourced facts, pointed to none of them. |
| Do the headings open with the same word? | On six of seven pages written with the set, 43% to 71% of them do. In the 80 write-ups the share is 15% with no skill and 18% with it. |
| Do the sections look less alike with the skill? | Not shown. |

Two things were changed on 2026-11-27 after these counts. `skimmable-writing` now asks for a pointer to the source of a fact, and `skim_check.py` notes headings that open with the same word. No writer has been tested with the note.

## The pointer rule, tried on a writer

**With the rule, 15 of 20 write-ups point to a line of a file that their session shows, against 5 of 20 without it.** Claude Haiku wrote both sets on 2026-11-27 from the same four sessions. The two skill texts are the skill before and after commit `cf5d538`, which added the rule and a paragraph on the heading note.

A script looked each pointer up in the transcript the write-up was written from. Of the 83 pointers made with the rule it could not place 2, and both are right on reading. Where a transcript showed no line of any file, the writers made none up.

The writer had a transcript and no files. It also does not show that the line a pointer names says what the sentence says.

## The pointer rule, on a writer that opens files

**With the rule, 18 of 20 write-ups point to a line that exists, against 0 of 20 without it, and none of 142 pointers leads nowhere.**

On 2026-11-27 Claude Haiku got a folder with one script and its tests, tools to read them, and a request for a hand-over that named no pointer. Four folders, five write-ups each, with the two skill texts of the check above.

A script looked each pointer up in the folder: the file is there and has that line. Without the rule no write-up named a line, and both sets named bare file names about as often, 181 and 183 times. The write-ups are as long in both sets.

The limits: one model, and files of 83 to 352 lines. A rough count found a number or a code word of the sentence on the lines named for 63 of the 142 pointers, and that is not a reading of whether a line says what its sentence says.

## A pointer is trusted whether or not it is right

**The pointer rule is safe only together with `check-sources`.** In a study of 303 people who asked a chatbot their own questions, answers with citations were trusted more than answers without, and the abstract says this held even when the citations were random ([Ding et al. 2025](https://arxiv.org/abs/2501.01303)).

Few readers open a pointer. In one month of English Wikipedia logs, 0.29% of page views included a click on a reference ([Piccardi, Redi, Colavizza and West 2020](https://arxiv.org/abs/2001.08614), read as the abstract). So a text with pointers looks checked to a reader who checks nothing, and a second reader has to look the pointers up before the text is shown.

## The `cold-read` reader, run the way the skill runs it

**Run as a session on Claude Sonnet that opens the file, the reader blocked 7 of 12 write-ups on each of two reads.** On Claude Haiku with the text inline it had blocked 12 of 12. Three runs on 2026-11-27 read 12 write-ups made with no skill, and each run's bars were written first.

| Bar | One reader | Two readers |
|---|---|---|
| Two reads agree on block or pass for at least 10 of 12 write-ups | 8 of 12, not met | 10 of 12, met |
| At most 9 of 12 blocked on each read | 7 and 7, met | 8 and 6, met |
| "The first screen does not hold the point" rises on copies with the opening summary moved to the end | +0.05 against a bar of 0.42, not met | +0.10 against a bar of 0.34, not met |

A guessed word, which had blocked 11 of 12 write-ups on Claude Haiku, was listed in 1 of 24 reads.

The skill asks its reader to read the first screen before the rest. All 34 sessions of the one-reader run opened the whole document at once, so the skill now gives the first screen a reader of its own. The two columns are one round each, and no bar was set for the difference between them.

## What the runs on that reader do not show

**That the reader sees a first screen without the point is not shown.** In three of the ten copies the next section moved up and stated the same point, so the damage was too weak to tell.

The limits: one model as reader and judge, 12 write-ups of four synthetic sessions, and a `claude -p` session with the tool `Read` standing in for a subagent. No write-up here is known to deserve a pass, so nothing shows that a block is right.

## What was not measured, or only on earlier forms

**Whether a person finds the text easier to skim was never measured.** The form rules come from one person reading write-ups side by side.

| Claim | What was seen | Measured on |
|---|---|---|
| Claude runs the form check when it can | In 12 of 12 runs; listed problems went from 7.9 to 0. | the same script, an older skill text |
| A count of statements with no source is stable | No: two readings of one text differed as much as planted sentences moved it. This is why "no source" does not block. | an earlier prompt |
| `keep-sources` | Not measured here. | |
| `draw-figures`, `render-page` | Not measured. Their scripts have tests, and each was tried once by its author on one text. | |

A model reader cannot judge whether a text is pleasant to read. Treat the form rules as one person's taste, written down.

## Credits

**`deslop-prose` adapts published text, and the table lists published work that was read for comparison on 2026-11-21 and 2026-11-22.**

- The tells in `deslop-prose` follow Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) and the [humanizer](https://github.com/blader/humanizer) skill (MIT), reworded and cut down to sentences. Its formatting rules are left out on purpose: here the structure belongs to the writer.

| Work | Bears on | What it is |
|---|---|---|
| [plain-writing-skill](https://github.com/docwriter-org/plain-writing-skill) | `skimmable-writing` | 25 word and sentence rules with an eval harness |
| [docs-writing](https://github.com/mblode/agent-skills) by mblode, since retired | `skimmable-writing` | 51 rules for technical docs: the bottom line first, one idea a section |
| Microsoft, [Scannable content](https://learn.microsoft.com/en-us/style-guide/scannable-content) | `skimmable-writing` | a style-guide page for human writers |
| NN/g, [Concise, Scannable, and Objective](https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/) (1997) | `skimmable-writing` | a reader study of scannable web text |
| [lucid-lint](https://github.com/bastien-gallay/lucid-lint) | its check script | a linter of paragraph and sentence length |
| Suhail Mohebi, [handoff packets](https://suhailmohebi.com/notes/handoff-packets/) | the hand-over rules | a hand-over template with evidence and open questions |
| [Handoff Debt](https://arxiv.org/html/2606.02875) | the hand-over rules | a paper that measures a successor agent given notes or the raw record |
| [review-report](https://github.com/Hiveteq/review-report) | `cold-read` | a diff walkthrough with a fresh reader pass |
| [cold-read-gate](https://www.claudepluginhub.com/skills/laurigates-agent-patterns-plugin-agent-patterns-plugin-2/cold-read-gate) | `cold-read` | a fresh reader that states what a draft asks |
| [Hermes Grounded Citations](https://hermes-agent.nousresearch.com/docs/user-guide/skills/bundled/research/research-grounded-citations) | `keep-sources` | a ledger script that rejects a quote not in the page |
| [citefact](https://github.com/hearthresearch/citefact) | `check-sources` | a checker of verbatim quotes against the cited source |
| [anti-slop-writing](https://github.com/adewale/anti-slop-writing) | `deslop-prose` | a style skill with pre-registered evals |

## Where the figures and the page come from

**`draw-figures` and `render-page` come out of `illustrate`, a skill of the same author that is not public.** It began as an adaptation of [visual-explainer](https://github.com/nicobailon/visual-explainer) by Nico Bailon (MIT), which in turn credits [Anthropic's frontend-design skill](https://github.com/anthropics/skills) and [interface-design](https://github.com/Dammyjay93/interface-design) for ideas.

The drawing rules and the checks here were written after that start, and the page layout was written new. Of the 2,434 lines of the two skills, 3 stand word for word in visual-explainer 0.7.1, and all three are one-line CSS idioms. The count takes lines of 30 characters or more.

## Tests

```
cd tests && python3 -m unittest discover -s .
```

## License

MIT
