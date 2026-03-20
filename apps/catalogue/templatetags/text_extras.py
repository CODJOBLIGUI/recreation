from django import template
from django.utils.safestring import mark_safe
import html
import re

register = template.Library()


@register.filter
def unescape_html(value):
    if value is None:
        return ""
    return html.unescape(str(value))


@register.filter
def unescape_html_twice(value):
    if value is None:
        return ""
    first = html.unescape(str(value))
    return html.unescape(first)


@register.filter
def unescape(value):
    return unescape_html(value)


@register.filter
def fix_mojibake(value):
    if value is None:
        return ""
    text = str(value)
    replacements = {
        "\u00c3\u00a9": "\u00e9",  # Ã© -> é
        "\u00c3\u00a8": "\u00e8",  # Ã¨ -> è
        "\u00c3\u00aa": "\u00ea",  # Ãª -> ê
        "\u00c3\u00a0": "\u00e0",  # Ã  -> à
        "\u00c3\u00a2": "\u00e2",  # Ã¢ -> â
        "\u00c3\u00ab": "\u00eb",  # Ã« -> ë
        "\u00c3\u00b4": "\u00f4",  # Ã´ -> ô
        "\u00c3\u00b9": "\u00f9",  # Ã¹ -> ù
        "\u00c3\u00a7": "\u00e7",  # Ã§ -> ç
        "\u00e2\u20ac\u2122": "\u2019",  # â€™ -> ’
        "\u00e2\u20ac\u201c": "\u201c",  # â€œ -> “
        "\u00e2\u20ac\u201d": "\u201d",  # â€ -> ”
        "\u00e2\u20ac\u2014": "\u2014",  # â€” -> —
        "\u00e2\u20ac\u2013": "\u2013",  # â€“ -> –
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text


@register.filter
def highlight_query(value, query):
    if value is None:
        return ""
    text = str(value)
    q = str(query or "").strip()
    if not q:
        return text
    escaped = re.escape(q)
    pattern = re.compile(escaped, re.IGNORECASE)

    def _repl(match):
        return f"<mark>{match.group(0)}</mark>"

    return mark_safe(pattern.sub(_repl, text))
