#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  Copyright © 2016 Maximiliano Curia <maxy@gnuservers.com.ar>

#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses/>.

'''
Check the produced binary packages and checks if there are conflicting files
against packages that are not declared with breaks and replaces.
'''

import argparse
import collections
import logging
import os
import subprocess
import sys

import debian.deb822 as deb822
import debian.debfile as debfile
import debian.debian_support as debian_support

from junit_xml import TestSuite, TestCase


def get_pkg_file(lines):
    found = collections.defaultdict(set)
    for line in lines.split('\n'):
        if not line:
            continue
        package, filename = line.split(': ', 1)
        found[package].add(filename)
    return found


def get_relations(field_value):
    relations = collections.defaultdict(lambda: collections.defaultdict(str))
    if not field_value:
        return relations
    parsed = deb822.PkgRelation.parse_relations(field_value)
    for or_part in parsed:
        for part in or_part:
            rel_name = part['name']
            if 'version' in part:
                if 'version' in relations[rel_name]:
                    if debian_support.version_compare(
                            part['version'][1],
                            relations[rel_name]['version']) > 0:
                        relations[rel_name]['version'] = part['version'][1]
            else:
                relations[rel_name] = collections.defaultdict(str)
    return relations


def process_options():
    kw = {
        'format': '[%(levelname)s] %(message)s',
    }
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('--debug', action='store_true')
    arg_parser.add_argument('--changes-file',
                            default=os.environ.get('CHANGES_FILE', ''))
    arg_parser.add_argument(
        '-o', '--output', help='Output file',
        default='{}/missing_breaks_replaces.xml'.format(
            os.environ.get('EXPORT_DIR', '.')))
    args = arg_parser.parse_args()

    if args.debug:
        kw['level'] = logging.DEBUG

    logging.basicConfig(**kw)

    return args


def process_entry(dirname, entry):
    ''' Process a single changes files entry '''
    logging.debug(entry['name'])
    deb_filename = os.path.join(dirname, entry['name'])
    deb = debfile.DebFile(deb_filename)

    deb_control = deb.debcontrol()
    logging.info('Processing: {} {}'.format(deb_control['Package'],
                                            deb_control['Version']))
    name = deb_control['Package']

    deb_replaces = deb_control.get('Replaces', '')
    # deb_provides = deb_control.get('Provides', '')
    deb_breaks = deb_control.get('Breaks', '')
    deb_conflicts = deb_control.get('Conflicts', '')

    breaks_rels = get_relations(deb_breaks)
    conflicts_rels = get_relations(deb_conflicts)
    replaces_rels = get_relations(deb_replaces)

    # apt-file now returns 1 if the files are not found, specially bothering
    # with the dbgsym packages (and the packages not yet uploaded)
    completed_process = subprocess.run(
        ['apt-file', '-D', 'search', deb_filename],
        universal_newlines=True, stdout=subprocess.PIPE)
    if completed_process.returncode and completed_process.stdout:
        completed_process.check_returncode()
    output = completed_process.stdout
    interesting = get_pkg_file(output)
    result = []
    for package_name in interesting:
        if package_name == name:
            continue
        if package_name in conflicts_rels:
            # TODO check versions
            continue
        if package_name in breaks_rels and \
           package_name in replaces_rels:
            # TODO check versions
            continue
        msg = '{a} conflicts with {b} files: {files}'.format(
            a=name, b=package_name, files=interesting[package_name])
        logging.error('Missing Breaks/Replaces found')
        logging.error(msg)
        result.append(msg)

    return name, result, output


def generate_test_cases(results):
    test_cases = []
    for name, (result, output) in results.items():
        test_case = TestCase(name, stdout=output)
        if result:
            test_case.add_error_info('\n'.join(result))

        test_cases.append(test_case)

    return test_cases


def main():
    """ Check changes files for missing Breaks/Replaces using apt-file

    """
    args = process_options()
    dirname = os.path.dirname(args.changes_file)
    results = {}
    with open(args.changes_file) as changes_file:
        changes = deb822.Changes(changes_file)
        for entry in changes['Files']:
            if not entry['name'].endswith('.deb'):
                continue
            name, result, output = process_entry(dirname, entry)
            results[name] = (result, output)
    test_cases = generate_test_cases(results)
    test_suite = TestSuite('check_for_missing_breaks_replaces', test_cases)
    with open(args.output, 'w') as output_file:
        output_file.write(TestSuite.to_xml_string([test_suite]))
    return 1 if any(test_case.is_error() for test_case in test_cases) else 0


if __name__ == '__main__':
    sys.exit(main())
