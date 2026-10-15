import pytest

from garfinho_client import Catalog, Ingredient, Query, Recipe, Sort, Tag


def recipe(rid, title, tags=(), ings=(), created=0):
    return Recipe(
        rid,
        title,
        None,
        created,
        tuple(Tag(f"t-{t}", t) for t in tags),
        tuple(Ingredient(f"i-{i}", i) for i in ings),
    )


@pytest.fixture
def catalog():
    return Catalog(
        [
            recipe("1", "Pão de queijo", ["Lanche", "Sem glúten"], ["queijo", "polvilho"], 3),
            recipe("2", "Omelete", ["Jantar", "Fácil"], ["ovo", "queijo"], 2),
            recipe("3", "Bolo de cenoura", ["Lanche", "Sem ovo"], ["cenoura", "farinha"], 1),
        ]
    )


def ids(rs):
    return [r.id for r in rs]


def test_text_is_accent_and_case_insensitive(catalog):
    assert ids(catalog.search(Query(text="PAO"))) == ["1"]


def test_text_matches_ingredients_and_ranks_title_first(catalog):
    assert ids(catalog.search(Query(text="queijo"))) == ["1", "2"]


def test_every_word_must_match(catalog):
    assert ids(catalog.search(Query(text="queijo omelete"))) == ["2"]


def test_tag_filter_by_name_ignores_accents(catalog):
    assert ids(catalog.search(Query(tags=["sem gluten"]))) == ["1"]


def test_tag_filter_by_id(catalog):
    assert ids(catalog.search(Query(tags=["t-Jantar"]))) == ["2"]


def test_exclude_tag(catalog):
    assert ids(catalog.search(Query(exclude_tags=["Lanche"]))) == ["2"]


def test_ingredient_include_and_exclude(catalog):
    assert ids(catalog.search(Query(ingredients=["queijo"], exclude_ingredients=["ovo"]))) == ["1"]


def test_sort_newest_and_title(catalog):
    assert ids(catalog.search(Query(sort=Sort.NEWEST))) == ["1", "2", "3"]
    assert ids(catalog.search(Query(sort=Sort.TITLE))) == ["3", "2", "1"]


def test_pagination(catalog):
    assert ids(catalog.search(Query(sort=Sort.TITLE, limit=1, offset=1))) == ["2"]


def test_tags_counts(catalog):
    counts = {t.name: n for t, n in catalog.tags()}
    assert counts["Lanche"] == 2 and counts["Fácil"] == 1
