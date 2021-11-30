#!/usr/bin/env python3
'''
P4 types
'''
from ..control import ControlFlow, ControlDeparse, ControlBlock
from ..parameter import Parameter
from ..templateable import Templateable
from ..statement import Statement

class ControlChecksum(ControlBlock):
    ''' A v1model function to update a header's checksum. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, enable, action='verify', field=None, name=None, verify=None,
                 checked_fields=None, algorithm='HashAlgorithm.csum16', **kwargs):
        # pylint: disable=too-many-arguments
        # XXX written for v1model, might be reusable
        kwargs['target'] = 'v1model'
        super().__init__(**kwargs)
        self.enable = enable
        self.action = action
        self.field = field
        if not name:
            name = '_'.join(['checksum', action])
        self.name = name
        self.algorithm = algorithm
        self.verify = verify
        if not checked_fields:
            checked_fields = []
        self.checked_fields = checked_fields

    def _template_name(self):
        return 'ControlChecksum' + self._jinja2_suffix

class ChecksumVerify(ControlChecksum):
    ''' A v1model function to verify a header's checksum. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, enable, **kwargs):
        super().__init__(enable, action='verify', **kwargs)

class ChecksumUpdate(ControlChecksum):
    ''' A v1model function to update a header's checksum. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, enable, **kwargs):
        super().__init__(enable, action='update', **kwargs)

class V1ModelControlFlow(ControlFlow):
    ''' A v1model instance of ControlFlow. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, name, **kwargs):
        kwargs['target'] = 'v1model'
        kwargs['parameters'] = [
            Parameter('inout headers', 'h', target='v1model'),
            Parameter('inout metadata', 'meta', target='v1model'),
            Parameter('inout standard_metadata_t', 'standard_metadata', target='v1model'),
        ]
        super().__init__(name, **kwargs)

class Ingress(V1ModelControlFlow):
    ''' A v1model ingress control block. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, sequence=None, **kwargs):
        if not sequence:
            sequence = []
        super().__init__('ingress', sequence=sequence, **kwargs)

class Egress(V1ModelControlFlow):
    ''' A v1model egress control block. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, **kwargs):
        super().__init__('egress', **kwargs)

class V1ModelControlDeparse(ControlDeparse):
    ''' A v1model deparse control block. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, header, **kwargs):
        kwargs['target'] = 'v1model'
        parameter = [
            Parameter('packet_out', 'p', target=kwargs['target']),
            Parameter('in headers', 'h', target=kwargs['target']),
        ]
        super().__init__(parameter, header, **kwargs)

def generate_controls():
    controls = {}
    controls['verify'] = ChecksumVerify(
        False,
        target='v1model',
    )
    controls['ingress'] = Ingress(
        target='v1model',
    )
    controls['egress'] = Egress(
        target='v1model',
    )
    controls['update'] = ChecksumUpdate(
        False,
        target='v1model',
    )
    return controls
