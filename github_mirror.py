#!/usr/bin/env python
# See http://stackoverflow.com/questions/3581031/backup-mirror-github-repositories/13917251#13917251
# You can find the latest version of this script at
# https://gist.github.com/4319265
import os
import sys
import json
import urllib
import subprocess

__version__ = '0.2'
__author__ = 'Marius Gedminas <marius@gedmin.as>'
__url__ = 'https://gist.github.com/4319265'

# configuration
username = 'mgedmin'
backup_dir = os.path.expanduser('~/github')
gist_backup_dir = os.path.expanduser('~/github/gists')

# helpers
def ensure_dir(dir):
    if not os.path.isdir(dir):
        os.makedirs(dir)

def get_github_list(url):
    response = urllib.urlopen(url + '?per_page=100')
    if response.info().getheader('Link'):
        print >> sys.stderr, "error: pagination is not supported yet"
    return json.load(response)

def info(*args):
    print(" ".join(map(str, args)))
    sys.stdout.flush()

def backup(git_url, dir):
    if os.path.exists(dir):
        subprocess.call(['git', 'fetch'], cwd=dir)
    else:
        subprocess.call(['git', 'clone', '--mirror', git_url])

def update_description(git_dir, description):
    with open(os.path.join(git_dir, 'description'), 'w') as f:
        f.write(description + '\n')

# action
ensure_dir(gist_backup_dir)
os.chdir(gist_backup_dir)
for gist in get_github_list('https://api.github.com/users/%s/gists' % username):
    dir = gist['id'] + '.git'
    description = gist['description'] or "(no description)"
    info("+", "gists/" + gist['id'], "-", description.partition('\n')[0])
    backup(gist['git_pull_url'], dir)
    update_description(dir, description + '\n\n' + gist['html_url'])

ensure_dir(backup_dir)
os.chdir(backup_dir)
for repo in get_github_list('https://api.github.com/users/%s/repos' % username):
    dir = repo['name'] + '.git'
    description = repo['description'] or "(no description)"
    info("+", repo['full_name'])
    backup(repo['git_url'], dir)
    update_description(dir, description + '\n\n' + gist['html_url'])
