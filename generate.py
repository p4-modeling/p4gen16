#!/usr/bin/env python3
"""
Generate P4_16 code.
"""
import argparse
import logging
import os.path
import sys

import ipcalc

import p4gen16.header as p4header
import p4gen16.complexity as p4complexity
import p4gen16.types.rule
import p4gen16.types as p4
from p4gen16.program import Program
from p4gen16.controller import Controller

FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'

TARGETS = ['v1model',       # p4lang/p4c's simple_switch
           'sume_switch',   # Xilinx P4-SDNet's SimpleSumeSwitch
          ]
SUB_TARGETS = [
    't4p4s',
]

MATCH_TYPES = ['exact',
               'lpm',
               'ternary'
               ]

def _actions(action):
    _actions = {
        'drop': p4.common.action.drop,
        'set_egress_port': p4.common.action.set_egress_port,
        'set_fixed_egress_port': p4.common.action.set_fixed_egress_port,
        'scale_action_data': p4.common.action.scale_action_data,
    }
    try:
        func = (action, _actions[action])
        return func
    except KeyError:
        raise argparse.ArgumentTypeError('valid actions: {}'.format(','.join(_actions.keys())))

def create_parser():
    """ Argument parser creation wrapper. """
    parser = argparse.ArgumentParser(
        description='A programs that generate a P4_16 program for benchmarking'
        ' a particular feature')
    parser.add_argument('-o', '--output', metavar='DIR',
                        help='output directory for generated files, must exist')
    parser.add_argument('-t', '--target', choices=TARGETS, required=True,
                        help='select a target architecture for benchmarking')
    parser.add_argument('--sub-target', choices=SUB_TARGETS,
                        help='select a sub-target of an architecture')

    # Processing options
    parser.add_argument('--number-tables', default=1, type=int,
                        help='number of tables')
    parser.add_argument('--repeat-apply-tables', default=1, type=int,
                        help='number of apply for tables')
    parser.add_argument('--number-table-entries', default=0, type=int,
                        help='number of table entries per table')
    parser.add_argument('--match-type', choices=MATCH_TYPES, default='exact',
                        help='the used type for matching (exact, lpm,ternary)')
    parser.add_argument('--number-match-keys', default=1, type=int,
                        help='number of match keys per table')
    parser.add_argument('--match-key-size', default=8, type=int,
                        help='size of match key in bit')
    parser.add_argument('--action', default='set_fixed_egress_port', type=_actions,
                        help='select available action')
    parser.add_argument('--default-action', default='set_fixed_egress_port', type=_actions,
                        help='select default action')
    parser.add_argument('--number-action-data', default=0, type=int,
                        help='number of action data passed to function')
    parser.add_argument('--match-last', action='store_true',
                        help='use match keys beginning with last parsed fields')

    # Parser (Field|Header) and Packet Modification options
    parser.add_argument('--header-stack-height', default=1, type=int,
                        help='height of the header stack')
    parser.add_argument('--header-fields', default=1, type=int,
                        help='number of fields per header')
    parser.add_argument('--header-field-size', default=8, type=int,
                        help='size of a header field in bit')
    parser.add_argument('--parser-branching-factor', default=1, type=int,
                        help='number of potential next headers for each parser state')
    parser.add_argument('--header-field-modifies', default=0, type=int,
                        help='number of consecutive writes to header fields')
    parser.add_argument('--meta-field-modifies', default=0, type=int,
                        help='number of consecutive writes to metadata fields')

    ## deparser options
    parser.add_argument('--no-emit', action='store_true',
                        help='emit no headers')
    parser.add_argument('--deparser-add-headers', type=int, default=0,
                        help='add extra headers in deparser')
    parser.add_argument('--deparser-add-headers-size', type=int, default=1,
                        help='add extra headers in deparser of x bytes')
    parser.add_argument('--deparser-remove-headers', type=int, default=0,
                        help='remove headers in deparser')

    # general options
    parser.add_argument('--skip-ethernet', action='store_true',
                        help='add dummy ethernet header not used for anything')
    parser.add_argument('--skip-ip', action='store_true',
                        help='add dummy IPv4 header not used for anything')
    parser.add_argument('--add-uninteresting-header', action='store_true',
                        help='add dummy header for ethernet and IP not used for anything')
    parser.add_argument('--default-egress-spec', default='1', type=str,
                        help='default value of the set_egress_spec action')
    parser.add_argument('--skip-filling-tables', action='store_true',
                        help='do not create any table filling rules')
    # Logging level, inspired by https://stackoverflow.com/a/34065768
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='increase the logging level with each call')
    return parser


