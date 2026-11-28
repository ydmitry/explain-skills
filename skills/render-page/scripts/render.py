#!/usr/bin/env python3
"""Render a Markdown text as one HTML page: python3 render.py TEXT [-o PAGE] [--title T] [--figures DIR]

The page says what the text says and nothing else: the only words it adds are a list of the sections and
two switches, in a bar. It asks the network for nothing. A `Figure: <sentence>` line becomes the Nth figure,
taken from fig-N.svg in figures/<name of the text>/ beside the text (or DIR), with the sentence as caption.

What it renders: headings, paragraphs, bold, italic, strike, code, links, lists that nest, tables, fenced
code, quotes, rules, local pictures. What it cannot render it refuses, with the line: raw HTML, a `mermaid`
block, a picture from the web, a footnote, a mark with no figure file. Then it writes no page.

Prints the page's path and `sections=N figures=M`, or `ERROR line N: ...` lines and `errors=N` (exit 1).
"""
import argparse
import base64
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARK = re.compile(r"Figure:\s+(\S.*?)\s*$")
IMAGE = re.compile(r"!\[(.*)\]\(\s*<?([^()<>]+?)>?\s*\)\s*$")
ITEM = re.compile(r"(\s*)([-*+]|\d+[.)])\s+(.*)$")
FENCE = re.compile(r"\s*(```+|~~~+)\s*([\w+-]*)\s*$")
ROW_RULE = re.compile(r"\s*\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)*\|?\s*$")
ROOT = re.compile(r"<svg\b(?:[^>\"']|\"[^\"]*\"|'[^']*')*>")
TOKENS = re.compile(r"\s*<style data-tokens[^>]*>.*?</style>", re.S)
ABBREV = re.compile(r"(?i)\b(?:e\.g|i\.e|etc|vs|approx|incl|cf|ca|fig)\.$")
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif",
        ".webp": "image/webp", ".svg": "image/svg+xml"}
SHRINK = 0.8  # a figure is shown at its drawn size down to this share of it, then it scrolls sideways
INLINE = re.compile(
    r"(?P<code>(?P<cd>`+)(?P<ctext>.+?)(?P=cd))"
    r"|(?P<image>!\[[^\]]*\]\([^)]*\))"
    r"|(?P<link>\[(?P<ltext>(?:[^\[\]]|\[[^\]]*\])+)\]\(\s*<?(?P<lurl>[^\s)>]+)>?(?:\s+\"[^\"]*\")?\s*\))"
    r"|(?P<auto><(?P<aurl>(?:https?://|mailto:)[^>\s]+)>)"
    r"|(?P<note>\[\^[^\]]+\])"
    r"|(?P<tag></?[a-zA-Z][\w-]*(?:\s[^<>]*)?/?>|<!--)"
    r"|(?P<bold>(?P<bd>\*\*|__)(?=\S)(?P<btext>.+?)(?<=\S)(?P=bd))"
    r"|(?P<strike>~~(?=\S)(?P<stext>.+?)(?<=\S)~~)"
    r"|(?P<ital>(?<![\w*])(?P<id>[*_])(?=\S)(?P<itext>.+?)(?<=\S)(?P=id)(?![\w*]))"
    r"|(?P<esc>\\(?P<echar>[\\`*_{}\[\]()#+\-.!|<>~]))"
    r"|(?P<br> {2,}\n|\\\n)")


