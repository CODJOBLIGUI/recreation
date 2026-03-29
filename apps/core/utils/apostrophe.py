from html.parser import HTMLParser

class _ApostropheHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self._out = []
        self._stack = []

    @property
    def output(self):
        return ??.join(self._out)

    def handle_starttag(self, tag, attrs):
        self._stack.append(tag.lower())
        self._out.append(?<? + tag)
        for k, v in attrs:
            if v is None:
                self._out.append(f? {k}?)
            else:
                escaped = v.replace(?"?, ?&quot;?)
                self._out.append(f? {k}="{escaped}"?)
        self._out.append(?>?)

    def handle_endtag(self, tag):
        if self._stack:
            self._stack.pop()
        self._out.append(f?</{tag}>?)

    def handle_startendtag(self, tag, attrs):
        self._out.append(?<? + tag)
        for k, v in attrs:
            if v is None:
                self._out.append(f? {k}?)
            else:
                escaped = v.replace(?"?, ?&quot;?)
                self._out.append(f? {k}="{escaped}"?)
        self._out.append(? />?)

    def handle_data(self, data):
        if self._stack and self._stack[-1] in {?script?, ?style?}:
            self._out.append(data)
            return
        self._out.append(data.replace("?", "\u2019"))

    def handle_entityref(self, name):
        self._out.append(f?&{name};?)

    def handle_charref(self, name):
        self._out.append(f?&#{name};?)

    def handle_comment(self, data):
        self._out.append(f?<!--{data}-->?)

    def handle_decl(self, decl):
        self._out.append(f?<!{decl}>?)


def replace_apostrophes(html_text: str) -> str:
    parser = _ApostropheHTMLParser()
    parser.feed(html_text)
    parser.close()
    return parser.output
