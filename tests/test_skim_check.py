import tempfile
import unittest
from pathlib import Path

from util import run

K = "skimmable-writing/scripts/skim_check.py"
LONG = " ".join(["word"] * 61)


class SkimCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.file = Path(self.tmp.name) / "text.md"

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, text: str, *more):
        self.file.write_text(text)
        return run(K, self.file, *more)

    def test_a_text_inside_the_rules_passes(self):
        code, out = self.check("# Title\n\nThe point comes first. **It holds.**\n")
        self.assertEqual(code, 0, out)
        self.assertIn("problems=0", out)

    def test_a_long_paragraph_and_a_section_with_no_bold_are_listed(self):
        code, out = self.check(f"# Title\n\n{LONG}\n")
        self.assertEqual(code, 1)
        self.assertIn("paragraph of 61 words", out)
        self.assertIn("nothing in bold", out)

    def test_a_long_run_of_bullets_is_listed(self):
        code, out = self.check("# Title\n\n**Nine things.**\n\n" + "".join(f"- item {i}\n" for i in range(9)))
        self.assertIn("9 bullets in a row", out)

    def test_a_long_run_of_bullets_is_a_note_and_not_a_problem(self):
        code, out = self.check("# Title\n\n**Nine things.**\n\n" + "".join(f"- item {i}\n" for i in range(9)))
        self.assertEqual(code, 0)
        self.assertIn("NOTE Title: 9 bullets in a row", out)
        self.assertIn("problems=0", out)

    def test_settings_at_the_top_are_not_text(self):
        front = f"---\nname: a-skill\ndescription: {LONG}\n---\n\n"
        code, out = self.check(front + "# Title\n\nThe point comes first. **It holds.**\n")
        self.assertEqual(code, 0, out)

    def test_skim_prints_headings_bold_and_first_sentences(self):
        code, out = self.check("# Title\n\nThe point comes first. More follows here. **It holds.**\n", "--skim")
        self.assertIn("# Title", out)
        self.assertIn("The point comes first.", out)
        self.assertIn("bold: It holds.", out)
        self.assertNotIn("More follows here", out.split("bold:")[0])

    def test_headings_that_open_with_one_word_are_noted(self):
        code, out = self.check("# Title\n\n## What it reads\n\n## What it prints\n\n## What it cannot show\n\n## Limits\n")
        self.assertIn('NOTE 3 of 5 headings open with "What"', out)

    def test_the_note_on_headings_is_not_a_problem(self):
        code, out = self.check("# Title\n\n## What it reads\n\n## What it prints\n\n## What it cannot show\n\n## Limits\n")
        self.assertEqual(code, 0, out)
        self.assertEqual(out.strip().split("\n")[-1], "problems=0")

    def test_headings_that_open_with_different_words_get_no_note(self):
        code, out = self.check("# Title\n\n## Sources\n\n## Reading order\n\n## What it cannot show\n\n## Limits\n")
        self.assertNotIn("NOTE", out)

    def test_two_headings_with_one_opening_word_get_no_note(self):
        code, out = self.check("# Title\n\n## What it reads\n\n## What it prints\n")
        self.assertNotIn("NOTE", out)

    def test_a_shared_word_in_under_two_fifths_of_the_headings_gets_no_note(self):
        heads = ["What it reads", "What it prints", "What it cannot show", "Sources", "Order", "Limits", "Cost", "Records"]
        code, out = self.check("# Title\n\n" + "".join(f"## {h}\n\n" for h in heads))
        self.assertNotIn("NOTE", out)

    def test_a_number_before_the_opening_word_is_left_out(self):
        code, out = self.check("# Title\n\n## 1. How it starts\n\n## 2. How it runs\n\n## 3. how it stops\n")
        self.assertIn('NOTE 3 of 4 headings open with "How"', out)

    def test_a_heading_inside_a_code_fence_is_not_counted(self):
        fence = "```\n# What a\n# What b\n# What c\n```\n"
        code, out = self.check("# Title\n\n## Sources\n\n" + fence + "\n## Limits\n")
        self.assertNotIn("NOTE", out)


if __name__ == "__main__":
    unittest.main()
