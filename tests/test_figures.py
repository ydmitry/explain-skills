import importlib.util
import re
import tempfile
import unittest
from pathlib import Path

from util import SKILLS, run

F = "draw-figures/scripts/figures.py"
CLAIM = "Before the fix 3 of 8 checks passed, after it all 8 pass."
TEXT = f"# Title\n\nThe fix changed the checks.\n\nFigure: {CLAIM}\n\nMore text.\n"
GOOD = f'''<svg xmlns="http://www.w3.org/2000/svg" id="fig-1" viewBox="0 0 320 120" role="img"
     aria-label="{CLAIM}">
  <defs><style>
    #fig-1 .lbl {{ font-size: 12px; }}
  </style></defs>
  <rect x="24" y="40" width="112" height="20" rx="4" style="fill:var(--bg); stroke:var(--border)"/>
  <rect x="24" y="40" width="42" height="20" rx="4" style="fill:var(--error)"/>
  <text class="lbl" x="24" y="84">3 of 8 pass</text>
  <rect x="184" y="40" width="112" height="20" rx="4" style="fill:var(--ok)"/>
  <text class="lbl" x="184" y="84">all 8 pass</text>
</svg>
'''
BRIEF = f"""# Figure brief: text.md

text: text.md
canvas: 320 wide
palette: --ok pass, --error fail

## fig-1
claim: {CLAIM}
shape: the Gap
data: before 3 of 8, after 8 of 8 (text.md:5)
constraints: one track width for both states
"""
HAS_BROWSER = importlib.util.find_spec("playwright") is not None


