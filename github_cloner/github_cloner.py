#!/usr/bin/env python2
# See http://stackoverflow.com/questions/3581031/backup-mirror-github-repositories/13917251#13917251
import os, io, sys
import requests
import subprocess
import argparse
from flufl.enum import Enum




API_GITHUB_COM = 'https://api.github.com'

__version__ = 'b0.4'
__author__ = 'Marius Gedminas <marius@gedmin.as> and Asger Askov Blekinge <abr@statsbiblioteket.dk>'
__url__ = 'https://gist.github.com/blekinge/84981145fe5cc7860b65e39bc0f27fb7'

# configuration
repos_dir=os.path.join(os.getcwd(), "repos")
gists_dir=os.path.join(os.getcwd(), "gists")


# helpers

class Error(Exception):
    """An error that is not a bug in this script."""

class UserType(Enum):
    USER = 'users'
    ORG = 'orgs'

class RepoType(Enum):
    REPO = 'repos'
    GIST = 'gists'



def ensure_dir(dir):
    if not os.path.isdir(dir):
        os.makedirs(dir)


def get_json_and_headers(url):
    """Perform HTTP GET for a URL, return deserialized JSON and headers.

    Returns a tuple (json_data, headers) where headers is an instance
    of email.message.Message (because that's what urllib gives us).
    """
    r = requests.get(url)
    return r.json(), r.headers


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
    print((" ".join(map(str, args))))
    sys.stdout.flush()


def backup(git_url, dir):
    if os.path.exists(dir):
        subprocess.call(['git', 'fetch'], cwd=dir)
    else:
        subprocess.call(['git', 'clone', '--mirror', git_url])


def update_description(git_dir, description):
    with io.open(file=os.path.join(git_dir, 'description'), mode='w', encoding='UTF-8') as f:
        f.write(description + '\n')


def update_cloneurl(git_dir, cloneurl):
    with open(os.path.join(git_dir, 'cloneurl'), 'w') as f:
        f.write(cloneurl + '\n')


def back_up(name, userType=UserType.USER, repoType=RepoType.REPO):
    gist_dir = os.path.join(gists_dir, name)
    ensure_dir(gist_dir)
    os.chdir(gist_dir)
    githubUrl = '{github}/{userType}/{name}/{repoType}'.format(github=API_GITHUB_COM, userType=userType.value, name=name,
                                                                  repoType=repoType.value)
    print(githubUrl)
    for repo in get_github_list(githubUrl):
        dir = repo.get('name', repo['id']) + '.git'
        description = repo['description'] or "(no description)"
        info("+", repoType.value + '/' + repo.get('name',repo['id']), "-", description.partition('\n')[0])
        backup(repo.get('ssh_url', None) or repo['git_pull_url'], dir)
        update_description(dir, description + '\n\n' + repo['html_url'])
        update_cloneurl(dir, repo.get('ssh_url', None) or repo['git_push_url'])


parser = argparse.ArgumentParser(description='Clones github repositories and github gists')
parser.add_argument('--org', action='append',
                    help='The github organisation to backup', dest='orgs')
parser.add_argument('--user', action='append',
                    help='The github user to backup', dest='users')

args = parser.parse_args()
# action
if __name__ == '__main__':
    for org in args.orgs or []:
        for repoType in RepoType:
            back_up(org,userType=UserType.ORG,repoType=repoType)
    for user in args.users or []:
        for repoType in RepoType:
            back_up(user,userType=UserType.USER,repoType=repoType)
