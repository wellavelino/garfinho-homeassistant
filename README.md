# Garfinho for Home Assistant

Browse and search the [Garfinho](https://garfinhoapp.com/) recipe collection from your Home Assistant sidebar, read the full ingredients and steps, and manage your favorites without leaving your dashboard.

[![Open your Home Assistant instance and open this repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=wellavelino&repository=garfinho-homeassistant&category=integration)
[![Open your Home Assistant instance and start setting up the integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=garfinho)

[![Stars](https://img.shields.io/github/stars/wellavelino/garfinho-homeassistant?style=for-the-badge)](https://github.com/wellavelino/garfinho-homeassistant)
[![Last commit](https://img.shields.io/github/last-commit/wellavelino/garfinho-homeassistant?style=for-the-badge)](https://github.com/wellavelino/garfinho-homeassistant/commits/main)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange?style=for-the-badge)](https://hacs.xyz)
[![License](https://img.shields.io/github/license/wellavelino/garfinho-homeassistant?style=for-the-badge)](LICENSE)

> **Unofficial.** Not affiliated with or endorsed by Garfinho or BuildFire. It uses the same public data and endpoints as the official app, on behalf of *your own* account. You need your own Garfinho account; this project does not give access to anything you haven't paid for. Respect the app's terms of service. The backend can change without notice and break the integration.

<br>

## Table of contents

**[`Features`](#features)**  **[`Installation`](#installation)**  **[`Setup`](#setup)**  **[`The Garfinho panel`](#the-garfinho-panel)**  **[`Sensor and services`](#sensor-and-services)**  **[`Automation examples`](#automation-examples)**  **[`FAQ`](#faq)**  **[`Python library and CLI`](#python-library-and-cli)**  **[`Development`](#development)**

<br>

## Features

- **Sidebar panel** to search the whole collection (776 recipes) by name or ingredient, filter by tag, sort, and open any recipe.
- **Full recipe view** with ingredients and quantities, step by step instructions and a link to the video when there is one.
- **Favorites** in sync with the app: add or remove with one click, grouped by your folders.
- **Favorite recipes sensor** with the count, titles and folders.
- **Services** for scripts and automations: `search`, `add_favorite`, `remove_favorite`, `refresh`.
- **Daily refresh** of recipes and instructions, so new recipes show up on their own.
- Works with any Home Assistant theme, on desktop and mobile. Portuguese and English.

<br>

## Installation

**Home Assistant lowest supported version:** 2025.2.0

<details>

<summary>With HACS (Recommended)</summary>

<br>

1. If HACS is not installed yet, follow [the HACS setup guide](https://hacs.xyz/docs/use/download/download/).
2. Click the button below, or in HACS open the menu (⋮) → **Custom repositories**, paste `https://github.com/wellavelino/garfinho-homeassistant` and choose the type **Integration**.

   [![Open your Home Assistant instance and open this repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=wellavelino&repository=garfinho-homeassistant&category=integration)

3. Click **Download**.
4. Restart Home Assistant.

</details>

<details>

<summary>Without HACS</summary>

<br>

1. Download this repository and copy the folder `custom_components/garfinho` into `<config>/custom_components/`, so you end up with `<config>/custom_components/garfinho/manifest.json`.
2. Restart Home Assistant.

If you use the Terminal & SSH add-on, `<config>` is `/homeassistant`.

</details>

<br>

## Setup

1. Go to **Settings → Devices & services → Add integration** and search for **Garfinho**, or click the button:

   [![Open your Home Assistant instance and start setting up the integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=garfinho)

2. Open the sign-in link that appears and log in with your Garfinho account (Google).
3. Come back to Home Assistant and press **Submit**.

Your password never reaches Home Assistant. Only your Garfinho user id, name and email are stored.

<br>

## The Garfinho panel

After setup you get a **Garfinho** item (chef hat icon) in the sidebar.

| Tab | What you can do |
| --- | --- |
| **Search** | Type a name or ingredient, click tag chips to filter, change the sort order (relevance, newest, A to Z, random). |
| **Favorites** | See everything you saved, grouped by your folders from the app. |
| **Recipe** | Click any card to open it: photo, tags, ingredients, steps and video link. |

Tap the heart on a card or in the recipe to add or remove a favorite. It changes your real Garfinho account, so it shows up in the app too. Removing a favorite also removes it from your folders, just like the app does.

<br>

## Sensor and services

**Sensor:** `sensor.garfinho_favorite_recipes` is the number of favorites. Its attributes have `recipes` (titles) and `folders` (folder name and size).

**Services:**

```yaml
# Search. Returns the matches as response data.
action: garfinho.search
data:
  text: bolo
  tags: ["Sem glúten"]
  exclude_ingredients: ["ovo"]
  sort: random            # relevance | newest | title | random
  limit: 3
response_variable: result # result.recipes[].title / .id / .image / .tags / .ingredients
```

```yaml
action: garfinho.add_favorite
data:
  recipe_id: "<id from search>"
```

```yaml
action: garfinho.remove_favorite
data:
  recipe_id: "<id from search>"
```

```yaml
# Download the latest recipes and instructions right now (this also runs every 24 hours)
action: garfinho.refresh
```

<br>

## Automation examples

A random easy dinner idea on your phone every day at 17:00:

```yaml
alias: Dinner idea
triggers:
  - trigger: time
    at: "17:00:00"
actions:
  - action: garfinho.search
    data:
      tags: ["Jantar", "Fácil"]
      sort: random
      limit: 1
    response_variable: result
  - action: notify.mobile_app_your_phone
    data:
      title: "Tonight's idea"
      message: "{{ result.recipes[0].title }}"
```

<br>

## FAQ

**How often are recipes updated?** Recipes and instructions are downloaded in the background when Home Assistant starts and then every 24 hours. Run `garfinho.refresh` to update on demand.

**Does it work without a Garfinho account?** Searching and reading recipes needs no login, but the integration setup asks you to sign in because favorites belong to your account.

**The panel does not show up.** Restart Home Assistant after installing, then hard refresh the browser (Ctrl+Shift+R). If it is still hidden, check Profile → sidebar settings.

**A recipe says "No instructions available".** Some recipes have no text in the app either. If you think one is missing, run `garfinho.refresh` first.

**Is it safe?** The integration only talks to Garfinho's own servers and to YouTube when you open a video link. Instructions are cleaned before they are shown: only basic formatting is kept.

<br>

## Python library and CLI

The client lives in `custom_components/garfinho/garfinho_client/` and also works on its own:

```python
import asyncio
from garfinho_client import GarfinhoClient, Query


async def main():
    async with GarfinhoClient() as client:
        for r in await client.search(Query(text="bolo", tags=["Sem glúten"], limit=5)):
            print(r.title)
        content = await client.recipe_content(r.id)  # steps as clean HTML, or None
        print(content.html if content else "no text")


asyncio.run(main())
```

```
uv run garfinho login            # sign in through your browser
uv run garfinho tags
uv run garfinho search bolo --tag "Sem glúten" --without ovo
uv run garfinho fav add <recipe-id>
```

| module | role |
| --- | --- |
| `http.py` | aiohttp transport (JSON, JSONP, bytes) |
| `auth.py` | browser login via one-time code |
| `datastore.py` | BuildFire documents (recipe index, user data) |
| `content.py` | recipe texts from the app's offline bundle, cleaned |
| `catalog.py` | pure search and filtering |
| `favorites.py` | bookmark read-modify-write |
| `client.py` | facade; accepts an existing `aiohttp.ClientSession` |

<br>

## Development

```
uv sync && uv run pytest && uv run ruff check . && uv run mypy   # Python 3.13
```

To try changes in a real Home Assistant, copy `custom_components/garfinho` into your config folder and restart.

<br>

## Credits and license

Recipes, photos and texts belong to [Garfinho](https://garfinhoapp.com/) and its authors. This project is MIT licensed and only provides the glue. README layout inspired by [Bubble Card](https://github.com/Clooos/Bubble-Card).
