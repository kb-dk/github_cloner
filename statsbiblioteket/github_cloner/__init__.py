# -*- coding: utf-8 -*-

# Set default logging handler to avoid "No handler found" warnings.
import logging

# Methods
from statsbiblioteket.github_cloner.github_cloner \
    import \
    github_backup, \
    fetch_or_clone, \
    get_github_repositories, \
    parse_github_repositories, \
    create_parser  # This import is important for the sphinx-argparse docs

# Types
from statsbiblioteket.github_cloner.github_cloner import \
    RepoType, \
    UserType, \
    Repository, \
    Url, \
    Path

__author__ = 'Asger Askov Blekinge'
__email__ = 'asger.askov.blekinge@gmail.com'
__version__ = '0.2.1rc'

logging.getLogger(__name__).addHandler(logging.NullHandler())
