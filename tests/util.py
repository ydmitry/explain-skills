"""Run a skill's script the way a session does: as a command, in a folder of its own."""
import subprocess
import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parent.parent / "skills"


def run(script: str, *args, cwd=None, stdin=None):
    """(exit code, what it printed) of `python3 skills/<script> args`."""
    done = subprocess.run([sys.executable, str(SKILLS / script), *map(str, args)], cwd=cwd, input=stdin,
                          capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr
