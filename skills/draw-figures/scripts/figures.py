#!/usr/bin/env python3
"""Figures for a Markdown text: python3 figures.py marks|brief|check|preview|place TEXT [--figures DIR]

A line `Figure: <one sentence>` that stands as a paragraph of its own marks a figure. The Nth mark of TEXT is
drawn as fig-N.svg in the figures folder: figures/<name of the text>/ beside the text, or DIR.

  marks    list the marks and the file each one gets; last line `marks=N drawn=M`
  brief    write brief.md into the figures folder, a block for each mark; fill it before drawing
  check    read the source of every figure and, when the playwright package is installed, measure the drawn
           boxes in a headless browser. One line per finding: PROBLEM blocks, WARN is fixed or its reason
           given, NOTE is advice. Then `measured=yes|no`, `warnings=N` and, last, `problems=N`.
           Exit 0 when problems=0. --no-measure skips the browser.
  preview  write a picture of each figure for a light and a dark screen into --out DIR (a new folder of the
           system's temporary folder by default), and preview.html to open in a browser
  place    finish the files (the token block, width and height from the viewBox) and write an image line
           above each mark. Changes nothing while the source check lists a problem.
"""
import argparse
import json
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
SVG_NS = "http://www.w3.org/2000/svg"
XLINK = "{http://www.w3.org/1999/xlink}href"
MAX_WIDTH = 720    # a page's text column: one viewBox unit is one CSS pixel at full size
MIN_FONT = 12      # units; a page shows a figure down to four fifths of its size, and 12 x 0.8 stays above 9.5 pixels
SHRINK = 0.8       # so the figures are measured at that size
MIN_CLAIM = 4      # words; a shorter mark names a medium and states no claim
MARK = re.compile(r"Figure:\s+(\S.*?)\s*$")
IMAGE = re.compile(r"!\[.*\]\(\s*<?([^()<>]+?)>?\s*\)\s*$")
ROOT = re.compile(r"<svg\b(?:[^>\"']|\"[^\"]*\"|'[^']*')*>")
TOKENS = re.compile(r"\s*<style data-tokens[^>]*>.*?</style>", re.S)
TOKEN = re.compile(r"\d+(?:[.,]\d+)*|[^\W\d_][^\W_]*")
BANNED = ("script", "foreignObject", "linearGradient", "radialGradient", "animate", "animateTransform",
          "animateMotion", "set", "image")
COLOUR_PROPS = ("fill", "stroke", "color", "stop-color", "flood-color")
NO_COLOUR = {"none", "currentcolor", "transparent", "inherit", "initial", "unset", "context-fill", "context-stroke"}
FIELDS = ("claim", "shape", "data", "constraints")
TIERS = {"error": "PROBLEM", "warn": "WARN", "advisory": "NOTE"}


# ---- the text and its marks -------------------------------------------------------------------------------

def plain(md: str) -> str:
    """A line of Markdown as the words a reader sees: no backticks, stars or link targets."""
    md = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", md)
    md = re.sub(r"`+([^`]*)`+", r"\1", md)
    md = re.sub(r"(\*\*|__)(.+?)\1", r"\2", md)
    md = re.sub(r"(?<![\w*])([*_])(.+?)\1(?!\w)", r"\2", md)
    return " ".join(md.split())


def read_marks(text: str) -> list:
    """The marks of a text in order. Each: n, id, line (from 1), at (index in the lines), claim, alone,
    image (the index of its own image line two lines above it, or None)."""
    lines, marks, fenced, front = text.split("\n"), [], False, False
    for i, line in enumerate(lines):
        if i == 0 and line.strip() == "---":
            front = True
        elif front:
            front = line.strip() != "---"
        elif re.match(r"\s*(```|~~~)", line):
            fenced = not fenced
        elif not fenced and MARK.match(line):
            n = len(marks) + 1
            alone = (i == 0 or not lines[i - 1].strip()) and (i + 1 >= len(lines) or not lines[i + 1].strip())
            link = IMAGE.match(lines[i - 2]) if i >= 2 and not lines[i - 1].strip() else None
            own = link is not None and Path(link.group(1)).name == f"fig-{n}.svg"
            marks.append({"n": n, "id": f"fig-{n}", "line": i + 1, "at": i, "claim": plain(MARK.match(line).group(1)),
                          "alone": alone, "image": i - 2 if own else None})
    return marks


