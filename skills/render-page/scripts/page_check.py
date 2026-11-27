#!/usr/bin/env python3
"""Check a page against the text it was rendered from: python3 page_check.py PAGE TEXT [--figures DIR]

One line per problem, then `words=N`, `measured=yes|no` and, last, `problems=N`. Exit 0 when problems=0.

  not-the-render  the page is not what render.py makes of the text now: the page was edited by hand, or
                  the text or a figure changed after it was rendered. Render again; never edit the page.
  words-differ    the words a reader sees on the page are not the words of the text, in order. The bar
                  (the list of sections and the two switches) is not counted. This is read from the page
                  and from the Markdown separately, so it also catches a fault of the renderer.
  network         the page would ask the network for a file.
  figures         the page does not hold one figure for each mark.
  overflow        (measured) at a width of 320, 360 or 768 the page is wider than the screen.
  small-text      (measured) at a width of 360 a label of a figure is drawn under 9.5 pixels.
  console         (measured) the page's script reported an error.

The measured checks need the playwright package; without it they do not run and the output says so.
--no-measure skips them.
"""
import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render  # noqa: E402

WORD = re.compile(r"[^\W_]+")
WIDTHS = (320, 360, 768)
MIN_FONT = 9.5


class Seen(HTMLParser):
    """The words a reader sees in the page's text: not the bar, not a script or a style, not inside a figure's drawing."""
    VOID = {"meta", "br", "hr", "img", "link", "input", "path", "rect", "line", "circle", "ellipse", "use", "polyline", "polygon", "stop"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.hidden, self.words, self.figures, self.net = [], 0, [], 0, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "svg" and (a.get("id") or "").startswith("fig-"):
            self.figures += 1
        for key in ("src", "href"):
            if tag != "a" and re.match(r"(?:https?:)?//", a.get(key) or ""):
                self.net.append(f"<{tag} {key}={a[key][:60]}>")
        if tag in self.VOID:
            return
        hide = tag in ("script", "style", "svg", "title", "head") or "data-chrome" in a
        self.stack.append((tag, hide))
        self.hidden += hide

    def handle_startendtag(self, tag, attrs):
        if tag not in self.VOID:
            self.handle_starttag(tag, attrs)
            self.handle_endtag(tag)
        else:
            self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        while self.stack:
            t, hide = self.stack.pop()
            self.hidden -= hide
            if t == tag:
                break

    def handle_data(self, data):
        if not self.hidden:
            self.words += WORD.findall(data)


def text_words(text: str, title=None) -> list:
    """The words of a Markdown text as a reader of the rendered page meets them."""
    lines, _ = render.strip_front(text)
    out, fenced, marks = [], False, 0
    if title:
        out += WORD.findall(title)
    for i, line in enumerate(lines):
        if re.match(r"\s*(```|~~~)", line):
            fenced = not fenced
            continue
        if fenced:
            out += WORD.findall(line)
            continue
        if re.match(r"\s*!\[.*\]\([^)]*\)\s*$", line):          # a picture: its words are not on the page
            continue
        if render.ROW_RULE.match(line) and "-" in line and "|" in line:  # the rule under a table's head
            continue
        if re.match(r"\s{0,3}([-*_])(\s*\1){2,}\s*$", line):
            continue
        line = re.sub(r"^Figure:\s+", "", line)
        line = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line)
        line = re.sub(r"^(?:>\s?)+", "", line)
        line = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line)
        line = re.sub(r"^#{1,6}\s+", "", line)
        line = re.sub(r"!?\[((?:[^\[\]]|\[[^\]]*\])*)\]\(\s*<?[^\s)>]+>?(?:\s+\"[^\"]*\")?\s*\)", r"\1", line)
        line = re.sub(r"<mailto:([^>\s]+)>", r"\1", line)
        out += WORD.findall(line)
    return out