class Folder(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.text = self.root / "text.md"
        self.figs = self.root / "figures" / "text"
        self.figs.mkdir(parents=True)
        self.text.write_text(TEXT)

    def tearDown(self):
        self.tmp.cleanup()

    def draw(self, svg=GOOD, brief=BRIEF, name="fig-1.svg"):
        (self.figs / name).write_text(svg)
        if brief is not None:
            (self.figs / "brief.md").write_text(brief)

    def check(self, *more):
        return run(F, "check", self.text, "--no-measure", *more)

    def last(self, out):
        return out.strip().split("\n")[-1]


class Marks(Folder):
    def test_marks_lists_each_mark_with_its_file(self):
        code, out = run(F, "marks", self.text)
        self.assertEqual(code, 0, out)
        self.assertIn("fig-1", out)
        self.assertIn("line 5", out)
        self.assertIn("figures/text/fig-1.svg", out)
        self.assertIn(CLAIM, out)
        self.assertEqual(self.last(out), "marks=1 drawn=0")

    def test_a_figure_line_inside_a_code_fence_is_not_a_mark(self):
        self.text.write_text("# Title\n\n```\nFigure: This is an example of a mark.\n```\n")
        code, out = run(F, "marks", self.text)
        self.assertEqual(self.last(out), "marks=0 drawn=0")

    def test_marks_are_numbered_in_the_order_they_stand(self):
        self.text.write_text(TEXT + "\nFigure: A second claim stands lower in the text.\n")
        code, out = run(F, "marks", self.text)
        self.assertRegex(out, r"fig-2\s+line 9")
        self.assertEqual(self.last(out), "marks=2 drawn=0")


class Brief(Folder):
    def test_brief_writes_a_block_for_each_mark_with_its_sentence(self):
        code, out = run(F, "brief", self.text)
        self.assertEqual(code, 0, out)
        brief = (self.figs / "brief.md").read_text()
        self.assertIn("## fig-1", brief)
        self.assertIn(f"claim: {CLAIM}", brief)
        for field in ("shape:", "data:", "constraints:", "canvas:", "palette:"):
            self.assertIn(field, brief)

    def test_brief_keeps_what_was_filled_and_follows_a_changed_mark(self):
        self.draw()
        self.text.write_text(TEXT.replace("all 8 pass", "all 8 of them pass"))
        code, out = run(F, "brief", self.text)
        brief = (self.figs / "brief.md").read_text()
        self.assertIn("shape: the Gap", brief)
        self.assertIn("claim: Before the fix 3 of 8 checks passed, after it all 8 of them pass.", brief)
        self.assertNotIn(f"claim: {CLAIM}", brief)

    def test_brief_strips_markdown_from_the_claim(self):
        self.text.write_text("# T\n\nFigure: The **guard** in `retry.py` stops [a third try](https://example.com).\n")
        run(F, "brief", self.text)
        self.assertIn("claim: The guard in retry.py stops a third try.", (self.figs / "brief.md").read_text())


class Check(Folder):
    def test_a_complete_figure_passes(self):
        self.draw()
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertEqual(self.last(out), "problems=0")
        self.assertIn("measured=no", out)

    def test_a_mark_with_no_file_is_a_problem(self):
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("PROBLEM fig-1: not-drawn", out)

    def test_a_label_that_is_not_the_marks_sentence_is_a_problem(self):
        self.draw(GOOD.replace("after it all 8 pass.", "then all pass."))
        code, out = self.check()
        self.assertIn("PROBLEM fig-1: label-differs", out)
        self.assertEqual(code, 1)

    def test_a_typed_colour_is_a_problem(self):
        for bad in ('style="fill:#3f7d5c"', 'fill="green"', 'style="stroke: rgb(1,2,3)"'):
            self.draw(GOOD.replace('style="fill:var(--ok)"', bad))
            code, out = self.check()
            self.assertIn("PROBLEM fig-1: raw-color", out, bad)

    def test_keywords_that_are_no_colour_pass(self):
        self.draw(GOOD.replace('style="fill:var(--ok)"', 'fill="none" style="stroke:currentColor"'))
        code, out = self.check()
        self.assertNotIn("raw-color", out)

    def test_an_id_without_the_figures_id_is_a_problem(self):
        self.draw(GOOD.replace('<rect x="184"', '<rect id="after" x="184"'))
        code, out = self.check()
        self.assertIn("PROBLEM fig-1: unscoped-id", out)
        self.assertIn("after", out)

    def test_a_selector_without_the_figures_id_is_a_problem(self):
        self.draw(GOOD.replace("#fig-1 .lbl", ".lbl"))
        code, out = self.check()
        self.assertIn("PROBLEM fig-1: unscoped-style", out)

    def test_a_media_query_in_the_figure_is_a_problem(self):
        self.draw(GOOD.replace("#fig-1 .lbl { font-size: 12px; }",
                               "@media (prefers-color-scheme: dark) { #fig-1 .lbl { font-size: 12px; } }"))
        code, out = self.check()
        self.assertIn("PROBLEM fig-1: at-rule", out)

    def test_a_word_the_text_does_not_have_is_a_problem(self):
        self.draw(GOOD.replace(">all 8 pass<", ">all 8 pass in staging<"))
        code, out = self.check()
        self.assertIn("PROBLEM fig-1: new-words", out)
        self.assertIn("staging", out)
        self.assertNotIn("pass,", out)

    def test_a_number_the_text_does_not_have_is_a_problem(self):
        self.draw(GOOD.replace(">3 of 8 pass<", ">3 of 8 pass in 42 ms<"))
        code, out = self.check()
        self.assertIn("PROBLEM fig-1: new-numbers", out)
        self.assertIn("42", out)

    def test_a_word_in_the_figures_block_of_the_brief_passes(self):
        self.draw(GOOD.replace(">all 8 pass<", ">all 8 pass in staging<"),
                  BRIEF.replace("after 8 of 8", "after 8 of 8 in staging"))
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_a_number_in_a_source_pointer_allows_nothing(self):
        self.draw(GOOD.replace(">3 of 8 pass<", ">3 of 8 pass, 5<"))
        code, out = self.check()
        self.assertIn("PROBLEM fig-1: new-numbers", out)

    def test_a_number_of_the_brief_that_is_not_drawn_is_a_problem(self):
        self.draw(brief=BRIEF.replace("after 8 of 8", "after 8 of 8, 17 skipped"))
        code, out = self.check()
        self.assertIn("PROBLEM fig-1: value-not-drawn", out)
        self.assertIn("17", out)

    def test_no_brief_is_a_problem(self):
        self.draw(brief=None)
        code, out = self.check()
        self.assertIn("PROBLEM brief-missing", out)

    def test_a_brief_with_an_empty_shape_is_a_problem(self):
        self.draw(brief=BRIEF.replace("shape: the Gap", "shape:"))
        code, out = self.check()
        self.assertIn("PROBLEM fig-1: brief-incomplete", out)

    def test_a_brief_whose_claim_is_not_the_mark_is_a_problem(self):
        self.draw(brief=BRIEF.replace(CLAIM, "Something else is claimed here."))
        code, out = self.check()
        self.assertIn("PROBLEM fig-1: brief-claim-differs", out)

    def test_a_file_that_is_not_xml_is_a_problem(self):
        self.draw(GOOD.replace(">3 of 8 pass<", ">3 of 8 pass & more<"))
        code, out = self.check()
        self.assertIn("PROBLEM fig-1: not-xml", out)

    def test_a_script_a_gradient_and_a_link_out_are_problems(self):
        self.draw(GOOD.replace("</svg>", '<script>1</script><linearGradient id="fig-1-g"/>'
                                         '<use href="https://example.com/x.svg#a"/></svg>'))
        code, out = self.check()
        self.assertIn("banned-element", out)
        self.assertIn("script", out)
        self.assertIn("linearGradient", out)
        self.assertIn("PROBLEM fig-1: external-ref", out)

    def test_a_reference_to_an_id_that_is_not_there_is_a_problem(self):
        self.draw(GOOD.replace('rx="4" style="fill:var(--ok)"', 'rx="4" style="fill:var(--ok)" marker-end="url(#fig-1-arrow)"'))
        code, out = self.check()
        self.assertIn("PROBLEM fig-1: unresolved-ref", out)

    def test_a_typed_font_is_a_problem(self):
        self.draw(GOOD.replace("font-size: 12px;", "font-size: 12px; font-family: Helvetica;"))
        code, out = self.check()
        self.assertIn("PROBLEM fig-1: typed-font", out)

    def test_small_text_and_a_wide_canvas_are_problems(self):
        self.draw(GOOD.replace("font-size: 12px", "font-size: 8px").replace('viewBox="0 0 320 120"', 'viewBox="0 0 900 120"'))
        code, out = self.check()
        self.assertIn("PROBLEM fig-1: text-too-small", out)
        self.assertIn("PROBLEM fig-1: too-wide", out)

    def test_a_typed_size_is_a_problem(self):
        self.draw(GOOD.replace('viewBox="0 0 320 120"', 'viewBox="0 0 320 120" width="640" height="240"'))
        code, out = self.check()
        self.assertIn("PROBLEM fig-1: typed-size", out)

    def test_a_missing_namespace_and_role_are_problems(self):
        self.draw(GOOD.replace(' xmlns="http://www.w3.org/2000/svg"', "").replace(' role="img"', ""))
        code, out = self.check()
        self.assertIn("PROBLEM fig-1: no-xmlns", out)
        self.assertIn("PROBLEM fig-1: a11y-missing", out)

    def test_a_figure_file_with_no_mark_is_a_problem(self):
        self.draw()
        self.draw(GOOD.replace("fig-1", "fig-2"), name="fig-2.svg")
        code, out = self.check()
        self.assertIn("PROBLEM extra-file", out)
        self.assertIn("fig-2.svg", out)

    def test_a_mark_that_shares_its_paragraph_is_a_problem(self):
        self.draw()
        self.text.write_text(TEXT.replace(f"\n\nFigure: {CLAIM}\n\n", f"\nFigure: {CLAIM}\n\n"))
        code, out = self.check()
        self.assertIn("PROBLEM mark-not-alone", out)

    def test_a_mark_of_two_words_states_no_claim(self):
        self.text.write_text("# Title\n\nFigure: coverage chart\n")
        code, out = self.check()
        self.assertIn("PROBLEM mark-too-short", out)

    def test_a_text_with_no_marks_passes(self):
        self.text.write_text("# Title\n\nNo figure here.\n")
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertEqual(self.last(out), "problems=0")


class Place(Folder):
    def test_place_writes_the_tokens_the_size_and_an_image_line(self):
        self.draw()
        code, out = run(F, "place", self.text)
        self.assertEqual(code, 0, out)
        svg = (self.figs / "fig-1.svg").read_text()
        self.assertIn("<style data-tokens", svg)
        self.assertIn("--ok:", svg)
        self.assertIn("prefers-color-scheme: dark", svg)
        self.assertRegex(svg, r'<svg[^>]*\swidth="320"')
        self.assertRegex(svg, r'<svg[^>]*\sheight="120"')
        text = self.text.read_text()
        self.assertIn(f"![{CLAIM}](figures/text/fig-1.svg)\n\nFigure: {CLAIM}\n", text)

    def test_place_twice_changes_nothing_more(self):
        self.draw()
        run(F, "place", self.text)
        svg, text = (self.figs / "fig-1.svg").read_text(), self.text.read_text()
        code, out = run(F, "place", self.text)
        self.assertEqual(code, 0, out)
        self.assertEqual((self.figs / "fig-1.svg").read_text(), svg)
        self.assertEqual(self.text.read_text(), text)
        self.assertEqual(svg.count("<style data-tokens"), 1)
        self.assertEqual(text.count("![") , 1)

    def test_a_placed_figure_still_passes_the_check_and_is_one_mark(self):
        self.draw()
        run(F, "place", self.text)
        code, out = self.check()
        self.assertEqual(code, 0, out)
        code, out = run(F, "marks", self.text)
        self.assertEqual(self.last(out), "marks=1 drawn=1")

    def test_place_refuses_while_the_check_lists_problems(self):
        self.draw(GOOD.replace("var(--ok)", "#00ff00"))
        code, out = run(F, "place", self.text)
        self.assertEqual(code, 1)
        self.assertIn("raw-color", out)
        self.assertNotIn("data-tokens", (self.figs / "fig-1.svg").read_text())
        self.assertNotIn("![", self.text.read_text())

    def test_the_image_line_follows_a_changed_mark(self):
        self.draw()
        run(F, "place", self.text)
        new = CLAIM.replace("all 8 pass", "all 8 of them pass")
        self.text.write_text(self.text.read_text().replace(f"Figure: {CLAIM}", f"Figure: {new}"))
        (self.figs / "fig-1.svg").write_text((self.figs / "fig-1.svg").read_text().replace(CLAIM, new))
        (self.figs / "brief.md").write_text(BRIEF.replace(CLAIM, new))
        code, out = run(F, "place", self.text)
        self.assertEqual(code, 0, out)
        text = self.text.read_text()
        self.assertIn(f"![{new}](figures/text/fig-1.svg)", text)
        self.assertEqual(text.count("!["), 1)


class Tokens(unittest.TestCase):
    """The ratios the colour reference states hold for the values in tokens.css."""

    def setUp(self):
        css = (SKILLS / "draw-figures/assets/tokens.css").read_text()
        light, dark = css.split("@media")
        self.light = dict(re.findall(r"--([\w-]+):\s*(#[0-9a-f]{6});", light))
        self.dark = dict(self.light, **dict(re.findall(r"--([\w-]+):\s*(#[0-9a-f]{6});", dark)))

    @staticmethod
    def ratio(a, b):
        def lum(c):
            v = [x / 255 for x in c]
            v = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in v]
            return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]
        hi, lo = sorted((lum(a), lum(b)), reverse=True)
        return (hi + 0.05) / (lo + 0.05)

    @staticmethod
    def rgb(h):
        return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))

    def mix(self, a, share, b):
        return tuple(round(x * share + y * (1 - share)) for x, y in zip(a, b))

    def test_every_ink_reads_on_the_ground_and_on_its_own_zone(self):
        for name, t in (("light", self.light), ("dark", self.dark)):
            ground, text = self.rgb(t["surface"]), self.rgb(t["text"])
            for hue in ("ok", "warn", "error", "muted", "info"):
                ink = self.mix(self.rgb(t[hue]), 0.38, text)
                zone = self.mix(self.rgb(t[hue]), 0.12, ground)
                self.assertGreaterEqual(self.ratio(ink, ground), 4.5, f"{name} {hue}-ink on the ground")
                self.assertGreaterEqual(self.ratio(ink, zone), 4.5, f"{name} {hue}-ink on its zone")

    def test_every_solid_hue_is_a_visible_mark_on_the_ground(self):
        for name, t in (("light", self.light), ("dark", self.dark)):
            for hue in ("ok", "warn", "error", "muted", "info"):
                self.assertGreaterEqual(self.ratio(self.rgb(t[hue]), self.rgb(t["surface"])), 3, f"{name} {hue}")

    def test_label_text_reads_on_the_ground(self):
        for name, t in (("light", self.light), ("dark", self.dark)):
            for ink in ("text", "text-dim", "muted"):
                self.assertGreaterEqual(self.ratio(self.rgb(t[ink]), self.rgb(t["surface"])), 4.5, f"{name} {ink}")