class Page:
    def __init__(self, text_path: Path, figures: Path):
        self.dir, self.figures = text_path.parent, figures
        self.errors, self.ids, self.sections, self.nfig = [], {}, [], 0
        self.title = None

    def error(self, line: int, what: str):
        self.errors.append((line, what))

    # ---- inline ----------------------------------------------------------------------------------------

    def inline(self, s: str, line: int) -> str:
        out, at = [], 0
        for m in INLINE.finditer(s):
            out.append(html.escape(s[at:m.start()], quote=False))
            at = m.end()
            if m.group("code"):
                out.append(f"<code>{html.escape(m.group("ctext").strip() or m.group("ctext"), quote=False)}</code>")
            elif m.group("image"):
                self.error(line, "a picture inside a line of text: give it a paragraph of its own")
            elif m.group("link"):
                url = m.group("lurl")
                out.append(f'<a href="{html.escape(url)}">{self.inline(m.group("ltext"), line)}</a>')
            elif m.group("auto"):
                url = m.group("aurl")
                out.append(f'<a href="{html.escape(url)}">{html.escape(url.removeprefix("mailto:"), quote=False)}</a>')
            elif m.group("note"):
                self.error(line, f"a footnote ({m.group('note')}): say it in the text, a page has no footnotes")
            elif m.group("tag"):
                self.error(line, f"raw HTML ({m.group('tag')[:30]}): write it as Markdown, or put it in backticks to show it")
            elif m.group("bold"):
                out.append(f"<strong>{self.inline(m.group('btext'), line)}</strong>")
            elif m.group("strike"):
                out.append(f"<del>{self.inline(m.group('stext'), line)}</del>")
            elif m.group("ital"):
                out.append(f"<em>{self.inline(m.group('itext'), line)}</em>")
            elif m.group("esc"):
                out.append(html.escape(m.group("echar"), quote=False))
            elif m.group("br"):
                out.append("<br>\n")
        out.append(html.escape(s[at:], quote=False))
        return "".join(out)

    def prose(self, s: str, line: int) -> str:
        """A paragraph's inline HTML with everything after its first sentence marked, for the skim switch."""
        cut = first_sentence_end(s)
        if cut is None:
            return self.inline(s, line)
        return self.inline(s[:cut], line) + '<span class="rest">' + self.inline(s[cut:], line) + "</span>"

    # ---- blocks ----------------------------------------------------------------------------------------

    def blocks(self, lines: list, base: int, tight=False) -> str:
        """HTML for a run of lines. `base` is the number of the first line in the file."""
        out, i, n = [], 0, len(lines)
        while i < n:
            line = lines[i]
            no = base + i
            if not line.strip():
                i += 1
                continue
            fence = FENCE.match(line)
            if fence:
                j = i + 1
                while j < n and not re.match(rf"\s*{re.escape(fence.group(1)[:3])}+\s*$", lines[j]):
                    j += 1
                if fence.group(2).lower() == "mermaid":
                    self.error(no, "a mermaid block: a page shows drawn figures only. Replace it by a `Figure:` line "
                                   "and draw it, or keep this text as Markdown")
                indent = len(line) - len(line.lstrip())
                body = "\n".join(l[indent:] if l[:indent].strip() == "" else l for l in lines[i + 1:j])
                out.append(f"<pre><code>{html.escape(body, quote=False)}</code></pre>")
                i = j + 1
                continue
            head = re.match(r"(#{1,6})\s+(.*?)\s*#*\s*$", line)
            if head:
                out.append(self.heading(len(head.group(1)), head.group(2), no))
                i += 1
                continue
            if re.match(r"\s{0,3}([-*_])(\s*\1){2,}\s*$", line):
                out.append("<hr>")
                i += 1
                continue
            if line.startswith(">"):
                j = i
                while j < n and lines[j].startswith(">"):
                    j += 1
                inner = [re.sub(r"^> ?", "", l) for l in lines[i:j]]
                out.append(f"<blockquote>\n{self.blocks(inner, no)}\n</blockquote>")
                i = j
                continue
            if "|" in line and i + 1 < n and ROW_RULE.match(lines[i + 1]) and "-" in lines[i + 1]:
                j = i + 2
                while j < n and lines[j].strip() and "|" in lines[j]:
                    j += 1
                out.append(self.table(lines[i:j], no))
                i = j
                continue
            if ITEM.match(line):
                j = self.list_end(lines, i)
                out.append(self.list(lines[i:j], no))
                i = j
                continue
            mark = MARK.match(line)
            if mark:
                out.append(self.figure(mark.group(1), no))
                i += 1
                continue
            image = IMAGE.match(line.strip())
            if image:
                nxt = next((l for l in lines[i + 1:] if l.strip()), "")
                own = MARK.match(nxt) and Path(image.group(2)).name == f"fig-{self.nfig + 1}.svg"
                if not own:
                    out.append(self.picture(image.group(1), image.group(2), no))
                i += 1
                continue
            if re.match(r"\s*<(?:[a-zA-Z/!])", line):
                self.error(no, f"raw HTML ({line.strip()[:30]}): write it as Markdown")
                i += 1
                continue
            if re.match(r"( {4,}|\t)\S", line) and (i == 0 or not lines[i - 1].strip()):
                self.error(no, "an indented code block: put the code between ``` lines")
                i += 1
                continue
            j = i + 1
            while j < n and lines[j].strip() and not self.starts_block(lines[j]):
                j += 1
            if j < n and re.match(r"\s*(=+|-+)\s*$", lines[j]):
                self.error(base + j, "a line of = or - right under text: put a blank line above a rule, write a heading with #")
            para = " ".join(l.strip() for l in lines[i:j])
            body = self.prose(para, no)
            out.append(body if tight else f"<p>{body}</p>")
            i = j
        return "\n".join(out)

    @staticmethod
    def starts_block(line: str) -> bool:
        return bool(FENCE.match(line) or re.match(r"#{1,6}\s", line) or line.startswith(">") or ITEM.match(line)
                    or MARK.match(line) or re.match(r"\s{0,3}([-*_])(\s*\1){2,}\s*$", line))

    def heading(self, level: int, raw: str, line: int) -> str:
        body = self.inline(raw, line)
        words = re.sub(r"<[^>]+>", "", body)
        if level == 1 and self.title is None:
            self.title = html.unescape(words)
            return f"<h1>{body}</h1>"
        slug = re.sub(r"[^\w]+", "-", html.unescape(words).lower()).strip("-") or "section"
        self.ids[slug] = self.ids.get(slug, 0) + 1
        if self.ids[slug] > 1:
            slug = f"{slug}-{self.ids[slug]}"
        if level == 2:
            self.sections.append((slug, words))
        return f'<h{level} id="{slug}">{body}</h{level}>'

    def table(self, rows: list, line: int) -> str:
        def cells(row):
            row = row.strip()
            row = row[1:] if row.startswith("|") else row
            row = row[:-1] if row.endswith("|") and not row.endswith("\\|") else row
            return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", row)]

        align = [(" style=\"text-align:right\"" if c.endswith(":") and not c.startswith(":") else
                  " style=\"text-align:center\"" if c.endswith(":") and c.startswith(":") else "") for c in cells(rows[1])]
        pad = lambda k: align[k] if k < len(align) else ""
        out = ['<div class="scroll"><table>', "<thead><tr>"]
        out += [f"<th{pad(k)}>{self.inline(c, line)}</th>" for k, c in enumerate(cells(rows[0]))]
        out.append("</tr></thead>\n<tbody>")
        for r, row in enumerate(rows[2:]):
            out.append("<tr>" + "".join(f"<td{pad(k)}>{self.inline(c, line + 2 + r)}</td>" for k, c in enumerate(cells(row))) + "</tr>")
        out.append("</tbody></table></div>")
        return "\n".join(out)

    @staticmethod
    def list_end(lines: list, i: int) -> int:
        """The index after the last line of the list that starts at i."""
        indent = len(ITEM.match(lines[i]).group(1))
        j = i + 1
        while j < len(lines):
            line = lines[j]
            if not line.strip():
                k = j + 1
                while k < len(lines) and not lines[k].strip():
                    k += 1
                if k < len(lines) and (len(lines[k]) - len(lines[k].lstrip()) > indent
                                       or (ITEM.match(lines[k]) and len(ITEM.match(lines[k]).group(1)) == indent)):
                    j = k
                    continue
                break
            lead = len(line) - len(line.lstrip())
            if lead < indent or (lead == indent and not ITEM.match(line)):
                break
            j += 1
        return j

    def list(self, lines: list, line: int) -> str:
        first = ITEM.match(lines[0])
        indent, ordered = len(first.group(1)), first.group(2)[0].isdigit()
        items, starts = [], []
        for k, l in enumerate(lines):
            m = ITEM.match(l)
            if m and len(m.group(1)) == indent:
                items.append([m.group(3)])
                starts.append(k)
                width = len(l) - len(m.group(3))
            elif items:
                items[-1].append(l[width:] if l[:width].strip() == "" else l.lstrip())
        tag = "ol" if ordered else "ul"
        start = first.group(2)[:-1]
        open_tag = f'<ol start="{start}">' if ordered and start != "1" else f"<{tag}>"
        body = "\n".join(f"<li>{self.blocks(item, line + starts[k], tight=len([x for x in item if x.strip()]) == 1 or self.one_para(item))}</li>"
                         for k, item in enumerate(items))
        return f"{open_tag}\n{body}\n</{tag}>"

    def one_para(self, item: list) -> bool:
        """True when an item is one paragraph, alone or followed only by a nested list."""
        rest = [l for l in item[1:] if l.strip()]
        return bool(rest) and (ITEM.match(rest[0]) is not None) and "" not in item[:item.index(rest[0])] if rest else True

    def figure(self, raw: str, line: int) -> str:
        self.nfig += 1
        fid = f"fig-{self.nfig}"
        path = self.figures / f"{fid}.svg"
        if not path.exists():
            self.error(line, f"the mark has no figure: {path} is not there. Draw it, or take the mark out")
            return ""
        svg = TOKENS.sub("", re.sub(r"<\?xml[^>]*\?>", "", path.read_text())).strip()
        root = ROOT.search(svg)
        box = re.search(r"viewBox=[\"']\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)", root.group(0)) if root else None
        if not box:
            self.error(line, f"{path.name} is no figure file: its root has no viewBox")
            return ""
        width = float(box.group(1))
        tag = re.sub(r"\s(?:width|height|style)=(\"[^\"]*\"|'[^']*')", "", root.group(0))
        tag = tag[:-1].rstrip() + f' style="max-width:{width:g}px;min-width:{width * SHRINK:g}px">'
        svg = svg[:root.start()] + tag + svg[root.end():]
        return f'<figure>\n<figcaption>{self.inline(raw, line)}</figcaption>\n<div class="fig">{svg}</div>\n</figure>'

    def picture(self, alt: str, src: str, line: int) -> str:
        if re.match(r"[a-zA-Z][\w+.-]*:", src):
            self.error(line, f"a picture from the web ({src[:50]}): the page asks the network for nothing; save it beside the text")
            return ""
        path = (self.dir / src).resolve()
        kind = MIME.get(path.suffix.lower())
        if not path.is_file() or not kind:
            self.error(line, f"the picture {src} is not a file this page can carry (png, jpg, gif, webp, svg)")
            return ""
        data = base64.b64encode(path.read_bytes()).decode()
        return f'<p><img alt="{html.escape(plain(alt))}" src="data:{kind};base64,{data}"></p>'


