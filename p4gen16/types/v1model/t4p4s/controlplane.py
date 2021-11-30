#!/usr/bin/env python3
'''
P4 v1model t4p4s controlplane type
'''
from ....types.templateable import Templateable

class ControlPlane(Templateable):
    ''' A t4p4s controlplane.c.py type. '''
    def __init__(self, program, sub_target, egress_port=0, action=None, **kwargs):
        super().__init__(target=program.target, sub_target=sub_target, suffix='.j2', 
                         delimiter='c', **kwargs)

        self.tables = program.get_main_pipeline().tables
        self.egress_port = egress_port
        if self.tables:
            self.action = [ac for ac in self.tables[0].actions if ac.name == action[0]][0]

    def _template_name(self):
        return self.__class__.__name__ + self._jinja2_suffix
