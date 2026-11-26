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


if __name__ == "__main__":
    unittest.main()
