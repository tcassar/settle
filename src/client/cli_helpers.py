import click
import requests

from crypto import hashes as hasher

SERVER = "http://127.0.0.1:5000/"


class AuthError(Exception):
    ...


def hash_password(password) -> str:
    return str(hasher.Hasher(password.encode(encoding="utf8")).digest().h)


def url(query: str) -> str:
    return SERVER + query


def invalid_response(response: requests.Response) -> bool:
    if str(response.status_code)[0] != "2":
        e = response.json()
        click.secho(f"ERROR: {e}", fg="red")
        return True
    else:
        return False