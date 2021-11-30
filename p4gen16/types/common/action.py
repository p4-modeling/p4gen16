#!/usr/bin/env python3
'''
P4 common actions
'''
from .. import action
from .. import parameter
from .. import statement
from ..v1model import action as v1model
from ..sume_switch import action as sume_switch

def drop(target):
    ''' Selects action drop implementation based on target. '''
    actions = {}
    default = action.Action('drop')
    # known architectures and their drop implementation:
    actions['v1model'] = v1model.drop
    actions['sume_switch'] = sume_switch.drop
    return actions.get(target, default)

def set_id(target):
    ''' Selects action set_id implementation based on target. '''
    default = action.Action('set_id', parameters=[
        parameter.Parameter('bit<8>', 'identifier'),
    ], statements=[
        # XXX meta is defined only inside parser/control blocks
        statement.Statement('meta.id = identifier', target=target),
    ])
    return default

def set_egress_port(target):
    ''' Selects action set_egress_port implementation based on target. '''
    actions = {}
    default = action.Action('set_egress_port')
    # known architectures and their drop implementation:
    actions['v1model'] = v1model.set_egress_port
    actions['sume_switch'] = sume_switch.set_egress_port
    return actions.get(target, default)

def set_fixed_egress_port(target, port):
    ''' Selects action set_egress_port with fixed port,
    implementation based on target. '''
    actions = {}
    # known architectures and their drop implementation:
    actions['v1model'] = v1model.set_fixed_egress_port
    #actions['sume_switch'] = sume_switch.set_fixed_egress_port
    return actions.get(target)(port)

def scale_action_data(target, port, num):
    ''' Selects action scale_action_data with fixed port and num action datas,
    implementation based on target. '''
    actions = {}
    # known architectures and their drop implementation:
    actions['v1model'] = v1model.scale_action_data
    #actions['sume_switch'] = sume_switch.set_fixed_egress_port
    return actions.get(target)(port, num)