def tokens(s: str):
    """(words, numbers) of a string. A word is two characters or more and starts with a letter; a plural and
    its singular count as one word. A number loses its thousands commas."""
    words, numbers = set(), set()
    for t in TOKEN.findall(s):
        if t[0].isdigit():
            numbers.add(re.sub(r",(?=\d{3}(?!\d))", "", t))
        elif len(t) > 1:
            w = t.lower()
            words.add(w[:-1] if len(w) > 3 and w.endswith("s") and w.isalpha() else w)
    return words, numbers


# ---- the brief --------------------------------------------------------------------------------------------

def read_brief(path: Path) -> dict:
    """{figure id: {field: value}}. A field runs on until the next field or heading."""
    blocks, cur, field = {}, None, None
    for line in path.read_text().split("\n"):
        head = re.match(r"##\s+(fig-\d+)\s*$", line)
        if head:
            cur, field = blocks.setdefault(head.group(1), {}), None
        elif line.startswith("#"):
            cur = None
        elif cur is not None:
            f = re.match(rf"({'|'.join(FIELDS)}):\s*(.*)$", line)
            if f:
                field = f.group(1)
                cur[field] = f.group(2).strip()
            elif field and line.strip():
                cur[field] = (cur[field] + " " + line.strip()).strip()
    return blocks


def no_pointers(s: str) -> str:
    """A field of the brief without what stands in parentheses: a pointer to a source allows no label."""
    return re.sub(r"\([^()]*\)", " ", s or "")


def brief(a) -> int:
    marks = read_marks(a.text.read_text())
    path = a.figures / "brief.md"
    a.figures.mkdir(parents=True, exist_ok=True)
    new = updated = 0
    if path.exists():
        lines = path.read_text().rstrip("\n").split("\n")
    else:
        lines = [f"# Figure brief: {a.text.name}", "", f"text: {a.text}",
                 "canvas: one or two widths for all the figures, 720 at most, 400 or less to show whole on a phone; each height from its content",
                 "palette: what each colour means in every figure, for example --ok pass, --error fail, --muted the state before"]
    for m in marks:
        heads = [i for i, line in enumerate(lines) if re.match(rf"##\s+{m['id']}\s*$", line)]
        if not heads:
            lines += ["", f"## {m['id']}", f"claim: {m['claim']}", "shape:", "data:", "constraints:"]
            new += 1
            continue
        end = next((i for i in range(heads[0] + 1, len(lines)) if lines[i].startswith("#")), len(lines))
        at = next((i for i in range(heads[0] + 1, end) if lines[i].startswith("claim:")), None)
        want = f"claim: {m['claim']}"
        if at is None:
            lines.insert(heads[0] + 1, want)
            updated += 1
        elif lines[at] != want:
            lines[at] = want
            updated += 1
    path.write_text("\n".join(lines) + "\n")
    known = {m["id"] for m in marks}
    for fid in read_brief(path):
        if fid not in known:
            print(f"{fid}: the text has no such mark now; remove the block when the figure is gone")
    print(path)
    print(f"blocks={len(marks)} new={new} updated={updated}")
    return 0


# ---- reading a figure's source ----------------------------------------------------------------------------