@unittest.skipUnless(HAS_BROWSER, "the playwright package is not installed")
class Measured(Folder):
    def test_two_labels_drawn_on_top_of_each_other_are_a_problem(self):
        self.draw(GOOD.replace('<text class="lbl" x="184" y="84">', '<text class="lbl" x="30" y="86">'))
        code, out = run(F, "check", self.text)
        self.assertIn("measured=yes", out)
        self.assertIn("PROBLEM fig-1: text-collision", out)
        self.assertEqual(code, 1)

    def test_a_label_that_leaves_the_canvas_is_a_problem(self):
        self.draw(GOOD.replace('x="184" y="84">all 8 pass<', 'x="290" y="84">all 8 pass<'))
        code, out = run(F, "check", self.text)
        self.assertIn("PROBLEM fig-1: outside-viewbox", out)

    def test_a_complete_figure_passes_when_measured(self):
        self.draw()
        code, out = run(F, "check", self.text)
        self.assertIn("measured=yes", out)
        self.assertNotIn("PROBLEM", out)
        self.assertEqual(code, 0, out)

    def test_preview_writes_a_picture_for_a_light_and_a_dark_screen(self):
        self.draw()
        shots = self.root / "shots"
        code, out = run(F, "preview", self.text, "--out", shots)
        self.assertEqual(code, 0, out)
        light, dark = shots / "fig-1.png", shots / "fig-1-dark.png"
        self.assertTrue(light.exists() and dark.exists(), out)
        self.assertNotEqual(light.read_bytes(), dark.read_bytes())
        self.assertTrue((shots / "preview.html").exists())


