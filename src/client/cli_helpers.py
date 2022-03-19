# coding=utf-8
import click
import requests

from src.crypto import hashes as hasher
from src.server import models

SERVER = "http://127.0.0.1:5000/"


class AuthError(Exception):
    ...


class InvalidResponseError(Exception):
    "Resource could not be found on the server"


def hash_password(password) -> str:
    return str(hasher.Hasher(password.encode(encoding="utf8")).digest().h)


def url(query: str) -> str:
    return SERVER + query


def validate_response(response: requests.Response) -> None:
    """Raises InvalidResponseError if response is invalid"""
    if str(response.status_code)[0] != "2":
        e = response.json()
        click.secho(f"ERROR: {e}", fg="red")
        raise InvalidResponseError(response.text)


def _auth(resource: str, password: str):
    usr_response: requests.Response = requests.get(url(resource))
    try:
        validate_response(usr_response)
    except InvalidResponseError:
        raise InvalidResponseError(f"No {resource.split('/')[0]} with identifier {resource.split('/')[1]} found")

    # build a user from received data

    rep = usr_response.json()

    if rep["password"] != hash_password(password):
        raise AuthError("Password Incorrect")


def auth_usr(email: str, password: str):
    """Authorises user, raises AuthError if fails"""
    return _auth(f"user/{email}", password)


def auth_group(group_id: int, password: str):
    return _auth(f"group/{group_id}", password)


def get_user(email: str) -> models.User:
    usr_rep = requests.get(url(f"user/{email}"))

    try:
        validate_response(usr_rep)
    except InvalidResponseError:
        raise InvalidResponseError(f"No user associated with email {email}")

    usr = usr_rep.json()

    return models.User(
        usr["name"], usr["email"], usr["modulus"], usr["pub_exp"], '', usr["id"]
    )


def trap(func) -> object:
    """
    Decorator to handle errors on these functions
    """

    def inner(*args, **kwargs):
        try:
            func(*args, **kwargs)

        except AuthError as ae:
            click.secho("Authorisation Error; aborting...", fg="red")
            click.secho(ae, fg='red')

        except InvalidResponseError as nre:
            click.secho(
                f"Could not find requested resource on servers; aborting...", fg="yellow"
            )
            click.secho(nre, fg='red')

    return inner
