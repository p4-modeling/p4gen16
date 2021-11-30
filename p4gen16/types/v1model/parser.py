'''
parser for v1model
'''

from ..parser import Parser
from ..parameter import Parameter

class V1ModelParser(Parser):
    ''' A v1model parser. '''
    def __init__(self, **kwargs):
        kwargs['target'] = 'v1model'
        kwargs['parameters'] = [
            Parameter('packet_in', 'p', target='v1model'),
            Parameter('out headers', 'h', target='v1model'),
            Parameter('inout metadata', 'meta', target='v1model'),
            Parameter('inout standard_metadata_t', 'v1model_metadata', target='v1model'),
        ]

        super().__init__(**kwargs)

    def _template_name(self):
        return 'Parser' + self._jinja2_suffix
