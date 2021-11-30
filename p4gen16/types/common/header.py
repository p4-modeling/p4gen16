#!/usr/bin/env python3
'''
P4 common header
'''
from ..header import Header, HeaderField
# pylint: disable=invalid-name
Ethernet = Header('ethernet', fields=[
    HeaderField(48, 'addr_dst'),
    HeaderField(48, 'addr_src'),
    HeaderField(16, 'ethertype'),
])

IPv4 = Header('ipv4', fields=[
    HeaderField(4, 'version'),
    HeaderField(4, 'ihl'),
    HeaderField(8, 'tos'),
    HeaderField(16, 'total_length'),
    HeaderField(16, 'identification'),
    HeaderField(3, 'flags'),
    HeaderField(13, 'fragment_offset'),
    HeaderField(8, 'ttl'),
    HeaderField(8, 'protocol'),
    HeaderField(16, 'checksum'),
    HeaderField(32, 'addr_src'),
    HeaderField(32, 'addr_dst'),
])

Ethernet_IP_Dummy = Header('eth_ip_dummy', fields=[
    HeaderField(32, 'eth0'),
    HeaderField(32, 'eth1'),
    HeaderField(32, 'eth2'),
    HeaderField(16, 'eth3'),
    HeaderField(32, 'ip0'),
    HeaderField(32, 'ip1'),
    HeaderField(32, 'ip2'),
    HeaderField(32, 'ip3'),
    HeaderField(32, 'ip4'),
])

Uninteresting = Header('uninteresting', fields=[
    HeaderField(336, 'ignore'),
])
