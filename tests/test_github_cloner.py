#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_github_cloner
----------------------------------

Tests for `github_cloner` module.
"""


import unittest

#from github_cloner import github_cloner

import requests
import requests_mock

class TestGithub_cloner(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_000_something(self):
        with requests_mock.Mocker() as m:
            m.get('http://test.com', text='resp')
            print(requests.get('http://test.com').text)



if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
