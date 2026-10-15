"""In-memory search and filtering over the recipe index (pure, no I/O)."""

from __future__ import annotations

import random
import unicodedata
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import StrEnum

from .models import Recipe, Tag


def fold(text: str) -> str:
    """Lowercase and strip accents so 'Pão' matches 'pao'."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).casefold().strip()


class Sort(StrEnum):
    RELEVANCE = "relevance"
    NEWEST = "newest"
    TITLE = "title"
    RANDOM = "random"


@dataclass(frozen=True, slots=True)
class Query:
    """All conditions are ANDed. Tags match by id or accent-insensitive name."""

    text: str = ""
    tags: Sequence[str] = ()
    exclude_tags: Sequence[str] = ()
    ingredients: Sequence[str] = ()
    exclude_ingredients: Sequence[str] = ()
    sort: Sort = Sort.RELEVANCE
    limit: int | None = None
    offset: int = 0


class Catalog:
    def __init__(self, recipes: Iterable[Recipe]) -> None:
        self._recipes = list(recipes)
        self._by_id = {r.id: r for r in self._recipes}
        self._folded = {r.id: _Folded.of(r) for r in self._recipes}

    def __len__(self) -> int:
        return len(self._recipes)

    def get(self, recipe_id: str) -> Recipe | None:
        return self._by_id.get(recipe_id)

    def tags(self) -> list[tuple[Tag, int]]:
        """Every tag with how many recipes use it, most used first."""
        counts: Counter[Tag] = Counter(t for r in self._recipes for t in set(r.tags))
        return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0].name))

    def search(self, query: Query = Query()) -> list[Recipe]:  # noqa: B008
        words = fold(query.text).split()
        want_tags = _tag_matcher(query.tags)
        skip_tags = _tag_matcher(query.exclude_tags)
        want_ing = [fold(i) for i in query.ingredients]
        skip_ing = [fold(i) for i in query.exclude_ingredients]

        scored: list[tuple[int, Recipe]] = []
        for recipe in self._recipes:
            f = self._folded[recipe.id]
            if not all(want_tags(recipe, t) for t in query.tags):
                continue
            if any(skip_tags(recipe, t) for t in query.exclude_tags):
                continue
            if not all(any(i in n for n in f.ingredients) for i in want_ing):
                continue
            if any(any(i in n for n in f.ingredients) for i in skip_ing):
                continue
            score = _text_score(words, f)
            if words and score == 0:
                continue
            scored.append((score, recipe))

        ordered = _order(scored, query.sort)
        end = None if query.limit is None else query.offset + query.limit
        return ordered[query.offset : end]


@dataclass(frozen=True, slots=True)
class _Folded:
    title: str
    ingredients: tuple[str, ...]

    @classmethod
    def of(cls, recipe: Recipe) -> _Folded:
        return cls(fold(recipe.title), tuple(fold(i.name) for i in recipe.ingredients))


def _tag_matcher(wanted: Sequence[str]):  # type: ignore[no-untyped-def]
    folded = {w: fold(w) for w in wanted}

    def match(recipe: Recipe, wanted_tag: str) -> bool:
        needle = folded[wanted_tag]
        return any(t.id == wanted_tag or fold(t.name) == needle for t in recipe.tags)

    return match


def _text_score(words: list[str], f: _Folded) -> int:
    """0 means no match. Every word must hit the title or an ingredient."""
    if not words:
        return 1
    score = 0
    for w in words:
        if f.title.startswith(w):
            score += 4
        elif w in f.title:
            score += 3
        elif any(w in n for n in f.ingredients):
            score += 1
        else:
            return 0
    return score


def _order(scored: list[tuple[int, Recipe]], sort: Sort) -> list[Recipe]:
    if sort is Sort.NEWEST:
        return [r for _, r in sorted(scored, key=lambda s: -s[1].created_at)]
    if sort is Sort.TITLE:
        return [r for _, r in sorted(scored, key=lambda s: fold(s[1].title))]
    if sort is Sort.RANDOM:
        items = [r for _, r in scored]
        random.shuffle(items)
        return items
    return [r for _, r in sorted(scored, key=lambda s: (-s[0], fold(s[1].title)))]