def main(args=None):
    """ Wrapper for script content. """
    # pylint: disable=too-many-branches, too-many-locals, too-many-nested-blocks, too-many-statements
    parser = create_parser()
    if not args:
        args = sys.argv[1:] # drop script name
    args = parser.parse_args(args)
    logging.basicConfig(
        # see logging documentation "16.6.2 Logging Levels"
        level=(5 - min(4, args.verbose)) * 10,
        format=FORMAT)
    logging.info('successfully parsed command line arguments')

    # build program
    program = Program(target=args.target,
                      skip_ethernet=args.skip_ethernet,
                      skip_ip=args.skip_ip,
                      add_uninteresting=args.add_uninteresting_header)
    program.generate_headers(stack_height=args.header_stack_height,
                             branching_factor=args.parser_branching_factor,
                             field_count=args.header_fields,
                             field_size=args.header_field_size,
                             deparser_headers=args.deparser_add_headers,
                             deparser_remove_headers=args.deparser_remove_headers,
                             deparser_field_count=args.deparser_add_headers_size,
                             meta_field_modifies=args.meta_field_modifies,
                             )
    program.generate_parser_tree(stack_height=args.header_stack_height,
                                 branching_factor=args.parser_branching_factor)
    program.generate_controls(egress_port=args.default_egress_spec,
                              number_tables=args.number_tables,
                              repeat_apply_tables=args.repeat_apply_tables,
                              number_table_entries=args.number_table_entries,
                              match_type=args.match_type,
                              match_last=args.match_last,
                              number_match_keys=args.number_match_keys,
                              match_key_size=args.match_key_size,
                              action=args.action,
                              default_action=args.default_action,
                              number_action_data=args.number_action_data,
                              header_field_modifies=args.header_field_modifies,
                              meta_field_modifies=args.meta_field_modifies)
    program.generate_deparser(emit=not args.no_emit)

    logging.debug('Generating controller')
    controller = Controller(program, args.sub_target,
			    skip_filling_tables=args.skip_filling_tables,
                            egress_port=args.default_egress_spec)

    # some targets have extra utilities
    utilities = {}
    if args.sub_target == 't4p4s' and args.number_table_entries or args.skip_filling_tables:
        from p4gen16.types.v1model.t4p4s.controlplane import ControlPlane
        utilities['controlplane.c.py'] = ControlPlane(
            program, args.sub_target, egress_port=args.default_egress_spec, action=args.action)


    logging.debug('Generated program:\n%s', program)
    logging.debug('Generated controller:\n%s', controller)
    for name, content in utilities.items():
        logging.debug('Generated %s:\n%s', name, content)

    if args.output:
        try:
            # write content to file, if condition is true
            files = [
                # use lambda to delay evaluation (if tuple[0] is None)
                (program, lambda: os.path.join(args.output, 'program.p4')),
                (controller, lambda: os.path.join(args.output, 'controller')),
            ]
            for name, content in utilities.items():
                files.append((content, lambda: os.path.join(args.output, name)))

            for content, file_name in files:
                if not content:
                    continue
                with open(file_name(), 'wt+') as file_:
                    file_.write(str(content))
        except FileNotFoundError:
            logging.fatal('Please ensure that the output directory is present.')
            return 1
    else:
        logging.warning('No output directory given.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
