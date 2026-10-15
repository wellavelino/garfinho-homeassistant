"""Recipe texts (ingredients with quantities, steps) from the app's offline bundle.

The index served by the datastore only has titles, tags and ingredient names. The full
text ships inside the app's public offline data dump, a zip holding one JS file that
starts with ``var offlineDataDump = {"result": [...]}``. Pure parsing, no I/O.
"""

from __future__ import annotations

import io
import json
import re
import zipfile
from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser

from .exceptions import ApiError

_ALLOWED = {
    "p",
    "br",
    "ul",
    "ol",
    "li",
    "strong",
    "b",
    "em",
    "i",
    "u",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
}
_VOID = {"br", "img", "hr", "input", "meta", "link"}
_SKIP_CONTENT = {"script", "style", "iframe"}
_HIDDEN_CLASS = "bf-wysiwyg-hide-app"
_YOUTUBE = re.compile(r"youtube(?:-nocookie)?\.com/embed/([\w-]{6,})")


@dataclass(frozen=True, slots=True)
class RecipeContent:
    html: str
    video_id: str | None = None


class _Sanitizer(HTMLParser):
    """Keeps a small set of formatting tags, drops attributes, images and hidden blocks."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.video_id: str | None = None
        self._stack: list[tuple[str, bool]] = []  # (tag, hidden-or-skipped)
        self._hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "iframe" and self.video_id is None:
            found = _YOUTUBE.search(values.get("src") or "")
            self.video_id = found.group(1) if found else None
        if tag in _VOID:
            if tag == "br" and not self._hidden:
                self.out.append("<br>")
            return
        hides = tag in _SKIP_CONTENT or _HIDDEN_CLASS in (values.get("class") or "")
        self._stack.append((tag, hides))
        if hides:
            self._hidden += 1
        elif not self._hidden and tag in _ALLOWED:
            self.out.append(f"<{tag}>")

    def handle_endtag(self, tag: str) -> None:
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i][0] != tag:
                continue
            for _, hides in self._stack[i:]:
                if hides:
                    self._hidden -= 1
            del self._stack[i:]
            if not self._hidden and tag in _ALLOWED:
                self.out.append(f"</{tag}>")
            return

    def handle_data(self, data: str) -> None:
        if not self._hidden:
            self.out.append(escape(data.replace("\xa0", " ")))


def clean_html(raw: str) -> RecipeContent:
    parser = _Sanitizer()
    parser.feed(raw)
    parser.close()
    html = "".join(parser.out)
    html = re.sub(r"<(p|li|h[1-6]|strong|b|em|i|u)>\s*</\1>", "", html)
    return RecipeContent(html.strip(), parser.video_id)


def parse_bundle(archive: bytes) -> dict[str, RecipeContent]:
    """Map recipe id -> cleaned content."""
    try:
        with zipfile.ZipFile(io.BytesIO(archive)) as zf:
            text = zf.read(zf.namelist()[0]).decode("utf-8")
        start = text.index("{")
        doc, _ = json.JSONDecoder().raw_decode(text[start:])
        rows = doc["result"]
    except (zipfile.BadZipFile, ValueError, KeyError, IndexError) as err:
        raise ApiError("Content bundle has an unexpected shape") from err
    out: dict[str, RecipeContent] = {}
    for row in rows:
        if row.get("tag") != "recipes":
            continue
        data = row.get("data") or {}
        recipe_id, raw = data.get("localRecordId"), data.get("content")
        if isinstance(recipe_id, str) and isinstance(raw, str):
            content = clean_html(raw)
            if content.html or content.video_id:
                out[recipe_id] = content
    return out
