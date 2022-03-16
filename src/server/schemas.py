# coding=utf-8

from marshmallow import Schema, fields


class UserSchema(Schema):
    name = fields.Str()
    email = fields.Email()
    modulus = fields.Str()
    pub_exp = fields.Str()


class TransactionSchema(Schema):
    ...


class GroupSchema(Schema):
    ...
