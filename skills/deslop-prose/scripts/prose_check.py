#!/usr/bin/env python3
"""Help a sentence-level rewrite of a Markdown file stay inside its limits: python3 prose_check.py COMMAND FILE

    start FILE                     keep a copy of the file as it is now, before the rewrite
    scan  FILE                     list the lines that hold a known tell of machine-written prose
    check FILE [--before OTHER] [--gone VALUE ...]
                                   compare the file with the copy: same headings, lists, tables, bold and code;
                                   every number, code name and link kept; none added. Prints errors=N.

scan is a finder, not a grade: a listed line may be fine, and it cannot see forced threes, closers that repeat
or a paragraph that says nothing. check exits 0 when there is nothing to fix. --gone VALUE accepts the loss of
one number, code name or link that stood only in a sentence the rewrite was right to cut.
"""
import argparse
import hashlib
import re
import sys
import tempfile
from pathlib import Path

NUM = re.compile(r"(?<![\w.,])\d+(?:[.,]\d+)*")
START = r"(?:^|(?<=[.!?:] ))"  # the start of a line or of a sentence

TELLS = [
    ("not X but Y", [
        r"\bnot (?:just|only|merely|simply)\b",
        r"\b(?:it|this|that)(?:'s| is)(?:n't| not) (?:just |only |merely |about )?[^.;:!?]{1,60}[,;] (?:it|this|that)(?:'s| is)\b",
        r"\b(?:is|are|was|were)n't (?:mainly |really |just )?about\b",
        r"\b(?:does|do|did)(?:n't| not) mean\b[^.]{0,80}\. (?:it|this|that) means\b",
    ]),
    ("run-up", [
        r"\blet'?s (?:dive|explore|break (?:this|it) down|take a (?:closer )?look|unpack)\b",
        r"\bhere'?s (?:what you need to know|the thing|the catch|the kicker)\b",
        r"\bthe thing is\b", r"\blet'?s be honest\b", r"\breal talk\b", r"\bwithout further ado\b",
        r"\bthe (?:hard|tricky|interesting|important|real|best|new|fun|scary) part (?:is|was)\b",
        r"\bthe part (?:that|worth|where)\b",
        r"\bit'?s worth (?:noting|mentioning|pointing out)\b",
        r"\bit is (?:important|worth|crucial|essential) to (?:note|mention|remember|understand)\b",
        START + r"(?:importantly|notably|interestingly|crucially|essentially|basically|simply put|in short),",
    ]),
    ("closer", [
        r"\bthat'?s the (?:real|whole|key) (?:win|point|story|lesson|takeaway)\b",
        r"\bthat distinction matters\b", r"\blet that sink in\b", r"\bread that again\b",
        START + r"(?:in conclusion|in summary|to sum up|overall|ultimately|at the end of the day)\b",
        r"\bthe (?:bottom line|takeaway) (?:is|here)\b",
    ]),
    ("sounds deep", [
        r"\bat its core\b", r"\bthe real question\b", r"\bwhat really matters\b", r"\bthe heart of the matter\b",
        r"\bthe deeper (?:issue|question|truth)\b", r"\bfundamentally\b", r"\bthe truth is\b",
    ]),
    ("arguing with no one", [
        r"\bto be clear\b", r"\bdon'?t get me wrong\b", r"\bthis is not to say\b",
        r"\bsome (?:might|may|would) (?:say|argue)\b", r"\byou might think\b", r"\bone might be tempted\b",
        r"\ba tempting approach\b", r"\bit would be easy to\b", r"\bi'?m not (?:saying|arguing)\b",
    ]),
    ("stacked hedge", [
        r"\b(?:could|might|may) (?:potentially|possibly|arguably|perhaps)\b", r"\bit could be argued\b",
        r"\bpotentially possibly\b",
    ]),
    ("stock word", [
        r"\bdelv(?:e|es|ed|ing)\b", r"\btapestry\b", r"\btestament\b", r"\bpivotal\b", r"\bcrucial(?:ly)?\b",
        r"\bmeticulous(?:ly)?\b", r"\bintrica(?:te|cies|cy)\b", r"\bvibrant\b", r"\bshowcas(?:e|es|ed|ing)\b",
        r"\bunderscor(?:es|ed|ing)\b", r"\bbolster(?:s|ed|ing)?\b", r"\bgarner(?:s|ed|ing)?\b", r"\binterplay\b",
        r"\bseamless(?:ly)?\b", r"\bleverag(?:e|es|ed|ing)\b", r"\bfoster(?:s|ed|ing)?\b", r"\bholistic(?:ally)?\b",
        r"\bgame[- ]chang(?:er|ing)\b", r"\bcutting[- ]edge\b", r"\brealm\b", r"\bembark(?:s|ed|ing)?\b",
        r"\belevat(?:e|es|ed|ing)\b", r"\bempower(?:s|ed|ing)?\b", r"\bmultifaceted\b", r"\bnuanced\b",
        r"\blandscape\b", r"\bstreamlin(?:e|es|ed|ing)\b", r"\bharness(?:es|ed|ing)?\b",
        r"\bnavigat(?:e|es|ed|ing) the\b", r"\badditionally\b", r"\bmoreover\b", r"\bfurthermore\b",
        r"\bkey (?:role|insight|insights|takeaway|takeaways|aspect|aspects|factor|factors)\b",
        r"\ba wide (?:range|array|variety) of\b", r"\ba (?:myriad|plethora) of\b", r"\bever[- ](?:evolving|changing)\b",
        r"\bin today'?s\b", r"\bfast[- ]paced\b", r"\bdeep dive\b", r"\bvaluable insights?\b",
    ]),
    ("inflated", [
        r"\b(?:stands?|serves?|functions?) as (?:a|an|the)\b",
        r"\bplays? (?:a|an) (?:key|crucial|vital|pivotal|significant|important|central|critical) role\b",
        r"\bmark(?:s|ed|ing) a (?:pivotal|significant|major|turning|new)\b", r"\bsett(?:ing|s) the stage\b",
        r"\brich (?:history|heritage|tradition|tapestry)\b", r"\bin the heart of\b", r"\bnestled\b", r"\bboasts?\b",
        r"\bbreathtaking\b", r"\bstunning\b", r"\brenowned\b", r"\bgroundbreaking\b", r"\bindelible\b",
        r"\ba step in the right direction\b", r"\bthe future looks\b",
        r"\bit'?s no (?:secret|surprise|wonder) that\b",
    ]),
    ("bolted-on -ing", [
        r",\s+(?:highlighting|underscoring|emphasizing|emphasising|showcasing|reflecting|symbolizing|symbolising"
        r"|ensuring|fostering|cultivating|contributing to|demonstrating|illustrating|signaling|signalling)\b",
    ]),
    ("borrowed authority", [
        r"\b(?:experts|researchers|critics|observers|analysts)(?: \w+)? (?:say|argue|believe|agree|suggest|note|have noted|point out)\b",
        r"\b(?:studies|research) (?:show|shows|suggest|suggests|has shown|have shown)\b", r"\bindustry reports?\b",
        r"\bit is (?:widely|generally|commonly) (?:believed|accepted|known|regarded)\b",
    ]),
    ("chat leftover", [
        r"\bi hope this helps\b", r"\bgreat question\b", START + r"(?:certainly|of course|sure|absolutely)[!,]",
        r"\byou'?re absolutely right\b", r"\blet me know if\b", r"\bwould you like me to\b", r"\bfeel free to\b",
        r"\bhappy to help\b", r"\bas an ai\b", r"\bas of my (?:last|latest|knowledge)\b",
        r"\bhere(?:'s| is) (?:a|an|the|your) (?:overview|summary|breakdown|rundown|revised|updated)\b",
    ]),
    ("about the text", [
        r"\bthis (?:section|document|page|article|guide|post) (?:covers|describes|explains|outlines|provides|walks)\b",
        r"\bin this (?:section|document|article|guide|post),? (?:we|i)\b",
        r"\bas (?:mentioned|discussed|noted|described|outlined) (?:above|earlier|before|previously|below)\b",
        r"\bin the (?:following|next|previous) section\b",
    ]),
]
COMPILED = [(name, [re.compile(p, re.I) for p in pats]) for name, pats in TELLS]