def local(tag) -> str:
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def typed_colour(value: str) -> bool:
    """True when a fill or stroke names a colour itself and does not read a token."""
    v = re.sub(r"url\([^)]*\)", "", value).strip()
    if re.search(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color)\(", v):
        return True
    return bool(re.fullmatch(r"[a-zA-Z-]+", v)) and v.lower() not in NO_COLOUR


def declarations(css: str) -> list:
    """(property, value) pairs of a run of declarations."""
    out = []
    for part in css.split(";"):
        if ":" in part:
            prop, value = part.split(":", 1)
            out.append((prop.strip().lower(), value.strip()))
    return out


def number(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def view_box(root):
    """(width, height) of a root's viewBox, or None."""
    parts = re.split(r"[\s,]+", (root.get("viewBox") or "").strip())
    nums = [number(p) for p in parts]
    return (nums[2], nums[3]) if len(nums) == 4 and None not in nums and nums[2] > 0 and nums[3] > 0 else None


def source_findings(mark: dict, path: Path, text_tokens, block) -> list:
    """What the source of one figure file shows, as (tier, where, type, detail)."""
    fid, out = mark["id"], []

    def problem(kind, detail=""):
        out.append(("PROBLEM", fid, kind, detail))

    if not path.exists():
        problem("not-drawn", f"no {path.name} for the mark on line {mark['line']}")
        return out
    raw = path.read_text()
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        problem("not-xml", f"{exc}: a label needs &amp; for & and &lt; for <, and every tag closes")
        return out
    if local(root.tag) != "svg":
        problem("not-xml", f"the root is <{local(root.tag)}>, not <svg>")
        return out
    if root.tag != f"{{{SVG_NS}}}svg":
        problem("no-xmlns", f'the root needs xmlns="{SVG_NS}" or the file shows nothing on its own')
    box = view_box(root)
    if not box:
        problem("no-viewbox", 'the root needs viewBox="0 0 W H"')
    else:
        if box[0] > MAX_WIDTH:
            problem("too-wide", f"the viewBox is {box[0]:g} wide; {MAX_WIDTH} at most")
        for attr, want in (("width", box[0]), ("height", box[1])):
            if root.get(attr) is not None and number(root.get(attr)) != want:
                problem("typed-size", f'{attr}="{root.get(attr)}"; leave width and height to `place`')
    if root.get("role") != "img" or not (root.get("aria-label") or "").strip():
        problem("a11y-missing", 'the root needs role="img" and an aria-label')
    elif " ".join(root.get("aria-label").split()) != mark["claim"]:
        problem("label-differs", f'the aria-label is "{" ".join(root.get("aria-label").split())}" and the mark says "{mark["claim"]}"')
    if root.get("id") != fid:
        problem("id-differs", f'the root has id="{root.get("id")}"; it is {fid}')

    ids, refs, css_rules, decls, shown = [], [], [], [], []
    for el in root.iter():
        tag = local(el.tag)
        if tag in BANNED:
            problem("banned-element", f"<{tag}>")
        if tag == "style":
            if el.get("data-tokens") is None:
                css_rules.append(re.sub(r"/\*.*?\*/", "", el.text or "", flags=re.S))
            continue
        if tag in ("text", "title", "desc"):
            shown.append(" ".join(el.itertext()))
        if el is not root and el.get("id") is not None:
            ids.append(el.get("id"))
        for key, value in el.attrib.items():
            name = local(key)
            if name == "href" or key == XLINK:
                if value.startswith("#"):
                    refs.append(value[1:])
                else:
                    problem("external-ref", f'{name}="{value[:60]}"')
            for ref in re.findall(r"url\(\s*[\"']?([^)\"']*)", value):
                if ref.startswith("#"):
                    refs.append(ref[1:])
                else:
                    problem("external-ref", f"url({ref[:60]})")
            if name == "style":
                decls += declarations(value)
            elif name in COLOUR_PROPS or name in ("font-family", "font-size"):
                decls.append((name, value))
            if name in ("x", "y", "x1", "y1", "x2", "y2", "cx", "cy", "width", "height", "r", "rx", "ry", "points", "d") \
                    and re.search(r"\bNaN\b", value):
                problem("nan-coord", f'<{tag} {name}="{value[:40]}">')
            if name in ("width", "height", "r", "rx", "ry") and (number(value) or 0) < 0:
                problem("negative-size", f'<{tag} {name}="{value}">')
    for css in css_rules:
        for at in sorted(set(re.findall(r"@[\w-]+", css))):
            problem("at-rule", f"{at}: a figure holds no at-rule; the tokens already turn with the screen")
        for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
            for sel in selectors.split(","):
                sel = sel.strip()
                if sel and not sel.startswith("@") and not re.match(rf"#{fid}(?![\w-])", sel):
                    problem("unscoped-style", f'"{sel}": start the selector with #{fid}')
            decls += declarations(body)
            for ref in re.findall(r"url\(\s*[\"']?([^)\"']*)", body):
                refs.append(ref[1:]) if ref.startswith("#") else problem("external-ref", f"url({ref[:60]})")
    for prop, value in decls:
        if prop in COLOUR_PROPS and typed_colour(value):
            problem("raw-color", f"{prop}: {value[:40]}; read a token, for example var(--text)")
        if prop == "font-family" and not re.fullmatch(r"var\(\s*--font-(?:body|mono)\s*\)|inherit", value.strip()):
            problem("typed-font", f"font-family: {value[:40]}; only var(--font-body) or var(--font-mono)")
        size = re.fullmatch(r"([\d.]+)\s*(?:px)?", value.strip()) if prop == "font-size" else None
        if size and float(size.group(1)) < MIN_FONT:
            problem("text-too-small", f"font-size {size.group(1)}; {MIN_FONT} at least: a page shows a figure at four fifths of its size")
    for i in sorted(set(ids)):
        if not i.startswith(fid + "-"):
            problem("unscoped-id", f'id="{i}": start it with {fid}-')
        if ids.count(i) > 1:
            problem("duplicate-id", f'id="{i}" is defined {ids.count(i)} times')
    for ref in sorted(set(refs)):
        if ref not in ids and ref != fid:
            problem("unresolved-ref", f"#{ref} is defined nowhere in the file")

    words, numbers = tokens(" ".join(shown))
    allowed_w, allowed_n = text_tokens
    if block is not None:
        if block.get("claim", "") != mark["claim"]:
            problem("brief-claim-differs", f'the brief says "{block.get("claim", "")}"; run `brief` again')
        empty = [f for f in ("shape", "data") if not block.get(f)]
        if empty:
            problem("brief-incomplete", f"fill {' and '.join(empty)} in the block of {fid}")
        more_w, more_n = tokens(" ".join(no_pointers(block.get(f)) for f in ("shape", "data", "constraints")))
        allowed_w, allowed_n = allowed_w | more_w, allowed_n | more_n
        missing = sorted(tokens(no_pointers(block.get("data")))[1] - numbers)
        if missing:
            problem("value-not-drawn", f"the brief's data has {', '.join(missing)} and the figure does not show it")
    if words - allowed_w:
        problem("new-words", f"neither the text nor the brief has: {', '.join(sorted(words - allowed_w))}")
    if numbers - allowed_n:
        problem("new-numbers", f"neither the text nor the brief has: {', '.join(sorted(numbers - allowed_n))}")
    return out


def source_check(a):
    """(marks, findings, figures that parsed as [(id, svg text, width)]) for a text."""
    text = a.text.read_text()
    marks, found, drawn = read_marks(text), [], []
    for m in marks:
        if not m["alone"]:
            found.append(("PROBLEM", "", "mark-not-alone", f"line {m['line']}: put a blank line above and below the Figure: line"))
        if len(m["claim"].split()) < MIN_CLAIM:
            found.append(("PROBLEM", "", "mark-too-short", f'line {m["line"]}: "{m["claim"]}" states no claim; write the sentence the figure shows'))
    blocks = None
    if marks:
        if (a.figures / "brief.md").exists():
            blocks = read_brief(a.figures / "brief.md")
        else:
            found.append(("PROBLEM", "", "brief-missing", f"no brief.md in {a.figures}: run `brief`, fill it, then draw"))
    text_tokens = tokens(text)
    for m in marks:
        path = a.figures / f"{m['id']}.svg"
        block = None
        if blocks is not None:
            block = blocks.get(m["id"])
            if block is None:
                found.append(("PROBLEM", m["id"], "brief-block-missing", "the brief has no block for it: run `brief` again"))
        mine = source_findings(m, path, text_tokens, block)
        found += mine
        if path.exists() and not any(k in ("not-xml",) for _, _, k, _ in mine):
            box = view_box(ET.fromstring(path.read_text()))
            drawn.append((m["id"], path.read_text(), box[0] if box else MAX_WIDTH))
    if a.figures.is_dir():
        for extra in sorted(a.figures.glob("fig-*.svg")):
            n = re.fullmatch(r"fig-(\d+)", extra.stem)
            if n and int(n.group(1)) > len(marks):
                found.append(("PROBLEM", "", "extra-file", f"{extra.name} has no mark in the text: remove the file or restore the mark"))
    return marks, found, drawn


def show(found: list) -> int:
    """Print the findings; the number of problems."""
    for tier, where, kind, detail in found:
        print(f"{tier} {where + ': ' if where else ''}{kind} {detail}".rstrip())
    return sum(tier == "PROBLEM" for tier, _, _, _ in found)


# ---- the page the figures are measured and pictured in ----------------------------------------------------

def token_css() -> str:
    """tokens.css without its comments."""
    return re.sub(r"/\*.*?\*/", "", (HERE.parent / "assets" / "tokens.css").read_text(), flags=re.S).strip()


def token_block() -> str:
    """What `place` writes into a figure file: the tokens for both screens, the ground, the default text."""
    return ('<style data-tokens="1">\n' + token_css() + "\n"
            ":root { background: var(--surface); font-family: var(--font-body); }\n"
            "text { fill: var(--text); }\n</style>")


def bare(svg: str) -> str:
    """A figure file as it stands inline in a page: no XML declaration, no token block, no typed size."""
    svg = TOKENS.sub("", re.sub(r"<\?xml[^>]*\?>", "", svg))
    root = ROOT.search(svg)
    if not root:
        return svg
    tag = re.sub(r"\s(?:width|height)=(\"[^\"]*\"|'[^']*')", "", root.group(0))
    return svg[:root.start()] + tag + svg[root.end():]


def host_page(figs: list, switch=False) -> str:
    """One HTML page with every figure inline on its ground, as a page of the text would show it."""
    css = token_css()
    light, dark = css.split("@media", 1)
    dark_decls = re.search(r":root\s*\{(.*?)\}", dark, re.S).group(1)
    size = 1 if switch else SHRINK  # pictures at full size; measuring at the smallest size a page shows
    panels = "\n".join(f'<div class="fig" style="max-width:{w * size:g}px">{bare(svg)}</div>' for _, svg, w in figs)
    button = ('<button onclick="var r=document.documentElement;r.dataset.theme=r.dataset.theme===\'dark\'?\'light\':\'dark\'">'
              "light / dark</button>") if switch else ""
    return f"""<!doctype html>
<html lang="en" data-theme="light"><head><meta charset="utf-8"><title>figures</title>
<style>
{light}
:root[data-theme="dark"] {{{dark_decls}}}
body {{ margin: 0; background: var(--bg); }}
main {{ width: {MAX_WIDTH + 2}px; margin: 0 auto; padding: 16px 0; }}
.fig {{ background: var(--surface); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; margin: 0 0 24px; }}
.fig svg {{ display: block; width: 100%; height: auto; font-family: var(--font-body); }}
.fig svg text {{ fill: var(--text); }}
</style></head>
<body><main>
{button}
{panels}
</main></body></html>
"""


def browser_error(exc) -> str:
    """The first line of an error that says what failed."""
    for line in str(exc).splitlines():
        if line.strip() and not re.match(r"[─-╿]", line.strip()):
            return line.strip()
    return type(exc).__name__


def in_browser(figs: list, work, out: Path = None):
    """Open the figures in a headless browser and call work(page). (result, why it did not run)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, (f"the playwright package is not importable from {sys.executable}; "
                      "install it only where your instructions allow installing packages")
    with tempfile.TemporaryDirectory() as tmp:
        page_path = (out or Path(tmp)) / ("preview.html" if out else "figures.html")
        page_path.write_text(host_page(figs, switch=out is not None))
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": 1440, "height": 2000}, device_scale_factor=2)
                page.goto(page_path.resolve().as_uri())
                page.wait_for_timeout(200)
                result = work(page)
                browser.close()
        except Exception as exc:  # the browser is missing or did not start: say so, measure nothing
            return None, f"the browser did not start ({browser_error(exc)}); `python3 -m playwright install chromium` where installing is allowed"
    return result, ""


def check(a) -> int:
    marks, found, drawn = source_check(a)
    measured = False
    if drawn and not a.no_measure:
        js = (HERE / "svg_geom_lint.js").read_text()
        result, why = in_browser(drawn, lambda page: page.evaluate(js))
        if result is None:
            found.append(("NOTE", "", "", f"measured checks did not run: {why}"))
        else:
            measured = True
            found = [f for f in found if f[2] != "text-too-small"]
            order = {"error": 0, "warn": 1, "advisory": 2}
            for f in sorted(result, key=lambda f: (f.get("svg", ""), order.get(f.get("tier"), 3))):
                tier, where, kind = TIERS.get(f.pop("tier", ""), "NOTE"), f.pop("svg", ""), f.pop("type", "")
                found.append((tier, where, kind, json.dumps(f, ensure_ascii=False)))
    problems = show(found)
    print(f"measured={'yes' if measured else 'no'}")
    print(f"warnings={sum(tier == 'WARN' for tier, _, _, _ in found)}")
    print(f"problems={problems}")
    return 1 if problems else 0


def preview(a) -> int:
    marks, found, drawn = source_check(a)
    if not drawn:
        print("nothing to show: no figure file that parses")
        return 1
    out = Path(a.out) if a.out else Path(tempfile.mkdtemp(prefix="figures-preview-"))
    out.mkdir(parents=True, exist_ok=True)

    def shoot(page):
        paths = []
        for theme, suffix in (("light", ""), ("dark", "-dark")):
            page.evaluate("t => { document.documentElement.dataset.theme = t; }", theme)
            for i, (fid, _, _) in enumerate(drawn):
                path = out / f"{fid}{suffix}.png"
                page.locator(".fig").nth(i).screenshot(path=str(path))
                paths.append(path)
        return paths

    paths, why = in_browser(drawn, shoot, out)
    if paths is None:
        (out / "preview.html").write_text(host_page(drawn, switch=True))
        print(f"NOTE no pictures: {why}")
        print(f"open {out / 'preview.html'} in a browser and look at each figure there")
        return 0
    for p in paths:
        print(p)
    print(out / "preview.html")
    print(f"pictures={len(paths)}")
    return 0


# ---- finishing the files ----------------------------------------------------------------------------------

def stamp(svg: str, width: float, height: float) -> str:
    """The figure file with the token block as its first child and its size on the root."""
    svg = TOKENS.sub("", svg)
    root = ROOT.search(svg)
    tag = re.sub(r"\s(?:width|height)=(\"[^\"]*\"|'[^']*')", "", root.group(0))
    tag = tag[:-1].rstrip() + f' width="{width:g}" height="{height:g}">'
    return svg[:root.start()] + tag + "\n  " + token_block() + svg[root.end():]


def place(a) -> int:
    marks, found, drawn = source_check(a)
    problems = show(found)
    if problems:
        print(f"problems={problems}")
        print("nothing was placed: fix what the check lists first")
        return 1
    lines = a.text.read_text().split("\n")
    for m in reversed(marks):
        path = a.figures / f"{m['id']}.svg"
        svg = path.read_text()
        done = stamp(svg, *view_box(ET.fromstring(svg)))
        if done != svg:
            path.write_text(done)
        target = Path(os.path.relpath(path, a.text.parent)).as_posix()
        if re.search(r"[\s()]", target):
            target = f"<{target}>"
        alt = m["claim"].replace("[", "\\[").replace("]", "\\]")
        image = f"![{alt}]({target})"
        if m["image"] is not None:
            lines[m["image"]] = image
        else:
            lines[m["at"]:m["at"]] = [image, ""]
    a.text.write_text("\n".join(lines))
    for m in marks:
        print(f"{m['id']}: placed")
    print(f"placed={len(marks)}")
    return 0


def list_marks(a) -> int:
    marks = read_marks(a.text.read_text())
    drawn = 0
    for m in marks:
        path = a.figures / f"{m['id']}.svg"
        drawn += path.exists()
        where = Path(os.path.relpath(path, a.text.parent)).as_posix()
        print(f"{m['id']}  line {m['line']}  {where}  {'drawn' if path.exists() else 'not drawn'}  {m['claim']}")
    print(f"marks={len(marks)} drawn={drawn}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("marks", list_marks), ("brief", brief), ("check", check), ("preview", preview), ("place", place)):
        p = sub.add_parser(name)
        p.add_argument("text", type=Path)
        p.add_argument("--figures", type=Path, help="the figures folder, if not figures/<name of the text>/ beside the text")
        p.set_defaults(fn=fn)
        if name == "check":
            p.add_argument("--no-measure", action="store_true", help="read the sources only, start no browser")
        if name == "preview":
            p.add_argument("--out", help="the folder for the pictures")
    a = ap.parse_args(argv)
    if not a.text.is_file():
        print(f"no such file: {a.text}")
        return 2
    a.figures = a.figures or a.text.parent / "figures" / a.text.stem
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
