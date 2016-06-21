import argparse
import json
import os
import typing

import requests
import subprocess

import sys

"""The Github cloner"""

API_GITHUB_COM = 'https://api.github.com'

from github_cloner.types import *


def get_github_repositories(githubName: str,
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
    result = parse_github_repositories(repositories, repo_type)

    return result


def parse_github_repositories(repositories: dict, repo_type: RepoType) -> \
        typing.List[Repository]:
    """
    Parse the github repositories into our Repository objects

    :param repositories: a dict of the github json for repositories
    :param repo_type: enum denoting real Repos or Gists
    :return: A list of Repository objects
    """

    def _get_repository_url(repository: dict):
        if repo_type is RepoType.GIST:
            return repository['git_pull_url']
        else:
            return repository['ssh_url']

    def _get_repository_name(repository: dict):
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
    """
    If the repository already exists, perform a fetch. Otherwise perform a
    clone.
    The repository is cloned 'bare' i.e. with the --mirror flag

    :param git_url: The git url to clone/fetch from
    :param repository_path: The path to clone the repository to
    :returns: None
    :raises CalledProcessError: If any of the git processes failed
    """
    if os.path.isdir(repository_path):
        subprocess.check_call(['git', 'remote', 'set-url',
                               'origin',
                               git_url],
                              cwd=os.path.abspath(repository_path))
        subprocess.check_call(['git', 'fetch'],
                              cwd=os.path.abspath(repository_path))
    else:
        # dir.mkdir(parents=True,exist_ok=True)
        subprocess.check_call(['git', 'clone', '--mirror',
                               git_url])


def githubBackup(githubName: str,
                 user_type: UserType = UserType.USER,
                 repo_type: RepoType = RepoType.REPO):
    """
    Backup all repositories from a specific user/org on github to current
    working dir

    :param githubName: The name of the organisation/user on github
    :param user_type: enum USER or ORG
    :param repo_type: enum REPO or GIST
    :return: None
    :raises CalledProcessError: If any of the git processes failed
    """
    repositories = get_github_repositories(githubName, user_type, repo_type)
    for repository in repositories:
        fetchOrClone(repository.url, repository.name + '.git')


def main():
    """
    Parse command line args and backup the github repos

    :param argv: the command line arguments
    :return: None
    """
    parser = argparse.ArgumentParser(
        description='Clones github repositories and github gists')
    parser.add_argument('--org', action='append',
                        help='The github organisation to backup', dest='orgs')
    parser.add_argument('--user', action='append',
                        help='The github user to backup', dest='users')
    args = parser.parse_args(sys.argv[1:])
    for org in args.orgs or []:
        for repoType in RepoType:
            githubBackup(githubName=org, user_type=UserType.ORG,
                         repo_type=repoType)
    for user in args.users or []:
        for repoType in RepoType:
            githubBackup(githubName=user, user_type=UserType.USER,
                         repo_type=repoType)


# action
if __name__ == '__main__':
    main()
