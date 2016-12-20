# -*- coding: utf-8 -*-
from wilddog import wilddog, jsonutil

import argparse
import json
import os
import re


def backup(app, path, output_dir):
    result = app.get(path, None)

    path = re.sub('^\/*|\/*$', '', path)
    path = path.replace('/', '_')

    if path == '':
        path = 'root'

    json_file = os.path.abspath('{}/{}.json'.format(output_dir, path))

    with open(json_file, 'w') as json_output_file:
        json_output_file.write(json.dumps(result, cls=jsonutil.JSONEncoder))


def restore(app, path, json_file):
    path = re.sub('^\/*|\/*$', '', path)
    path = '/{}'.format(path).split('/')

    snapshot_name = path.pop()
    path = '/{}'.format('/'.join(path))

    assert snapshot_name, 'Specify path other than "/"'

    json_file = os.path.abspath(json_file)

    with open(json_file, 'r') as json_output_file:
        data = json.load(json_output_file)
        app.put(path, snapshot_name, data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', type=str, help='Wilddog URL')
    parser.add_argument('-s', '--secret', type=str, help='Wilddog secret')
    parser.add_argument('-e', '--email', type=str, help='Wilddog email')
    parser.add_argument('-p', '--path', type=str, help='Node path')
    parser.add_argument('-a', '--action', type=str,
                        choices=['backup', 'restore'])

    #  backup
    parser.add_argument('-o', '--output_dir', type=str,
                        help='Output directory')

    #  restore
    parser.add_argument('-j', '--json_file', type=str,
                        help='JSON file to restore')

    args = parser.parse_args()

    app = wilddog.WilddogApplication(args.url, None)

    if args.action == 'backup':
        backup(app, args.path, args.output_dir)
    elif args.action == 'restore':
        restore(app, args.path, args.json_file)
