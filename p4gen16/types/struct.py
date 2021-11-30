#!/usr/bin/env python3
'''
P4 struct types
'''
import collections
from .templateable import Templateable
from .header import Header

class StructField(Templateable):
    ''' A struct field. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, type_, name, **kwargs): # pylint: disable=redefined-builtin
        super().__init__(**kwargs)
        if not isinstance(type_, str) and not isinstance(type_, Header):
            raise TypeError('{that} is not an instance of str or Header'.format(
                that=type_.__class__.__name__))
        if not isinstance(name, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=name.__class__.__name__))
        self.name = name
        self.header = None
        if isinstance(type_, str):
            self.type = type_
        else:
            self.header = type_
            self.type = type_.type
            self.name = name
        self.parent = None

    def set_parent(self, parent):
        if not isinstance(parent, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=parent.__class__.__name__))
        self.parent = parent

class Struct(Templateable):
    ''' A struct. '''
    def __init__(self, name, fields=None, **kwargs):
        super().__init__(**kwargs)
        if not isinstance(name, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=name.__class__.__name__))
        self.name = name
        self._fields = collections.OrderedDict()
        if fields:
            self.fields = fields

    @property
    def fields(self): # pylint: disable=missing-docstring
        return self._fields.values()

    def get_fields(self): # pylint: disable=missing-docstring
        return self._fields.values()

    @fields.setter
    def fields(self, fields):
        for field in fields:
            self.add_field(field)

    def add_field(self, field):
        ''' Add a new field to this struct. '''
        if not isinstance(field, StructField):
            raise TypeError('{that} is not an instance of StructField'.format(
                that=field.__class__.__name__))
        self._fields[field.name] = field
