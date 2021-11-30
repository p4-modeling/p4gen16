#!/usr/bin/env python3
'''
P4 target rule types
'''
from ..program import Program
from .templateable import Templateable

class Test(Templateable):
    ''' Fill in a test template. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, file, feature, program, **kwargs):
        super().__init__(**kwargs)
        if not isinstance(file, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=file.__class__.__name__))
        if not isinstance(feature, str):
            raise TypeError('{that} is not an instance of str'.format(
                that=feature.__class__.__name__))
        if not isinstance(program, Program):
            raise TypeError('{that} is not an instance of Program'.format(
                that=program.__class__.__name__))
        self.file = file
        self.feature = feature
        self.program = program

    def _template_name(self):
        return self.file
