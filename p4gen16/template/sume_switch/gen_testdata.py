#!/usr/bin/env python2
'''
Test generated programs targeting sume_switch.
{#- This is a jinja2 template, but also a Python (2 or 3) script. #}
'''
import functools
import itertools
import logging
import operator

import scapy.layers.l2 as l2
import scapy.layers.inet as inet
import scapy.utils
from scapy.packet import Raw

# mutable variant of collections.namedtuple
import namedlist

# templatable globals
## SUME
NF_SRC = 1
NF_DST_GOOD = 0
NF_DST_BAD = 'drop'
## Ethernet
MAC0 = '00:00:00:00:00:00'
MAC1 = '00:00:00:00:00:01'
## IPv4
IP0 = '10.1.0.0' #src ip
IP1 = '10.1.0.1' #dest ip
## Generic
REPETITIONS = 2
FIELDS = 2
FIELD_SIZE = 1 # byte
# override defaults, if used as jinja2 template ('this' is defined)
#% if not this
''' # dummy case to start the doc string
#% else
REPETITIONS = {{ this.program.headers | length }}
# subtract number of non-generic header
REPETITIONS -= 2
if {{ this.program.headers | selectattr('name', 'equalto', 'offset') | list | length }} > 0:
    # offset header is defined
    REPETITIONS -= 1
# XXX assumes: third header is generic
FIELDS = {{ this.program.headers | drop(2) | safe_first(default=this.program.headers|first) | attr('fields') | length }}
# XXX assumes: field size is multiple of 8bit
FIELD_SIZE = {{ this.program.headers | drop(2) | safe_first(default=this.program.headers|first) | attr('fields') | first | attr('bits') }}
FIELD_SIZE = int(FIELD_SIZE / 8) # bit -> byte
# doc string comment hack end '''
#% endif

## scapy PCAP files
PCAP_RX = 'dst.pcap' # SUME->
PCAP_TX = 'src.pcap' # ->SUME
PCAP_NF_TX = 'nf{nr}_applied.pcap'
PCAP_NF_RX = 'nf{nr}_expected.pcap'
TUPLE_RX = 'Tuple_in.txt'
TUPLE_TX = 'Tuple_expect.txt'

# introduce "invalid" layers
class Invalid(object):
    '''
    Marks a layer as invalid. If a packet contains at least one invalid layer,
    the switch is expected to drop it.
    '''
    # pylint: disable=too-few-public-methods
    def __nonzero__(self):
        return False

class InvalidEther(Invalid, l2.Ether):
    ''' Invalid Ether '''
    pass
class InvalidIP(Invalid, inet.IP):
    ''' Invalid IP '''
    pass
class InvalidRaw(Invalid, Raw):
    ''' Invalid Raw packet '''
    pass

SumeTuple = namedlist.namedlist('SumeTuple', [ # pylint: disable=invalid-name
    'dma_q_size',

    'nf0_q_size',
    'nf1_q_size',
    'nf2_q_size',
    'nf3_q_size',

    'send_dig_to_cpu',

    'drop',

    'dst_port',
    'src_port',

    'pkt_len',
])
SUME_FIELD_LEN = SumeTuple(
    # *_size
    16, 16, 16, 16, 16,
    # send_dig_to_cpu & drop & *_port
    8, 8, 8, 8,
    # pkt_len
    16,
)
DigestTuple = namedlist.namedlist('DigestTuple', [ # pylint: disable=invalid-name
    'unused',
])
NF_PORT = {
    # Format:
    # * 2 bit per interface
    # * d bit: send to dma (of if no #)
    # * p bit: send to phy (of if no #)
    #    3 2 1 0
    #    dpdpdpdp
    0: 0b00000001,
    1: 0b00000100,
    2: 0b00010000,
    3: 0b01000000,
    'drop': 0b00000000,
}

