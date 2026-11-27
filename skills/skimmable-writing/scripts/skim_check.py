#!/usr/bin/env python3
"""Check that a Markdown write-up is easy to skim: python3 skim_check.py FILE [--skim]

Prints one line per problem and `problems=N`. Exit 0 when there are none.
A line that starts NOTE is a count and not a problem: it says how many
headings open with the same word.
--skim prints what a skimming eye sees: the headings, the bold text, each
paragraph's first sentence and the first sentence of each bullet in a short
list. Read that view alone: it should tell the story.
"""
import re
import sys
from collections import Counter

MAX_PARA = 60      # words in one prose paragraph
MAX_SECTION = 300  # words in one section
MAX_BULLET_RUN = 8 # bullets in a row before the eye stops reading them
MAX_BOLD = 0.15    # share of a section's words in bold, labels not counted
SAME_HEAD = 0.4    # share of the headings that open with one word before it is noted
MIN_SAME_HEAD = 3  # and at least this many of them
ABBREV = r"(?i)\b(?:e\.g|i\.e|etc|vs|approx|incl|cf|ca|fig)\.$"


def split_sections(text: str) -> list:
    """The text cut at its headings. A line that starts with # inside a code fence is not a heading."""
    parts, fenced = [[]], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced and re.match(r"#{1,6} ", line):
            parts.append([])
        parts[-1].append(line)
    return ["\n".join(p) for p in parts if "".join(p).strip()]


def first_sentence(line: str) -> str:
    """A line up to the end of its first sentence, at most 160 characters.
    A list marker ("1.", "-") and an abbreviation ("e.g.") do not end a sentence."""
    line = line.strip()
    marker = re.match(r"(?:[-*]|\d+\.)\s+", line)
    start = marker.end() if marker else 0
    for m in re.finditer(r"[.!?](?=\s)", line[start:]):
        end = start + m.end()
        if re.search(ABBREV, line[:end]) or line[end:].lstrip()[:1].islower():
            continue
        line = line[:end]
        break
    return line if len(line) < 160 else line[:157] + "..."


def same_opening(headings: list):
    """(how many, of how many, the word) when one first word opens at least MIN_SAME_HEAD headings
    and SAME_HEAD of them all; else None. A leading number is left out: "2. What was found" opens with "What"."""
    firsts = [w[0] for w in ([w for w in re.findall(r"[^\W_]+", h) if not w.isdigit()] for h in headings) if w]
    if not firsts:
        return None
    word, n = Counter(w.lower() for w in firsts).most_common(1)[0]
    if n < MIN_SAME_HEAD or n / len(firsts) < SAME_HEAD:
        return None
    return n, len(firsts), next(w for w in firsts if w.lower() == word)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    text = open(args[0]).read()
    # a block of settings between two --- lines at the top is not text for a reader
    text = re.sub(r"\A---\n.*?\n---\n", "", text, count=1, flags=re.S)
    sections = split_sections(text)
    problems, skim = [], []
    same = same_opening([sec.split("\n")[0] for sec in sections if sec.startswith("#")])
    for sec in sections:
        lines = sec.split("\n")
        head = lines[0].strip() if lines[0].startswith("#") else "(before the first heading)"
        body = lines[1:] if lines[0].startswith("#") else lines
        name = head.lstrip("# ")[:50]
        skim.append("\n" + head)
        words = len(" ".join(body).split())
        bold = " ".join(re.findall(r"\*\*(.+?)\*\*", " ".join(body)))
        # a label that opens a paragraph or a list item is not emphasis: leave it out of the bold share
        emphasis = " ".join(re.findall(r"\*\*(.+?)\*\*", " ".join(re.sub(r"^\s*(?:[-*]|\d+\.)?\s*\*\*.+?\*\*", "", l) for l in body)))
        if words > MAX_SECTION:
            problems.append(f"{name}: section is {words} words (over {MAX_SECTION}); split it")
        if words > 40 and not bold:
            problems.append(f"{name}: nothing in bold; mark the one thing that matters most here")
        if words > 40 and len(emphasis.split()) / words > MAX_BOLD:
            problems.append(f"{name}: {100 * len(emphasis.split()) // words}% of the section is bold beyond its labels; keep one key point")
        run = []
        for line in body + [""]:
            if re.match(r"\s*([-*]|\d+\.) ", line):
                run.append(line.strip())
                continue
            if len(run) > MAX_BULLET_RUN:
                problems.append(f"{name}: {len(run)} bullets in a row; group them under labels or use a table")
            else:
                # the eye still reads a short list; of a long one it keeps only the bold words
                for item in run:
                    skim.append("  " + first_sentence(item))
            run = []
            if not line.strip() or line.startswith("|") or line.startswith(("```", ">")):
                continue
            n = len(line.split())
            skim.append("  " + first_sentence(line))
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
    if same:
        print(f'NOTE {same[0]} of {same[1]} headings open with "{same[2]}"; let each open with what its section holds')
    print(f"problems={len(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
