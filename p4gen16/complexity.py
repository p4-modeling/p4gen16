#!/usr/bin/env python3
"""
Generate programs that test the value read / write / update capabilities.
"""
import logging
from . import types as p4

def _control_name(target):
    """
    Returns the target-dependent control block name where the capability tests
    shall be performed.
    """
    return {
        'v1model': 'ingress',
        'sume_switch': 'pipeline',
    }[target]

def update(operations, checksum=False, target='v1model'):
    """
    Apply the given number of write updates to a header field of each packet.
    """
    # XXX complexity.update writes to metadata to avoid dependencies on packet
    #     structure.
    logging.debug('complexity.update(%d)', operations)
    # generate a minimal parser / program
    program = parse.parser_tree(0, checksum=checksum, target=target)
    # mis-/reuse the ID field (used to determine the outgoing interface) to
    # perform the repeated writes - prior to final update by 'table_ipv4.apply()'
    for i in range(operations):
        set_statement = p4.statement.Statement('set_id(%d)' % i, target=target)
        getattr(program.control, _control_name(target)).sequence.insert(0, set_statement)
    return program

def pipeline(depth, target='v1model', match_type='exact'):
    """
    Apply the given number of tables.
    """
    logging.debug('complexity.pipeline(%d)', depth)
    program = parse.parser_tree(0, target=target)
    def table(i):
        """ Tries to generate inhomogeneous tables (given an integer). """
        # pylint: disable=invalid-name
        pos_header = i % len(program.headers)
        headers = list(program.headers)
        header = headers[pos_header]
        pos_field = (i + pos_header) % len(header.fields)
        field = list(header.fields)[pos_field]
        return p4.table.Table(
            'dummy_table_%d' % i, # name
            keys=[p4.table.TableKey('.'.join(
                ['h', header.name, field.name]), match_type)], # dummy key
            action_names=['drop', 'NoAction'],
        )
    for i in range(depth):
        table_i = table(i)
        table_apply = p4.statement.Statement(table_i.name + '.apply()', target=target)
        getattr(program.control, _control_name(target)).tables.append(table_i)
        getattr(program.control, _control_name(target)).sequence.insert(0, table_apply)
    return program

#pylint: disable=too-many-arguments
def memory(registers, elements, element_width, operations, write=False, target='v1model'):
    """
    Perform arbitrary many read and write operations on a given number of
    registers (with a given number of elements per register as well as an
    arbitrary element width), respectively.
    """
    if target == 'sume_switch' and operations > 1:
        logging.critical('Target "%s" does NOT support accessing a register ' +
                         'more than once. YMMV.', target)
    program = parse.parser_tree(0, target=target)
    # either write(integer) or read()
    # temporary variable used to store read result
    tmp_reg_name = 'register_value_tmp'
    read_result = p4.statement.Statement(
        'bit<%d> %s = 37' % (element_width, tmp_reg_name),
        target=target)
    getattr(program.control, _control_name(target)).sequence.append(read_result)
    for j in range(registers):
        # declare register
        declare_register_j = p4.common.register.declare(
            'register%d' % j, # name
            width=element_width, # bit width of an register element
            size=elements, # no. of elements per register
            target=target,
        )
        getattr(program.control, _control_name(target)).instantiations.append(declare_register_j)
        # "use" register
        if write:
            # write tmp_reg_name's content to element no. `j % element_width`
            usage = p4.common.register.write(
                'register%d' % j, # register
                j % element_width, # register index
                tmp_reg_name, # storage variable
                target=target,
            )
        else:
            # read value from index `j % element_width` and write it to
            # `register_value_tmp`
            usage = p4.common.register.read(
                'register%d' % j, # register
                j % element_width, # register index
                tmp_reg_name, # storage variable
                target=target,
            )
        for _ in range(operations):
            getattr(program.control, _control_name(target)).sequence.append(usage)
    return program

def tablewidth(width, checksum, target='v1model'):
    """
    Creates additional header of specified size and matches that field
        agains a custom table
    """
    program = parse.parser_tree(
        stack_height=1,
        branching_factor=1,
        field_count=1,
        field_size=width,
        checksum=checksum,
        target=target)

    custom_header = list(program.headers)[-1]
    custom_field = list(custom_header.fields)[-1]

    table = p4.table.Table(
        'table_custom_width',
        keys=[p4.table.TableKey('.'.join(['h', custom_header.name, custom_field.name]), 'exact')],
        action_names=['drop', 'NoAction'],
    )

    table_apply = p4.statement.Statement('if (valid) { ' + table.name + '.apply(); }',
                                         target=target)
    programcontrol = getattr(program.control, _control_name(target))
    programcontrol.tables.append(table)
    programcontrol.sequence.insert(len(programcontrol.sequence)-1,
                                   table_apply) # insert before eth table

    return program