def ethernet():
    ''' Returns a list of (in-)valid Ethernet instances. '''
    bad_mac = '00:00:00:00:00:02'
    valid = l2.Ether(
        src=MAC0,
        dst=MAC1,
    )
    # XXX parser accepts "invalid" addresses
    # TODO introduce different (i.e. more than one) "invalid"-states to fix this?
    wrong_dst = InvalidEther(
        src=MAC0,
        dst=bad_mac,
    )
    wrong_ethertype = InvalidEther(
        src=MAC0,
        dst=MAC1,
        type=0,
    )
    return [
        valid,
        wrong_ethertype,
    ]

def ipv4():
    ''' IPv4 packet generator. '''
    bad_addr = '10.1.1.1'
    valid = inet.IP(
        src=IP0,
        dst=IP1,
        proto=0x11,
    )
    # XXX parser accepts "invalid" addresses
    wrong_dst = InvalidIP(
        src=IP0,
        dst=bad_addr,
        proto=0x11,
    )
    wrong_proto = InvalidIP(
        src=IP0,
        dst=IP1,
        proto=0,
    )
    return [
        valid,
        wrong_proto,
    ]

def repeat_header(once, repetitions=REPETITIONS):
    ''' Repeat and reduce. '''
    if repetitions == 0:
        return InvalidRaw()
    return functools.reduce(lambda l, u: l / u, itertools.repeat(once, repetitions))

def generic():
    ''' Generic header generator. '''
    if REPETITIONS < 1:
        return None
    valid = repeat_header(Raw(
        load=('\x00' * FIELD_SIZE) * FIELDS,
    ))
    wrong_field_size = repeat_header(InvalidRaw(
        load=('\x00' * (FIELD_SIZE - 1)) * FIELDS,
    ))
    wrong_field_count = repeat_header(InvalidRaw(
        load=('\x00' * FIELD_SIZE) * int(FIELDS / 2), # FIXME issues w/ -1?
    ))
    wrong_repetition_count = repeat_header(InvalidRaw(
        load=('\x00' * FIELD_SIZE) * FIELDS,
    ), repetitions=int(REPETITIONS / 2)) # FIXME issues w/ -1?
    return [
        valid,
        wrong_field_size,
        wrong_field_count,
        wrong_repetition_count,
    ]

def offset():
    ''' Offset header generator. '''
    offset_size = 0
    has_offset = False
    # override defaults, if used as jinja2 template ('this' is defined)
    #% if not this
    ''' # dummy case to start the doc string
    #% else
    # check if last header in struct has name offset
    if {{ this.program.headers | selectattr('name', 'equalto', 'offset') | list | length }} > 0:
        has_offset = True
        offset_size = {{ this.program.headers | last | attr('fields') | first | attr('bits') }}
    # doc string comment hack end '''
    #% endif
    if not has_offset:
        return None
    # XXX assumes: field size is multiple of 8bit
    offset_size = int(offset_size / 8) # bit -> byte
    return [Raw(load='\x55' * offset_size)]

def tuple_lines(sume_tuples, length=None):
    ''' Converts a list of SumeTuple/DigestTuple into a list of binary strings '''
    for entry in sume_tuples:
        binary = []
        for field, value in iter(entry._asdict().items()):
            # convert value to binary with length as specified in length[field]
            as_binary = '{0:0%db}' % getattr(length, field)
            # append the value to the current line
            binary.append(as_binary.format(value))
        binary = ''.join(binary)
        # for each 4 bits (char) for each line (string):
        # read them as integer value with base 2, then format them to hexadecimal
        assert len(binary) % 4 == 0, 'binary line is not representable in hexadecimal'
        hexadecimal = []
        for i in range(0, len(binary), 4):
            hexadecimal.append('{0:1x}'.format(int(binary[i:i+4], 2)))
        yield ''.join(hexadecimal)

