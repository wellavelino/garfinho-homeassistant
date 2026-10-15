"""Plain data models. No I/O here."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Tag:
    id: str
    name: str


@dataclass(frozen=True, slots=True)
class Ingredient:
    id: str
    name: str


@dataclass(frozen=True, slots=True)
class Recipe:
    id: str
    title: str
    image_url: str | None
    created_at: int
    tags: tuple[Tag, ...] = ()
    ingredients: tuple[Ingredient, ...] = ()

    @classmethod
    def from_api(cls, raw: dict[str, Any]) -> Recipe:
        return cls(
            id=raw["id"],
            title=raw.get("title", "").strip(),
            image_url=raw.get("img") or None,
            created_at=int(raw.get("createdAt") or 0),
            tags=tuple(Tag(str(t["tagId"]), t["tagName"].strip()) for t in raw.get("tags", [])),
            ingredients=tuple(
                Ingredient(str(i["id"]), i["name"].strip()) for i in raw.get("ingredients", [])
            ),
        )


@dataclass(frozen=True, slots=True)
class Session:
    """What is needed to act as a user. Deliberately excludes OAuth provider tokens."""

    user_id: str
    display_name: str = ""
    email: str = ""

    def to_dict(self) -> dict[str, str]:
        return {"user_id": self.user_id, "display_name": self.display_name, "email": self.email}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Session:
        return cls(data["user_id"], data.get("display_name", ""), data.get("email", ""))

    @classmethod
    def from_api(cls, raw: dict[str, Any]) -> Session:
        return cls(raw["userId"], raw.get("displayName", ""), raw.get("email", ""))


@dataclass(slots=True)
class Folder:
    id: int
    title: str
    recipes: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class UserData:
    """The per-user document. ``extra`` keeps unknown keys so saves never drop data."""

    bookmarks: list[str] = field(default_factory=list)
    folders: list[Folder] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> UserData:
        known = {"bookmarks", "folders"}
        return cls(
            bookmarks=list(data.get("bookmarks", [])),
            folders=[
                Folder(
                    f["id"],
                    f.get("title", ""),
                    list(f.get("recipes", [])),
                    {k: v for k, v in f.items() if k not in {"id", "title", "recipes"}},
                )
                for f in data.get("folders", [])
            ],
            extra={k: v for k, v in data.items() if k not in known},
        )

    def to_api(self) -> dict[str, Any]:
        return {
            **self.extra,
            "bookmarks": self.bookmarks,
            "folders": [
                {**f.extra, "id": f.id, "title": f.title, "recipes": f.recipes}
                for f in self.folders
            ],
        }
