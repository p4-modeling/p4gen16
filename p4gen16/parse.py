#!/usr/bin/env python3
"""
Generate programs that test the parsing capabilities.
"""
import logging
from .types import sume_switch
from .types import v1model
from . import types as p4

# pylint: disable=too-many-locals,too-many-arguments,too-many-statements
def parser_tree(stack_height=1, branching_factor=1, field_count=1, field_size=8,
                target='default'):
    """
    Generate a program with the given header stack height, branching factor and
    number of fields per header. (Note: stack height *does not* take used
    Ethernet/IPv4 header into account)
    """
    logging.debug('parse.parser_tree(%d, %d, %d, %d, %s, %s)', stack_height,
                  branching_factor, field_count, field_size, target)
    _nodes_in_tree = lambda b, h: int((b ** h - 1) / (b - 1)) if b > 1 and h > 0 else max(0, h)
    # number of generic headers to generate
    header_count = _nodes_in_tree(branching_factor, stack_height)

    ## preparing header
    headers = [p4.common.header.Ethernet, p4.common.header.IPv4]
    fields = [p4.header.HeaderField(
        field_size,
        'f{:03}'.format(i),
        target=target,
    ) for i in range(field_count)]
    for i in range(header_count):
        headers.append(p4.header.Header(
            'h{:03}'.format(i),
            fields=fields,
            target=target,
        ))

    ## preparing struct
    header_struct_fields = [
        p4.struct.StructField(
            p4.common.header.Ethernet.type,
            p4.common.header.Ethernet.name,
            target=target
        ),
        p4.struct.StructField(
            p4.common.header.IPv4.type,
            p4.common.header.IPv4.name,
            target=target
        ),
    ]
    for i in range(header_count):
        hname = 'h{:03}'.format(i)
        htype = 'h{:03}_t'.format(i)
        header_struct_fields.append(p4.struct.StructField(htype, hname, target=target))
    struct = [
        p4.struct.Struct('headers', fields=header_struct_fields, target=target),
        p4.common.struct.metadata,
    ]

    if target == 'sume_switch':
        struct.append(sume_switch.struct.digest)

    ## preparing parser
    pstates = []
    pstates.append(p4.parser.ParserState(
        p4.common.header.Ethernet.name,
        'ethertype',
        transitions=[
            p4.parser.ParserStateTransition(
                '16w0x0800',
                'parse_' + p4.common.header.IPv4.name,
                target=target,
            ),
        ],
        target=target,
    ))
    pstates.append(p4.parser.ParserState(
        p4.common.header.IPv4.name,
        'protocol',
        transitions=[
            p4.parser.ParserStateTransition(
                '8w0x11',
                'parse_h000' if header_count > 0 else 'happy',
                target=target
            ),
        ],
        target=target,
    ))
    # link parser states, leafs of parser tree are final states
    internal_node_count = _nodes_in_tree(branching_factor, stack_height - 1)
    for i in range(internal_node_count):
        transitions = [
            p4.parser.ParserStateTransition(
                '{}w{}'.format(field_size, j),
                'parse_h{:03}'.format(i * branching_factor + j),
                target=target,
            ) for j in range(1, branching_factor)
        ]
        next_ = branching_factor * (i + 1)
        if next_ < header_count:
            transitions += [
                # XXX explicitly set default next header
                p4.parser.ParserStateTransition(
                    'default',
                    'parse_h{:03}'.format(next_),
                    target=target,
                ),
            ]
        if not transitions:
            continue # skip parser states without transitions
        pstates.append(p4.parser.ParserState(
            'h{:03}'.format(i), # name
            'f{:03}'.format(0), # select, XXX fixed selected field
            # matches, link node to its children
            transitions=transitions,
            target=target,
        ))
    parser = p4.parser.make_parser(
        p4.common.header.Ethernet.name,
        states=pstates,
        ends=['h{:03}'.format(i) # name
              for i in range(internal_node_count, header_count)],
        target=target,
    )

    program = p4.program.Program(
        parser,
        control,
        headers=headers,
        structs=struct,
        actions=[],
        target=target,
    )
    return program