def plain(md: str) -> str:
    md = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", md)
    md = re.sub(r"`+([^`]*)`+", r"\1", md)
    md = re.sub(r"(\*\*|__)(.+?)\1", r"\2", md)
    return " ".join(md.split())


def first_sentence_end(s: str):
    """The index where a paragraph's first sentence ends, when more follows and no code, link or bold is cut."""
    for m in re.finditer(r"[.!?][\"')\]*_]*(?=\s)", s):
        end = m.end()
        head, tail = s[:end], s[end:]
        if not tail.strip() or ABBREV.search(s[:m.start() + 1]) or tail.lstrip()[:1].islower():
            continue
        if head.count("`") % 2 or head.count("**") % 2 or head.count("__") % 2 or head.count("[") != head.count("]") \
                or head.count("(") != head.count(")") or len(re.findall(r"(?<![\w*])[*_](?=\S)|(?<=\S)[*_](?![\w*])", re.sub(r"\*\*|__", "", head))) % 2:
            continue
        return end
    return None


def strip_front(text: str):
    """(the lines of the text, how many lines of settings were taken off the top)."""
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return lines[i + 1:], i + 1
    return lines, 0


def token_css() -> str:
    """The tokens for a light screen, a dark one, and the reader's own choice in the bar."""
    css = re.sub(r"/\*.*?\*/", "", (HERE.parent / "assets" / "tokens.css").read_text(), flags=re.S).strip()
    light, dark = css.split("@media", 1)
    dark = re.search(r":root\s*\{(.*?)\}", dark, re.S).group(1).strip()
    dark = "\n".join("    " + d.strip() for d in dark.split("\n"))
    return (light.strip() + "\n"
            ':root[data-theme="dark"] {\n' + dark + "\n}\n"
            '@media (prefers-color-scheme: dark) {\n:root:not([data-theme="light"]) {\n' + dark + "\n}\n}")


