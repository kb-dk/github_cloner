#!/usr/bin/env python3
# See http://stackoverflow.com/questions/3581031/backup-mirror-github-repositories/13917251#13917251
# You can find the latest version of this script at
# https://gist.github.com/4319265
import os
import sys
import json
import urllib.request
import subprocess
import argparse

__version__ = '0.4'
__author__ = 'Marius Gedminas <marius@gedmin.as> and Asger Askov Blekinge <abr@statsbiblioteket.dk>'
__url__ = 'https://gist.github.com/blekinge/84981145fe5cc7860b65e39bc0f27fb7'

# configuration
repos_dir=os.path.join(os.getcwd(), "repos")
gists_dir=os.path.join(os.getcwd(), "gists")


# helpers

class Error(Exception):
    """An error that is not a bug in this script."""


def ensure_dir(dir):
    if not os.path.isdir(dir):
        os.makedirs(dir)


def get_json_and_headers(url):
    """Perform HTTP GET for a URL, return deserialized JSON and headers.

    Returns a tuple (json_data, headers) where headers is an instance
    of email.message.Message (because that's what urllib gives us).
    """
    with urllib.request.urlopen(url) as r:
        # We expect Github to return UTF-8, but let's verify that.
        content_type = r.info().get('Content-Type', '').lower()
        if content_type not in ('application/json; charset="utf-8"',
                                'application/json; charset=utf-8'):
            raise Error('Did not get UTF-8 JSON data from {0}, got {1}'
                        .format(url, content_type))
        return json.loads(r.read().decode('UTF-8')), r.info()


def get_github_list(url, batch_size=100):
    """Perform (a series of) HTTP GETs for a URL, return deserialized JSON.

    Format of the JSON is documented at
    http://developer.github.com/v3/repos/#list-organization-repositories

    Supports batching (which Github indicates by the presence of a Link header,
    e.g. ::

        Link: <https://api.github.com/resource?page=2>; rel="next",
              <https://api.github.com/resource?page=5>; rel="last"

    """
    # API documented at http://developer.github.com/v3/#pagination
    res, headers = get_json_and_headers('{0}?per_page={1}'.format(
        url, batch_size))
    page = 1
    while 'rel="next"' in headers.get('Link', ''):
        page += 1
        more, headers = get_json_and_headers('{0}?page={1}&per_page={2}'.format(
            url, page, batch_size))
        res += more
    return res


def info(*args):
    print(" ".join(map(str, args)))
    sys.stdout.flush()


def backup(git_url, dir):
    if os.path.exists(dir):
        subprocess.call(['git', 'fetch'], cwd=dir)
    else:
        subprocess.call(['git', 'clone', '--mirror', git_url])


def update_description(git_dir, description):
    with open(os.path.join(git_dir, 'description'), 'w', encoding='UTF-8') as f:
        f.write(description + '\n')


def update_cloneurl(git_dir, cloneurl):
    with open(os.path.join(git_dir, 'cloneurl'), 'w') as f:
        f.write(cloneurl + '\n')


def back_up_gists_of_user(username):
    gist_dir = os.path.join(gists_dir, username)
    ensure_dir(gist_dir)
    os.chdir(gist_dir)
    for gist in get_github_list('https://api.github.com/users/%s/gists' % username):
        dir = gist['id'] + '.git'
        description = gist['description'] or "(no description)"
        info("+", "gists/" + gist['id'], "-", description.partition('\n')[0])
        backup(gist['git_pull_url'], dir)
        update_description(dir, description + '\n\n' + gist['html_url'])
        update_cloneurl(dir, gist['git_push_url'])

def back_up_gists_of_org(orgname):
    gist_dir = os.path.join(gists_dir, orgname)
    ensure_dir(gist_dir)
    os.chdir(gist_dir)
    for gist in get_github_list('https://api.github.com/users/%s/gists' % orgname):
        dir = gist['id'] + '.git'
        description = gist['description'] or "(no description)"
        info("+", "gists/" + gist['id'], "-", description.partition('\n')[0])
        backup(gist['git_pull_url'], dir)
        update_description(dir, description + '\n\n' + gist['html_url'])
        update_cloneurl(dir, gist['git_push_url'])


def back_up_repos_of_user(username):
    repo_dir = os.path.join(repos_dir, username)
    ensure_dir(repo_dir)
    os.chdir(repo_dir)
    for repo in get_github_list('https://api.github.com/users/%s/repos' % username):
        dir = repo['name'] + '.git'
        description = repo['description'] or "(no description)"
        info("+", repo['full_name'])
        backup(repo['git_url'], dir)
        update_description(dir, description + '\n\n' + repo['html_url'])
        update_cloneurl(dir, repo['ssh_url'])

def back_up_repos_of_org(orgname):
    repo_dir = os.path.join(repos_dir, orgname)
    ensure_dir(repo_dir)
    os.chdir(repo_dir)
    for repo in get_github_list('https://api.github.com/orgs/%s/repos' % orgname):
        dir = repo['name'] + '.git'
        description = repo['description'] or "(no description)"
        info("+", repo['full_name'])
        backup(repo['git_url'], dir)
        update_description(dir, description + '\n\n' + repo['html_url'])
        update_cloneurl(dir, repo['ssh_url'])


parser = argparse.ArgumentParser(description='Clones github repositories and github gists')
parser.add_argument('--org', action='append',
                    help='The github organisation to backup', dest='orgs')
parser.add_argument('--user', action='append',
                    help='The github user to backup', dest='users')

args = parser.parse_args()
# action
if __name__ == '__main__':
    for org in args.orgs or []:
        back_up_gists_of_org(org)
        back_up_repos_of_org(org)
    for user in args.users or []:
        back_up_gists_of_user(user)
        back_up_repos_of_user(user)
