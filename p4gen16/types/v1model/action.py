#!/usr/bin/env python3
'''
v1model actions
'''
from ..action import Action
from ..parameter import Parameter
from ..statement import Statement

# pylint: disable=invalid-name
drop = Action('drop', statements=[
    Statement('mark_to_drop()', target='v1model'),
    #Statement('standard_metadata.egress_spec = 9w2', target='v1model'),
])

set_egress_port = Action('set_egress_port', parameters=[
    Parameter('bit<9>', 'egress_spec', size=9),
], statements=[
    Statement('standard_metadata.egress_spec = egress_spec', target='v1model'),
])

def set_fixed_egress_port(port):
    return Action('set_fixed_egress_port', parameters=[
    ], statements=[
        Statement('standard_metadata.egress_spec = {}'.format(port), target='v1model'),
    ])

def scale_action_data(port, num):
    return Action(
        'scale_action_data', 
        parameters=[Parameter('bit<8>', 'data_{:03}'.format(i), size=8) for i in range(num)],
        statements=[
            Statement('standard_metadata.egress_spec = {}'.format(port), target='v1model'),
    ])
