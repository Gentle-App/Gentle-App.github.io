"""
Builds the website and publishes it to GitHub Pages: https://gentle-app.github.io/

The live site is the repository Gentle-App/Gentle-App.github.io. Git is kept out of the Gentle project folder: this
script keeps its own copy of that repository in %LOCALAPPDATA%\\GentlePages, copies the built site into it, and pushes.
GitHub then republishes the site, usually within a minute or two.

Run:  python website/scripts/deploy.py "What changed"
Needs git, and the GitHub CLI signed in as BenRobart (gh auth login). Commits are made as BenRobart, never anyone else.
"""
import os
import pathlib
import shutil
import subprocess
import sys

REPO = "https://github.com/Gentle-App/Gentle-App.github.io.git"
# Commits are always published as BenRobart (GitHub's private no-reply address for that account), whatever this
# computer's own git name and email are, and pushed with the GitHub CLI's sign-in (gh auth login as BenRobart).
AUTHOR_NAME = "BenRobart"
AUTHOR_EMAIL = "277800073+BenRobart@users.noreply.github.com"
GH_CREDENTIALS = ["-c", "credential.helper=", "-c", "credential.helper=!gh auth git-credential"]
SITE = pathlib.Path(__file__).resolve().parent.parent
DEPLOY = pathlib.Path(os.environ.get("LOCALAPPDATA", pathlib.Path.home())) / "GentlePages"
SKIP = {"__pycache__", ".git"}


def run(*args, cwd=None):
    print("  $", " ".join(args))
    subprocess.run(args, cwd=cwd, check=True)


def main():
    message = sys.argv[1] if len(sys.argv) > 1 else "Update the website"
    run(sys.executable, "-I", str(SITE / "scripts" / "build.py"))
    if not (DEPLOY / ".git").exists():
        DEPLOY.parent.mkdir(parents=True, exist_ok=True)
        run("git", *GH_CREDENTIALS, "clone", REPO, str(DEPLOY))
    else:
        run("git", *GH_CREDENTIALS, "pull", "--ff-only", cwd=DEPLOY)
    run("git", "config", "user.name", AUTHOR_NAME, cwd=DEPLOY)
    run("git", "config", "user.email", AUTHOR_EMAIL, cwd=DEPLOY)
    # Replace everything in the copy with the current site.
    for item in DEPLOY.iterdir():
        if item.name in SKIP:
            continue
        shutil.rmtree(item) if item.is_dir() else item.unlink()
    for item in SITE.iterdir():
        if item.name in SKIP:
            continue
        dest = DEPLOY / item.name
        if item.is_dir():
            shutil.copytree(item, dest, ignore=shutil.ignore_patterns(*SKIP))
        else:
            shutil.copy2(item, dest)
    (DEPLOY / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    run("git", "add", "-A", cwd=DEPLOY)
    changed = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=DEPLOY).returncode != 0
    if not changed:
        print("Nothing has changed since the last publish.")
        return
    run("git", "commit", "-m", message, cwd=DEPLOY)
    run("git", *GH_CREDENTIALS, "push", "-u", "origin", "HEAD:main", cwd=DEPLOY)
    print("Pushed. The site updates at https://gentle-app.github.io/ in a minute or two.")


if __name__ == "__main__":
    main()
