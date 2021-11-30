''' Python 2&3 snippet to modify 'pkt'. '''
# XXX rm-header feature does not require any packet modifications
if not functools.reduce(operator.and_, map(operator.truth, combination[3:]), True):
    continue # FIXME valid macro ignores hxxx header
