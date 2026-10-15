import pytest

from garfinho_client import Session, UserData
from garfinho_client.favorites import Favorites


class FakeStore:
    def __init__(self, data):
        self.data = data
        self.saves = 0

    async def load_user_data(self, session):
        return UserData.from_api(self.data.to_api())

    async def save_user_data(self, session, data):
        self.data = data
        self.saves += 1


@pytest.fixture
def store():
    return FakeStore(
        UserData.from_api(
            {
                "bookmarks": ["a", "b"],
                "folders": [{"id": 1, "title": "F", "recipes": ["b"]}],
                "x": 1,
            }
        )
    )


@pytest.fixture
def favs(store):
    return Favorites(store, Session("u"))


async def test_add_is_idempotent(favs, store):
    assert await favs.add("c") is True
    assert await favs.add("c") is False
    assert store.data.bookmarks == ["a", "b", "c"] and store.saves == 1


async def test_remove_strips_folders_and_keeps_extra(favs, store):
    assert await favs.remove("b") is True
    assert store.data.bookmarks == ["a"] and store.data.folders[0].recipes == []
    assert store.data.to_api()["x"] == 1


async def test_remove_missing_does_not_save(favs, store):
    assert await favs.remove("zzz") is False
    assert store.saves == 0
