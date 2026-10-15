from garfinho_client import Recipe, UserData
from garfinho_client.http import parse_jsonp


def test_user_data_roundtrip_preserves_unknown_keys():
    raw = {
        "bookmarks": ["a"],
        "folders": [{"id": 1, "title": "F", "recipes": ["a"], "color": "red"}],
        "reviews": [1, 2],
        "completedRecipes": [],
    }
    assert UserData.from_api(raw).to_api() == raw


def test_recipe_from_api():
    r = Recipe.from_api(
        {
            "id": "x",
            "title": " Bolo ",
            "img": "u",
            "createdAt": 5,
            "tags": [{"tagId": 1, "tagName": "A "}],
            "ingredients": [{"id": 2, "name": "ovo"}],
        }
    )
    assert (r.title, r.tags[0].id, r.tags[0].name, r.ingredients[0].name) == (
        "Bolo",
        "1",
        "A",
        "ovo",
    )


def test_parse_jsonp():
    text = '/**/ typeof cb === \'function\' && cb({"id":1,"result":null});'
    assert parse_jsonp(text) == {"id": 1, "result": None}
