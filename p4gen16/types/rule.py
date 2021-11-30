#!/usr/bin/env python3
'''
P4 target rule types
'''
import collections
import ipcalc
from .templateable import Templateable

class L3Rule(Templateable):
    ''' A layer 3 rule. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, address, port, table=0, match_type='exact', **kwargs):
        super().__init__(**kwargs)
        if not isinstance(address, ipcalc.IP):
            raise TypeError('{that} is not an instance of IP or Network'.format(
                that=address.__class__.__name__))
        if not isinstance(port, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=port.__class__.__name__))
        if not isinstance(address, ipcalc.Network):
            address = ipcalc.Network(address)
        if not isinstance(table, int):
            raise TypeError('{that} is not an instance of int'.format(
                that=table.__class__.__name__))
        if not isinstance(table, int):
            raise TypeError('{that} is not an instance of str'.format(
                that=match_type.__class__.__name__))

        self.address = address
        self.port = port
        self.table = table
        self.match_type = match_type

class TableRule(Templateable):
    '''A table rule'''
    # pylint: disable=too-few-public-methods
    def __init__(self, table_name, value, port, **kwargs):
        super.__init__(**kwargs)
        if not isinstance(table_name, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=table_name.__class__.__name__))
        if not isinstance(port, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=value.__class__.__name__))
        if not isinstance(value, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=port.__class__.__name__))

        self.port = port
        self.value = value
        self.table_name = table_name

class Rules(Templateable):
    ''' A set of rules. '''
    def __init__(self, file, l3_rules=None, table_rules=None, **kwargs):
        super().__init__(**kwargs)
        if not isinstance(file, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=file.__class__.__name__))
        self.file = file
        self._l3_rules = collections.OrderedDict()
        if l3_rules:
            self.l3_rules = l3_rules

        self._table_rules = collections.OrderedDict()
        if table_rules:
            self.table_rules = table_rules

    def _template_name(self):
        return self.file + '.j2'

    @property
    def l3_rules(self): # pylint: disable=missing-docstring
        return self._l3_rules.values()

    @property
    def table_rules(self): # pylint: disable=missing-docstring
        return self._table_rules.values()

    @l3_rules.setter
    def l3_rules(self, l3_rules):
        self._l3_rules = collections.OrderedDict()
        for rule in l3_rules:
            self.add_l3_rule(rule)

    @table_rules.setter
    def table_rules(self, table_rules):
        self._table_rules = collections.OrderedDict()
        for rule in table_rules:
            self.add_table_rule(rule)

    def add_l3_rule(self, rule):
        ''' Add a new rule for this target. '''
        if not isinstance(rule, L3Rule):
            raise TypeError('{that} is not an instance of L3Rule'.format(
                that=rule.__class__.__name__))
        self._l3_rules[str(rule.address)+str(rule.table)] = rule

    def add_table_rule(self, rule):
        ''' Add a new rule for this target. '''
        if not isinstance(rule, L3Rule):
            raise TypeError('{that} is not an instance of L3Rule'.format(
                that=rule.__class__.__name__))
        self._table_rules[str(rule.address)] = rule
