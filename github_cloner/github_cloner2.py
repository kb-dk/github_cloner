import argparse
import typing
import enum
from pathlib import Path

import requests
import subprocess

API_GITHUB_COM = 'https://api.github.com'

Url = str

Repo = typing.NamedTuple('Repo', [('name', str), ('description', str),
                                  ('url', Url)])


class UserType(enum.Enum):
    USER = 'users'
    ORG = 'orgs'


class RepoType(enum.Enum):
    REPO = 'repos'
    GIST = 'gists'


def getRepos(githubName: str,
             user_type: UserType,
             repo_type: RepoType,
             batch_size: int = 100) -> typing.List[Repo]:
    """
    Format of the JSON is documented at
     http://developer.github.com/v3/repos/#list-organization-repositories

    Supports batching (which Github indicates by the presence of a Link header,
    e.g. ::

        Link: <https://api.github.com/resource?page=2>; rel="next",
              <https://api.github.com/resource?page=5>; rel="last"

    """
    # API documented at http://developer.github.com/v3/#pagination
    githubUrl = '{github}/{userType}/{name}/{repoType}'.format(
        github=API_GITHUB_COM, userType=user_type.value, name=githubName,
        repoType=repo_type.value)

    r = requests.get(githubUrl, params={"per_page": batch_size})
    repos = r.json()

    page = 1
    while 'rel="next"' in r.headers.get('Link', ''):
        page += 1
        r = requests.get(githubUrl, params={"page": page, "per_page":
            batch_size})
        repos += r.json()

    result = [Repo(name=repo.get('name', repo['id']),
                   description=repo['description'] or "(no description)",
                   url=repo.get('ssh_url', None) or repo['git_pull_url']) for
              repo in repos]
    return result


def fetchOrClone(git_url: Url, directory: Path):
    if directory.is_dir():
        subprocess.call(['git', 'fetch'], cwd=str(directory.absolute()))
    else:
        # dir.mkdir(parents=True,exist_ok=True)
        subprocess.call(['git', 'clone', '--mirror', git_url])


def backup(name: str,
           user_type: UserType = UserType.USER,
           repo_type: RepoType = RepoType.REPO):
    for repo in getRepos(name, user_type, repo_type):
        fetchOrClone(repo.url, Path(repo.name + '.git'))


# Args
parser = argparse.ArgumentParser(
    description='Clones github repositories and github gists')
parser.add_argument('--org', action='append',
                    help='The github organisation to backup', dest='orgs')
parser.add_argument('--user', action='append',
                    help='The github user to backup', dest='users')

args = parser.parse_args()

# action
if __name__ == '__main__':
    for org in args.orgs or []:
        for repoType in RepoType:
            backup(name=org, user_type=UserType.ORG, repo_type=repoType)
    for user in args.users or []:
        for repoType in RepoType:
            backup(name=user, user_type=UserType.USER, repo_type=repoType)
