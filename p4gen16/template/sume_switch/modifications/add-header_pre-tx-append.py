''' Python 2&3 snippet to modify 'pkt'. '''
# pylint: disable=undefined-variable,invalid-name
# packet is valid if Ethernet, IP, and offset are valid; ignore generic header
valid = functools.reduce(operator.and_, map(operator.truth, combination[:3]), True)
pkt = functools.reduce(lambda l, u: l / u, combination[:3])
pkt.time = time
# XXX P4 program does not update checksum, set it to an arbitrary value
pkt.chksum = 0x1234
