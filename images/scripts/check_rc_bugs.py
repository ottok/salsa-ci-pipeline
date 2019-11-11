#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# check_rc_bugs, lists the rc bugs that are not being addressed
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

import argparse
import logging
import os
import sys

import debianbts
import debian.deb822 as deb822
import debian.changelog as changelog

from junit_xml import TestSuite, TestCase


def process_options():
    kw = {
        'format': '[%(levelname)s] %(message)s',
    }

    arg_parser = argparse.ArgumentParser(
        description='List rc bugs not being addressed.')
    arg_parser.add_argument('-c', '--changes-file',
                            default=os.environ.get('CHANGES_FILE', ''))
    arg_parser.add_argument(
        '-o', '--output', help='Output file',
        default='{}/check_rc_bugs.xml'.format(
            os.environ.get('EXPORT_DIR', '.')))
    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument('--debug', action='store_true')
    args = arg_parser.parse_args()

    if args.debug:
        kw['level'] = logging.DEBUG

    logging.basicConfig(**kw)

    return args


def get_changes_info(filename):
    if not filename:
        logging.warning('No changes file specified')
        sys.exit(1)

    with open(filename, encoding='utf-8') as fp:
        changes = deb822.Changes(fp)
        changelog_block = changelog.ChangeBlock(
            changes=changes.get('Changes', '').split('\n'))
        logging.debug('Bugs closed: %s', changelog_block.bugs_closed)
        return (changes['Source'], changes.get('Binary', '').split(),
                set(changelog_block.bugs_closed))


def merged_dupe(merged_bugs, current, bug_nrs):
    if not merged_bugs:
        return False
    for merged_bug in sorted(merged_bugs):
        if merged_bug > current:
            return False
        if merged_bug < current and merged_bug in bug_nrs:
            return True


def get_bug_nrs(source_name, binaries):
    bug_nrs = set(debianbts.get_bugs(src=source_name, status='open'))
    for binary in binaries:
        bug_nrs.update(debianbts.get_bugs(package=binary, status='open'))
    return bug_nrs


def generate_test_cases(bug_reports, closes, bug_nrs, options):
    test_cases = []

    for bug in bug_reports:
        # logging.debug(str(bug))
        if merged_dupe(bug.mergedwith, bug.bug_num, bug_nrs):
            continue
        # Check if the bug, or any of the merged bugs, is closed in the
        # current changes
        bug_aliases = {bug.bug_num} | set(bug.mergedwith)
        if bug_aliases & closes:
            continue
        # Ignore done bugs
        if bug.done:
            continue
        name = bug.package if bug.package else bug.source
        tags_str = '({})'.format(','.join(bug.tags)) if bug.tags else ''
        summary = bug.summary if bug.summary else bug.subject
        url = 'https://bugs.debian.org/{}'.format(bug.bug_num)
        test_case = TestCase(name, bug.bug_num)
        test_case.stdout = str(bug)
        msg = '{name}[{bug.bug_num}]/{bug.severity}{tags} {summary} {url}'.format(
            name=name, bug=bug, tags=tags_str, summary=summary, url=url)
        if options.verbose:
            print(msg)
        if bug.severity in ('critical', 'grave', 'serious'):
            test_case.add_error_info(msg)
        else:
            test_case.add_skipped_info(msg)
        test_cases.append(test_case)

    return test_cases


def main():
    options = process_options()

    source_name, binaries, closes = get_changes_info(options.changes_file)

    bug_nrs = get_bug_nrs(source_name, binaries)
    bug_reports = debianbts.get_status(bug_nrs)
    test_cases = generate_test_cases(bug_reports, closes, bug_nrs, options)
    test_suite = TestSuite('Check_RC_BUGS', test_cases)
    with open(options.output, 'w', encoding='utf-8') as output_file:
        output_file.write(TestSuite.to_xml_string([test_suite]))
    return 1 if any(test_case.is_error() for test_case in test_cases) else 0


if __name__ == '__main__':
    sys.exit(main())
