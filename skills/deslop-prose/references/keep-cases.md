# The case to keep for each tell, and what the check cannot see

Read this before cutting a sentence whole, when a listed line may be carrying information, and for the meaning read after the rewrite. **Each tell has a look-alike that carries information.** The question each time is what the reader would lose.

Each row gives one edit and one case where the same turn of phrase stays. The examples are made up.

## Staging tells that open or close a point

**The construction stays when each of its parts tells the reader something.**

| Tell | Reword | Keep |
|---|---|---|
| A contrast nobody asked for | "It's not a workaround, it's a fix." becomes "It is a fix." | "The flag changes the log level, not the log file." The reader could expect either. |
| A run-up | "It's worth noting that the job retries twice." becomes "The job retries twice." | "Before you run this, stop the worker." It changes what the reader does first. |
| A closer that repeats | "The build now takes four minutes. That is a real improvement." ends after the first sentence. | "That left an hour to rerun the migration." It says why the four minutes mattered. |
| A saying that sounds deep | "Caching is about trust. Users cannot see how old a price is." keeps the second sentence. | A comparison that explains a mechanism the reader does not know. |

When a saying is the only sentence and the point behind it is missing, leave it and name it in the report. The pass adds no fact, so it cannot supply the point.

## Staging tells inside a sentence

**A limit is not a hedge:** "only on staging" and "at least" are claims, and they stay.

| Tell | Reword | Keep |
|---|---|---|
| Arguing with no one | "To be clear, nobody blames the engineer on call. The alert fired 40 minutes late." keeps the second sentence. | The same words when someone in the thread did ask whose fault it was. |
| Threes by habit | "fast, simple and reliable", where the text shows only the speed, becomes the speed with its number. | "Restart the worker, the scheduler and the cache, in that order." The reader acts on all three. |
| A dash for every join | "The deploy stalled — the queue was full — and we scaled up." becomes "The deploy stalled because the queue was full, so we scaled up." | A range such as 12–18, and the punctuation inside a quotation or code. |
| Stacked hedges | "might possibly reduce timeouts" becomes "might reduce timeouts". | The one hedge on a real doubt, and every limit: "only on staging", "at least", "up to", "usually". |

Write "because" for a dash only when the text says the first part caused the second. Otherwise make two sentences.

## Tells that inflate, and leftovers

**The fact under the dressing stays, with every word that limits it.**

| Tell | Reword | Keep |
|---|---|---|
| Stock words | "leverages the index to facilitate lookups" becomes "uses the index for lookups". | A word in its technical sense. When "robust" stands for a tested guarantee that the text states, say the guarantee. |
| Inflated weight | "The release marks a turning point: a cold start fell from 9 s to 2 s." becomes "A cold start fell from 9 s to 2 s." | "The replica serves as the primary during a failover." "Is the primary" would lose that the role is temporary. |
| An -ing phrase bolted on | "We added a retry, ensuring reliability." becomes "We added a retry." | "The script deleted 12 rows, skipping two that were locked." The phrase holds an action and a number. |
| Borrowed authority | "Experts agree the redesign is confusing", where the text has one tester's note, becomes "One tester found the redesign confusing." | An attribution the text has. "Two reviewers reported a slowdown" does not become "There is a slowdown". |
| Chat leftovers | "Certainly! Here is the summary." and "Let me know if you want changes." go. | "Tell me by Thursday if you need access." It is a request to this reader. |
| The text about itself | Under the heading "How to cancel", "This section explains how to cancel." goes. | "Only the account owner can cancel.", and a method note such as "Failed runs are not counted." |

## Five more tells, each weak alone

**Act on one of these only beside other tells, or when the sentence hides who did something.** They are not in the skill's two tables, and the scan does not list them.

| Tell | Reword | Keep |
|---|---|---|
| The same opening, sentence after sentence | "The worker reads the queue. The worker reads the retry count. The worker schedules the job." becomes "The worker reads the queue and the retry count, then schedules the job." | Parallel openings that make a comparison easy to scan. Never rename the thing to avoid repeating its name. |
| A passive that hides who acts | "Approval is then given by the duty manager." becomes "The duty manager then approves it." | "Three records were deleted.", when the text does not say by whom. Naming someone adds a claim. |
| A vague link in place of a role | "was associated with the project, serving as its maintainer" becomes "maintained the project". | The vague words, when they are all the text knows. |
| Sales words in a neutral text | "boasts a stunning dashboard" becomes "has a dashboard". | An advert, and a person's own opinion: "I loved the dashboard." |
| A disclaimer, then a guess | "Details are scarce, but it probably shipped in 2019." becomes "It probably shipped in 2019." | "Logs before March were not read." It limits what the text can claim, and it does not become "There were no logs before March". |

## The meaning read, after the rewrite

**The script compares what it can count, and it cannot tell that a sentence now says something else.** `prose_check.py check` looks at headings, lists, tables, bold, code, numbers and links. A rewrite can pass it and still change a claim.

So read each changed sentence against the copy for these six:

- **A negation:** "not", "never", "no longer".
- **A condition:** "only if", "unless", "while".
- **A limit:** "only on staging", "at least", "up to", "usually".
- **A hedge on a real doubt:** "may", "might", "probably".
- **Who said it:** an opinion stays with the person who holds it.
- **What was seen and what was concluded:** "the logs show" is not "the cause was".

| | The sentence |
|---|---|
| Before | "It should be noted that the cache may return stale prices, but only for items changed in the last minute." |
| A good rewrite | "The cache may return stale prices, but only for items changed in the last minute." |
| A bad rewrite | "The cache returns stale prices for recently changed items." It lost "may" and widened "the last minute". |

Restore whatever the reader would act on differently. When the two pull apart, keep the sentence that says what the copy said, with the tell left in.
