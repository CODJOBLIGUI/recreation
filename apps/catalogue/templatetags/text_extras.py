from html import unescape
import unicodedata

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="unescape")
def unescape_filter(value):
    if value is None:
        return ""
    return mark_safe(unescape(str(value)))


@register.filter(name="fix_mojibake")
def fix_mojibake(value):
    if value is None:
        return ""
    text = str(value)
    replacements = {
        "Ã©": "é",
        "Ã¨": "è",
        "Ãª": "ê",
        "Ã«": "ë",
        "Ã ": "à",
        "Ã¢": "â",
        "Ã®": "î",
        "Ã´": "ô",
        "Ã¹": "ù",
        "Ã»": "û",
        "Ã§": "ç",
        "Ã‰": "É",
        "Ã€": "À",
        "â€™": "’",
        "â€œ": "“",
        "â€": "”",
        "â€“": "–",
        "â€”": "—",
        "Â": "",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return mark_safe(text)


@register.filter(name="highlight_query")
def highlight_query(value, query):
    if value is None:
        return ""
    original_text = str(value)
    if not query:
        return mark_safe(escape(original_text))
    words = [w.strip() for w in str(query).split() if w.strip()]
    if not words:
        return mark_safe(escape(original_text))

    def _normalize_text(text):
        normalized = unicodedata.normalize("NFKD", text)
        cleaned = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn").lower()
        return "".join(ch for ch in cleaned if ch.isalnum())

    normalized_text = ""
    norm_to_orig = []
    for idx, ch in enumerate(original_text):
        normalized = unicodedata.normalize("NFKD", ch)
        normalized = "".join(c for c in normalized if unicodedata.category(c) != "Mn")
        if not normalized:
            continue
        for norm_ch in normalized.lower():
            if not norm_ch.isalnum():
                continue
            normalized_text += norm_ch
            norm_to_orig.append(idx)

    normalized_words = []
    for word in words:
        normalized = _normalize_text(word)
        if normalized:
            normalized_words.append(normalized)
    if not normalized_words:
        return mark_safe(escape(original_text))

    spans = []
    for word in normalized_words:
        start = 0
        while True:
            pos = normalized_text.find(word, start)
            if pos == -1:
                break
            end = pos + len(word) - 1
            orig_start = norm_to_orig[pos]
            orig_end = norm_to_orig[end]
            spans.append((orig_start, orig_end))
            start = pos + len(word)

    if not spans:
        return mark_safe(escape(original_text))

    spans.sort()
    merged = []
    for start, end in spans:
        if not merged:
            merged.append([start, end])
            continue
        last = merged[-1]
        if start <= last[1] + 1:
            last[1] = max(last[1], end)
        else:
            merged.append([start, end])

    output = []
    last_index = 0
    for start, end in merged:
        if start > last_index:
            output.append(escape(original_text[last_index:start]))
        output.append('<mark class="hl">')
        output.append(escape(original_text[start:end + 1]))
        output.append("</mark>")
        last_index = end + 1
    if last_index < len(original_text):
        output.append(escape(original_text[last_index:]))

    return mark_safe("".join(output))
