#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_github_cloner
----------------------------------

Tests for `github_cloner` module.
"""
import json
import unittest
from pathlib import Path

import requests
import requests_mock

import github_cloner

curdir = Path(__file__).parent


class TestGithub_cloner(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_repositories(self):
        with Path(curdir, 'repositories.json').open() as jsonFile:
            repositories_github = json.load(jsonFile)
        repositories = github_cloner.parse_repositories(repositories_github,
                                                        github_cloner.RepoType.REPO)
        self.assertEqual(len(repositories), 3)
        repo1 = repositories[0]
        repo2 = repositories[1]
        repo3 = repositories[2]
        self.assertEqual(repo1.name, 'akubra-jdbc')
        self.assertEqual(repo1.url, 'git@github.com:blekinge/akubra-jdbc.git')
        self.assertEqual(repo2.name, 'altoviewer')
        self.assertEqual(repo2.url, 'git@github.com:blekinge/altoviewer.git')
        self.assertEqual(repo3.name, 'cloudera-vmware-setup')
        self.assertEqual(repo3.url,
                         'git@github.com:blekinge/cloudera-vmware-setup.git')

    def test_parse_repositories_gists(self):
        with Path(curdir, 'gists.json').open() as jsonFile:
            repositories_github = json.load(jsonFile)
        repositories = github_cloner.parse_repositories(repositories_github,
                                                        github_cloner.RepoType.GIST)
        self.assertEqual(len(repositories), 1)
        repo1 = repositories[0]
        self.assertEqual(repo1.name, '84981145fe5cc7860b65e39bc0f27fb7')
        self.assertEqual(repo1.url, 'https://gist.github.com/84981145fe5cc7860b65e39bc0f27fb7.git')

    def test_clone_repository(self):
        #github_cloner.
        pass

    def test_000_something(self):
        with requests_mock.Mocker() as m:
            m.get('http://test.com', text='resp')
            print(requests.get('http://test.com').text)

#
# if __name__ == '__main__':
#     import sys
#     sys.exit(unittest.main())
