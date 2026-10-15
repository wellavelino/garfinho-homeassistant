from unittest.mock import AsyncMock, MagicMock

from garfinho_client import Catalog, Ingredient, Recipe, RecipeContent, Session, Tag, UserData

SESSION = Session("user-1", "Ana", "ana@example.com")
RECIPES = [
    Recipe("r1", "Bolo de cenoura", None, 2, (Tag("t1", "Fácil"),), (Ingredient("i1", "cenoura"),)),
    Recipe("r2", "Omelete", None, 1, (Tag("t2", "Jantar"),), (Ingredient("i2", "ovo"),)),
]


def fake_client(session=SESSION, bookmarks=("r1",)):
    client = MagicMock()
    client.session = session
    catalog = Catalog(RECIPES)
    client.catalog = AsyncMock(return_value=catalog)
    client.recipe_content = AsyncMock(
        side_effect=lambda rid: (
            RecipeContent("<h4>Como preparar:</h4>", "vid123") if rid == "r1" else None
        )
    )
    client.refresh = AsyncMock()
    client.search = AsyncMock(side_effect=lambda q: catalog.search(q))
    favorites = MagicMock()
    favorites.snapshot = AsyncMock(return_value=UserData(bookmarks=list(bookmarks)))
    favorites.ids = AsyncMock(return_value=list(bookmarks))
    favorites.add = AsyncMock(return_value=True)
    favorites.remove = AsyncMock(return_value=True)
    client.favorites = favorites
    client.auth.request_code = AsyncMock(return_value="code-1")
    client.auth.login_url = MagicMock(return_value="https://auth.example/login?code=code-1")
    client.auth.poll = AsyncMock(return_value=None)
    return client
