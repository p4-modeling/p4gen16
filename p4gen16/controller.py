#!/usr/bin/env python3
'''
P4 controller type
'''
from .types.templateable import Templateable

class Controller(Templateable):
    ''' A program. '''
    def __init__(self, program, sub_target, skip_filling_tables=False, egress_port=0, **kwargs):
        super().__init__(target=program.target, sub_target=sub_target, suffix='.j2', **kwargs)

        self.tables = program.get_main_pipeline().tables
        self.skip_filling_tables = skip_filling_tables
        self.egress_port = egress_port
