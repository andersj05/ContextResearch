#!/usr/bin/env python3
"""Build an offline Markdown/HTML reading copy; no third-party dependencies."""
from __future__ import annotations

import html
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CITATION = re.compile(r"\[((?:@[A-Za-z0-9_-]+)(?:\s*;\s*@[A-Za-z0-9_-]+)*)\]")


def read_bibliography(path: Path) -> dict[str, dict[str, str]]:
    """Read this workspace's one-line braced BibTeX fields, rejecting bad entries.

    This deliberately small reader is not a general BibTeX engine. It accepts
    nested braces within a field, but not macros, concatenation, or quoted fields.
    """
    text = path.read_text(encoding="utf-8")
    entries = {}
    matches = list(re.finditer(r"(?ms)^@\w+\{([\w-]+),\s*\n(.*?)^\}", text))
    if len(matches) != len(re.findall(r"(?m)^@", text)):
        raise ValueError("Unsupported or unclosed BibTeX entry")
    for match in matches:
        key, body = match.groups()
        if key in entries:
            raise ValueError(f"Duplicate bibliography key: {key}")
        fields = {}
        for line in body.splitlines():
            if not line.strip() or line.lstrip().startswith("%"):
                continue
            field = re.fullmatch(r"\s*(\w+)\s*=\s*\{(.*)\},?\s*", line)
            if not field:
                raise ValueError(f"{key}: use one-line braced fields: {line}")
            name, value = field.groups()
            if value.count("{") != value.count("}"):
                raise ValueError(f"{key}: unbalanced field braces")
            fields[name] = value.replace("{", "").replace("}", "")
        if not all(fields.get(name) for name in ("title", "year", "url")):
            raise ValueError(f"{key}: title, year, and URL are required")
        if not fields["url"].startswith("https://"):
            raise ValueError(f"{key}: reference URL must use HTTPS")
        entries[key] = fields
    if not entries:
        raise ValueError("Empty bibliography")
    return entries


def citation_keys(text: str) -> set[str]:
    return {key for match in CITATION.finditer(text)
            for key in re.findall(r"@([\w-]+)", match.group(1))}


def inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\((https://[^\s)]+)\)", r'<a href="\2">\1</a>', escaped)
    return CITATION.sub(lambda m: "[" + "; ".join(
        f'<a href="#ref-{key}">{key}</a>' for key in re.findall(r"@([\w-]+)", m.group(1))) + "]", escaped)


def render_markdown(text: str) -> tuple[str, str]:
    """Render the small Markdown subset used by the paper, with no external assets."""
    output, toc, paragraph, code = [], [], [], []
    fenced = False

    def flush():
        if paragraph:
            output.append("<p>" + inline(" ".join(paragraph)) + "</p>")
            paragraph.clear()

    for line in text.splitlines():
        if line.startswith("```"):
            flush()
            if fenced:
                output.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
                code.clear()
            fenced = not fenced
        elif fenced:
            code.append(line)
        elif re.match(r"^#{1,6} ", line):
            flush()
            level = len(line) - len(line.lstrip("#"))
            title = line[level + 1:]
            anchor = "section-" + str(len(toc))
            output.append(f'<h{level} id="{anchor}">{inline(title)}</h{level}>')
            toc.append(f'<a class="level-{level}" href="#{anchor}">{html.escape(title)}</a>')
        elif not line.strip():
            flush()
        else:
            paragraph.append(line)
    if fenced:
        raise ValueError("Unclosed code fence in manuscript")
    flush()
    return "\n".join(output), "\n".join(toc)


def main() -> None:
    manuscript = (ROOT / "paper/manuscript.md").read_text(encoding="utf-8")
    bibliography = read_bibliography(ROOT / "paper/references.bib")
    used = citation_keys(manuscript)
    if missing := used - bibliography.keys():
        raise ValueError(f"Unknown manuscript citations: {sorted(missing)}")
    references = []
    markdown_refs = ["\n## References\n"]
    for key in sorted(used):
        ref = bibliography[key]
        author = ref.get("author", "Author metadata not yet verified")
        description = f"{author} ({ref['year']}). {ref['title']}."
        references.append(f'<li id="ref-{key}"><strong>{html.escape(key)}</strong><br>'
                          f'{html.escape(description)} <a href="{html.escape(ref["url"], quote=True)}">Source</a>'
                          f'<p class="note">{html.escape(ref.get("note", ""))}</p></li>')
        markdown_refs.append(f"- **{key}** — {author} ({ref['year']}). [{ref['title']}]({ref['url']}). {ref.get('note', '')}\n")
    assembled = CITATION.sub(lambda m: "[" + "; ".join(re.findall(r"@([\w-]+)", m.group(1))) + "]", manuscript)
    assembled += "\n".join(markdown_refs)
    body, toc = render_markdown(manuscript)
    document = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ContextResearch — working paper</title>
<style>
:root{color-scheme:light}*{box-sizing:border-box}body{margin:0;background:#f3f2ee;color:#23282d;font:18px/1.65 Georgia,serif}
nav{position:fixed;width:270px;inset:0 auto 0 0;padding:32px 24px;background:#18362f;overflow:auto;font:14px/1.5 system-ui}
nav strong{display:block;color:#fff;margin-bottom:24px}nav a{display:block;color:#d7e8df;text-decoration:none;margin:13px 0}nav .level-1{font-weight:600}
main{max-width:1060px;margin-left:270px;padding:55px 75px;background:#fff;min-height:100vh}h1,h2{font-family:system-ui;line-height:1.25;letter-spacing:-.025em}
h1{font-size:38px;margin-top:0}h2{font-size:26px;margin-top:48px}a{color:#27695c;overflow-wrap:anywhere}pre{padding:18px;background:#f3f5f4;overflow:auto;font-size:15px}code{font-family:ui-monospace,monospace;font-size:.88em}
.badge{font:12px system-ui;letter-spacing:.08em;color:#65756e;text-transform:uppercase;margin-bottom:20px}.note{font:14px/1.5 system-ui;color:#58625d}li{margin-bottom:20px}h1,h2,li{scroll-margin-top:25px}
@media(max-width:850px){nav{position:static;width:auto;padding:20px}nav a{display:inline-block;margin:6px 12px 6px 0}main{margin:0;padding:30px 22px}h1{font-size:31px}}
@media print{nav{display:none}main{margin:0;padding:0;max-width:none}body{font-size:11pt;background:white}h2{break-after:avoid}}
</style></head><body><nav><strong>ContextResearch</strong>'''
    document += toc + '<a href="#references">References</a></nav><main><div class="badge">Working draft · offline reading copy</div>'
    document += body + '<h2 id="references">References</h2><ol>' + "\n".join(references) + "</ol></main></body></html>\n"
    destination = ROOT / "build/paper"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "manuscript.md").write_text(assembled, encoding="utf-8", newline="\n")
    (destination / "preview.html").write_text(document, encoding="utf-8", newline="\n")
    print(f"Built Markdown and offline HTML preview; {len(used)} cited sources.")
    print(destination)


if __name__ == "__main__":
    main()
