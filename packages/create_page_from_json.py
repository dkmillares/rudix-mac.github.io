#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import re
import argparse
import hashlib

from json import loads
from cgi import escape
from distutils.version import LooseVersion
from datetime import date

SITE = 'https://raw.githubusercontent.com/rudix-mac/packages/2015/{osx}/'
PACKAGE = SITE + '/{package}'
DOWNLOAD = '/Users/ruda/Projects/rudix-packages/{osx}/'
MANIFEST = DOWNLOAD + '/00MANIFEST.txt'

OSX_NAMES = {'10.9': 'Mavericks',
             '10.8': 'Mountain Lion',
             '10.7': 'Lion',
             '10.6': 'Snow Leopard',
             '10.10': 'Yosemite'}

OSX_VERSIONS = ['10.10', '10.9', '10.8', '10.7', '10.6']

def version_compare(v1, v2):
    'Compare software version'
    ver_rel_re = re.compile('([^-]+)-(\d+)$')
    v1, r1 = ver_rel_re.match(v1).groups()
    v2, r2 = ver_rel_re.match(v2).groups()
    v_cmp = cmp(LooseVersion(v1), LooseVersion(v2))
    # if they are in the same version, then compare the revision
    if v_cmp == 0:
        if r1 is None:
            r1 = 0
        if r2 is None:
            r2 = 0
        return cmp(int(r1), int(r2))
    else:
        return v_cmp

def parse_manifest(source):
    pat = re.compile(r'(.+)-([^-]+-\d+)\.pkg')
    return re.findall(pat, source)

def parse_all_manifests():
    m = {}
    for version in OSX_VERSIONS:
        src = open(MANIFEST.format(osx=version)).read()
        m[version] = parse_manifest(src)
    return m

def latest_version(manifest, name):
    versions = [x for x in manifest if x[0] == name]
    versions = sorted(list(set(versions)),
                      reverse=True,
                      cmp=lambda x, y: version_compare(x[1], y[1]))
    if versions:
        pkg = '%s-%s.pkg' % versions[0]
    else:
        pkg = None
    return pkg

def update_downloads(manifests, d):
    d['downloads'] = []
    for version in OSX_VERSIONS:
        latest = latest_version(manifests[version],
                                d['name'])
        if not latest:
            continue
        path = os.path.join(DOWNLOAD.format(osx=version), latest)
        stat = os.stat(path)
        ts = stat.st_mtime
        size = stat.st_size / float(1024 * 1024)
        dt = date.fromtimestamp(ts)
        h = hashlib.sha1()
        h.update(open(path).read())
        sha = h.hexdigest()
        del h
        url = SITE.format(osx=version)
        x = {'url': url, 'pkg': latest, 'osx': version, 'date': dt, 'size': size, 'sha1': sha}
        d['downloads'].append(x)
    return d

def update_port(d):
    link = 'https://github.com/rudix-mac/rudix/tree/2015/Ports/%s' % d['name']
    d['port'] = '<a href="%s">%s</a>' % (link, link)
    return d

def update_notes(d):
    if d.has_key('notes'):
        if isinstance(d['notes'], str):
            d['notes'] = [d['notes']]
    else:
        d['notes'] = ['Upgraded to version %s' % d.get('version', '?')]
    n = ['<li>%s</li>' % x for x in d['notes']]
    d['notes'] = '\n'.join(n)
    return d

def update_files(d):
    name_files = d['name'] + '.files'
    try:
        with open(name_files) as nf:
            d['files'] = ['<h3 id="files">Files</h3>']
            lines = nf.readlines()
            d['files'].extend([x.strip() + '<br>' for x in lines])
            d['files'] = '\n'.join(d['files'])
    except:
        d['files'] = ''
    return d

def output_html(stream, template, package):
    package['site'] = '<a href="%s">%s</a>' % (package['site'], package['site'])
    package['title'] = escape(package['title'])
    package['description'] = escape(package['description'])
    # Install and usage
    if not package.has_key('install'):
        package['install'] = 'sudo rudix install %s' % package['name']
    if not package.has_key('usage'):
        package['usage'] = '%s --help' % package['name']
    # Expand downloads
    downloads = []
    downloads.append('<tr><th>OS X</th><th>Latest Version</th><th>Date</th><th>Size (MB)</th><th>SHA1</th></tr>')
    for download in package['downloads']:
        downloads.append('<tr>')
        downloads.append('  <td>%s (%s)</td>' % (OSX_NAMES[download['osx']], download['osx']))
        downloads.append('  <td><a href="%s">%s</a></td>' % ( download['url']+download['pkg'], download['pkg']))
        downloads.append('  <td>%s</td>' % download['date'])
        downloads.append('  <td>%.2f</td>' % download['size'])
        downloads.append('  <td><small>%s</small></td>' % download['sha1'])
        downloads.append('</tr>')
    package['downloads'] = '\n'.join(downloads)
    html = template.format(**package)
    stream.write(html)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', type=argparse.FileType('w'),
                        default=sys.stdout)
    parser.add_argument('template_file', type=str)
    parser.add_argument('package_info_file', type=str)
    args = parser.parse_args()
    manifests = parse_all_manifests()
    tmpl = open(args.template_file).read()
    d = loads(open(args.package_info_file).read())
    d = update_downloads(manifests, d)
    d = update_port(d)
    d = update_notes(d)
    d = update_files(d)
    output_html(args.output, tmpl, d)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
