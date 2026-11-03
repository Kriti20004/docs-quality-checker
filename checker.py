"""Docs Quality Checker
Scans Markdown files and reports common documentation problems:
  1. Missing title (no front matter title and no H1 heading)
  2. Skipped heading levels (e.g. H1 followed by H3)
  3. Broken internal links (relative links to files that do not exist)
  4. Broken external links (optional, use --check-external)
  5. Discouraged phrases / inconsistent terminology

Usage:
    python checker.py docs/
    python checker.py docs/ --check-external
"""
import argparse
import re
import sys
import urllib.request
from pathlib import Path

# Words to avoid and what to use instead. Edit this list to match a style guide.
DISCOURAGED = {
    "click here": "use descriptive link text, for example 'see the installation guide'",
    "simply": "remove it; it can sound dismissive if the step is hard for the reader",
    "easy": "describe the steps instead of judging the difficulty",
    "e-mail": "use 'email'",
    "log-in": "use 'sign in' (verb) or 'login' (noun) consistently",
}

HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def has_front_matter_title(lines):
    """True if the file starts with a --- block that contains 'title:'."""
    if not lines or lines[0].strip() != "---":
        return False
    for line in lines[1:]:
        if line.strip() == "---":
            return False
        if line.lower().startswith("title:"):
            return True
    return False


def check_external(url):
    """Return an error string if the URL cannot be reached, else None."""
    try:
        req = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": "docs-quality-checker"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status >= 400:
                return f"returned HTTP {resp.status}"
    except Exception as exc:  # network errors, 404s, timeouts
        return f"could not be reached ({exc})"
    return None


def check_file(path, external):
    issues = []  # list of (line_number, message)
    lines = path.read_text(encoding="utf-8").splitlines()

    # 1. Title check
    has_h1 = any(HEADING.match(l) and len(HEADING.match(l).group(1)) == 1 for l in lines)
    if not has_h1 and not has_front_matter_title(lines):
        issues.append((1, "Missing title: add a front matter 'title:' or an H1 heading"))

    in_code = False
    prev_level = 0
    for number, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue  # ignore code blocks

        # 2. Heading levels
        m = HEADING.match(line)
        if m:
            level = len(m.group(1))
            if prev_level and level > prev_level + 1:
                issues.append((number, f"Heading level skipped: H{prev_level} followed by H{level}"))
            prev_level = level

        # 3 and 4. Links
        for target in LINK.findall(line):
            if target.startswith(("http://", "https://")):
                if external:
                    error = check_external(target)
                    if error:
                        issues.append((number, f"External link {target} {error}"))
            elif target.startswith(("#", "mailto:")):
                continue
            else:
                file_part = target.split("#")[0]
                if file_part and not (path.parent / file_part).exists():
                    issues.append((number, f"Broken internal link: {target}"))

        # 5. Terminology
        lowered = line.lower()
        for phrase, advice in DISCOURAGED.items():
            if phrase in lowered:
                issues.append((number, f"Discouraged phrase '{phrase}': {advice}"))
    return issues


def main():
    parser = argparse.ArgumentParser(description="Check Markdown docs for common problems.")
    parser.add_argument("folder", help="Folder containing .md files")
    parser.add_argument("--check-external", action="store_true",
                        help="Also check http/https links (needs internet, slower)")
    args = parser.parse_args()

    files = sorted(Path(args.folder).rglob("*.md"))
    if not files:
        print(f"No Markdown files found in {args.folder}")
        return 0

    total = 0
    for f in files:
        issues = check_file(f, args.check_external)
        total += len(issues)
        for number, message in issues:
            print(f"{f}:{number}: {message}")

    print(f"\nChecked {len(files)} file(s). Found {total} issue(s).")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
