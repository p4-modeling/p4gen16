#!/usr/bin/env python3
'''
P4 statement type
'''
from .templateable import Templateable

class Statement(Templateable):
    ''' A statement. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, statement, **kwargs):
        super().__init__(**kwargs)
        if not isinstance(statement, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=statement.__class__.__name__))
        self.statement = statement

class Instantiation(Statement): # pylint: disable=too-few-public-methods
    ''' An instantiation. (Restricted declaration.) '''
    # XXX relaxed instantiation definition

class Define(Statement): # pylint: disable=too-few-public-methods
    ''' A define statement. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, name, statement, **kwargs):
        super().__init__(statement, **kwargs)
        if not isinstance(name, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=name.__class__.__name__))
        if not isinstance(statement, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=statement.__class__.__name__))
        self.name = name
        self.statement = statement

class ApplyTable(Statement):
    ''' Apply a table '''
    def __init__(self, tbl, **kwargs):
        from .table import Table
        if not isinstance(tbl, Table):
            raise TypeError('{that} is not an instance of Table'.format(
                that=tbl.__class__.__name__))
        super().__init__(tbl.name + '.apply()', **kwargs)

    def _template_name(self):
        return 'Statement' + self._jinja2_suffix

class ModifyHeader(Statement):
    ''' Modify a header value'''
    def __init__(self, field, value, **kwargs):
        from .header import HeaderField
        if not isinstance(field, HeaderField):
            raise TypeError('{that} is not an instance of HeaderField'.format(
                that=field.__class__.__name__))
        super().__init__('h.' + field.parent.name + '.' + field.name + ' = ' + str(value), **kwargs)

    def _template_name(self):
        return 'Statement' + self._jinja2_suffix

class ModifyMeta(Statement):
    ''' Modify a meta value'''
    def __init__(self, field, value, **kwargs):
        from .struct import StructField
        if not isinstance(field, StructField):
            raise TypeError('{that} is not an instance of StructField'.format(
                that=field.__class__.__name__))
        super().__init__(field.parent + '.' + field.name + ' = ' + str(value), **kwargs)

    def _template_name(self):
        return 'Statement' + self._jinja2_suffix

class SetHeaderValid(Statement):
    ''' set a header valid '''
    def __init__(self, hdr, **kwargs):
        from .header import Header
        if not isinstance(hdr, Header):
            raise TypeError('{that} is not an instance of str'.format(
                that=hdr.__class__.__name__))
        super().__init__('h.' + hdr.name + '.setValid()', **kwargs)

    def _template_name(self):
        return 'Statement' + self._jinja2_suffix
