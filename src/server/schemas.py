# coding=utf-8

from models import User
from marshmallow import Schema, fields, post_load


class UserSchema(Schema):
    name = fields.Str()
    email = fields.Email()
    modulus = fields.Str()
    pub_exp = fields.Str()

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)

class TransactionSchema(Schema):
    ...


class GroupSchema(Schema):
    ...
