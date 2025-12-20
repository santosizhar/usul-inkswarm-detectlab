from __future__ import annotations

import html
import re
from typing import Iterable

_CODE_FENCE_RE = re.compile(r"^```(.*)$")


def md_to_html_document(md: str, *, title: str = "Report") -> str:
    """A minimal, dependency-free Markdown -> HTML renderer.

    Supported:
    - Headings (#, ##, ###)
    - Bullet lists (-, *)
    - Fenced code blocks (```lang)
    - Inline code (`code`)
    - Bold (**text**)
    - Links [text](url)
    - Paragraphs

    This is intentionally conservative for stakeholder-readable exports.
    """

    lines = md.splitlines()
    out: list[str] = []
    in_code = False
    code_lang = ""
    list_open = False

    def close_list():
        nonlocal list_open
        if list_open:
            out.append("</ul>")
            list_open = False

    def open_list():
        nonlocal list_open
        if not list_open:
            out.append("<ul>")
            list_open = True

    def render_inlines(s: str) -> str:
        s = html.escape(s)

        # inline code
        s = re.sub(r"`([^`]+)`", lambda m: f"<code>{html.escape(m.group(1))}</code>", s)

        # bold
        s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)

        # links
        s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)

        return s

    for raw in lines:
        line = raw.rstrip("\n")
        m = _CODE_FENCE_RE.match(line.strip())
        if m:
            if not in_code:
                close_list()
                in_code = True
                code_lang = (m.group(1) or "").strip()
                out.append(f'<pre><code class="lang-{html.escape(code_lang)}">')
            else:
                in_code = False
                out.append("</code></pre>")
            continue

        if in_code:
            out.append(html.escape(line) + "\n")
            continue

        if not line.strip():
            close_list()
            out.append("")
            continue

        # headings
        if line.startswith("### "):
            close_list()
            out.append(f"<h3>{render_inlines(line[4:])}</h3>")
            continue
        if line.startswith("## "):
            close_list()
            out.append(f"<h2>{render_inlines(line[3:])}</h2>")
            continue
        if line.startswith("# "):
            close_list()
            out.append(f"<h1>{render_inlines(line[2:])}</h1>")
            continue

        # list items
        stripped = line.lstrip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            open_list()
            out.append(f"<li>{render_inlines(stripped[2:])}</li>")
            continue

        close_list()
        out.append(f"<p>{render_inlines(line)}</p>")

    close_list()
    body = "\n".join(out)

    css = """

    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 24px; color: #111; }
    h1 { font-size: 28px; margin: 0 0 12px; }
    h2 { font-size: 20px; margin: 18px 0 8px; }
    h3 { font-size: 16px; margin: 14px 0 6px; }
    p, li { font-size: 14px; line-height: 1.5; }
    code { background: rgba(0,0,0,0.06); padding: 2px 6px; border-radius: 6px; }
    pre { background: rgba(0,0,0,0.06); padding: 12px; border-radius: 12px; overflow-x: auto; }
    a { color: #2563eb; text-decoration: none; }
    a:hover { text-decoration: underline; }
    hr { border: 0; border-top: 1px solid rgba(0,0,0,0.12); margin: 16px 0; }
    """.strip()

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{html.escape(title)}</title>
<style>{css}</style>
</head>
<body>
{body}
</body>
</html>
"""


__all__ = ["md_to_html_document"]
