#!/usr/bin/env python3
'''
P4 common register actions.
'''
from ..v1model import register as v1model
from ..sume_switch import register as sume_switch

def declare(name, width=8, size=1, target=None):
    ''' Selects register declaration implementation based on target. '''
    declarations = {}
    # known architectures and their register declaration implementation:
    declarations['v1model'] = v1model.declare(name, width, size)
    declarations['sume_switch'] = sume_switch.declare(name, width, size)
    return declarations.get(target)

def read(name, index, store, target=None):
    ''' Read register, store it's result - target dependent implementation. '''
    reads = {}
    # known architectures and their register declaration implementation:
    reads['v1model'] = v1model.read(name, index, store)
    reads['sume_switch'] = sume_switch.read(name, index, store)
    return reads.get(target)

def write(name, index, store, target=None):
    ''' Write to register - target dependent implementation. '''
    writes = {}
    # known architectures and their register declaration implementation:
    writes['v1model'] = v1model.write(name, index, store)
    writes['sume_switch'] = sume_switch.write(name, index, store)
    return writes.get(target)
