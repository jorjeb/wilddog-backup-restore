# -*- coding: utf-8 -*-
from wilddog import wilddog, jsonutil

import argparse
import json
import os
import re


def backup(app, path, output_dir, order_by, start, limit):
    file_name = re.sub('^\/*|\/*$', '', path)
    file_name = file_name.replace('/', '_')

    if file_name == '':
        file_name = 'root'

    while True:
        part = re.sub('[^\w]+', '', start)
        result = app.get(path, None, {'orderBy': order_by, 'startAt': start, 'limitToFirst': limit})
        
        if result is not None:
            start = sorted(result.keys())[-1]
            json_file = os.path.abspath('{}/{}_{}.json'.format(output_dir, file_name, part))

            with open(json_file, 'w') as json_output_file:
                json_output_file.write(json.dumps(result, cls=jsonutil.JSONEncoder))
        else:
            break


def restore(app, path, json_file, limit=10):
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
    parser.add_argument('-p', '--path', type=str, help='Node path')
    parser.add_argument('-a', '--action', type=str,
                        choices=['backup', 'restore'])

    #  backup
    parser.add_argument('-O', '--order_by', type=str, help='Sort nodes by')
    parser.add_argument('-S', '--start', type=str, help='Starting point')
    parser.add_argument('-l', '--limit', type=int, 
                        help='Number of nodes to fetch per request')
    parser.add_argument('-o', '--output_dir', type=str,
                        help='Output directory')

    #  restore
    parser.add_argument('-j', '--json_file', type=str,
                        help='JSON file to restore')

    args = parser.parse_args()

    app = wilddog.WilddogApplication(args.url, None)

    if args.action == 'backup':
        backup(app, args.path, args.output_dir, args.order_by, args.start, 
               args.limit)
    elif args.action == 'restore':
        restore(app, args.path, args.json_file)