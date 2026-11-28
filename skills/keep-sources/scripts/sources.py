#!/usr/bin/env python3
"""Keep the sources of a piece of work in one folder: python3 sources.py COMMAND FOLDER ...

    snap  FOLDER NAME [--origin TEXT] [--file PATH | --text TEXT]
          Save text that will not stay (a page, a command's output, what someone said) as
          FOLDER/snapshots/NAME.txt. Without --file or --text it reads standard input.
    snap  FOLDER NAME --image PATH --origin TEXT
          Save a screenshot (png, jpg, gif, webp) as FOLDER/snapshots/NAME with its type. The origin says what
          it shows, where it was taken and when: the picture cannot say that itself.
    add   FOLDER --source PATH --quote TEXT --says TEXT [--near LINE] [--calc TEXT]
          One row in FOLDER/ledger.jsonl. The quote is looked up in the source; that fixes its lines.
    list  FOLDER [--all]
          The rows, one line each: id, where, what it says, the quote. --all shows dropped rows too.
    drop  FOLDER ID --why TEXT
          Mark a row as no longer true or no longer needed. It stays in the file.
    check FOLDER
          Look every quote up again. One line per problem, then errors=N.

A row is refused when its quote is not in the source word for word, or when --says holds a number the
quote does not hold (--calc "how it follows" records a number that comes by arithmetic or from words).
Exit 0 when there is nothing to fix.
"""
import argparse
import hashlib
import json
import re
import shutil
import sys
import time
from pathlib import Path

MAX_QUOTE = 40  # words in one quote
NUM = re.compile(r"(?<![\w.,])\d+(?:[.,]\d+)*")


def norm(s: str) -> str:
    """Text as compared: typographic quotes made straight, every run of white space one space."""
    s = s.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()


def flat(text: str):
    """The text as one normalised string, and for each of its characters the line it came from."""
    parts, where = [], []
    for i, line in enumerate(text.splitlines(), 1):
        n = norm(line)
        if n:
            parts.append(n + " ")
            where += [i] * (len(n) + 1)
    return "".join(parts), where


def find(quote: str, text: str) -> list:
    """Every place the quote stands in the text, as (first line, last line). A quote may run over line ends."""
    q = norm(quote)
    s, where = flat(text)
    out, at = [], s.find(q) if q else -1
    while at != -1:
        out.append((where[at], where[at + len(q) - 1]))
        at = s.find(q, at + 1)
    return out


