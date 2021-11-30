#!/usr/bin/env python3
'''
P4 parameter type
'''
from .templateable import Templateable

class Parameter(Templateable):
    ''' A parameter. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, type_, name, size=0, **kwargs): # pylint: disable=redefined-builtin
        super().__init__(**kwargs)
        if not isinstance(type_, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=type_.__class__.__name__))
        self.type = type_
        if not isinstance(name, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=name.__class__.__name__))
        self.name = name
        self.size = size
