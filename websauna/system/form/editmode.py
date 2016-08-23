"""Describe different form edit modes."""

from enum import Enum


class EditMode(Enum):
    """Different edit modes for where a form can be."""

    #: Generate form for viewing contents (read-only)
    show = "show"

    #: Generated form for creating a new object
    add = "add"

    #: Generated form for editing an existing object
    edit = "edit"

