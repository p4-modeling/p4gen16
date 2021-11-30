''' Python 2&3 snippet to modify 'pkt'. '''
# pylint: disable=undefined-variable,invalid-name
# XXX assumes first header returned by generic() is valid
if valid:
    pkt = functools.reduce(lambda l, u: l / u, list(combination[:3]) + [generic()[0]])
    pkt.time = time
    # XXX P4 program does not update checksum, set it to an arbitrary value
    pkt.chksum = 0x1234
