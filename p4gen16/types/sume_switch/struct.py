#!/usr/bin/env python3
'''
P4 sume_switch specific structs
'''
from ..struct import Struct, StructField

# pylint: disable=invalid-name
digest = Struct('digest_data_t', fields=[StructField('bit<80>', 'unused')])