class Scans(Folder):
    """Everything on a figure is scanned, not read: a long label and a crowd of words are listed."""

    def test_the_good_figure_gets_neither_warning(self):
        self.draw()
        code, out = self.check()
        self.assertNotIn("label-long", out)
        self.assertNotIn("words-many", out)

    def test_a_label_of_more_than_seven_words_is_a_warning(self):
        self.draw(GOOD.replace(">all 8 pass<", ">all 8 pass and all 8 pass and all<"))
        code, out = self.check()
        self.assertIn("WARN fig-1: label-long", out)
        self.assertIn("9 words", out)

    def test_more_than_twenty_words_on_a_figure_is_a_warning(self):
        more = "".join(f'<text class="lbl" x="10" y="{100 + i}">all 8 pass</text>' for i in range(7))
        self.draw(GOOD.replace("</svg>", more + "</svg>"))
        code, out = self.check()
        self.assertIn("WARN fig-1: words-many", out)
        self.assertNotIn("label-long", out)

    def test_a_pie_with_no_number_on_its_slices_is_listed(self):
        self.draw(brief=BRIEF.replace("shape: the Gap", "shape: pie"), svg=GOOD.replace(' data-value="3" data-of="8"', "").replace(' data-value="8" data-of="8"', ""))
        code, out = self.check()
        self.assertIn("values-not-marked", out)


