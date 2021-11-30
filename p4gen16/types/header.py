#!/usr/bin/env python3
'''
P4 header types
'''
import collections
from .templateable import Templateable

class HeaderField(Templateable):
    ''' A header field. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, bits, name, **kwargs):
        super().__init__(**kwargs)
        if not isinstance(bits, int):
            raise TypeError('{that} is not an instance of int'.format(
                that=bits.__class__.__name__))
        if not isinstance(name, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=name.__class__.__name__))
        self.bits = bits
        self.required_bytes = self.bits // 8 + (1 if self.bits % 8 else 0)
        self.name = name
        self.parent = None

    def set_parent(self, parent):
        if not isinstance(parent, Header):
            raise TypeError('{that} is not an instance of Header'.format(
                that=parent.__class__.__name__))
        self.parent = parent

class Header(Templateable):
    ''' A header. '''
    def __init__(self, name, type=None, fields=None, **kwargs):
        # pylint: disable=redefined-builtin
        super().__init__(**kwargs)
        if not isinstance(name, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=name.__class__.__name__))
        self.name = name
        if not type:
            self.type = name + '_t'
        else:
            self.type = type
        self._fields = collections.OrderedDict()
        if fields:
            self.fields = fields

    @property
    def fields(self): # pylint: disable=missing-docstring
        return self._fields.values()

    @fields.setter
    def fields(self, fields):
        self._fields = collections.OrderedDict()
        for field in fields:
            self.add_field(field)

    def add_field(self, field):
        ''' Add a new field to this header. '''
        if not isinstance(field, HeaderField):
            raise TypeError('{that} is not an instance of HeaderField'.format(
                that=field.__class__.__name__))
        self._fields[field.name] = field
        field.set_parent(self)