def first_difference(page: list, text: list) -> str:
    n = next((i for i, (a, b) in enumerate(zip(page, text)) if a != b), min(len(page), len(text)))
    show = lambda words: " ".join(words[max(0, n - 4):n + 6]) or "(the end)"
    return f'at word {n + 1} the page reads "{show(page)}" and the text reads "{show(text)}"'


def measure(page_path: Path):
    """(problems, why it did not run)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, f"the playwright package is not importable from {sys.executable}; install it only where your instructions allow"
    found = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for width in WIDTHS:
                page = browser.new_page(viewport={"width": width, "height": 900})
                errors = []
                page.on("pageerror", lambda e: errors.append(str(e).splitlines()[0]))
                page.goto(page_path.as_uri())
                page.wait_for_timeout(150)
                over = page.evaluate("""() => {
                    const w = document.documentElement.clientWidth, out = [];
                    if (document.documentElement.scrollWidth > w + 1) out.push('the page is ' + document.documentElement.scrollWidth + ' wide');
                    for (const el of document.querySelectorAll('main *')) {
                      if (el.closest('.fig, .scroll, pre')) continue;
                      const r = el.getBoundingClientRect();
                      if (r.width && r.right > w + 1) { out.push('<' + el.tagName.toLowerCase() + '> ends at ' + Math.round(r.right)); break; }
                    }
                    return out; }""")
                found += [("overflow", f"at {width} wide: {o}") for o in over]
                if width == 360:
                    small = page.evaluate("""(min) => [...document.querySelectorAll('.fig svg')].flatMap(svg => {
                        const vb = svg.viewBox.baseVal, scale = vb && vb.width ? svg.getBoundingClientRect().width / vb.width : 1;
                        const bad = [...svg.querySelectorAll('text')].map(t => parseFloat(getComputedStyle(t).fontSize) * scale).filter(px => px < min);
                        return bad.length ? [svg.id + ': ' + bad.length + ' label(s), the smallest ' + Math.min(...bad).toFixed(1) + 'px'] : []; })""", MIN_FONT)
                    found += [("small-text", f"at 360 wide {s}") for s in small]
                found += [("console", e) for e in errors]
                page.close()
            browser.close()
    except Exception as exc:
        return None, f"the browser did not start ({str(exc).splitlines()[0]})"
    return found, ""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page", type=Path)
    ap.add_argument("text", type=Path)
    ap.add_argument("--figures", type=Path)
    ap.add_argument("--title")
    ap.add_argument("--no-measure", action="store_true")
    a = ap.parse_args(argv)
    for f in (a.page, a.text):
        if not f.is_file():
            print(f"no such file: {f}")
            return 2
    html_text = a.page.read_text()
    problems = []
    fresh, made = render.render(a.text, a.figures, a.title)
    if fresh is None:
        problems.append(("not-the-render", f"the text does not render now: {made.errors[0][1]} (line {made.errors[0][0]})"))
    elif fresh != html_text:
        problems.append(("not-the-render", "the page is not what render.py makes of the text now: render again, and never edit the page"))
    seen = Seen()
    seen.feed(html_text)
    wanted = text_words(a.text.read_text(), a.title if made.title == a.title else None)
    if seen.words != wanted:
        problems.append(("words-differ", first_difference(seen.words, wanted)))
    problems += [("network", n) for n in seen.net]
    if re.search(r"@import|url\(\s*[\"']?(?:https?:)?//", html_text):
        problems.append(("network", "a stylesheet asks for a file from the web"))
    if fresh is not None and seen.figures != made.nfig:
        problems.append(("figures", f"the text has {made.nfig} mark(s) and the page holds {seen.figures} figure(s)"))
    measured = False
    if not a.no_measure:
        found, why = measure(a.page)
        if found is None:
            print(f"NOTE measured checks did not run: {why}")
        else:
            measured = True
            problems += found
    for kind, detail in problems:
        print(f"PROBLEM {kind} {detail}")
    print(f"words={len(seen.words)}")
    print(f"measured={'yes' if measured else 'no'}")
    print(f"problems={len(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
