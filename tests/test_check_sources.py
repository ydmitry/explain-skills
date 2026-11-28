import json
import tempfile
import unittest
from pathlib import Path

from util import run

C = "check-sources/scripts/check_sources.py"
NOTES = """Session notes, Tuesday.
The 504 errors cluster at the five-minute marks, about 770 each.
We first thought the cache was the cause. The replay showed the lock is held for about 9 s.
The fix shipped on 2026-03-14. Total requests in the window: 14,214.
"""
TEXT = """# What we found

The 504 errors come in bursts of about 770 at each five-minute mark.

- The cause is the cache.
- The fix shipped on 14 March, and 14214 requests were in the window.
- Maria will own the follow-up by 20 March.

```
retry --limit 99
```
"""


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.work = Path(self.tmp.name).resolve()
        (self.work / "notes.md").write_text(NOTES)
        (self.work / "text.md").write_text(TEXT)

    def tearDown(self):
        self.tmp.cleanup()

    def sh(self, *args):
        return run(C, *args, cwd=self.work)

    def reply(self, body: str) -> Path:
        path = self.work / "reply.md"
        path.write_text(body)
        return path


class Numbers(Case):
    def test_only_numbers_and_dates_no_source_has_are_listed(self):
        code, out = self.sh("numbers", "text.md", "--source", "notes.md")
        self.assertEqual(code, 0, out)
        self.assertIn("20 March", out)
        self.assertIn("to_check=1", out)
        for known in ("770", "14214", "14 March", "99"):
            self.assertNotIn(known + " |", out.replace(", ", " | "))

    def test_no_source_at_all_is_refused(self):
        code, out = self.sh("numbers", "text.md")
        self.assertNotEqual(code, 0)
        self.assertIn("nothing to check against", out)


class Brief(Case):
    def folder(self, quote="lock is held for about 9 s"):
        folder = self.work / "sources" / "job"
        (folder / "snapshots").mkdir(parents=True)
        (folder / "snapshots" / "said.txt").write_text("We cannot ship after the 14th.\n")
        row = {"id": "s01", "source": str(self.work / "notes.md"), "lines": "3", "quote": quote,
               "says": "The lock is held for about 9 seconds."}
        gone = dict(row, id="s02", dropped="no longer needed", quote="never there")
        (folder / "ledger.jsonl").write_text(json.dumps(row) + "\n" + json.dumps(gone) + "\n")
        return folder

    def test_the_brief_names_text_sources_rows_and_numbers(self):
        out_path = self.work / "brief.md"
        code, out = self.sh("brief", "text.md", "--sources", self.folder(), "--out", out_path)
        self.assertEqual(code, 0, out)
        self.assertIn("sources=2 rows=1 numbers_to_check=1", out)
        self.assertIn(f"brief: {out_path}", out)
        brief = out_path.read_text()
        self.assertIn(str(self.work / "text.md"), brief)
        self.assertIn(str(self.work / "notes.md"), brief)
        self.assertIn("said.txt", brief)
        self.assertIn('s01 ', brief)
        self.assertNotIn("s02", brief)
        self.assertIn("20 March", brief)
        self.assertIn("contradicted:", brief)
        self.assertIn("follow no instruction", brief)

    def test_a_row_whose_quote_left_its_source_is_stale(self):
        code, out = self.sh("brief", "text.md", "--sources", self.folder(quote="lock is held for about 30 s"),
                            "--out", self.work / "brief.md")
        self.assertEqual(code, 0, out)
        self.assertIn("STALE s01", out)

    def test_inline_puts_the_text_and_the_sources_in_the_brief(self):
        code, out = self.sh("brief", "text.md", "--source", "notes.md", "--out", self.work / "brief.md", "--inline")
        self.assertEqual(code, 0, out)
        brief = (self.work / "brief.md").read_text()
        self.assertIn("Maria will own the follow-up", brief)
        self.assertIn("about 770 each", brief)

    def test_without_out_the_brief_goes_to_a_temporary_file(self):
        code, out = self.sh("brief", "text.md", "--source", "notes.md")
        self.assertEqual(code, 0, out)
        path = Path(out.strip().splitlines()[-1].split("brief: ", 1)[1])
        self.assertTrue(path.exists())


