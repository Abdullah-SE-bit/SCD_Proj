"""Strip instructions aimed at models from fetched content (M05-002). Fetched text is data, never instructions.

ponytail: pattern matching catches known phrasings only. The other layers are that callers pass evidence as delimited
data, M12 checks claims, and no model can set a verdict.
"""

import json
import re
import unicodedata
from html.parser import HTMLParser

REMOVED = "[removed instruction]"
INSTRUCTIONS = re.compile("|".join((
    r"\b(ignore|disregard|forget|override|bypass)\b.{0,60}\b(instructions?|prompts?|rules|guidelines|context)\b",
    r"\byou (are|will) (now )?(be |act as )?(a|an|the)\b.{0,40}\b(assistant|ai|model|agent|bot|llm)\b",
    r"\b(system|developer) (prompt|message|instructions?)\b",
    r"<\|[^|>]{0,40}\|>|\[/?(inst|sys)\]|</?(system|assistant|instructions?)>",
    r"^\W{0,4}(system|assistant|developer)\s*:",
    r"\b(give|rate|score|assign|mark|return|output)\b.{0,60}\b(verdict|score|rating)\b.{0,40}"
    r"\b(5|five|go|maximum|highest|perfect)\b",
    r"\b(give|rate|assign|award)\b.{0,60}\b(highest|maximum|perfect|top)\s+(score|rating|verdict|marks?)\b",
    r"\b(you (must|should)|please|always)\b.{0,40}\b(respond|reply|answer|output|say|recommend)\b.{0,40}"
    r"\b(only|with|that|go)\b",
    r"\b(as an?|dear) (ai|language model|llm|assistant)\b",
    r"\bdo not (tell|inform|alert|mention (this )?to) the (user|human)\b",
    r"\bnew instructions?\s*:",
)), re.IGNORECASE)
SENTENCE = re.compile(r"(?<=[.!?])\s+|[\r\n]+")
HIDDEN_STYLE = re.compile(r"display\s*:\s*none|visibility\s*:\s*hidden|font-size\s*:\s*0|opacity\s*:\s*0", re.I)
SILENT = {"script", "style", "noscript", "template", "svg", "iframe"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
BLOCKS = {"p", "div", "li", "br", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article", "blockquote"}


class VisibleText(HTMLParser):
    """Text a person would see: no scripts, comments or hidden elements."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden: list[str] = []  # open tags inside a hidden element

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in BLOCKS:
            self.parts.append("\n")
        if tag in VOID:
            return
        values = dict(attrs)
        invisible = (tag in SILENT or "hidden" in values or values.get("aria-hidden") == "true"
                     or HIDDEN_STYLE.search(values.get("style") or ""))
        if self.hidden or invisible:
            self.hidden.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in self.hidden:
            del self.hidden[len(self.hidden) - 1 - self.hidden[::-1].index(tag):]
        elif tag in BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)


def visible_text(html: str) -> str:
    parser = VisibleText()
    parser.feed(html)
    parser.close()
    return re.sub(r"[ \t]*\n\s*", "\n", "".join(parser.parts)).strip()


def clean_text(text: str) -> tuple[str, int]:
    """(text without instruction sentences or invisible characters, number of sentences removed)."""
    text = unicodedata.normalize("NFKC", text)
    text = "".join(c for c in text if c in "\n\t" or unicodedata.category(c) not in ("Cc", "Cf", "Co", "Cs"))
    pieces = re.split(f"({SENTENCE.pattern})", text)
    removed = 0
    for index in range(0, len(pieces), 2):
        if INSTRUCTIONS.search(pieces[index]):
            pieces[index] = REMOVED
            removed += 1
    return "".join(pieces), removed


def _clean_value(value: object) -> tuple[object, int]:
    if isinstance(value, str):
        if re.fullmatch(r"https?://\S+", value):
            return value, 0
        return clean_text(visible_text(value) if re.search(r"</?[a-zA-Z!][^>]*>|&#?\w+;", value) else value)
    if isinstance(value, list):
        cleaned = [_clean_value(item) for item in value]
        return [c for c, _ in cleaned], sum(n for _, n in cleaned)
    if isinstance(value, dict):
        pairs = {key: _clean_value(item) for key, item in value.items()}
        return {key: c for key, (c, _) in pairs.items()}, sum(n for _, n in pairs.values())
    return value, 0


def sanitise(content: str, content_type: str) -> tuple[str, int]:
    """Clean a response body. HTML becomes visible text; JSON keeps its structure with every string cleaned."""
    if content_type == "application/json":
        try:
            value, removed = _clean_value(json.loads(content))
            return json.dumps(value, ensure_ascii=False), removed
        except (ValueError, RecursionError):
            pass
    if "html" in content_type or "xml" in content_type:
        content = visible_text(content)
    return clean_text(content)
