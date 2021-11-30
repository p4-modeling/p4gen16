#!/usr/bin/env python3
'''
P4 table types
'''
from .templateable import Templateable
from .header import Header, HeaderField
from .action import Action

class TableKey(Templateable):
    ''' A table key. '''
    # pylint: disable=too-few-public-methods
    _types = ['exact', 'lpm', 'ternary', 'NoAction']
    def __init__(self, header, field, match_kind, **kwargs):
        super().__init__(**kwargs)
        if not isinstance(header, Header):
            raise TypeError('{that} is not an instance of Header'.format(
                that=header.__class__.__name__))
        if not isinstance(field, HeaderField):
            raise TypeError('{that} is not an instance of HeaderField'.format(
                that=field.__class__.__name__))
        if not isinstance(match_kind, str):
            raise TypeError('{that} is not a valid match kind'.format(
                that=match_kind.__class__.__name__))
        if match_kind not in self._types:
            self.log.warn('Match kind "{it}" is non-standard and might be unsupported.',
                          it=match_kind)
        self.header = header
        self.field = field
        self.match_kind = match_kind

class Table(Templateable):
    ''' A table. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, name, keys=None, actions=None, size=None, default_action=None,
                 **kwargs):
        super().__init__(**kwargs)
        if not isinstance(name, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=name.__class__.__name__))
        self.name = name

        if not keys:
            keys = []
        for key in keys:
            if not isinstance(key, TableKey):
                raise TypeError('{that} is not an instance of TableKey'.format(
                    that=key.__class__.__name__))
        self.keys = keys

        if not actions:
            actions = []
        for action in actions:
            if not isinstance(action, Action):
                raise TypeError('{that} is not an instance of Action'.format(
                    that=action.__class__.__name__))
        self.actions = actions

        if not isinstance(size, int):
            raise TypeError('size is not an instance of int')
        self.size = size

        if not default_action:
            default_action = 'NoAction'
        if not isinstance(default_action, Action):
            raise TypeError('{that} is not an instance of Action'.format(
                that=default_action.__class__.__name__))
        if default_action not in actions:
            warnings.warn('Table "{name}": default action not in actions list'.format(
                name=name))
        self.default_action = default_action
