#!/usr/bin/env python3
'''
Common rule interface.
'''
from ..rule import Rules


def make_rules(target, size=None):
    ''' Points to the right template for each target. '''
    files = {
        'v1model': 'rules',
        'sume_switch': 'commands',
    }

    if size:
        return Rules('{0}_{1}.txt'.format(files[target], size), target=target)
    return Rules('{0}.txt'.format(files[target]), target=target)
