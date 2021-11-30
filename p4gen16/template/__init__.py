#!/usr/bin/env python3
"""
Wrapper around templates using jinja2.
"""
import logging
import jinja2 as j

def fill(values, template):
    """
    Fill the given template (default v1switch.p4.j2) with the supplied values.
    Returns a P4_16 program as string.
    """
    env = j.Environment(
        loader=j.PackageLoader('p4gen16', 'template'),
    )
    template = env.get_template(template)
    try:
        values = values._asdict()
    except AttributeError:
        logging.info('fill: values has no _asdict method - using as is (type %s)', type(values))
    return template.render(values)
