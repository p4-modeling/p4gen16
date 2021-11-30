#!/usr/bin/env python3
'''
v1model register operations
'''
from ..statement import Statement

def declare(name, ewidth=8, size=1):
    ''' Declares a new register. '''
    return Statement('register<bit<%d>>%s(%d)' % (ewidth, name, size), target='v1model')

def read(name, index, store):
    ''' Read from a register and store the result. '''
    return _rw(name, index, store, 'read')

def write(name, index, store):
    ''' Write to a register. '''
    return _rw(name, index, store, 'write')

def _rw(name, index, store, operation):
    instruction = '{register}.{operation}({variable}, {position})'.format(
        register=name,
        position=index,
        operation=operation,
        variable=store,
    )
    return Statement(instruction, target='v1model')