def render(text_path: Path, figures: Path = None, title: str = None):
    """(the page as a string or None, the page's Page with errors, sections and figure count)."""
    figures = figures or text_path.parent / "figures" / text_path.stem
    page = Page(text_path, figures)
    lines, skipped = strip_front(text_path.read_text())
    body = page.blocks(lines, skipped + 1)
    if page.title is None:
        if title:
            page.title = title
            body = f"<h1>{html.escape(title, quote=False)}</h1>\n" + body
        else:
            page.error(1, "the text has no `# ` title: give one with --title")
    if page.errors:
        return None, page
    toc = "\n".join(f'    <a href="#{slug}">{words}</a>' for slug, words in page.sections)
    out = (HERE.parent / "assets" / "page.html").read_text()
    for key, value in (("{{title}}", html.escape(page.title, quote=False)), ("{{tokens}}", token_css()),
                       ("{{toc}}", toc), ("{{body}}", body)):
        out = out.replace(key, value, 1)
    return out, page


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text", type=Path)
    ap.add_argument("-o", "--out", type=Path, help="the page to write; the text's name with .html by default")
    ap.add_argument("--title", help="the title, for a text with no `# ` heading")
    ap.add_argument("--figures", type=Path, help="the figures folder, if not figures/<name of the text>/ beside the text")
    a = ap.parse_args(argv)
    if not a.text.is_file():
        print(f"no such file: {a.text}")
        return 2
    out, page = render(a.text, a.figures, a.title)
    if out is None:
        for line, what in sorted(page.errors):
            print(f"ERROR line {line}: {what}")
        print(f"errors={len(page.errors)}")
        return 1
    target = a.out or a.text.with_suffix(".html")
    target.write_text(out)
    print(target)
    print(f"sections={len(page.sections)} figures={page.nfig}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
