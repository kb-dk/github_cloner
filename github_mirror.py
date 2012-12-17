#!/usr/bin/env python
# See http://stackoverflow.com/questions/3581031/backup-mirror-github-repositories/13917251#13917251
import os
import json
import urllib
import subprocess
os.chdir(os.path.expanduser('~/github'))
username = 'mgedmin'
url = 'https://api.github.com/users/%s/repos?per_page=100' % username
for repo in json.load(urllib.urlopen(url)):
    print "+", repo['full_name']
    if os.path.exists(repo['name']):
        subprocess.call(['git', 'pull'], cwd=repo['name'])
    else:
        subprocess.call(['git', 'clone', repo['git_url']])