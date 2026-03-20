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
        "Ã©": "é",
        "Ã¨": "è",
        "Ãª": "ê",
        "Ã": "à",
        "Ã¢": "â",
        "Ã«": "ë",
        "Ã´": "ô",
        "Ã¹": "ù",
        "Ã§": "ç",
        "â€™": "’",
        "â€\": "—",
        "â€“": "–",
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
