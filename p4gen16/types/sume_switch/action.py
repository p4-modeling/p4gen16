#!/usr/bin/env python3
'''
sume_switch actions
'''
from ..action import Action
from ..parameter import Parameter
from ..statement import Statement

# pylint: disable=invalid-name
drop = Action('drop', statements=[
    # XXX sume_metadata is defined only inside control blocks
    Statement('sume_metadata.dst_port = 0b00000000', target='sume_switch'),
    # FIXME removed to work around issues in add/rm header
#    Statement('sume_metadata.drop = 1', target='sume_switch'),
])

set_egress_port = Action('set_egress_port', parameters=[
    Parameter('port_t', 'port', target='sume_switch'),
], statements=[
    Statement('sume_metadata.dst_port = port', target='sume_switch'),
])
