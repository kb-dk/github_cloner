#!/usr/bin/env python
# See http://stackoverflow.com/questions/3581031/backup-mirror-github-repositories/13917251#13917251
# You can find the latest version of this script at
# https://gist.github.com/4319265
import os
import sys
import json
import urllib
import subprocess

# configuration
username = 'mgedmin'
backup_dir = os.path.expanduser('~/github')

# action
if not os.path.isdir(backup_dir):
    os.makedirs(backup_dir)
os.chdir(backup_dir)
url = 'https://api.github.com/users/%s/repos?per_page=100' % username
response = urllib.urlopen(url)
for repo in json.load(response):
    print "+", repo['full_name']
    sys.stdout.flush()
    if os.path.exists(repo['name']):
        subprocess.call(['git', 'pull'], cwd=repo['name'])
    else:
        subprocess.call(['git', 'clone', repo['git_url']])
if response.info().getheader('Link'):
    # looks like you've got more than 100 repositories
    print >> sys.stderr, "error: pagination is not supported yet"