#!/usr/bin/env python3
'''
P4 program type
'''

import sys
import collections
import logging
from .types.action import Action
from .types.header import Header
from .types.parser import Parser
from .types.struct import Struct
from .types.statement import Statement
from .types.templateable import Templateable
from .types.common.header import Ethernet, IPv4, Ethernet_IP_Dummy, Uninteresting
from . import types as p4

class Program(Templateable):
    ''' A program. '''
    _parser = None
    def __init__(self, target, skip_ethernet, skip_ip, add_uninteresting):
        super().__init__(target=target)
        self._parser = collections.OrderedDict()
        self._headers = collections.OrderedDict()
        self._structs = collections.OrderedDict()

        self.controls = p4.control.Control(
            target=target,
        )

        self.log = logging
        self.target = target

        # general options
        self.main_pipeline = None
        self.skip_ethernet = skip_ethernet and not skip_ip
        self.skip_ip = skip_ip and not skip_ethernet
        self.skip_ethernet_ip = skip_ethernet and skip_ip
        self.add_uninteresting = add_uninteresting

    @property
    def headers(self):
        return self._headers.values()

    @headers.setter
    def headers(self, headers):
        for header in headers:
            self.add_header(header)

    def add_header(self, header):
        ''' Add a new header to this program. '''
        if not isinstance(header, Header):
            raise TypeError('{that} is not an instance of Header'.format(
                that=header.__class__.__name__))
        self._headers[header.name] = header

    @property
    def structs(self):
        return self._structs.values()

    @structs.setter
    def structs(self, structs):
        for struct in structs:
            self.add_struct(struct)

    def add_struct(self, struct):
        ''' Add a new struct to this program. '''
        if not isinstance(struct, Struct):
            raise TypeError('{that} is not an instance of Struct'.format(
                that=struct.__class__.__name__))
        self._structs[struct.name] = struct

    @property
    def parser(self):
        return self._parser

    @parser.setter
    def parser(self, parser):
        if not isinstance(parser, Parser):
            raise TypeError('{that} is not an instance of Parser'.format(
                that=parser.__class__.__name__))
        self._parser = parser

    def _nodes_in_tree(self, b, h):
        '''
        Return number of nodes in tree width height h and branching factor b
        '''
        return int((b ** h - 1) / (b - 1)) if b > 1 and h > 0 else max(0, h)

    def struct_headers(self):
        return list(self.structs)[0]

    def struct_metadata(self):
        return list(self.structs)[1]

    def generate_headers(self, stack_height=1, branching_factor=1, field_count=1, field_size=8,
                         deparser_headers=0, deparser_remove_headers=0, deparser_field_count=1,
                         deparser_field_size=8, meta_field_modifies=0):
        self.log.info('generate_headers(%d, %d, %d, %d)', stack_height,
                       branching_factor, field_count, field_size)
        # number of generic headers to generate
        header_count = self._nodes_in_tree(branching_factor, stack_height)
    
        ## preparing header
        headers = []
        if self.skip_ethernet_ip:
            headers.append(Ethernet_IP_Dummy)
        if self.skip_ethernet:
            headers.append(Ethernet)
        if self.skip_ip:
            headers.append(IPv4)
        if self.add_uninteresting:
            headers.append(Uninteresting)
        # headers used in pipeline
        fields = [
            p4.header.HeaderField(
                field_size,
                'f{:03}'.format(i),
                target=self.target,
            ) for i in range(field_count)]
        for i in range(header_count):
            headers.append(
                p4.header.Header(
                    'h{:03}'.format(i),
                    fields=fields,
                    target=self.target,
                )
            )
        # deparser headers
        d_fields = [
            p4.header.HeaderField(
                deparser_field_size,
                'f{:03}'.format(i),
                target=self.target,
            ) for i in range(deparser_field_count)]
        dep_headers = []
        for i in range(deparser_headers):
            dep_headers.append(
                p4.header.Header(
                    'dep_h{:03}'.format(i),
                    fields=d_fields,
                    target=self.target,
                )
            )
        dep_remove_headers = []
        for i in range(deparser_remove_headers):
            dep_remove_headers.append(
                p4.header.Header(
                    'dep_r_h{:03}'.format(i),
                    fields=d_fields,
                    target=self.target,
                )
            )
        self.headers = headers + dep_headers + dep_remove_headers
        self.deparser_headers = dep_headers
        self.deparser_remove_headers = dep_remove_headers
        self.metadata = p4.common.struct.metadata

        for i in range(meta_field_modifies):
            f = p4.struct.StructField(
                'bit<{}>'.format(field_size),
                'f{:03}'.format(i),
                target=self.target,)
            self.metadata.add_field(f)
            f.set_parent('meta')

    
        ## preparing struct
        self.structs = [
            p4.struct.Struct('headers', target=self.target),
            self.metadata,
        ]

        header_struct_fields = []
        if self.skip_ethernet_ip:
            self._structs['headers'].add_field(
                p4.struct.StructField(Ethernet_IP_Dummy, Ethernet_IP_Dummy.name, target=self.target))
        if self.skip_ethernet:
            self._structs['headers'].add_field(
                p4.struct.StructField(Ethernet, Ethernet.name, target=self.target))
        if self.skip_ip:
            self._structs['headers'].add_field(
                p4.struct.StructField(IPv4, IPv4.name, target=self.target))
        if self.add_uninteresting:
            self._structs['headers'].add_field(
                p4.struct.StructField(Uninteresting, Uninteresting.name, target=self.target))
        start_idx = 0
        if self.skip_ethernet_ip:
            start_idx += 1
        if self.skip_ethernet:
            start_idx += 1
        if self.skip_ip:
            start_idx += 1
        if self.add_uninteresting:
            start_idx += 1
        for i, header in enumerate(self.headers):
            if i < start_idx:
                continue
            self._structs['headers'].add_field(
                p4.struct.StructField(header, header.name, target=self.target))
        for i, header in enumerate(self.deparser_remove_headers):
            self._structs['headers'].add_field(
                p4.struct.StructField(header, header.name, target=self.target))

    def generate_parser_tree(self, stack_height=1, branching_factor=1, field_count=1, field_size=8):
        self.log.info('generate_parser_tree(%d, %d, %d, %d)', stack_height,
                       branching_factor, field_count, field_size)
        # number of generic headers to generate
        header_count = self._nodes_in_tree(branching_factor, stack_height)
        ## preparing parser
        pstates = []
        # link parser states, leafs of parser tree are final states
        internal_node_count = self._nodes_in_tree(branching_factor, stack_height-1)
        for i in range(header_count):
            transitions = []
            if i < internal_node_count:
                transitions = [
                    p4.parser.ParserStateTransition(
                        '{}w{}'.format(field_size, j),
                        'parse_h{:03}'.format(i * branching_factor + j),
                        target=self.target,
                    ) for j in range(1, branching_factor)
                ]
                next_ = branching_factor * (i + 1)
                if next_ < header_count:
                    transitions += [
                        # XXX explicitly set default next header
                        p4.parser.ParserStateTransition(
                            'default',
                            'parse_h{:03}'.format(next_),
                            target=self.target,
                        ),
                    ]
            extra = []
            extra_after = []
            # some special cases that occur only once in first state
            if i == 0:
                if self.skip_ethernet_ip:
                    extra.append(Ethernet_IP_Dummy.name)
                if self.skip_ethernet:
                    extra.append(Ethernet.name)
                if self.skip_ip:
                    extra.append(IPv4.name)
                if self.add_uninteresting:
                    extra.append(Uninteresting.name)

                for header in self.deparser_remove_headers:
                    extra_after.append(header.name)
            pstates.append(p4.parser.ParserState(
                'h{:03}'.format(i), # name
                'f{:03}'.format(0), # select, XXX fixed selected field
                # matches, link node to its children
                transitions=transitions,
                is_start=i==0,
                target=self.target,
                extract_extra=extra,
                extract_extra_after=extra_after
            ))
        parser = p4.parser.make_parser(
            states=pstates,
            target=self.target,
        )
        self.parser = parser

    def generate_deparser(self, emit=True):
        self.log.info('generate_deparser()')
        deparse_headers = []
        if emit:
            deparse_headers = ['h.' + header.name for header in self.headers if header not in self.deparser_remove_headers]
        deparse = p4.control.make_deparser(deparse_headers, target=self.target)
        self.controls.add_declaration('deparse', deparse)

    def get_main_pipeline(self):
        return getattr(self.controls, self.main_pipeline)

    def generate_controls(self, egress_port=1, number_tables=1, repeat_apply_tables=1,
                          number_table_entries=0,
                          match_type='exact', number_match_keys=1, match_key_size=8,
                          match_last=False,
                          action=None, default_action=None, number_action_data=0,
                          header_field_modifies=0, meta_field_modifies=0):
        self.log.info('generate_controls()')
        controls = None
        if self.target == 'v1model':
            controls = p4.v1model.control.generate_controls()
            self.main_pipeline = 'ingress'
        elif self.target == 'sume_switch':
            log.fatal('NYI')
            return

        # add them
        for name, control in controls.items():
            self.controls.add_declaration(name, control)

        # actual processing in pipeline
        pipeline = self.get_main_pipeline()

        # add actions
        actions = [action]
        if not default_action:
            default_action = ('set_fixed_egress_port', p4.common.action.set_fixed_egress_port)
        actions.append(default_action)
        actions = list(set(actions))

        _actions = []
        # instantiate
        for name, action in actions:
            if name == 'set_fixed_egress_port':
                action = action(self.target, egress_port)
            elif name == 'scale_action_data':
                action = action(self.target, egress_port, number_action_data)
            else:
                action = action(self.target)
            _actions.append(action)
        actions = _actions
        default_action = [ac for ac in actions if ac.name == default_action[0]][0]

        for action in actions:
            pipeline.add_action(action)

        # meta field mods
        for i in range(meta_field_modifies):
            mod_meta= p4.statement.ModifyMeta(list(self.metadata.get_fields())[i], 0xff)
            pipeline.sequence.append(mod_meta)

        # TODO parameterize tables: action data
        # add tables and their invocation
        self.available_fields = []
        for i in range(number_tables):
            name = 'table_benchmark{:03}'.format(i)
            headers = list(self.structs)[0]
            for header in self.struct_headers().fields:
                header = header.header
                if self.skip_ethernet_ip and header.type == Ethernet_IP_Dummy.type:
                    self.log.debug('skipping ethernet ip dummy')
                    continue
                if self.skip_ethernet and header.type == Ethernet.type:
                    self.log.debug('skipping ethernet')
                    continue
                if self.skip_ip and header.type == IPv4.type:
                    self.log.debug('skipping ipv4')
                    continue
                if self.add_uninteresting and header.type == Uninteresting.type:
                    self.log.debug('skipping uninteresting')
                    continue
                for field in header.fields:
                    if not field.bits == match_key_size:
                        continue
                    self.available_fields.append((header, field))

            if len(self.available_fields) < number_match_keys:
                self.log.fatal('Not enough available match fields of {} bits found {} for mat({} required)'.format(
                    match_key_size, len(self.available_fields), number_match_keys))
                sys.exit(1)
            all_keys = [p4.table.TableKey(avail[0], avail[1], match_type)
                    for avail in self.available_fields]
            keys = all_keys[:number_match_keys]
            if match_last:
                all_keys.reverse()
                keys = all_keys[:number_match_keys]
                keys.reverse()
            table = pipeline.add_table(
                name,
                actions,
                keys,
                default_action=default_action, # TODO potential value of default action
                size=number_table_entries
            )
            table_apply = p4.statement.ApplyTable(table, target=self.target)
            for _ in range(repeat_apply_tables):
                pipeline.sequence.append(table_apply)
        if number_tables == 0:
            # outgoing port is normally set in action, set here
            pipeline.sequence.append(Statement('{}()'.format(default_action.name)))

        # header field mods
        if len(self.available_fields) < header_field_modifies:
            self.log.fatal('Not enough available match fields found for header updates {} ({} required)'.format(
                len(self.available_fields), header_field_modifies))
            sys.exit(1)
        for i in range(header_field_modifies):
            mod_header= p4.statement.ModifyHeader(self.available_fields[i][1], 0xff)
            pipeline.sequence.append(mod_header)

        # set deparser headers valid
        for header in self.deparser_headers:
            stmt = p4.statement.SetHeaderValid(header, target=self.target)
            pipeline.sequence.append(stmt)

    def generate_controller(self):
        self.log.info('generate_controller()')