if __name__ == "__main__":
    unittest.main()


class ReferenceExamples(unittest.TestCase):
    """Every whole figure a reference shows passes the check it teaches."""

    WORDS = {"new-words", "new-numbers", "value-not-drawn", "value-not-in-text", "brief-incomplete"}  # an example has no text behind it

    def test_every_whole_figure_in_the_references_passes_the_check(self):
        import xml.etree.ElementTree as ET
        failed = []
        for ref in sorted((SKILLS / "draw-figures/references").glob("*.md")):
            for n, block in enumerate(re.findall(r"```xml\n(.*?)```", ref.read_text(), flags=re.S), 1):
                start = block.find("<svg")
                if start < 0 or "</svg>" not in block:
                    continue
                svg = re.sub(r"\bfig-\d+\b", "fig-1", block[start:block.rindex("</svg>") + 6])
                try:
                    claim = " ".join(ET.fromstring(svg).get("aria-label").split())
                except ET.ParseError as exc:
                    failed.append(f"{ref.name} example {n}: not XML ({exc})")
                    continue
                with tempfile.TemporaryDirectory() as tmp:
                    text = Path(tmp) / "text.md"
                    text.write_text(f"# Title\n\nSome text.\n\nFigure: {claim}\n")
                    figs = Path(tmp) / "figures" / "text"
                    figs.mkdir(parents=True)
                    (figs / "fig-1.svg").write_text(svg)
                    (figs / "brief.md").write_text(f"# Figure brief: text.md\n\n## fig-1\nclaim: {claim}\nshape: the Gap\ndata: as drawn\nconstraints: none\n")
                    _, out = run(F, "check", text)
                for line in out.splitlines():
                    kind = line.split(": ", 1)[-1].split(" ")[0]
                    if line.startswith("PROBLEM") and kind not in self.WORDS:
                        failed.append(f"{ref.name} example {n}: {line[:150]}")
        self.assertEqual(failed, [], "\n" + "\n".join(failed))


