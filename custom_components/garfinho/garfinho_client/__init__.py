"""Unofficial async client for the Garfinho recipe app."""

from .catalog import Catalog, Query, Sort
from .client import GarfinhoClient
from .content import RecipeContent
from .exceptions import (
    ApiError,
    AuthError,
    GarfinhoError,
    LoginTimeoutError,
    NotAuthenticatedError,
)
from .models import Folder, Ingredient, Recipe, Session, Tag, UserData

__all__ = [
    "ApiError",
    "AuthError",
    "Catalog",
    "Folder",
    "GarfinhoClient",
    "GarfinhoError",
    "Ingredient",
    "LoginTimeoutError",
    "NotAuthenticatedError",
    "Query",
    "RecipeContent",
    "Recipe",
    "Session",
    "Sort",
    "Tag",
    "UserData",
]
