#!/usr/bin/env python3
'''
Common test interface.
'''
from ..test import Test

def make_tests(feature, program, target):
    ''' Points to the right template for each target. '''
    files = {
        'sume_switch': 'gen_testdata.py',
    }
    return Test(files[target], feature, program, target=target)
