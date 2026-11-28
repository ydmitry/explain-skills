import json
import tempfile
import unittest
from pathlib import Path

from util import run

S = "keep-sources/scripts/sources.py"
CONFIG = """# retry settings
MAX_RETRIES = 5
# a first violation is forgiven when you cure it
# prior to 7 days after the notice
TIMEOUT_S = 600
total rows: 14,214
"""


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.work = Path(self.tmp.name).resolve()
        self.folder = self.work / "sources" / "job"
        (self.work / "config.py").write_text(CONFIG)

    def tearDown(self):
        self.tmp.cleanup()

    def sh(self, *args, stdin=None):
        return run(S, *args, cwd=self.work, stdin=stdin)

    def rows(self):
        return [json.loads(line) for line in (self.folder / "ledger.jsonl").read_text().splitlines()]

    def add(self, quote, says, *more, source="config.py"):
        return self.sh("add", self.folder, "--source", source, "--quote", quote, "--says", says, *more)


class Add(Case):
    def test_a_quote_is_looked_up_and_its_line_recorded(self):
        code, out = self.add("MAX_RETRIES = 5", "A failed charge is retried 5 times.")
        self.assertEqual(code, 0, out)
        row = self.rows()[0]
        self.assertEqual((row["id"], row["lines"], row["quote"]), ("s01", "2", "MAX_RETRIES = 5"))
        self.assertEqual(row["source"], str(self.work / "config.py"))

    def test_a_quote_may_run_over_a_line_end(self):
        code, out = self.add("when you cure it # prior to 7 days after", "A first violation is forgiven within 7 days.")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.rows()[0]["lines"], "3-4")

    def test_a_retyped_quote_is_refused_and_the_closest_line_named(self):
        code, out = self.add("MAX_RETRIES = 3", "It retries 3 times.")
        self.assertEqual(code, 1)
        self.assertIn("copy it from the file", out)
        self.assertIn("closest line is 2", out)
        self.assertFalse((self.folder / "ledger.jsonl").exists())

    def test_a_number_the_quote_does_not_hold_is_refused(self):
        code, out = self.add("prior to 7 days after", "A violation is forgiven within 30 days.")
        self.assertEqual(code, 1)
        self.assertIn("30", out)

    def test_calc_records_a_number_that_follows(self):
        code, out = self.add("TIMEOUT_S = 600", "The timeout is 10 minutes.", "--calc", "600 s is 10 minutes")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.rows()[0]["calc"], "600 s is 10 minutes")

    def test_thousands_separators_do_not_make_a_new_number(self):
        code, out = self.add("total rows: 14,214", "The table has 14214 rows.")
        self.assertEqual(code, 0, out)

    def test_typographic_quotes_in_the_source_match_straight_ones(self):
        (self.work / "note.md").write_text("The lead said “ship on the 14th” and left.\n")
        code, out = self.add('said "ship on the 14th"', "The lead wants it shipped on the 14th.", source="note.md")
        self.assertEqual(code, 0, out)

    def test_near_picks_among_several_places(self):
        (self.work / "log.txt").write_text("status ok\nrun 1\nstatus ok\n")
        code, out = self.add("status ok", "The second run ended ok.", "--near", "3", source="log.txt")
        self.assertEqual(code, 0, out)
        self.assertIn("2 places", out)
        self.assertEqual(self.rows()[0]["lines"], "3")

    def test_a_missing_source_and_a_long_quote_are_refused(self):
        self.assertEqual(self.add("x y z", "Something.", source="nowhere.txt")[0], 1)
        code, out = self.add(" ".join(["word"] * 41), "Something.")
        self.assertEqual(code, 1)
        self.assertIn("41 words", out)


class Snap(Case):
    def test_text_that_will_not_stay_is_saved_and_can_be_quoted(self):
        code, out = self.sh("snap", self.folder, "test-run-1", "--origin", "make test", stdin="3 failed, 212 passed\n")
        self.assertEqual(code, 0, out)
        self.assertIn("snapshots/test-run-1.txt", out)
        code, out = self.add("3 failed, 212 passed", "Before the fix 3 of 215 tests failed.", "--calc", "3 + 212 = 215",
                             source=self.folder / "snapshots" / "test-run-1.txt")
        self.assertEqual(code, 0, out)
        row = self.rows()[0]
        self.assertEqual((row["source"], row["origin"]), ("snapshots/test-run-1.txt", "make test"))

    def test_a_snapshot_is_named_relative_to_the_folder_too(self):
        self.sh("snap", self.folder, "said", "--text", "We cannot ship after the 14th.")
        code, out = self.add("cannot ship after the 14th", "Shipping after the 14th is not possible.", source="snapshots/said.txt")
        self.assertEqual(code, 0, out)

    def test_a_snapshot_is_not_overwritten_with_other_text(self):
        self.assertEqual(self.sh("snap", self.folder, "page", "--text", "price 10")[0], 0)
        self.assertEqual(self.sh("snap", self.folder, "page", "--text", "price 10")[0], 0)
        code, out = self.sh("snap", self.folder, "page", "--text", "price 12")
        self.assertEqual(code, 1)
        self.assertIn("pick another name", out)

    def test_empty_text_and_an_odd_name_are_refused(self):
        self.assertEqual(self.sh("snap", self.folder, "page", stdin="  \n")[0], 1)
        self.assertEqual(self.sh("snap", self.folder, "my page", "--text", "x")[0], 1)


