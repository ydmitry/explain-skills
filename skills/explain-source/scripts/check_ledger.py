#!/usr/bin/env python3
"""Check an understanding ledger against its source.

    python3 check_ledger.py .logbooks/understanding/<slug> [--root DIR] [--gap 12]

Reads ledger.jsonl (and explanation.md when it exists) in the folder. Sources are
resolved against --root (default: the current directory). Sets each row's
`verified` field (yes | no) and prints one line per problem, then `errors=N`.
Exit 0 when errors=0.
"""
import argparse
import json
import re
import sys
from pathlib import Path

KINDS = {"stated", "inferred"}
IMPORTANCE = {"core", "supporting", "skipped"}


def norm(s: str) -> str:
    s = s.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()


def span(anchor: str):
    m = re.fullmatch(r"\s*L?(\d+)(?:\s*[-–]\s*L?(\d+))?\s*", str(anchor))
    if not m:
        return None
    a = int(m.group(1))
    b = int(m.group(2) or a)
    return (a, b) if a <= b else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--root", default=".")
    ap.add_argument("--gap", type=int, default=12, help="longest run of uncovered non-blank lines allowed")
    ap.add_argument("--wide", type=int, default=15, help="most lines a row that is not skipped may cover")
    args = ap.parse_args()
    folder, root = Path(args.folder), Path(args.root)
    path = folder / "ledger.jsonl"
    if not path.exists():
        print(f"ERROR no ledger: {path}")
        print("errors=1")
        return 1

    rows, errors = [], []
    for n, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            errors.append(f"ledger.jsonl:{n} is not JSON ({e.msg}); one object per line")
    sources, covered, seen = {}, {}, set()
    for r in rows:
        rid = r.get("id", "?")
        ok = True

        def bad(msg):
            nonlocal ok
            ok = False
            errors.append(f"{rid}: {msg}")

        if rid in seen:
            bad("id used twice")
        seen.add(rid)
        if r.get("kind") not in KINDS:
            bad(f"kind must be one of {sorted(KINDS)}")
        if r.get("importance") not in IMPORTANCE:
            bad(f"importance must be one of {sorted(IMPORTANCE)}")
        if not r.get("gloss"):
            bad("no gloss")
        src = r.get("source")
        if not src:
            bad("no source")
            r["verified"] = "no"
            continue
        if src not in sources:
            p = root / src
            sources[src] = p.read_text(errors="replace").splitlines() if p.exists() else None
            covered[src] = set()
        lines = sources[src]
        if lines is None:
            bad(f"no such file under {root}: {src}")
            r["verified"] = "no"
            continue
        sp = span(r.get("anchor", ""))
        if not sp:
            bad(f"anchor is not a line or a range: {r.get('anchor')!r}")
            r["verified"] = "no"
            continue
        a, b = sp
        if b > len(lines):
            bad(f"anchor {a}-{b} is past the end of {src} ({len(lines)} lines)")
            r["verified"] = "no"
            continue
        covered[src].update(range(a, b + 1))
        if r.get("importance") != "skipped" and b - a + 1 > args.wide:
            bad(f"row covers {b - a + 1} lines; one clause, paragraph or block per row, {args.wide} lines at most (split it)")
        if r.get("importance") != "core" and str(r.get("differs", "no")).strip().lower() not in ("no", ""):
            bad("differs is not 'no', so importance must be core")
        quote = norm(r.get("quote") or "")
        if not quote:
            if r.get("importance") != "skipped":
                bad("no quote (only a skipped row may have none)")
        elif len(quote.split()) > 40:
            bad("quote is over 40 words; quote the words that carry the point")
        elif quote not in norm(" ".join(lines[a - 1:b])):
            where = [i for i in range(1, len(lines) + 1) if quote in norm(" ".join(lines[i - 1:i + 6]))]
            if where:
                bad(f"quote is not on lines {a}-{b}; it starts near line {where[0]}")
            else:
                bad("quote is not in the source: copy it from the file, do not retype it")
        r["verified"] = "yes" if ok else "no"

    for src, lines in sources.items():
        if lines is None:
            continue
        run = []
        for i, text in enumerate(lines + [""], 1):
            if i <= len(lines) and i not in covered[src]:
                if text.strip():
                    run.append(i)
                continue
            if len(run) > args.gap:
                errors.append(f"{src}: lines {run[0]}-{run[-1]} are in no row; read them and add rows (skipped rows count)")
            run = []
        if len(run) > args.gap:
            errors.append(f"{src}: lines {run[0]}-{run[-1]} are in no row; read them and add rows (skipped rows count)")

    exp = folder / "explanation.md"
    if exp.exists():
        text = exp.read_text()
        cited = set(re.findall(r"\bp\d+\b", text))
        for rid in sorted(cited - seen):
            errors.append(f"explanation.md cites {rid}, which is not a ledger row")
        for r in rows:
            if r.get("importance") == "core" and r.get("id") not in cited:
                errors.append(f"explanation.md never cites core row {r.get('id')}")

    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    for e in errors:
        print("ERROR " + e)
    counts = {k: sum(r.get("importance") == k for r in rows) for k in sorted(IMPORTANCE)}
    print(f"rows={len(rows)} {counts} explanation={'yes' if exp.exists() else 'no'}")
    print(f"errors={len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
