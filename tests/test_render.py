import importlib.util
import re
import tempfile
import unittest
from pathlib import Path

from util import SKILLS, run

R = "render-page/scripts/render.py"
C = "render-page/scripts/page_check.py"
F = "draw-figures/scripts/figures.py"
CLAIM = "Before the fix 3 of 8 checks passed, after it all 8 pass."
FIG = f'''<svg xmlns="http://www.w3.org/2000/svg" id="fig-1" viewBox="0 0 320 120" role="img"
     aria-label="{CLAIM}">
  <defs><style>
    #fig-1 .lbl {{ font-size: 12px; }}
  </style></defs>
  <rect x="24" y="40" width="42" height="20" rx="4" style="fill:var(--error)"/>
  <text class="lbl" x="24" y="84">3 of 8 pass</text>
  <rect x="184" y="40" width="112" height="20" rx="4" style="fill:var(--ok)"/>
  <text class="lbl" x="184" y="84">all 8 pass</text>
</svg>
'''
BRIEF = f"## fig-1\nclaim: {CLAIM}\nshape: the Gap\ndata: 3 of 8, then 8 of 8\nconstraints: none\n"
TEXT = f"""# The fix and the checks

**The fix made every check pass.** Before it most of them failed. See `run.log`.

## What changed

The guard now runs first, so a bad header never registers. It is [documented](https://example.com/guard).

Figure: {CLAIM}

1. Parse the header.
2. Run the guard.
   - It reads the name.
   - It reads the description.

| Check | Before | After |
|---|---|---|
| name | fail | pass |
| description | fail | pass |

```
guard --strict a < b
```

> A header that fails is never registered.

## Limits

One run, one machine.
"""
HAS_BROWSER = importlib.util.find_spec("playwright") is not None


