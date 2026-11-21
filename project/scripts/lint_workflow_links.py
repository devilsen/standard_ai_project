# /// script
# requires-python = ">=3.11"
# dependencies = ["markdown-it-py==3.0.0"]
# ///
"""Check repository-relative Markdown links in the development and Bugfix workflows."""

from functools import cache
from pathlib import Path
from unicodedata import category
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt
from markdown_it.token import Token

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIRS = (ROOT / ".agents/skills", ROOT / "docs/workflow")
MARKDOWN = MarkdownIt("commonmark").enable("table")


@cache
def markdown_tokens(path: Path) -> list[Token]:
    """Parse each workflow document or linked Markdown target once per lint run."""
    return MARKDOWN.parse(path.read_text(encoding="utf-8"))


@cache
def heading_anchors(path: Path) -> set[str]:
    """Build heading anchors with GitHub's lowercase and duplicate suffix conventions."""
    anchors: set[str] = set()
    tokens = markdown_tokens(path)
    for index, token in enumerate(tokens):
        if token.type != "heading_open":
            continue
        title = "".join(child.content for child in tokens[index + 1].children or ())
        slug = "".join(
            char for char in title.lower()
            if char in " _-" or category(char)[0] in "LMN"
        ).replace(" ", "-")
        anchor = slug
        suffix = 1
        while anchor in anchors:
            anchor = f"{slug}-{suffix}"
            suffix += 1
        anchors.add(anchor)
    return anchors


def main() -> None:
    """Print broken relative links with their source location and exit nonzero."""
    problems = []
    for directory in WORKFLOW_DIRS:
        for source in sorted(directory.rglob("*.md")):
            for token in markdown_tokens(source):
                if token.type != "inline" or token.map is None:
                    continue
                for child in token.children or ():
                    if child.type != "link_open":
                        continue
                    href = child.attrGet("href")
                    if not href:
                        continue
                    destination = urlsplit(href)
                    if destination.scheme or destination.netloc or destination.path.startswith("/"):
                        continue
                    target = (source.parent / unquote(destination.path)).resolve() if destination.path else source
                    location = f"{source.relative_to(ROOT)}:{token.map[0] + 1}"
                    if not target.is_relative_to(ROOT) or not target.exists():
                        problems.append(f"{location}: missing repository target {href}")
                    elif destination.fragment and target.suffix.lower() == ".md":
                        if unquote(destination.fragment) not in heading_anchors(target):
                            problems.append(f"{location}: missing Markdown heading {href}")
    if problems:
        raise SystemExit("\n".join(problems))
    print("Workflow links passed.")


if __name__ == "__main__":
    main()
