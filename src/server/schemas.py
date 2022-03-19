# coding=utf-8

from marshmallow import Schema, fields, post_load

import models  # type: ignore
import src.transactions.transaction


class UserSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    email = fields.Email()
    modulus = fields.Str()
    pub_exp = fields.Str()
    password = fields.Str()

    @post_load
    def make_user(self, data, **kwargs):
        return models.User(**data)


class GroupSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    password = fields.Str()

    @post_load
    def make_group(self, data, **kwargs):
        return models.Group(**data)


class GroupLinkSchema(Schema):
    id = fields.Int()
    group_id = fields.Int()
    usr_id = fields.Int()

    @post_load
    def make_group_link(self, data, **kwargs):
        return models.GroupLink(**data)


class GroupListSchema(Schema):
    groups = fields.List(fields.Nested(GroupSchema()))

    @post_load
    def make_group_list(self, data, **kwargs):
        return models.GroupList(**data)


# Transaction schemas


class TransactionSchema(Schema):
    src = fields.Int()
    dest = fields.Int()
    amount = fields.Int()
    src_pub = fields.Str()
    dest_pub = fields.Str()
    ID = fields.Int()
    msg = fields.Str()
    time = fields.DateTime()
    signatures = fields.Dict()
    group = fields.Int()

    @post_load
    def make_group_list(self, data, **kwargs):
        return src.transactions.transaction.Transaction(**data)
