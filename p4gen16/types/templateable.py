#!/usr/bin/env python3
'''
P4 types
'''
import os.path
import jinja2
import logging

# jinja2 wrapper class
class Templateable():
    ''' Jinja2 powered __str__ implementations. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, module='p4gen16', target=None, sub_target=None, suffix='.p4.j2',
                 delimiter='default'):
        self._jinja2_suffix = suffix
        self._jinja2_module = module
        if not target:
            target = 'default'
        if sub_target:
            target = '/'.join([target, sub_target])
        self._jinja2_templates = target
        self.delimiter = delimiter

        self.log = logging

    def _template_name(self):
        return self.__class__.__name__ + self._jinja2_suffix

    def __str__(self):
        filename = self._template_name()
        _loader = jinja2.ChoiceLoader([
            jinja2.PackageLoader(self._jinja2_module, os.path.join(
                'template', self._jinja2_templates)),
            jinja2.PackageLoader(self._jinja2_module, os.path.join(
                'template', 'default')),
            ])

        delim = {}
        if self.delimiter == 'default':
            delim['bs'] = '{%'
            delim['be'] = '%}'
            delim['vs'] = '{{'
            delim['ve'] = '}}'
        elif self.delimiter == 'c':
            delim['bs'] = '@@'
            delim['be'] = '@@'
            delim['vs'] = '@='
            delim['ve'] = '=@'
        else:
            self.log.fatal('unknown delimiter: %s', self.delimiter)

        _env = jinja2.Environment(
            line_statement_prefix='#%',
            loader=_loader,
            block_start_string=delim['bs'],
            block_end_string=delim['be'],
            variable_start_string=delim['vs'],
            variable_end_string=delim['ve']
        )
        _env.filters['drop'] = _sequence_drop
        _env.filters['safe_first'] = _sequence_safe_first
        template = _env.get_template(filename)
        return template.render(this=self) # XXX cannot pass self as self

    def _id(self):
        ''' Allows no-op getattr calls. '''
        return self

def _sequence_safe_first(iterable, default=None):
    ''' Return head of iterable or default, if iterable is empty. '''
    if iterable is None or isinstance(iterable, jinja2.Undefined):
        return default
    try:
        return next(iterable)
    except StopIteration:
        return default

def _sequence_drop(iterable, i=1):
    ''' Drop first i elements from iterable. '''
    if iterable is None or isinstance(iterable, jinja2.Undefined):
        yield iterable
    # avoid `iterable[i:]` - would require isinstance(iterable, list)
    for j, element in enumerate(iterable, start=1):
        if j > i:
            yield element