class Folder(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.text = self.root / "text.md"
        self.page = self.root / "text.html"
        self.figs = self.root / "figures" / "text"
        self.figs.mkdir(parents=True)
        self.text.write_text(TEXT)
        (self.figs / "fig-1.svg").write_text(FIG)
        (self.figs / "brief.md").write_text(BRIEF)

    def tearDown(self):
        self.tmp.cleanup()

    def render(self, text=None, *more):
        if text is not None:
            self.text.write_text(text)
        code, out = run(R, self.text, *more)
        return code, out, self.page.read_text() if self.page.exists() else ""

    def last(self, out):
        return out.strip().split("\n")[-1]


class Render(Folder):
    def test_the_page_holds_the_title_the_sections_and_the_text(self):
        code, out, html = self.render()
        self.assertEqual(code, 0, out)
        self.assertIn("<title>The fix and the checks</title>", html)
        self.assertIn("<h1>The fix and the checks</h1>", html)
        self.assertRegex(html, r'<h2 id="what-changed">What changed</h2>')
        self.assertRegex(html, r'<a href="#what-changed">What changed</a>')
        self.assertRegex(html, r'<a href="#limits">Limits</a>')
        self.assertIn("<strong>The fix made every check pass.</strong>", html)
        self.assertIn("<code>run.log</code>", html)
        self.assertIn('<a href="https://example.com/guard">documented</a>', html)

    def test_lists_nest_and_a_table_and_code_and_a_quote_are_rendered(self):
        code, out, html = self.render()
        flat = re.sub(r"\s+", " ", html)
        self.assertRegex(flat, r"<ol> ?<li>Parse the header\.</li> ?<li>Run the guard\. ?<ul> ?<li>It reads the name\.</li>")
        self.assertRegex(flat, r"<th>Check</th> ?<th>Before</th>")
        self.assertRegex(flat, r"<td>description</td> ?<td>fail</td> ?<td>pass</td>")
        self.assertIn("guard --strict a &lt; b", html)
        self.assertRegex(flat, r"<blockquote> ?<p>A header that fails is never registered\.</p> ?</blockquote>")

    def test_the_figure_stands_inline_with_the_marks_sentence_as_its_caption(self):
        code, out, html = self.render()
        self.assertIn('id="fig-1"', html)
        self.assertRegex(re.sub(r"\s+", " ", html), rf"</svg> ?</div> ?<figcaption>{re.escape(CLAIM)}</figcaption>")
        self.assertNotIn("Figure:", html)
        self.assertRegex(html, r"max-width:\s*320px")
        self.assertRegex(html, r"min-width:\s*256px")

    def test_a_placed_figure_loses_its_token_block_and_its_image_line(self):
        run(F, "place", self.text)
        self.assertIn("data-tokens", (self.figs / "fig-1.svg").read_text())
        code, out, html = self.render()
        self.assertEqual(code, 0, out)
        self.assertNotIn("data-tokens", html)
        self.assertNotIn("<img", html)
        self.assertEqual(html.count('id="fig-1"'), 1)

    def test_the_rest_of_a_paragraph_after_its_first_sentence_is_marked(self):
        code, out, html = self.render()
        self.assertIn('The guard now runs first, so a bad header never registers.<span class="rest"> It is <a', html)

    def test_the_page_asks_the_network_for_nothing(self):
        code, out, html = self.render()
        self.assertNotRegex(html, r'<(?:script|link|img|iframe)[^>]+(?:src|href)="https?:')
        self.assertNotIn("@import", html)
        self.assertNotRegex(html, r"url\(\s*[\"']?https?:")

    def test_what_it_prints(self):
        code, out, html = self.render()
        self.assertIn(str(self.page), out)
        self.assertEqual(self.last(out), "sections=2 figures=1")

    def test_a_mermaid_block_is_refused(self):
        code, out, html = self.render("# T\n\n```mermaid\ngraph LR; a-->b\n```\n")
        self.assertEqual(code, 1)
        self.assertIn("ERROR line 3", out)
        self.assertIn("mermaid", out)
        self.assertEqual(html, "")

    def test_raw_html_is_refused(self):
        code, out, html = self.render("# T\n\n<div>raw</div>\n\nA line with <br> in it.\n")
        self.assertEqual(code, 1)
        self.assertIn("ERROR line 3", out)
        self.assertIn("ERROR line 5", out)
        self.assertEqual(self.last(out), "errors=2")

    def test_an_angle_bracket_that_is_no_tag_is_shown(self):
        code, out, html = self.render("# T\n\nUse it when a < b and b > c.\n")
        self.assertEqual(code, 0, out)
        self.assertIn("a &lt; b and b &gt; c", html)

    def test_a_picture_from_the_web_is_refused_and_a_local_one_is_carried_in_the_page(self):
        code, out, html = self.render("# T\n\n![a chart](https://example.com/c.png)\n")
        self.assertEqual(code, 1)
        self.assertIn("ERROR line 3", out)
        (self.root / "dot.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        code, out, html = self.render("# T\n\n![a dot](dot.png)\n")
        self.assertEqual(code, 0, out)
        self.assertIn('<img alt="a dot" src="data:image/png;base64,', html)

    def test_a_mark_with_no_figure_is_refused(self):
        (self.figs / "fig-1.svg").unlink()
        code, out, html = self.render()
        self.assertEqual(code, 1)
        self.assertIn("fig-1", out)

    def test_a_text_with_no_title_needs_one(self):
        code, out, html = self.render("Just a paragraph.\n")
        self.assertEqual(code, 1)
        self.assertIn("title", out)
        code, out, html = self.render("Just a paragraph.\n", "--title", "A note")
        self.assertEqual(code, 0, out)
        self.assertIn("<h1>A note</h1>", html)

    def test_settings_at_the_top_and_a_line_wrapped_paragraph(self):
        code, out, html = self.render("---\nname: x\n---\n\n# T\n\nOne line\nand its second half.\n")
        self.assertEqual(code, 0, out)
        self.assertNotIn("name: x", html)
        self.assertIn("<p>One line and its second half.</p>", html)

    def test_two_headings_with_the_same_words_get_two_ids(self):
        code, out, html = self.render("# T\n\n## Limits\n\na\n\n## Limits\n\nb\n")
        self.assertIn('id="limits"', html)
        self.assertIn('id="limits-2"', html)


class Contract(unittest.TestCase):
    def test_the_two_skills_hold_the_same_tokens(self):
        self.assertEqual((SKILLS / "draw-figures/assets/tokens.css").read_text(),
                         (SKILLS / "render-page/assets/tokens.css").read_text())


class PageCheck(Folder):
    def check(self, *more):
        return run(C, self.page, self.text, "--no-measure", *more)

    def test_a_page_just_rendered_passes(self):
        self.render()
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertEqual(self.last(out), "problems=0")
        self.assertRegex(out, r"words=\d+")

    def test_a_page_edited_by_hand_is_a_problem(self):
        self.render()
        self.page.write_text(self.page.read_text().replace("One run, one machine.", "One run, one machine, and it was great."))
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("PROBLEM not-the-render", out)
        self.assertIn("PROBLEM words-differ", out)

    def test_a_text_changed_after_the_render_is_a_problem(self):
        self.render()
        self.text.write_text(TEXT.replace("One run", "Two runs"))
        code, out = self.check()
        self.assertIn("PROBLEM not-the-render", out)

    def test_words_in_the_bar_are_not_counted_as_text(self):
        self.render()
        code, out = self.check()
        self.assertNotIn("Skim", out)

    @unittest.skipUnless(HAS_BROWSER, "the playwright package is not installed")
    def test_a_rendered_page_fits_a_phone(self):
        self.render()
        code, out = run(C, self.page, self.text)
        self.assertIn("measured=yes", out)
        self.assertEqual(code, 0, out)

    @unittest.skipUnless(HAS_BROWSER, "the playwright package is not installed")
    def test_a_page_wider_than_a_phone_is_a_problem(self):
        self.render()
        self.page.write_text(self.page.read_text().replace("<main>", '<main><div style="width:900px">x</div>'))
        code, out = run(C, self.page, self.text)
        self.assertIn("PROBLEM overflow", out)


if __name__ == "__main__":
    unittest.main()


class RelativePaths(Folder):
    def test_the_page_check_measures_when_the_paths_are_relative(self):
        self.render()
        code, out = run(C, "text.html", "text.md", cwd=self.root)
        self.assertIn("measured=yes", out)
        self.assertEqual(code, 0, out)
