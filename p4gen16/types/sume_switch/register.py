#!/usr/bin/env python3
'''
sume_switch register operations
'''
# XXX currently only RW externs supported
# Read /wiki/RW-Extern-Function for details.
import math
from ..templateable import Templateable
from ..statement import Statement

class RegisterDeclaration(Templateable):
    ''' A sume_switch register declaration. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, name, ewidth=8, size=1, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.width = ewidth
        self.size = size

def declare(name, width=8, size=1):
    ''' Declares a new register. '''
    # XXX determine width x for register index (has type bit<x>)
    size = int(math.ceil(math.log(size, 2)))
    return RegisterDeclaration(name, ewidth=width, size=size, target='sume_switch')

def read(name, index, store):
    ''' Read from a register and store the result. '''
    return _rw(name, index, store, _write=False)

def write(name, index, store):
    ''' Write to a register. '''
    return _rw(name, index, store, _write=True)

def _rw(name, index, store, _write=False):
    ''' Read from register (and store result) or write to register. '''
    # XXX case write of True -> '8w1' == REG_WRITE; False -> '8x0' == REG_READ
    instruction = '{register}_reg_rw({position}, {variable}, 8w{operation:b}, {variable})'.format(
        register=name,
        position=index,
        operation=_write,
        variable=store,
    )
    return Statement(instruction, target='sume_switch')
