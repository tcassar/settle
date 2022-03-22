# coding=utf-8
import click
import requests

from src.crypto import hashes as hasher
from src.server import models as models, schemas as schemas

SERVER = "http://127.0.0.1:5000/"


class AuthError(Exception):
    ...


class ResourceNotFoundError(Exception):
    """Resource could not be found on the server (404)"""


class InvalidResponseError(Exception):
    """Requested action was understood but not allowed (403 / 409)"""


class ServerError(Exception):
    ...


class NoChanges(Exception):
    ...


def hash_password(password) -> str:
    return str(hasher.Hasher(password.encode(encoding="utf8")).digest().h)


def url(query: str) -> str:
    return SERVER + query


def validate_response(response: requests.Response) -> None:
    """Raises InvalidResponseError if response is invalid"""
    e = response.text
    if response.status_code == 404:
        raise ResourceNotFoundError(
            f"ERROR: Could not find requested resource on server, {e}"
        )
    elif response.status_code == 409:
        raise ResourceNotFoundError(
            f"The resource that you are trying to create already exists, {e}"
        )
    elif response.status_code == 403:
        raise ResourceNotFoundError(f"This action was not allowed by the server, {e}")
    elif response.status_code // 100 == 5:
        raise ServerError(f"Error {response.status_code}: {response.json()['message']}")
    elif response.status_code == 202:
        raise NoChanges(response.text)


def _auth(resource: str, password: str):
    usr_response: requests.Response = requests.get(url(resource))
    try:
        validate_response(usr_response)
    except ResourceNotFoundError:
        raise ResourceNotFoundError(
            f"No {resource.split('/')[0]} with identifier {resource.split('/')[1]} found"
        )

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
    except ResourceNotFoundError:
        raise ResourceNotFoundError(f"No user associated with email {email}")

    usr = usr_rep.json()

    return models.User(
        usr["name"], usr["email"], usr["modulus"], usr["pub_exp"], "", usr["id"]
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
            click.secho(ae, fg="red")

        except ResourceNotFoundError as nre:
            click.secho(
                f"{nre}",
                fg="yellow",
            )

        except ServerError as se:
            click.secho(se, fg="red")

        except NoChanges as nc:
            click.secho(f"No changes were made\n{nc}", fg="yellow")

        except requests.exceptions.ConnectionError:
            click.secho('ERROR: Could not connect to server', fg='red')

    return inner


def show_transactions(transactions_data: requests.Response):
    try:
        unverified_running = 0.0
        verified_running = 0.0
        for pretty in transactions_data.json()["src_list"]:

            click.secho(
                f'\nYou owe {pretty["other"]} £{round(pretty["amount"] / 100, 2):02}',
                fg="yellow",
            )

            click.secho(
                f'\nReference: {pretty["time"]}'
                + f'\nAgreed upon at {pretty["reference"]}'
                + f'ID: {pretty["id"]}'
            )

            if pretty["verified"] == 1:
                click.secho("Verified", fg="green")
                verified_running += pretty["amount"]
            else:
                click.secho("Unverified", fg="red")
                unverified_running += pretty["amount"]

        for pretty in transactions_data.json()["dest_list"]:
            click.secho(
                f'\n{pretty["other"]} owes you £{round(pretty["amount"] / 100, 2):02}',
                fg="yellow",
            )

            click.secho(
                f'\nReference: {pretty["time"]}'
                + f'\nAgreed upon at {pretty["reference"]}'
                + f'ID: {pretty["id"]}'
            )

            if pretty["verified"] == 1:
                click.secho("Verified", fg="green")
                verified_running -= pretty["amount"]
            else:
                click.secho("Unverified", fg="red")
                unverified_running -= pretty["amount"]

        click.echo("----------\n")

        unverified_running = round(unverified_running / 100, 2)
        verified_running = round(verified_running / 100, 2)

        if verified_running > 0:
            click.secho(f"You owe a total of £{verified_running:02}", fg="red")
        elif verified_running < 0:
            click.secho(
                f"You are owed a total of £{verified_running * -1 :02}", fg="blue"
            )
        else:
            click.secho(f"You owe and are owed nothing; all debts settled", fg="green")

        if unverified_running > 0:
            click.secho(
                f"Your unverified totals => you owe £{unverified_running:02}",
                fg="yellow",
            )
        elif unverified_running < 0:
            click.secho(
                f"Your unverified totals => you are owed £{unverified_running * -1 :02}",
                fg="yellow",
            )
        else:
            click.secho(f"Your unverified totals => all debts settled", fg="yellow")

    except TypeError as te:
        if transactions_data.json() is None:
            click.secho("No open transactions", fg="green")
            click.echo(te)


def show_group(transaction_data: requests.Response):
    schema = schemas.PrettyListSchema()
    pretty_list: models.PrettyList = schema.make_pretty_list(transaction_data.json())
    print(pretty_list)
