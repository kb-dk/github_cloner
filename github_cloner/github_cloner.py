import argparse
import json
import typing
import enum
from pathlib import Path

import requests
import subprocess

import sys

API_GITHUB_COM = 'https://api.github.com'

Url = str

Repository = typing.NamedTuple('Repository', [('name', str),
                                        ('description', str),
                                        ('url', Url)])


class UserType(enum.Enum):
    USER = 'users'
    ORG = 'orgs'


class RepoType(enum.Enum):
    REPO = 'repos'
    GIST = 'gists'


def get_repositories(githubName: str,
                     user_type: UserType,
                     repo_type: RepoType,
                     batch_size: int = 100) -> typing.List[Repository]:
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
    repositories = r.json()

    page = 1
    while 'rel="next"' in r.headers.get('Link', ''):
        page += 1
        r = requests.get(githubUrl, params={"page": page, "per_page":
            batch_size})
        repositories += r.json()
    # print(json.dumps(repositories))
    result = parse_repositories(repositories, repo_type)

    return result


def parse_repositories(repositories: typing.Dict, repo_type: RepoType) -> \
        typing.List[Repository]:
    def _get_repository_url(repository: Repository):
        if repo_type is RepoType.GIST:
            return repository['git_pull_url']
        else:
            return repository['ssh_url']

    def _get_repository_name(repository: Repository):
        if repo_type is RepoType.GIST:
            return repository['id']
        else:
            return repository['name']

    result = [Repository(name=_get_repository_name(repository),
                         description=repository[
                                         'description'] or "(no description)",
                         url=_get_repository_url(repository)) for
              repository in repositories]
    return result


def fetchOrClone(git_url: Url, repository_path: Path):
    if repository_path.is_dir():
        subprocess.call(['git', 'remote', 'set-url', 'origin', git_url],
                        cwd=str(repository_path.absolute()))
        subprocess.call(['git', 'fetch'],
                        cwd=str(repository_path.absolute()))
    else:
        # dir.mkdir(parents=True,exist_ok=True)
        subprocess.call(['git', 'clone', '--mirror', git_url])


def backup(githubName: str,
           user_type: UserType = UserType.USER,
           repo_type: RepoType = RepoType.REPO):
    repositories = get_repositories(githubName, user_type, repo_type)
    for repository in repositories:
        fetchOrClone(repository.url, Path(repository.name + '.git'))



def main(args):
    # Args
    parser = argparse.ArgumentParser(
        description='Clones github repositories and github gists')
    parser.add_argument('--org', action='append',
                        help='The github organisation to backup', dest='orgs')
    parser.add_argument('--user', action='append',
                        help='The github user to backup', dest='users')
    args = parser.parse_args(args[1:])
    for org in args.orgs or []:
        for repoType in RepoType:
            backup(githubName=org, user_type=UserType.ORG, repo_type=repoType)
    for user in args.users or []:
        for repoType in RepoType:
            backup(githubName=user, user_type=UserType.USER,
                   repo_type=repoType)


# action
if __name__ == '__main__':
    main(args=sys.argv)