def main(): # pylint: disable=too-many-locals
    ''' Wrap script content in function. '''
    # for TUPLE_RX, _in
    sume_rxs = []
    # for TUPLE_TX, _expected
    sume_txs = []

    # digest
    digest_field_len = DigestTuple(80)
    digest_tuple_txs = []

    # packets: SUME->; 'expected'
    pkts_rx = []
    # assorted by port
    nf_rx = dict([(i, []) for i in NF_PORT])
    # packets: ->SUME; 'applied'
    pkts_tx = []
    nf_tx = dict([(i, []) for i in NF_PORT])

    layers = [ethernet(), ipv4(), offset(), generic()]
    # construct all possible layer combinations
    layers = itertools.product(*filter(None, layers))
    # for each possible packet (all layer combinations)
    for (time, combination) in enumerate(layers):
        #% macro mods(state)
        #% include 'modifications/' + this.feature + '_' + state + '.py'
        #% endmacro
        logging.debug('At time %d send combination: %s', time, combination)
        # - create
        pkt = functools.reduce(lambda l, u: l / u, combination)
        pkt.chksum = 0x1234
        pkt.time = time
        valid = functools.reduce(operator.and_, map(operator.truth, combination), True)
        # - apply
        # XXX perform expected packet modification on 'pkt'
        #{{ mods('pre-tx-append') | indent(8) }}
        # end of packet modification
        logging.debug('Constructed packet: %s', pkt.summary())
        pkts_tx.append(pkt)
        nf_tx[NF_SRC].append(pkt)
        # SUME will received transmitted pkt:
        sume_rx = SumeTuple(*([0]*10)) # all 10 arguments are 0
        sume_rx.src_port = NF_PORT[NF_SRC]
        sume_rx.pkt_len = len(pkt)
        sume_rxs.append(sume_rx)
        # - expect
        # XXX perform expected packet modification on 'pkt'
        #{{ mods('pre-rx-append') | indent(8) }}
        # end of packet modification
        logging.debug('Resulting packet: %s', pkt.summary())
        pkts_rx.append(pkt)
        nf_rx[NF_DST_GOOD if valid else NF_DST_BAD].append(pkt)
        # received pkt was transmitted by SUME:
        sume_tx = SumeTuple(*([0]*10)) # all 10 arguments are 0
        sume_tx.src_port = NF_PORT[NF_SRC]
        sume_tx.dst_port = NF_PORT[NF_DST_GOOD if valid else NF_DST_BAD]
        sume_tx.pkt_len = len(pkt)
        #sume_tx.drop = int(not valid)
        sume_txs.append(sume_tx)
        digest_tuple_txs.append(DigestTuple(0))

    logging.debug('Writing PCAP files: %s', [PCAP_RX, PCAP_TX])
    # write PCAP files
    scapy.utils.wrpcap(PCAP_RX, pkts_rx)
    scapy.utils.wrpcap(PCAP_TX, pkts_tx)

    for port in NF_PORT:
        if nf_rx[port]:
            logging.debug('Writing expected PCAP file for port: %s', port)
            scapy.utils.wrpcap(PCAP_NF_RX.format(nr=port), nf_rx[port])
        if nf_tx[port]:
            logging.debug('Writing applied PCAP file for port: %s', port)
            scapy.utils.wrpcap(PCAP_NF_TX.format(nr=port), nf_tx[port])

    with open(TUPLE_RX, 'w') as txt:
        txt.write('\n'.join(tuple_lines(sume_rxs, length=SUME_FIELD_LEN)))
    with open(TUPLE_TX, 'w') as txt:
        # Each line consists of two values (both hexadecimal strings) separated
        # by one white space. The first value represents an entry from
        # digest_tuple_txs, the second an entry from sume_txs. Those lines are
        # separated by newlines. This looks rather ugly but should do the trick:
        txt.write('\n'.join([' '.join([digest, sume]) for (digest, sume) in zip(
            tuple_lines(digest_tuple_txs, length=digest_field_len),
            tuple_lines(sume_txs, length=SUME_FIELD_LEN),
        )]))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
