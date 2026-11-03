# Docs Quality Checker

A small Python tool that scans Markdown documentation and reports common quality problems, so writers can fix them before a human review.

## What it checks

| Check | Example problem |
|---|---|
| Missing title | A file with no `title:` front matter and no H1 heading |
| Skipped heading levels | An H2 followed directly by an H4 |
| Broken internal links | A link to `advanced-guide.md` that does not exist |
| Broken external links (optional) | A web link that returns an error |
| Discouraged phrases | "click here", "simply", "easy", "e-mail" |

Text inside code blocks is ignored, so examples do not trigger false alarms.

## Requirements

- Python 3.8 or later
- No third-party packages

## Install

1. Clone this repository:
   ```
   git clone https://github.com/Kriti20004/docs-quality-checker.git
   cd docs-quality-checker
   ```
2. Confirm Python is installed:
   ```
   python --version
   ```

## Use

Check every Markdown file in a folder:

```
python checker.py docs/
```

Also check web links (needs an internet connection and is slower):

```
python checker.py docs/ --check-external
```

## Example output

```
docs/bad-guide.md:1: Missing title: add a front matter 'title:' or an H1 heading
docs/bad-guide.md:3: Discouraged phrase 'simply': remove it; it can sound dismissive if the step is hard for the reader
docs/bad-guide.md:5: Heading level skipped: H2 followed by H4
docs/bad-guide.md:7: Discouraged phrase 'click here': use descriptive link text, for example 'see the installation guide'
docs/bad-guide.md:8: Broken internal link: advanced-guide.md

Checked 3 file(s). Found 7 issue(s).
```

Each line shows the file, the line number, and what to fix. The tool exits with code `1` when it finds issues, so it can be added to an automated publishing pipeline later.

## Customize the style rules

Open `checker.py` and edit the `DISCOURAGED` dictionary. Each entry is a phrase to flag and a short suggestion for what to write instead.

## Limitations

- It only understands standard Markdown links in the form `[text](target)`. Reference-style links are not checked.
- It finds exact phrase matches only. It cannot judge tone or accuracy, so a human review is still needed.
- External link checks can fail on sites that block automated requests.

## Possible next steps

- Read the style rules from a configuration file
- Add checks for missing image alt text
- Run the tool automatically on every commit