def number(s: str) -> str:
    return re.sub(r",(?=\d{3}(?!\d))", "", s)


def body_lines(text: str):
    """The text as (line number, line, kind) with kind one of heading, code, quote, table, item, para, blank."""
    out, fenced = [], False
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if s.startswith("```") or s.startswith("~~~"):
            fenced = not fenced
            out.append((i, line, "code"))
        elif fenced:
            out.append((i, line, "code"))
        elif not s:
            out.append((i, line, "blank"))
        elif re.match(r"#{1,6} ", line):
            out.append((i, line, "heading"))
        elif s.startswith(">"):
            out.append((i, line, "quote"))
        elif s.startswith("|"):
            out.append((i, line, "table"))
        elif re.match(r"\s*(?:[-*+]|\d+[.)])\s+", line):
            out.append((i, line, "item"))
        else:
            out.append((i, line, "para"))
    return out


def plain(line: str) -> str:
    """A line without what a sentence-level rewrite must not read as prose: inline code and link targets."""
    line = re.sub(r"`[^`\n]*`", " ", line)
    line = re.sub(r"\]\([^)]*\)", "]", line)
    return re.sub(r"https?://\S+", " ", line)


def shape(text: str) -> dict:
    """What a sentence-level rewrite must leave as it is, and the facts it must keep."""
    lines = body_lines(text)
    sections, cur = [], {"heading": "(before the first heading)", "items": 0, "rows": 0, "bold": 0}
    code, block = [], None
    for _, line, kind in lines:
        if kind == "code":
            if block is None:
                block = []
            block.append(line)
            if len(block) > 1 and line.strip().startswith(("```", "~~~")):
                code.append("\n".join(block))
                block = None
            continue
        if kind == "heading":
            sections.append(cur)
            cur = {"heading": line.strip(), "items": 0, "rows": 0, "bold": 0}
            continue
        cur["items"] += kind == "item"
        cur["rows"] += kind == "table"
        cur["bold"] += len(re.findall(r"\*\*(.+?)\*\*", line))
    sections.append(cur)
    if block:
        code.append("\n".join(block))
    prose = "\n".join(line for _, line, kind in lines if kind not in ("code", "blank"))
    return {
        "sections": sections,
        "code": code,
        "numbers": {number(m.group(0)) for m in NUM.finditer(plain(prose))},
        "names": set(re.findall(r"`([^`\n]+)`", prose)),
        "links": set(re.findall(r"https?://[^\s)>\]]+", prose)),
        "words": len(re.sub(r"[#*|`>-]", " ", prose).split()),
    }


