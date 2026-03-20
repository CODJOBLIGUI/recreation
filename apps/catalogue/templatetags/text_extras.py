from django import template
import html

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