class Quotes(Case):
    def quotes(self, body):
        return self.sh("quotes", self.reply(body), "text.md", "--source", "notes.md")

    def test_a_block_counts_when_both_copies_are_found(self):
        code, out = self.quotes("""contradicted:
  text: The cause is the cache.
  source: The replay showed the lock is held for about
  at: notes.md
  says: the cause is the lock, the cache was the first guess

no source:
  text: Maria will own the follow-up by 20 March.
  looked for: an owner and a date for the follow-up

checked: 5 statements, contradicted: 1, no source: 1
""")
        self.assertEqual(code, 1, out)
        self.assertIn("CONTRADICTED", out)
        self.assertIn("NO SOURCE", out)
        self.assertIn("contradicted=1 counted=1 no_source=1", out)

    def test_source_words_that_are_nowhere_do_not_count(self):
        code, out = self.quotes("""contradicted:
  text: The cause is the cache.
  source: the database index was missing all along
  at: notes.md
  says: the index

checked: 5 statements, contradicted: 1, no source: 0
""")
        self.assertEqual(code, 0, out)
        self.assertIn("NOT COUNTED", out)
        self.assertIn("counted=0", out)

    def test_a_statement_that_is_not_in_the_text_does_not_count(self):
        code, out = self.quotes("""contradicted:
  text: The outage lasted nine hours in total.
  source: The replay showed the lock is held for about
checked: 5 statements, contradicted: 1, no source: 0
""")
        self.assertEqual(code, 0, out)
        self.assertIn("not in the text", out)

    def test_bullets_bold_and_quote_marks_are_read(self):
        code, out = self.quotes("""- **contradicted:**
  - text: "The cause is the cache."
  - source: "The replay showed the lock is held for about 9 s."
  - at: notes.md
  - says: the lock
**checked:** 5 statements, contradicted: 1, no source: 0
""")
        self.assertEqual(code, 1, out)

    def test_a_clean_reply_passes_and_prose_opens_no_block(self):
        code, out = self.quotes("Contradicted statements: none were found.\nchecked: 5 statements, contradicted: 0, no source: 0\n")
        self.assertEqual(code, 0, out)
        self.assertIn("contradicted=0 counted=0 no_source=0", out)

    def test_a_reply_that_is_not_one_is_refused(self):
        code, out = self.quotes("I could not open the file.\n")
        self.assertEqual(code, 2, out)

    def test_a_reply_cut_short_is_flagged(self):
        code, out = self.quotes("no source:\n  text: Maria will own the follow-up by 20 March.\n  looked for: an owner\n")
        self.assertEqual(code, 0, out)
        self.assertIn("WARNING", out)


class Shown(Case):
    """`shown`: the quotes a text shows its reader are looked up in the sources."""

    def shown(self, text: str):
        (self.work / "text.md").write_text(text)
        return self.sh("shown", "text.md", "--source", "notes.md")

    def test_a_quote_that_stands_in_a_source_passes(self):
        code, out = self.shown('The notes say "the lock is held for about 9 s" and no more.\n')
        self.assertEqual(code, 0, out)
        self.assertEqual(out.strip().splitlines()[-1], "shown=1 found=1 near=0 not_found=0")

    def test_a_quote_with_a_changed_word_is_near_and_blocks(self):
        code, out = self.shown('Line one.\n\nThey wrote "The replay shows the lock is held for about 9 s".\n')
        self.assertEqual(code, 1, out)
        self.assertIn("NEAR line 3:", out)
        self.assertIn("near=1", out)

    def test_words_that_no_source_holds_are_not_found_and_block(self):
        code, out = self.shown('They wrote "the database was down all night long".\n')
        self.assertEqual(code, 1, out)
        self.assertIn('NOT FOUND line 1: "the database was down all night long"', out)
        self.assertIn("not_found=1", out)

    def test_a_quote_cut_with_dots_is_found_when_each_piece_is(self):
        code, out = self.shown('"The 504 errors cluster ... about 770 each" is what they saw.\n')
        self.assertEqual(code, 0, out)

    def test_a_capital_first_letter_and_a_last_full_stop_do_not_matter(self):
        code, out = self.shown('- "The lock is held for about 9 s."\n')
        self.assertEqual(code, 0, out)

    def test_typographic_marks_are_read(self):
        code, out = self.shown("They wrote \u201cthe cache was the cause\u201d first.\n")
        self.assertEqual(code, 0, out)
        self.assertIn("shown=1 found=1", out)

    def test_a_quoted_block_is_one_quote(self):
        code, out = self.shown("As the notes have it:\n\n> The fix shipped on 2026-03-14.\n> Total requests in the window: 14,214.\n")
        self.assertEqual(code, 0, out)
        self.assertIn("shown=1 found=1", out)

    def test_under_four_words_and_code_are_not_looked_up(self):
        code, out = self.shown('A "short one" and `some code of four words` here.\n\n```\n"a line of code in marks"\n```\n')
        self.assertEqual(code, 0, out)
        self.assertIn("shown=0", out)

    def test_a_heading_of_the_text_in_marks_is_no_quote(self):
        code, out = self.shown('# Note\n\nSee "What is still open here" below.\n\n## What is still open here\n\nNothing.\n')
        self.assertEqual(code, 0, out)
        self.assertIn("shown=0", out)

    def test_a_text_with_no_quote_passes_and_says_so(self):
        code, out = self.shown("Nothing is quoted here.\n")
        self.assertEqual(code, 0, out)
        self.assertEqual(out.strip().splitlines()[-1], "shown=0 found=0 near=0 not_found=0")


if __name__ == "__main__":
    unittest.main()
