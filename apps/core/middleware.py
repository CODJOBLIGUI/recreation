from django.utils.deprecation import MiddlewareMixin
from .utils.apostrophe import replace_apostrophes


class SmartApostropheMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        content_type = response.get("Content-Type", "")
        if "text/html" not in content_type:
            return response
        if getattr(response, "streaming", False):
            return response
        try:
            charset = response.charset or "utf-8"
            content = response.content.decode(charset)
        except Exception:
            return response
        new_content = replace_apostrophes(content)
        if new_content != content:
            response.content = new_content.encode(charset)
            if response.get("Content-Length"):
                response["Content-Length"] = str(len(response.content))
        return response
