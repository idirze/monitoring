#!/usr/bin/env python

from ansible.utils.shlex import shlex_split
from ansible.plugins.inventory.ini import InventoryModule

import argparse
import json
import os
import sys


class MyInventoryModule(InventoryModule):
    def __init__(self):
        pass


def msg(_type, text, exit=0):
    sys.stderr.write("%s: %s\n" % (_type, text))
    sys.exit(exit)


def main():
    # Read command line options
    parser = argparse.ArgumentParser(
        description=(
            'Dynamic inventory script that reads inventory rootdir in the INI '
            'format.'))
    parser.add_argument(
        '--rootdir',
        metavar='rootdir',
        help='Path to the inventory rootdir')
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all groups and hosts')
    args = parser.parse_args()

    # Get the rootdir from the command line arguments
    if args.rootdir:
        rootdir = args.rootdir
    elif 'INI_INVENTORY_FILENAME' in os.environ:
        rootdir = os.environ['INI_INVENTORY_FILENAME']
    else:
        rootdir = "/Users/idir/MyProjects/workspace/monitoring/inventory/pm0002"
        #msg('E', 'No inventory file provided.')

    data = {}
    mim = MyInventoryModule()

    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            #print os.path.join(subdir, file)
            filepath = subdir + os.sep + file

            if not filepath.endswith(".py"):
                try:
                    f = open(filepath)
                except Exception as e:
                    msg('E', 'Cannot open inventory file %s. %s' % (filepath, str(e)))

            group = 'all' 
            state = 'hosts'

            # Walk through the file and build the data structure
            for line in f:
                line = line.strip()

                # Skip comments and empty lines
                if line.startswith('#') or line.startswith(';') or len(line) == 0:
                    continue

                if line.startswith('['):
                    # Parse group
                    section = file+'_'+line[1:-1]

                    if ':' in line:
                        group, state = line[1:-1].split(':')
                    else:
                        group = section
                        state = 'hosts'

                    if group not in data:
                        data[group] = {}

                    if state not in data[group]:
                        if state == 'vars':
                            data[group][state] = {}
                        else:
                            data[group][state] = []
                else:
                    # Parse hosts or group members/vars
                    try:
                        tokens = shlex_split(line, comments=True)
                    except ValueError as e:
                        msg('E', "Error parsing host definition '%s': %s" % (line, e))

                    (hostnames, port) = mim._expand_hostpattern(tokens[0])

                    # Create 'all' group if no group was defined yet
                    if not 'all' in data:
                        group = 'all'
                        state = 'hosts'
                        data['all'] = {
                            'hosts': []
                        }

                    tok = []

                    if state == 'hosts':
                        tok = tokens[1:]
                    elif state == 'vars':
                        tok = tokens

                    variables = {}

                    for t in tok:
                        if '=' not in t:
                            msg(
                                'E',
                                "Expected key=value host variable assignment, "
                                "got: %s" % (t))

                        (k, v) = t.split('=', 1)
                        variables[k] = mim._parse_value(v)

                    if state == 'vars':
                        for key, val in variables.items():
                            data[group][state][key] = val
                    else:
                        for host in hostnames:
                            data[group][state].append(host)

                            if state == 'hosts' and len(variables):
                                if '_meta' not in data:
                                    data['_meta'] = {
                                        'hostvars': {}
                                    }

                                data['_meta']['hostvars'][host] = {}

                                for key, val in variables.items():
                                    data['_meta']['hostvars'][host][key] = val
                   
            #try:
            #    f.close()
            #except IOError as e:
            #    msg('E', 'Cannot close inventory file %s. %s' % (filepath, str(e)))

    data['all']['hosts'] = list(set(data['all']['hosts']))
    if args.list:
        print(json.dumps(data, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
