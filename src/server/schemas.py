# coding=utf-8

from models import *
from marshmallow import Schema, fields, post_load


class UserSchema(Schema):
    name = fields.Str()
    email = fields.Email()
    modulus = fields.Str()
    pub_exp = fields.Str()
    password = fields.Str()

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)


class TransactionSchema(Schema):
    ...


class GroupSchema(Schema):
    name = fields.Str()
    password = fields.Str()

    @post_load
    def make_group(self, data, **kwargs):
        return Group(**data)

