#!/usr/bin/env python3
"""
Generate programs that test the header insertion / removal capabilities.
"""
import logging
from . import types as p4

def _block_name(target):
    """
    Returns the target-dependent control block name where the capability tests
    shall be performed.
    """
    return {
        'v1model': 'egress',
        'sume_switch': 'pipeline',
    }[target]

def add(number, offset, field_count=1, field_size=16, checksum=False, target='v1model'):
    """
    Introduce new header while deparsing.
    """
    logging.debug('header.add(%d, %d, %d, %s)', number, field_count, field_size, checksum)
    # create a program containing a parser for the required amount of header
    program = parse.parser_tree(
        # FIXME verify add-header adds correct no. of header (and not e.g.: -2)
        number,
        branching_factor=1,
        field_count=field_count,
        field_size=field_size,
        checksum=checksum,
        target=target,
    )
    # XXX if testing device stores information in packet it might be necessary
    #     to keep a fixed-length prefix of each packet. Dummy header will ensure
    #     this prefix is kept.
    program.add_header(p4.header.Header('offset', fields=[
        p4.header.HeaderField(offset, 'f_offset', target=target)], target=target))
    # update parser graph (reduce to minimal header stack; all header - (generic
    # header - generic header as final state))
    parser_states_generic = len(program.parser.states) - (number - 1)
    program.parser.states = list(program.parser.states)[:parser_states_generic]
    # last parser state transitions to offset header
    last_parser_state = list(program.parser.states)[-1]
    for value in list(program.parser.states)[-1]._transitions:
        last_parser_state.add_transition(p4.parser.ParserStateTransition(value, 'parse_offset'))
    # replace parser state definition
    program.parser.add_state(last_parser_state)
    program.parser.ends = ['offset']
    # add the new header to the headers struct
    # FIXME next line doesn't work on sume_switch
    #program._structs['headers'].add_field(p4.struct.StructField('offset_t', 'offset'))
    # XXX workaround for sume_switch quirk
    _h = list(program._structs['headers'].fields)
    _h = _h[:len(_h)-number] + [p4.struct.StructField('offset_t', 'offset')] + _h[len(_h)-number:]
    program._structs['headers'].fields = _h
    # update 'valid' macro
    for i, statement in enumerate(getattr(program.control, _block_name(target)).sequence):
        if not isinstance(statement, p4.statement.Define):
            continue
        if statement.name != 'valid':
            continue
        getattr(program.control, _block_name(target)).sequence[i] = p4.statement.Define(
            statement.name,
            '(' + ' && '.join(list(map(
                lambda h: '.'.join(['h', h.name, 'isValid()']),
                program.headers ,
            )) + ['meta.accept']) + ')',
            target=target,
        )
        break
    # make/mark generic header as valid - causes generic header to be deparsed
    mark_valid = p4.statement.Statement(
        'if (' + # all expected headers are valid
        ' && '.join(map(
            lambda h: '.'.join(['h', h.name, 'isValid()']),
            list(program.headers)[:-(number + 1)] # skip generic & offset
        )) + ' && h.offset.isValid()) ' +
        '{ ' + # then mark all generic header as valid
        ' '.join(map(
            lambda i: str(p4.statement.Statement(
                'h.h{:03}.setValid()'.format(i),
                target=target,
            )),
            range(number),
        )) + ' }',
        target=target,
    )
    getattr(program.control, _block_name(target)).sequence.insert(0, mark_valid)
    # FIXME make pretty
    # update sume length
    update_length = 'if (valid) {{ sume_metadata.pkt_len = sume_metadata.pkt_len + ({header}*{fields}*{size})/8; }}'
    update_length = p4.statement.Statement(update_length.format(
        header=number,
        fields=len(program._headers['h000'].fields),
        size=program._headers['h000']._fields['f000'].bits,
    ), target=target)
    getattr(program.control, _block_name(target)).sequence.append(update_length)
    # update ipv4 length
    update_length = 'if (valid) {{ h.ipv4.total_length = h.ipv4.total_length + ({header}*{fields}*{size})/8; }}'
    update_length = p4.statement.Statement(update_length.format(
        header=number,
        fields=len(program._headers['h000'].fields),
        size=program._headers['h000']._fields['f000'].bits,
    ), target=target)
    getattr(program.control, _block_name(target)).sequence.append(update_length)
    # update deparse sequence to: Ethernet / IPv4 / Offset / generic header
    program.control.deparse.header.insert(2, 'h.offset')
    return program

