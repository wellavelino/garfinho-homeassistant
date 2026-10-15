"""Identifiers of the Garfinho app on the BuildFire platform."""

APP_ID = "c33236bc-dd59-11ec-8dc6-0a8ebc214e8b"
PLUGIN_ID = "b99b546b-5fd7-4b34-a79f-568d3105957d"
INSTANCE_ID = f"{PLUGIN_ID}-1609375762773"

DATASTORE_URL = "https://datastore.buildfire.com"
AUTH_URL = "https://auth.buildfire.com"

LOGIN_PROVIDER = "google"
DEFAULT_TIMEOUT = 15.0

# The app ships its content (recipe texts included) as a public offline bundle.
BUNDLE_URL = f"https://cdn.datadump.buildfire.com/{APP_ID}/{APP_ID}.zip"
BUNDLE_TTL = 24 * 3600.0
