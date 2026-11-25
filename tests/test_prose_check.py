import tempfile
import unittest
from pathlib import Path

from util import run

P = "deslop-prose/scripts/prose_check.py"
BEFORE = """# Retry policy

Great question! Let's dive in. The retry limit plays a key role in billing: a failed charge is retried 5 times.

## Limits

- **Timeout:** each try waits 600 seconds, which is a testament to our commitment.
- **Backoff:** it's not just a delay, it's a strategy.

| Setting | Value |
|---|---|
| `MAX_RETRIES` | 5 |

See https://example.com/retries for the full list.

```
retry --limit 5  # we delve into this later
```

> A quoted line that says we delve into things.
"""
AFTER = """# Retry policy

A failed charge is retried 5 times.

## Limits

- **Timeout:** each try waits 600 seconds.
- **Backoff:** the delay doubles after each try.

| Setting | Value |
|---|---|
| `MAX_RETRIES` | 5 |

See https://example.com/retries for the full list.

```
retry --limit 5  # we delve into this later
```

> A quoted line that says we delve into things.
"""


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.work = Path(self.tmp.name).resolve()
        self.file = self.work / "text.md"
        self.file.write_text(BEFORE)
        self.assertEqual(self.sh("start", self.file)[0], 0)

    def tearDown(self):
        self.tmp.cleanup()

    def sh(self, *args):
        return run(P, *args, cwd=self.work)

    def check(self, after: str, *more):
        self.file.write_text(after)
        return self.sh("check", self.file, *more)


class Scan(Case):
    def test_known_tells_are_listed_with_their_line(self):
        code, out = self.sh("scan", self.file)
        self.assertEqual(code, 0, out)
        for tell in ("great question", "let's dive", "plays a key role", "testament", "it's not just a delay, it's"):
            self.assertIn(tell, out.lower())
        self.assertIn("LINE 3 [chat leftover]", out)
        self.assertIn("LINE 8 [not X but Y]", out)

    def test_code_quotes_and_headings_are_not_scanned(self):
        code, out = self.sh("scan", self.file)
        self.assertNotIn("delve", out.lower())

    def test_a_clean_text_has_nothing_listed(self):
        self.file.write_text(AFTER)
        code, out = self.sh("scan", self.file)
        self.assertIn("found=0 in 0 lines", out)

    def test_dashes_are_counted(self):
        self.file.write_text("The fix — shipped Tuesday — works. It was late -- very late.\n")
        self.assertIn("dashes=3", self.sh("scan", self.file)[1])


class Check(Case):
    def test_a_rewrite_inside_the_limits_passes(self):
        code, out = self.check(AFTER)
        self.assertEqual(code, 0, out)
        self.assertIn("errors=0", out)
        self.assertIn("NOTE words:", out)

    def test_an_unchanged_file_passes(self):
        self.assertEqual(self.check(BEFORE)[0], 0)

    def test_a_lost_number_is_an_error_unless_accepted(self):
        lost = AFTER.replace("each try waits 600 seconds", "each try waits a while")
        code, out = self.check(lost)
        self.assertEqual(code, 1)
        self.assertIn("number lost: 600", out)
        code, out = self.check(lost, "--gone", "600")
        self.assertEqual(code, 0, out)
        self.assertIn("accepted by --gone", out)

    def test_an_added_number_is_an_error(self):
        code, out = self.check(AFTER.replace("retried 5 times", "retried 5 times within 30 days"))
        self.assertEqual(code, 1)
        self.assertIn("number added: 30", out)

    def test_headings_stay_as_they_are(self):
        code, out = self.check(AFTER.replace("## Limits", "## The limits that matter"))
        self.assertEqual(code, 1)
        self.assertIn("heading changed or removed: ## Limits", out)

    def test_lists_tables_and_bold_keep_their_count(self):
        code, out = self.check(AFTER.replace("- **Backoff:** the delay doubles after each try.\n", ""))
        self.assertEqual(code, 1)
        self.assertIn("2 list items before, 1 after", out)
        code, out = self.check(AFTER.replace("**Timeout:**", "Timeout:"))
        self.assertIn("2 things in bold before, 1 after", out)
        code, out = self.check(AFTER.replace("| `MAX_RETRIES` | 5 |\n", ""))
        self.assertIn("table rows before", out)

    def test_code_names_links_and_code_blocks_are_kept(self):
        code, out = self.check(AFTER.replace("`MAX_RETRIES`", "the limit"))
        self.assertIn("code name lost: MAX_RETRIES", out)
        code, out = self.check(AFTER.replace("https://example.com/retries", "the docs"))
        self.assertIn("link lost: https://example.com/retries", out)
        code, out = self.check(AFTER.replace("retry --limit 5  # we delve into this later", "retry --limit 5"))
        self.assertIn("a code block changed", out)

    def test_before_names_another_copy(self):
        other = self.work / "other.md"
        other.write_text(AFTER)
        self.file.write_text(AFTER)
        self.assertEqual(self.sh("check", self.file, "--before", other)[0], 0)

    def test_check_without_a_copy_says_what_to_do(self):
        fresh = self.work / "fresh.md"
        fresh.write_text(AFTER)
        code, out = self.sh("check", fresh)
        self.assertEqual(code, 1)
        self.assertIn("run `start FILE` first", out)


if __name__ == "__main__":
    unittest.main()