def delete(number, offset, field_count=1, field_size=16, checksum=False, target='v1model'):
    """
    Decrease the number of header while deparsing (ensure constant prefix with offset).
    """
    logging.debug('header.delete(%d, %d, %d, %s)', number, field_count, field_size, checksum)
    # TODO problem: delete reduces packet size -> need to figure out which bits
    #      are required by MoonGen
    # create a program containing a parser for the given number of header
    program = parse.parser_tree(
        number,
        branching_factor=1,
        field_count=field_count,
        field_size=field_size,
        checksum=checksum,
        target=target,
    )
    # XXX if testing device stores information in packet it might be necessary
    #     to keep a fixed-length prefix of each packet. Dummy header will ensure
    #     this prefix is kept.
    program.add_header(p4.header.Header('offset', fields=[
        p4.header.HeaderField(offset, 'f_offset', target=target)], target=target))
    # add the new header to the headers struct
    # FIXME next line doesn't work on sume_switch
    #program._structs['headers'].add_field(p4.struct.StructField('offset_t', 'offset'))
    # XXX workaround for sume_switch quirk
    _h = list(program._structs['headers'].fields)
    _h = _h[:len(_h)-number] + [p4.struct.StructField('offset_t', 'offset')] + _h[len(_h)-number:]
    program._structs['headers'].fields = _h

    # add offset parser state
    offset_parser_state = p4.parser.ParserState(
        'offset',
        'f_offset',
        target=target,
    )
    for it in program.parser._states[p4.common.header.IPv4.name].transitions:
        offset_parser_state.add_transition(p4.parser.ParserStateTransition('default', it.next))
    # FIXME The offset's size is not always equal to IPv4's NH field.
    # Hence, in general, one cannot use the 'old' match values (since
    # their size differs from the size of the offset header's field).
    program.parser.add_state(offset_parser_state)
    # update next header for IPv4 to 'offset', FIXME needs improvement (doc or code)
    ipv4_parser_state = p4.parser.ParserState(
        p4.common.header.IPv4.name,
        'protocol',
        target=target,
    )
    for it in program.parser._states[p4.common.header.IPv4.name].transitions:
        ipv4_parser_state.add_transition(p4.parser.ParserStateTransition(it.expr, 'parse_offset'))
    program.parser.add_state(ipv4_parser_state)
    # add the offset header to to list of emitted header
    program.control.deparse.header.insert(2, 'h.offset')
    # update 'valid' macro
    for i, statement in enumerate(getattr(program.control, _block_name(target)).sequence):
        if not isinstance(statement, p4.statement.Define):
            continue
        if statement.name != 'valid':
            continue
        getattr(program.control, _block_name(target)).sequence[i] = p4.statement.Define(
            statement.name,
            '(' + ' && '.join(map(
                lambda h: '.'.join(['h', h.name, 'isValid()']),
                list(program.headers)[:-(number + 1)],
            )) + ' && h.offset.isValid() && meta.accept)',
            target=target,
        )
        break
    # make/mark generic header as invalid - causes generic header not to be deparsed
    mark_invalid = p4.statement.Statement(
        'if (' + # all expected headers are valid
        ' && '.join(map(
            lambda h: '.'.join(['h', h.name, 'isValid()']),
            list(program.headers)[:-(number + 1)] # skip generic & offset
        )) + ' && h.offset.isValid()) ' +
        '{ ' + # then mark all generic header as invalid
        ' '.join(map(
            lambda i: str(p4.statement.Statement(
                'h.h{:03}.setInvalid()'.format(i),
                target=target,
            )),
            range(number),
        )) + ' }',
        target=target,
    )
    getattr(program.control, _block_name(target)).sequence.insert(0, mark_invalid)
    # FIXME make pretty
    # update sume length
    update_length = 'if (valid) {{ sume_metadata.pkt_len = sume_metadata.pkt_len - ({header}*{fields}*{size})/8; }}'
    update_length = p4.statement.Statement(update_length.format(
        header=number,
        fields=len(program._headers['h000'].fields),
        size=program._headers['h000']._fields['f000'].bits,
    ), target=target)
    getattr(program.control, _block_name(target)).sequence.append(update_length)
    # update ipv4 length
    update_length = 'if (valid) {{ h.ipv4.total_length = h.ipv4.total_length - ({header}*{fields}*{size})/8; }}'
    update_length = p4.statement.Statement(update_length.format(
        header=number,
        fields=len(program._headers['h000'].fields),
        size=program._headers['h000']._fields['f000'].bits,
    ), target=target)
    getattr(program.control, _block_name(target)).sequence.append(update_length)
    return program
