"""Automatically map SQLAlchemy fields to schema nodes."""

import colander
import sqlalchemy
import enum
from collections import OrderedDict


from websauna.compat.typing import Union
from websauna.compat.typing import Iterable


def type_map(sa)
    pass



def default_mappers = OrderedDict([
    ("bool", type_map(sqlalchemy.Boolean, colander.Boolean)),
])


class AllFields:
    """Market class that all fields should be included"""
    pass




def deferred_auto_node_argument(name, options):

    @colander.deferred
    def inner():
        pass

    return inner


def colander_auto_node(name: str, options: Optional[dict]) -> colander.SchemaNode:

    arguments = [
        "typ",
        "missing",
        "name",
        "description",
        "validator",
        "default",
        "widget"
    ]

    kwargs = {arg: deferred_auto_node_argument(arg, options) for arg in arguments}

    if options:
        kwargs.update(options)

    return colander.SchemaNode(**kwargs)


def generate_placeholder(schema, name):
    setattr(schema, name, colander_auto_node(name))


def discover_model_fields(schema: colander.Schema, model: type, fields:Union[Iterable, AllFields]=AllFields()):
    """Iterate over SQLAlchemy model fields and add schema placeholders."""

    inspector = sqlalchemy.inspect(model)

    def match_by_name(column):
        if isinstance(fields, AllFields):
            return True
        else:
            column.name in fields

    for column in inspector.attrs:
        if match_by_name(column):
            generate_placeholder(schema, name)