class RelativePaths(Folder):
    def test_the_check_measures_when_the_text_is_given_by_a_relative_path(self):
        self.draw()
        code, out = run(F, "check", "text.md", cwd=self.root)
        self.assertIn("measured=yes", out)
        self.assertEqual(code, 0, out)

    def test_preview_writes_pictures_into_a_relative_folder(self):
        self.draw()
        code, out = run(F, "preview", "text.md", "--out", "shots", cwd=self.root)
        self.assertTrue((self.root / "shots" / "fig-1.png").exists(), out)


class PhoneWidth(Folder):
    def test_a_figure_drawn_wider_than_a_phone_shows_is_a_warning(self):
        self.draw(GOOD.replace('viewBox="0 0 320 120"', 'viewBox="0 0 560 120"'))
        code, out = self.check()
        self.assertIn("WARN fig-1: wide-for-phone", out)
        self.assertEqual(self.last(out), "problems=0")
        self.assertEqual(code, 0, out)

    def test_a_figure_400_wide_is_no_warning(self):
        self.draw(GOOD.replace('viewBox="0 0 320 120"', 'viewBox="0 0 400 120"'))
        code, out = self.check()
        self.assertNotIn("wide-for-phone", out)


class TwoLabelsNearEachOther(Folder):
    NEAR = GOOD.replace('<text class="lbl" x="184" y="84">all 8 pass</text>',
                        '<text class="lbl" x="27" y="103">all 8 pass</text>')

    def test_two_labels_that_do_not_line_up_are_not_called_one_split_label(self):
        self.draw(self.NEAR)
        code, out = run(F, "check", self.text)
        self.assertNotIn("split-label", out)
        self.assertIn("WARN fig-1: text-collision", out)
        self.assertIn("move", out)

    def test_two_lines_on_one_x_are_still_a_split_label(self):
        self.draw(self.NEAR.replace('x="27" y="103"', 'x="24" y="103"'))
        code, out = run(F, "check", self.text)
        self.assertIn("WARN fig-1: split-label", out)