def copy_path(path: Path) -> Path:
    key = hashlib.sha1(str(path.resolve()).encode()).hexdigest()[:16]
    return Path(tempfile.gettempdir()) / "deslop-prose" / f"{key}.md"


def start(a) -> int:
    path = Path(a.file).expanduser()
    copy = copy_path(path)
    copy.parent.mkdir(parents=True, exist_ok=True)
    copy.write_text(path.read_text())
    print(f"kept a copy of {path} as it is now: {copy}")
    return 0


def scan(a) -> int:
    text = Path(a.file).expanduser().read_text()
    hits, lines_hit, dashes, words = 0, set(), 0, 0
    for i, line, kind in body_lines(text):
        if kind not in ("para", "item", "table"):
            continue
        p = plain(line)
        p = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", p).replace("**", "").strip()
        words += len(p.split())
        dashes += len(re.findall(r"—|\s–\s|\s--\s", p))
        for name, pats in COMPILED:
            for pat in pats:
                for m in pat.finditer(p):
                    hits += 1
                    lines_hit.add(i)
                    lo, hi = max(0, m.start() - 40), min(len(p), m.end() + 40)
                    print(f"LINE {i} [{name}] \"{m.group(0).strip(' ,')}\": ...{p[lo:hi].strip()}...")
    rate = f"{1000 * dashes / words:.1f}" if words else "0"
    print(f"found={hits} in {len(lines_hit)} lines; dashes={dashes} ({rate} per 1,000 words)")
    print("A listed line may be fine. Forced threes, closers that repeat and empty paragraphs are not listed: read for them.")
    return 0


def check(a) -> int:
    path = Path(a.file).expanduser()
    before_path = Path(a.before).expanduser() if a.before else copy_path(path)
    if not before_path.exists():
        print(f"no copy from before the rewrite ({before_path}); run `start FILE` first, or give --before OTHER")
        print("errors=1")
        return 1
    old, new = shape(before_path.read_text()), shape(path.read_text())
    gone_ok = {number(g) for g in a.gone or []} | set(a.gone or [])
    errors, notes = [], []
    heads_old = [s["heading"] for s in old["sections"]]
    heads_new = [s["heading"] for s in new["sections"]]
    if heads_old != heads_new:
        for h in heads_old:
            if h not in heads_new:
                errors.append(f"heading changed or removed: {h}")
        for h in heads_new:
            if h not in heads_old:
                errors.append(f"heading new or reworded: {h}")
        if set(heads_old) == set(heads_new):
            errors.append("headings are in another order")
    else:
        for so, sn in zip(old["sections"], new["sections"]):
            name = so["heading"].lstrip("# ")[:50]
            for key, what in (("items", "list items"), ("rows", "table rows"), ("bold", "things in bold")):
                if so[key] != sn[key]:
                    errors.append(f"{name}: {so[key]} {what} before, {sn[key]} after")
    if old["code"] != new["code"]:
        errors.append("a code block changed; code is not prose")
    for label, key in (("number", "numbers"), ("code name", "names"), ("link", "links")):
        for v in sorted(old[key] - new[key]):
            if v in gone_ok:
                notes.append(f"{label} gone, accepted by --gone: {v}")
            else:
                errors.append(f"{label} lost: {v} (put it back, or pass --gone \"{v}\" when its whole sentence had to go)")
        for v in sorted(new[key] - old[key]):
            errors.append(f"{label} added: {v} (this pass adds no fact)")
    notes.append(f"words: {old['words']} before, {new['words']} after")
    if new["words"] > old["words"]:
        notes.append("the text grew; a pass that removes should not add")
    for e in errors:
        print("ERROR " + e)
    for n in notes:
        print("NOTE " + n)
    print(f"errors={len(errors)}")
    return 1 if errors else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("start")
    p.add_argument("file")
    p.set_defaults(run=start)
    p = sub.add_parser("scan")
    p.add_argument("file")
    p.set_defaults(run=scan)
    p = sub.add_parser("check")
    p.add_argument("file")
    p.add_argument("--before")
    p.add_argument("--gone", action="append")
    p.set_defaults(run=check)
    a = ap.parse_args(argv)
    return a.run(a)


if __name__ == "__main__":
    sys.exit(main())
