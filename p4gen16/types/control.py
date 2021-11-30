#!/usr/bin/env python3

'''
P4 types
'''

import collections
from .action import Action
from .parameter import Parameter
from .templateable import Templateable
from .statement import Statement, Instantiation
from .table import Table

class Control(Templateable):
    ''' A control section. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, declarations=None, **kwargs):
        super().__init__(**kwargs)

    def add_declaration(self, name, decl):
        ''' Add a new declaration to this control. '''
        if not isinstance(decl, ControlBlock):
            raise TypeError('{that} is not an instance of ControlBlock'.format(
                that=decl.__class__.__name__))
        setattr(self, name, decl)

class ControlBlock(Templateable):
    ''' A control block. '''
    pass

class ControlFlow(ControlBlock):
    ''' A control block. '''
    # pylint: disable=too-few-public-methods
    _types = {
        'parameters': Parameter,
        'instantiations': Instantiation,
        'actions': Action,
        'tables': Table,
        'sequence': Statement,
    }
    def __init__(self, name, parameters=None, instantiations=None, actions=None,
                 tables=None, sequence=None, **kwargs):
        # pylint: disable=too-many-arguments
        super().__init__(**kwargs)
        self.name = name
        if not parameters:
            parameters = []
        self.parameters = parameters
        if not instantiations:
            instantiations = []
        self.instantiations = instantiations
        if not actions:
            actions = []
        self.actions = actions
        if not tables:
            tables = []
        self.tables = tables
        if not sequence:
            sequence = []
        self.sequence = sequence

        for value in self._types:
            for entry in getattr(self, value):
                if not isinstance(entry, self._types[value]):
                    raise TypeError('{this} is not an instance of {that}'.format(
                        this=entry.__class__.__name__,
                        that=self._types[value].__name__))

    def _template_name(self):
        return 'ControlFlow' + self._jinja2_suffix

    def add_table(self, name, actions, keys, size=512, default_action=None):
        """ Tries to generate inhomogeneous tables """
        self.log.info('add_table(%s, [%s], [%s])', name, len(actions), len(keys))
        table = Table(
            name,
            keys=keys,
            actions=actions,
            size=size,
            default_action=default_action,
        )
        self.tables.append(table)
        return table

    def add_action(self, action):
        if not isinstance(action, self._types['actions']):
            raise TypeError('action is not an instance of Action')

        self.actions.append(action)

class ControlDeparse(ControlBlock):
    ''' A deparse control block. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, parameter, header, name='deparse', **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.parameter = parameter
        self.header = header

    def _template_name(self):
        return 'ControlDeparse' + self._jinja2_suffix

def make_deparser(*args, **kwargs):
    ''' Returns a parser for the given target (or a KeyError if unknown). '''
    # XXX cyclic import if global
    from .v1model import control as v1model
    from .sume_switch import control as sume_switch
    options = {
        'v1model': v1model.V1ModelControlDeparse,
        'sume_switch': sume_switch.SumeSwitchControlDeparse,
    }
    deparser = options[kwargs['target']]
    return deparser(*args, **kwargs)