def closest(quote: str, text: str):
    """The line that shares most words with the quote, when it shares at least half of them: (line number, the
    line), or None."""
    want = set(re.findall(r"\w+", norm(quote).lower()))
    best = (0, 0, "")
    for i, line in enumerate(text.splitlines(), 1):
        shared = len(want & set(re.findall(r"\w+", line.lower())))
        if shared > best[0]:
            best = (shared, i, line.strip())
    return (best[1], best[2]) if best[0] >= max(1, len(want) // 2) else None


def numbers(s: str) -> set:
    """The numbers of a text, thousands separators removed ("14,214" is "14214")."""
    return {re.sub(r",(?=\d{3}(?!\d))", "", m.group(0)).rstrip(".,") for m in NUM.finditer(s)}


def lines_of(span) -> str:
    return str(span[0]) if span[0] == span[1] else f"{span[0]}-{span[1]}"


def first_line(lines: str) -> int:
    return int(re.match(r"\d+", str(lines) or "0").group(0))


def resolve(folder: Path, source: str):
    """A source as a path: absolute, else under the current folder, else under the sources folder."""
    p = Path(source).expanduser()
    if p.is_absolute():
        return p if p.exists() else None
    for base in (Path.cwd(), folder):
        if (base / p).exists():
            return base / p
    return None


def stored(folder: Path, path: Path) -> str:
    """How a row names its source: relative to the sources folder when inside it, else the whole path."""
    try:
        return str(path.resolve().relative_to(folder.resolve()))
    except ValueError:
        return str(path.resolve())


def read_rows(folder: Path) -> list:
    path = folder / "ledger.jsonl"
    if not path.exists():
        return []
    rows = []
    for n, line in enumerate(path.read_text().splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                sys.exit(f"ledger.jsonl:{n} is not JSON ({e.msg}); one object per line")
    return rows


def write_rows(folder: Path, rows: list):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "ledger.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def origins(folder: Path) -> dict:
    path = folder / "snapshots" / "index.json"
    return json.loads(path.read_text()) if path.exists() else {}


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


PICTURES = (".png", ".jpg", ".jpeg", ".gif", ".webp")


def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pictures(folder: Path) -> dict:
    """{file name: its entry} for the pictures saved in a folder."""
    return {name: e for name, e in origins(folder).items() if isinstance(e, dict) and e.get("sha256")}


def snap_image(a, folder: Path) -> int:
    src = Path(a.image).expanduser()
    if not src.is_file() or src.suffix.lower() not in PICTURES:
        print(f"{a.image} is not a picture this folder keeps (png, jpg, gif, webp)")
        return 1
    if not (a.origin or "").strip():
        print("--origin is needed for a picture: what it shows, where it was taken and when")
        return 1
    stem = a.name[:-len(src.suffix)] if a.name.lower().endswith(src.suffix.lower()) else a.name
    name = stem + src.suffix.lower()
    target = folder / "snapshots" / name
    if target.exists() and target.read_bytes() != src.read_bytes():
        print(f"{target} exists with another picture; a snapshot is a record, so pick another name")
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, target)
    index = origins(folder)
    index[name] = {"origin": a.origin.strip(), "saved": now(), "sha256": fingerprint(target)}
    (target.parent / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n")
    print(f"{target} ({target.stat().st_size} bytes)")
    print(f"show it in the text as ![what it shows]({folder.name}/snapshots/{name}), with a line that gives the origin")
    return 0


def snap(a) -> int:
    folder = Path(a.folder)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", a.name):
        print("name: letters, digits, '.', '_' and '-' only, for example pricing-page")
        return 1
    if a.image:
        return snap_image(a, folder)
    if a.text is not None:
        text = a.text
    elif a.file:
        text = Path(a.file).expanduser().read_text(errors="replace")
    else:
        text = sys.stdin.read()
    if not text.strip():
        print("nothing to save: the text is empty")
        return 1
    name = a.name if a.name.endswith(".txt") else a.name + ".txt"
    target = folder / "snapshots" / name
    if target.exists() and target.read_text() != text:
        print(f"{target} exists with other text; a snapshot is a record, so pick another name")
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    index = origins(folder)
    index[name] = {"origin": a.origin or "", "saved": now()}
    (target.parent / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n")
    print(f"{target} ({len(text.splitlines())} lines)")
    return 0


def refuse_says(says: str, quote: str, calc) -> str:
    """Why a row's `says` cannot stand, or ''."""
    if not says.strip():
        return "--says is empty: say the fact in plain words"
    extra = sorted(numbers(says) - numbers(quote))
    if extra and not calc:
        return (f"--says has {', '.join(extra)}, which the quote does not hold. Take the number from the quote; "
                "if it follows by arithmetic or stands there in words, add --calc \"how it follows\"")
    return ""


def add(a) -> int:
    folder = Path(a.folder)
    path = resolve(folder, a.source)
    if path is None:
        print(f"no such file: {a.source} (save a page, an output or a message with `snap` first)")
        return 1
    quote = norm(a.quote)
    n = len(quote.split())
    if len(quote) < 3:
        print("the quote is too short to look up")
        return 1
    if n > MAX_QUOTE:
        print(f"the quote is {n} words; quote the words that carry the point, {MAX_QUOTE} at most")
        return 1
    text = path.read_text(errors="replace")
    spans = find(quote, text)
    if not spans:
        near = closest(quote, text)
        hint = f" The closest line is {near[0]}: {near[1][:160]}" if near else ""
        print(f"the quote is not in {a.source} as written: copy it from the file, do not retype it.{hint}")
        return 1
    why = refuse_says(a.says, quote, a.calc)
    if why:
        print(why)
        return 1
    span = min(spans, key=lambda s: abs(s[0] - a.near)) if a.near else spans[0]
    rows = read_rows(folder)
    used = [int(r["id"][1:]) for r in rows if re.fullmatch(r"s\d+", str(r.get("id", "")))]
    row = {"id": f"s{max(used, default=0) + 1:02d}", "source": stored(folder, path), "lines": lines_of(span),
           "quote": quote, "says": norm(a.says)}
    origin = origins(folder).get(Path(row["source"]).name, {}).get("origin") if row["source"].startswith("snapshots") else ""
    if origin:
        row["origin"] = origin
    if a.calc:
        row["calc"] = norm(a.calc)
    row["added"] = now()
    write_rows(folder, rows + [row])
    more = f" (the quote stands in {len(spans)} places; --near LINE picks another)" if len(spans) > 1 else ""
    print(f"{row['id']} {row['source']}:{row['lines']}{more}")
    return 0


def show(a) -> int:
    rows = read_rows(Path(a.folder))
    for r in rows:
        if r.get("dropped") and not a.all:
            continue
        gone = f"  [dropped: {r['dropped']}]" if r.get("dropped") else ""
        print(f"{r.get('id')}  {r.get('source')}:{r.get('lines')}  {r.get('says')} | \"{r.get('quote')}\"{gone}")
    live = sum(not r.get("dropped") for r in rows)
    shots = pictures(Path(a.folder))
    for name, e in shots.items():
        print(f"picture  snapshots/{name}  {e.get('origin')}  (saved {e.get('saved')})")
    print(f"rows={live}" + (f" dropped={len(rows) - live}" if len(rows) != live else "") + (f" pictures={len(shots)}" if shots else ""))
    return 0


def drop(a) -> int:
    folder = Path(a.folder)
    rows = read_rows(folder)
    hit = [r for r in rows if r.get("id") == a.id]
    if not hit:
        print(f"no row {a.id}")
        return 1
    hit[0]["dropped"] = norm(a.why)
    write_rows(folder, rows)
    print(f"{a.id} dropped")
    return 0


def check(a) -> int:
    folder = Path(a.folder)
    if not (folder / "ledger.jsonl").exists() and not pictures(folder):
        print(f"ERROR no ledger in {folder}")
        print("errors=1")
        return 1
    rows, errors, seen = read_rows(folder), [], set()
    for r in rows:
        rid = r.get("id", "?")
        if rid in seen:
            errors.append(f"{rid}: id used twice")
        seen.add(rid)
        if r.get("dropped"):
            continue
        path = resolve(folder, str(r.get("source", "")))
        if path is None:
            errors.append(f"{rid}: no such file: {r.get('source')}")
            continue
        spans = find(str(r.get("quote", "")), path.read_text(errors="replace"))
        if not spans:
            errors.append(f"{rid}: the quote is no longer in {r.get('source')} (the file changed, or the row was "
                          "written by hand); read the source again and add a new row, then drop this one")
            continue
        span = min(spans, key=lambda s: abs(s[0] - first_line(r.get("lines", "0"))))
        if lines_of(span) != str(r.get("lines")):
            print(f"MOVED {rid}: now lines {lines_of(span)} (was {r.get('lines')})")
            r["lines"] = lines_of(span)
        why = refuse_says(str(r.get("says", "")), str(r.get("quote", "")), r.get("calc"))
        if why:
            errors.append(f"{rid}: {why.replace('--says', 'says').replace('--calc', 'calc')}")
    if rows:
        write_rows(folder, rows)
    for name, e in pictures(folder).items():
        shot = folder / "snapshots" / name
        if not shot.is_file():
            errors.append(f"{name}: the picture is gone")
        elif fingerprint(shot) != e["sha256"]:
            errors.append(f"{name}: the picture changed since it was saved; a snapshot is a record, save the new one under another name")
    for e in errors:
        print("ERROR " + e)
    print(f"rows={sum(not r.get('dropped') for r in rows)}")
    print(f"errors={len(errors)}")
    return 1 if errors else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("snap")
    p.add_argument("folder")
    p.add_argument("name")
    p.add_argument("--origin", help="where the text came from: a URL, a command, who said it and when")
    p.add_argument("--file")
    p.add_argument("--text")
    p.add_argument("--image", help="a screenshot to save in place of text; --origin is then needed")
    p.set_defaults(run=snap)
    p = sub.add_parser("add")
    p.add_argument("folder")
    p.add_argument("--source", required=True)
    p.add_argument("--quote", required=True)
    p.add_argument("--says", required=True)
    p.add_argument("--near", type=int, help="when the quote stands in several places: the line closest to the one meant")
    p.add_argument("--calc", help="how a number in --says follows from the quote")
    p.set_defaults(run=add)
    p = sub.add_parser("list")
    p.add_argument("folder")
    p.add_argument("--all", action="store_true")
    p.set_defaults(run=show)
    p = sub.add_parser("drop")
    p.add_argument("folder")
    p.add_argument("id")
    p.add_argument("--why", required=True)
    p.set_defaults(run=drop)
    p = sub.add_parser("check")
    p.add_argument("folder")
    p.set_defaults(run=check)
    a = ap.parse_args(argv)
    return a.run(a)


if __name__ == "__main__":
    sys.exit(main())
