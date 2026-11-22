#!/usr/bin/env python3
"""Check that a Markdown write-up is easy to skim: python3 skim_check.py FILE [--skim]

Prints one line per problem and `problems=N`. Exit 0 when there are none.
--skim prints what a skimming eye sees: the headings, the bold text and each
paragraph's first sentence. Read that view alone: it should tell the story.
"""
import re
import sys

MAX_PARA = 60      # words in one prose paragraph
MAX_SECTION = 300  # words in one section
MAX_BULLET_RUN = 8 # bullets in a row before the eye stops reading them
MAX_BOLD = 0.15    # share of a section's words in bold


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    text = open(args[0]).read()
    sections = [s for s in re.split(r"(?m)^(?=#{1,6} )", text) if s.strip()]
    problems, skim = [], []
    for sec in sections:
        lines = sec.split("\n")
        head = lines[0].strip() if lines[0].startswith("#") else "(before the first heading)"
        body = lines[1:] if lines[0].startswith("#") else lines
        name = head.lstrip("# ")[:50]
        skim.append("\n" + head)
        words = len(" ".join(body).split())
        bold = " ".join(re.findall(r"\*\*(.+?)\*\*", " ".join(body)))
        if words > MAX_SECTION:
            problems.append(f"{name}: section is {words} words (over {MAX_SECTION}); split it")
        if words > 40 and not bold:
            problems.append(f"{name}: nothing in bold; mark the one thing that matters most here")
        if words and len(bold.split()) / words > MAX_BOLD and words > 40:
            problems.append(f"{name}: {100 * len(bold.split()) // words}% of the section is bold; keep the label and one key point")
        run = 0
        for line in body + [""]:
            if re.match(r"\s*([-*]|\d+\.) ", line):
                run += 1
                continue
            if run > MAX_BULLET_RUN:
                problems.append(f"{name}: {run} bullets in a row; group them under labels or use a table")
            run = 0
            if not line.strip() or line.startswith("|") or line.startswith(("```", ">")):
                continue
            n = len(line.split())
            first = re.split(r"(?<=[.!?])\s", line.strip())[0]
            skim.append("  " + (first if len(first) < 160 else first[:157] + "..."))
            if n > MAX_PARA:
                problems.append(f"{name}: paragraph of {n} words (over {MAX_PARA}) starting \"{line.strip()[:40]}\"")
        for b in re.findall(r"\*\*(.+?)\*\*", " ".join(body)):
            if not any(b in s for s in skim[-len(body) - 1:]):
                skim.append("    bold: " + b)
    if "--skim" in sys.argv:
        print("\n".join(skim))
        print()
    for p in problems:
        print("PROBLEM " + p)
    print(f"problems={len(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
