#!/usr/bin/env python
# coding=utf-8

import json
import glob

from cgi import escape


def read_index_template(filename='index.html.in'):
    f = open(filename) 
    data = f.read()
    f.close()
    return data

def build_table(jsons):
    rows = []
    row = '<tr><td><a href="{link}">{name}</a></td><td>{version}</td><td>{title}</td></tr>'
    for j in jsons:
        with open(j) as f:
            data = json.load(f)
            if data.has_key('notes'):
                del data['notes']
            if data.has_key('downloads'):
                del data['downloads']
            data['link'] = '{name}.html'.format(name=data['name'])
            data = {k:escape(v) for k, v in data.items()}
            html = row.format(**data)
            rows.append(html)
    return rows


if __name__ == '__main__':
    tpl = read_index_template()
    rows = [' ' * 8 + x for x in build_table(glob.glob('*.json'))]
    rows = '\n'.join(rows)
    html = tpl.format(packages=rows)
    print html

# vim:tabstop=8 expandtab shiftwidth=4 softtabstop=4
