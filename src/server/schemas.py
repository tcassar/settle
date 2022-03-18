# coding=utf-8

from marshmallow import Schema, fields, post_load

import models  # type: ignore


class UserSchema(Schema):
    name = fields.Str()
    email = fields.Email()
    modulus = fields.Str()
    pub_exp = fields.Str()
    password = fields.Str()

    @post_load
    def make_user(self, data, **kwargs):
        return models.User(**data)


class TransactionSchema(Schema):
    ...


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
