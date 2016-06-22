#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_github_cloner
----------------------------------

Tests for `github_cloner` module.
"""
import json

import os
import pytest
import shutil

from statsbiblioteket.github_cloner.github_cloner import \
    parse_github_repositories, fetch_or_clone
from statsbiblioteket.github_cloner import RepoType

curdir = os.path.dirname(os.path.realpath(__file__))


class TestGithubCloner:
    @pytest.fixture()
    def repositories(self):
        with open(curdir + '/repositories.json') as jsonFile:
            return json.load(jsonFile)

    @pytest.fixture()
    def gists(self):
        with open(curdir + '/gists.json') as jsonFile:
            return json.load(jsonFile)

    @pytest.fixture()
    def tempdir(self):
        import tempfile
        return tempfile.mkdtemp()

    def test_parse_repositories(self, repositories):
        repositories_parsed = parse_github_repositories(
            repositories,
            RepoType.REPO)
        assert len(repositories_parsed) == 3
        repo1 = repositories_parsed[0]
        repo2 = repositories_parsed[1]
        repo3 = repositories_parsed[2]
        assert repo1.name == 'akubra-jdbc'
        assert repo1.url == 'git@github.com:blekinge/akubra-jdbc.git'
        assert repo2.name == 'altoviewer'
        assert repo2.url == 'git@github.com:blekinge/altoviewer.git'
        assert repo3.name == 'cloudera-vmware-setup'
        assert repo3.url == 'git@github.com:blekinge/cloudera-vmware-setup' \
                            '.git'

    def test_parse_repositories_gists(self, gists):
        repositories = parse_github_repositories(gists,
                                                 RepoType.GIST)
        assert len(repositories) == 1
        repo1 = repositories[0]
        assert repo1.name == '84981145fe5cc7860b65e39bc0f27fb7'
        assert \
            repo1.url == \
            'https://gist.github.com/84981145fe5cc7860b65e39bc0f27fb7.git'

    def test_clone_repository(self, tempdir):
        os.chdir(tempdir)
        path = '84981145fe5cc7860b65e39bc0f27fb7' + '.git'
        fetch_or_clone(
            git_url='https://gist.github.com'
                    '/84981145fe5cc7860b65e39bc0f27fb7.git',
            repository_path=path)

        contents = [file for file in os.listdir(path)]
        expected = ['hooks', 'HEAD', 'config', 'objects', 'branches',
                    'packed-refs', 'description', 'info', 'refs']
        assert sorted(contents) == sorted(expected)
        shutil.rmtree(path)
