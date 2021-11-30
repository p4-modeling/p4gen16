#!/usr/bin/env python3
'''
P4 action type
'''
from .templateable import Templateable
from .parameter import Parameter
from .statement import Statement

class Action(Templateable):
    ''' An action. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, name, parameters=None, statements=None, **kwargs):
        super().__init__(**kwargs)
        if not isinstance(name, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=name.__class__.__name__))
        self.name = name
        if not parameters:
            parameters = []
        for parameter in parameters:
            if not isinstance(parameter, Parameter):
                raise TypeError('{that} is not an instance of Parameter'.format(
                    that=parameter.__class__.__name__))
        self.parameter = parameters
        if not statements:
            statements = []
        for statement in statements:
            if not isinstance(statement, Statement):
                raise TypeError('{that} is not an instance of Statement'.format(
                    that=statement.__class__.__name__))
        self.statements = statements
