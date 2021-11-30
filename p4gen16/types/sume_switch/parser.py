'''
parser for sume switch
'''

from ..parser import Parser
from ..parameter import Parameter

class SumeSwitchParser(Parser):
    ''' A sume_switch parser. '''
    def __init__(self, **kwargs):
        kwargs['target'] = 'sume_switch'
        kwargs['parameters'] = [
            Parameter('packet_in', 'p', target='sume_switch'),
            Parameter('out headers', 'h', target='sume_switch'),
            Parameter('out metadata', 'meta', target='sume_switch'),
            Parameter('out digest_data_t', 'digest_data', target='sume_switch'),
            Parameter('inout sume_metadata_t', 'sume_metadata', target='sume_switch'),
        ]
        super().__init__(**kwargs)

    def _template_name(self):
        return 'Parser' + self._jinja2_suffix