class DrawnValues(Folder):
    """A mark that carries its number as data-value is drawn in proportion to it."""

    BARS = GOOD.replace('width="42" height="20" rx="4" style="fill:var(--error)"', 'width="42" height="20" rx="4" data-value="3" style="fill:var(--error)"') \
               .replace('<rect x="184" y="40" width="112"', '<rect x="184" y="40" data-value="8" width="112"')

    def kinds(self, out):
        return [l.split(": ", 1)[1].split(" ")[0] for l in out.splitlines() if l.startswith(("PROBLEM", "WARN"))]

    def test_bars_in_proportion_to_their_values_pass(self):
        self.draw(self.BARS)
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertNotIn("value-", out)

    def test_a_bar_out_of_proportion_is_a_problem(self):
        self.draw(self.BARS.replace('width="42" height="20" rx="4" data-value="3"', 'width="70" height="20" rx="4" data-value="3"'))
        code, out = self.check()
        self.assertIn("PROBLEM fig-1: value-mismatch", out)
        self.assertEqual(code, 1)

    def test_a_share_is_measured_against_its_track(self):
        share = self.BARS.replace('data-value="3"', 'data-value="3" data-of="8"').replace(' data-value="8"', "")
        self.draw(share)
        self.assertNotIn("value-", self.check()[1])
        self.draw(share.replace('width="42" height="20" rx="4" data-value="3"', 'width="56" height="20" rx="4" data-value="3"'))
        self.assertIn("PROBLEM fig-1: value-mismatch", self.check()[1])

    def test_a_value_the_text_does_not_have_is_a_problem(self):
        self.draw(self.BARS.replace('data-value="3"', 'data-value="5"'))
        self.assertIn("PROBLEM fig-1: value-not-in-text", self.check()[1])

    def test_a_ring_is_filled_to_its_share(self):
        ring = '<circle cx="160" cy="100" r="10" fill="none" style="stroke:var(--ok)" data-value="3" data-of="8" stroke-dasharray="%s"/>\n</svg>'
        self.draw(GOOD.replace("</svg>", ring % "37.5 100"))
        self.assertNotIn("value-", self.check()[1])
        self.draw(GOOD.replace("</svg>", ring % "50 100"))
        self.assertIn("PROBLEM fig-1: value-mismatch", self.check()[1])

    def test_cells_are_counted(self):
        def cells(on):
            row = "".join(f'<rect x="{24 + i * 10}" y="100" width="8" height="8"{" data-on=\"\"" if i < on else ""} style="fill:var(--ok)"/>' for i in range(8))
            return GOOD.replace("</svg>", f'<g data-value="3" data-of="8">{row}</g>\n</svg>')
        self.draw(cells(3))
        self.assertNotIn("value-", self.check()[1])
        self.draw(cells(4))
        self.assertIn("PROBLEM fig-1: value-mismatch", self.check()[1])

    def test_a_limit_line_stands_at_its_value(self):
        line = '<line x1="%s" y1="30" x2="%s" y2="70" data-value="8" style="stroke:var(--muted)"/>\n</svg>'
        one = self.BARS.replace(' data-value="8"', "")
        self.draw(one.replace("</svg>", line % (136, 136)))
        self.assertNotIn("value-", self.check()[1])
        self.draw(one.replace("</svg>", line % (100, 100)))
        self.assertIn("PROBLEM fig-1: value-mismatch", self.check()[1])

    def test_a_shape_of_values_with_no_marked_value_is_a_warning(self):
        self.draw(GOOD, BRIEF.replace("shape: the Gap", "shape: n-of-m fill"))
        code, out = self.check()
        self.assertIn("WARN fig-1: values-not-marked", out)
        self.assertEqual(code, 0, out)


class LimitOnAShare(Folder):
    SHARE = DrawnValues.BARS.replace('data-value="3"', 'data-value="3" data-of="8"').replace(' data-value="8"', "")
    LINE = '<line x1="%s" y1="30" x2="%s" y2="70" data-value="8" style="stroke:var(--muted)"/>\n</svg>'

    def test_a_limit_across_a_share_is_measured_on_the_track(self):
        self.draw(self.SHARE.replace("</svg>", self.LINE % (136, 136)))
        self.assertNotIn("value-", self.check()[1])
        self.draw(self.SHARE.replace("</svg>", self.LINE % (100, 100)))
        self.assertIn("PROBLEM fig-1: value-mismatch", self.check()[1])

    def test_a_line_with_a_value_and_nothing_to_measure_it_on_is_a_warning(self):
        self.draw(GOOD.replace("</svg>", self.LINE % (100, 100)))
        self.assertIn("WARN fig-1: value-no-scale", self.check()[1])

    def test_a_layout_number_on_the_data_line_gets_a_hint(self):
        self.draw(GOOD, BRIEF.replace("data: before 3 of 8", "data: row 1 before 3 of 8"))
        out = self.check()[1]
        self.assertIn("value-not-drawn", out)
        self.assertIn("the top row", out)
