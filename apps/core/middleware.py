# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup


class SmartApostropheMiddleware:
    """Replace straight apostrophes with typographic ones in HTML text nodes."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get("Content-Type", "")
        if "text/html" not in content_type or not getattr(response, "content", None):
            return response

        try:
            charset = getattr(response, "charset", "utf-8") or "utf-8"
            html = response.content.decode(charset, errors="ignore")
            soup = BeautifulSoup(html, "html.parser")
            for node in soup.find_all(string=True):
                parent = node.parent.name if node.parent else ""
                if parent in {"script", "style", "code", "pre", "textarea"}:
                    continue
                if "'" in node:
                    node.replace_with(node.replace("'", "\u2019"))
            response.content = soup.encode(charset)
        except Exception:
            return response
        return response
