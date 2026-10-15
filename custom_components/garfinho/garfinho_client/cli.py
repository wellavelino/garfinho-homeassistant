"""Command line interface: ``garfinho login | tags | search | fav``."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from .catalog import Query, Sort
from .client import GarfinhoClient
from .exceptions import GarfinhoError
from .models import Session

SESSION_FILE = (
    Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "garfinho" / "session.json"
)


def _load_session() -> Session | None:
    try:
        return Session.from_dict(json.loads(SESSION_FILE.read_text()))
    except (OSError, ValueError, KeyError):
        return None


def _save_session(session: Session) -> None:
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(json.dumps(session.to_dict()))
    SESSION_FILE.chmod(0o600)


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="garfinho")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("login", help="sign in through the browser")
    sub.add_parser("tags", help="list filter tags")
    s = sub.add_parser("search", help="search recipes")
    s.add_argument("text", nargs="*")
    s.add_argument("--tag", action="append", default=[], help="require tag (name or id)")
    s.add_argument("--no-tag", action="append", default=[], help="exclude tag")
    s.add_argument("--with", dest="ing", action="append", default=[], help="require ingredient")
    s.add_argument("--without", action="append", default=[], help="exclude ingredient")
    s.add_argument("--sort", choices=[s.value for s in Sort], default=Sort.RELEVANCE.value)
    s.add_argument("--limit", type=int, default=20)
    fav = sub.add_parser("fav", help="manage favorites")
    fav.add_argument("action", choices=["list", "add", "remove"])
    fav.add_argument("recipe_id", nargs="?")
    return p


async def _run(args: argparse.Namespace) -> int:
    async with GarfinhoClient(_load_session()) as client:
        if args.cmd == "login":
            session = await client.login(lambda url: print(f"Open this URL and sign in:\n{url}"))
            _save_session(session)
            print(f"Logged in as {session.display_name or session.email or session.user_id}")
        elif args.cmd == "tags":
            for tag, count in (await client.catalog()).tags():
                print(f"{count:4d}  {tag.name}  ({tag.id})")
        elif args.cmd == "search":
            query = Query(
                text=" ".join(args.text),
                tags=args.tag,
                exclude_tags=args.no_tag,
                ingredients=args.ing,
                exclude_ingredients=args.without,
                sort=Sort(args.sort),
                limit=args.limit,
            )
            for r in await client.search(query):
                print(f"{r.id}  {r.title}")
        elif args.cmd == "fav":
            favs = client.favorites
            if args.action == "list":
                catalog = await client.catalog()
                for rid in await favs.ids():
                    recipe = catalog.get(rid)
                    print(f"{rid}  {recipe.title if recipe else '(unknown recipe)'}")
            elif not args.recipe_id:
                print("recipe_id is required", file=sys.stderr)
                return 2
            elif args.action == "add":
                print("added" if await favs.add(args.recipe_id) else "already a favorite")
            else:
                print("removed" if await favs.remove(args.recipe_id) else "was not a favorite")
    return 0


def main() -> None:
    try:
        sys.exit(asyncio.run(_run(_parser().parse_args())))
    except GarfinhoError as err:
        sys.exit(f"error: {err}")
