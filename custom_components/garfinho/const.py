"""Constants for the Garfinho integration."""

from datetime import timedelta

DOMAIN = "garfinho"
UPDATE_INTERVAL = timedelta(minutes=30)
MAX_TITLES_ATTRIBUTE = 50
RECIPE_REFRESH_INTERVAL = timedelta(hours=24)

SERVICE_SEARCH = "search"
SERVICE_ADD_FAVORITE = "add_favorite"
SERVICE_REMOVE_FAVORITE = "remove_favorite"
SERVICE_REFRESH = "refresh"
