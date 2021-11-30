#!/usr/bin/env python3
'''
sume_switch related types
'''
from ..control import ControlFlow, ControlDeparse
from ..parameter import Parameter

class SumeSwitchControlFlow(ControlFlow):
    ''' A sume_switch instance of ControlFlow. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, name, **kwargs):
        kwargs['target'] = 'sume_switch'
        kwargs['parameters'] = [
            Parameter('inout headers', 'h', target=kwargs['target']),
            Parameter('inout metadata', 'meta', target=kwargs['target']),
            Parameter('inout digest_data_t', 'digest_data', target=kwargs['target']),
            Parameter('inout sume_metadata_t', 'sume_metadata', target=kwargs['target']),
        ]
        super().__init__(name, **kwargs)

class Pipeline(SumeSwitchControlFlow):
    ''' A sume_switch pipeline control block. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, **kwargs):
        super().__init__('pipeline', **kwargs)

class SumeSwitchControlDeparse(ControlDeparse):
    ''' A sume_switch deparse control block. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, header, **kwargs):
        kwargs['target'] = 'sume_switch'
        parameter = [
            Parameter('packet_out', 'p', target=kwargs['target']),
            Parameter('in headers', 'h', target=kwargs['target']),
            Parameter('in metadata', 'meta', target=kwargs['target']),
            Parameter('inout digest_data_t', 'digest_data', target=kwargs['target']),
            Parameter('inout sume_metadata_t', 'sume_metadata', target=kwargs['target']),
        ]
        super().__init__(parameter, header, **kwargs)
