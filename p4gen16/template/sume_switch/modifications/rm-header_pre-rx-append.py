''' Python 2&3 snippet to modify 'pkt'. '''
# pylint: disable=undefined-variable,invalid-name
if valid:
    pkt = functools.reduce(lambda l, u: l / u, list(combination[:3]))
    pkt.time = time
    # XXX P4 program does not update checksum, set it to an arbitrary value
    pkt.chksum = 0x1234
