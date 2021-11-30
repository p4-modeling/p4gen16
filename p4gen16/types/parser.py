#!/usr/bin/env python3
'''
P4 types
'''
import collections
import warnings
from .parameter import Parameter
from .templateable import Templateable

class ParserStateTransition(Templateable):
    ''' A parser state transition. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, expr, next, **kwargs): # pylint: disable=redefined-builtin
        super().__init__(**kwargs)
        if not isinstance(expr, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=expr.__class__.__name__))
        if not isinstance(next, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=next.__class__.__name__))
        self.expr = expr
        self.next = next

class ParserState(Templateable):
    ''' A parser state. '''
    def __init__(self, header, field, transitions=None, is_start=False,
                 extract_extra=None, extract_extra_after=None, **kwargs):
        super().__init__(**kwargs)
        if not isinstance(field, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=field.__class__.__name__))
        if not isinstance(header, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=header.__class__.__name__))
        self.header = header
        self.field = field
        if is_start:
            self.name = 'start'
        else:
            self.name = 'parse_' + self.header
        self.is_end = not transitions
        self._transitions = collections.OrderedDict()
        if transitions:
            self.transitions = transitions
        self.extract_extra = extract_extra
        self.extract_extra_after = extract_extra_after

    @property
    def transitions(self): # pylint: disable=missing-docstring
        return self._transitions.values()

    @transitions.setter
    def transitions(self, transitions):
        self._transitions = collections.OrderedDict()
        for transition in transitions:
            self.add_transition(transition)

    def add_transition(self, transition):
        ''' Add a new transition to this parser state. '''
        if not isinstance(transition, ParserStateTransition):
            raise TypeError('{that} is not an instance of ParserStateTransition'.format(
                that=transition.__class__.__name__))
        self._transitions[transition.expr] = transition

class Parser(Templateable):
    ''' A parser. '''
    def __init__(self, parameters=None, states=None,
                 name='parse', **kwargs):
        # pylint: disable=too-many-arguments
        super().__init__(**kwargs)
        self._states = collections.OrderedDict()
        if states:
            self.states = states
        self.name = name

        if not parameters:
            parameters = []
        self.parameters = parameters

    @property
    def states(self): # pylint: disable=missing-docstring
        return self._states.values()

    @states.setter
    def states(self, states):
        self._states = collections.OrderedDict()
        for state in states:
            self.add_state(state)

    def add_state(self, state):
        ''' Add a new state to this parser. '''
        if not isinstance(state, ParserState):
            raise TypeError('{that} is not an instance of ParserState'.format(
                that=state.__class__.__name__))
        self._states[state.header] = state

def make_parser(*args, **kwargs):
    ''' Returns a parser for the given target (or a KeyError if the target is
        unknown).
    '''
    from .v1model.parser import V1ModelParser
    from .sume_switch.parser import SumeSwitchParser
    options = {
        'v1model': V1ModelParser,
        'v1model_t4p4s': V1ModelParser,
        'sume_switch': SumeSwitchParser,
    }
    parser = options[kwargs['target']]
    return parser(*args, **kwargs)