class ListDropCheck(Case):
    def setUp(self):
        super().setUp()
        self.add("MAX_RETRIES = 5", "A failed charge is retried 5 times.")
        self.add("TIMEOUT_S = 600", "The timeout is 600 seconds.")

    def test_list_shows_the_rows_and_drop_hides_one(self):
        code, out = self.sh("list", self.folder)
        self.assertIn("s01", out)
        self.assertIn("rows=2", out)
        self.assertEqual(self.sh("drop", self.folder, "s01", "--why", "the config was edited")[0], 0)
        code, out = self.sh("list", self.folder)
        self.assertNotIn("s01", out)
        self.assertIn("rows=1 dropped=1", out)
        self.assertIn("the config was edited", self.sh("list", self.folder, "--all")[1])
        self.assertEqual(self.sh("drop", self.folder, "s09", "--why", "x")[0], 1)

    def test_check_passes_and_follows_a_quote_that_moved(self):
        self.assertEqual(self.sh("check", self.folder)[0], 0)
        (self.work / "config.py").write_text("# new first line\n" + CONFIG)
        code, out = self.sh("check", self.folder)
        self.assertEqual(code, 0, out)
        self.assertIn("MOVED s01: now lines 3", out)
        self.assertEqual(self.rows()[0]["lines"], "3")

    def test_check_names_a_quote_that_is_gone_and_skips_a_dropped_row(self):
        (self.work / "config.py").write_text(CONFIG.replace("MAX_RETRIES = 5", "MAX_RETRIES = 8"))
        code, out = self.sh("check", self.folder)
        self.assertEqual(code, 1)
        self.assertIn("ERROR s01", out)
        self.assertIn("errors=1", out)
        self.sh("drop", self.folder, "s01", "--why", "the limit was raised")
        self.assertEqual(self.sh("check", self.folder)[0], 0)

    def test_check_refuses_a_row_edited_by_hand(self):
        rows = self.rows()
        rows[1]["says"] = "The timeout is 900 seconds."
        (self.folder / "ledger.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        code, out = self.sh("check", self.folder)
        self.assertEqual(code, 1)
        self.assertIn("900", out)

    def test_check_without_a_ledger_is_an_error(self):
        self.assertEqual(self.sh("check", self.work / "empty")[0], 1)


class Pictures(Case):
    """A screenshot is saved as a source, with where and when it was taken."""

    def setUp(self):
        super().setUp()
        self.shot = self.work / "shot.png"
        self.shot.write_bytes(b"\x89PNG\r\n\x1a\n" + b"dashboard at 14:05")

    def snap(self, name="errors-1405", origin="the errors dashboard on staging, 2026-11-28 14:05", image=None):
        args = ["snap", self.folder, name, "--image", image or self.shot]
        return self.sh(*args, *(["--origin", origin] if origin else []))

    def test_a_picture_is_copied_with_its_origin_and_a_fingerprint(self):
        code, out = self.snap()
        self.assertEqual(code, 0, out)
        saved = self.folder / "snapshots" / "errors-1405.png"
        self.assertEqual(saved.read_bytes(), self.shot.read_bytes())
        entry = json.loads((self.folder / "snapshots" / "index.json").read_text())["errors-1405.png"]
        self.assertEqual(entry["origin"], "the errors dashboard on staging, 2026-11-28 14:05")
        self.assertEqual(len(entry["sha256"]), 64)
        self.assertIn("snapshots/errors-1405.png", out)

    def test_a_picture_without_an_origin_is_refused(self):
        code, out = self.snap(origin=None)
        self.assertEqual(code, 1, out)
        self.assertIn("--origin", out)
        self.assertFalse((self.folder / "snapshots" / "errors-1405.png").exists())

    def test_a_file_that_is_no_picture_is_refused(self):
        code, out = self.snap(image=self.work / "config.py")
        self.assertEqual(code, 1, out)
        self.assertIn("png", out)

    def test_a_saved_picture_is_not_overwritten_by_another(self):
        self.snap()
        other = self.work / "other.png"
        other.write_bytes(b"\x89PNG another screen")
        code, out = self.snap(image=other)
        self.assertEqual(code, 1, out)
        self.assertIn("pick another name", out)

    def test_list_shows_the_pictures(self):
        self.snap()
        code, out = self.sh("list", self.folder)
        self.assertEqual(code, 0, out)
        self.assertIn("picture  snapshots/errors-1405.png  the errors dashboard on staging, 2026-11-28 14:05", out)
        self.assertIn("pictures=1", out)

    def test_check_passes_a_folder_of_pictures_and_catches_a_changed_one(self):
        self.snap()
        code, out = self.sh("check", self.folder)
        self.assertEqual(code, 0, out)
        self.assertIn("errors=0", out)
        (self.folder / "snapshots" / "errors-1405.png").write_bytes(b"edited")
        code, out = self.sh("check", self.folder)
        self.assertEqual(code, 1, out)
        self.assertIn("errors-1405.png: the picture changed since it was saved", out)


if __name__ == "__main__":
    unittest.main()
