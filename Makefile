.PHONY: clean-pyc clean-build docs help
.DEFAULT_GOAL := help
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@perl -nle'print $& if m{^[a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

clean: clean-build clean-pyc clean-test clean-docs
## remove all build, test, coverage and Python artifacts

clean-docs: ## remove build docs
	rm -f docs/statsbiblioteket.rst
	rm -f docs/statsbiblioteket.github_cloner.rst
	rm -f docs/modules.rst
	$(MAKE) -C docs clean


clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint: ## check style with flake8
	flake8 statsbiblioteket tests

test: ## run tests quickly with the default Python
		python setup.py test

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
		coverage run --source statsbiblioteket setup.py test
	    coverage report -m
		coverage html
		$(BROWSER) htmlcov/index.html

docs: clean-docs ## generate Sphinx HTML documentation, including API docs
	sphinx-apidoc -o docs/ statsbiblioteket
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

_git-push-tags:
	git push --tags

_release-minor:
	bumpversion minor

release-minor: clean _release-minor deploy _git-push-tags

_release-major:
	bumpversion major

release-major: clean _release-major deploy _git-push-tags

_release-patch:
	bumpversion patch

release-patch: clean _release-patch deploy _git-push-tags


deploy:
	python setup.py register
	python setup.py sdist upload
	python setup.py bdist_wheel upload
	python setup.py upload_docs

dist: clean docs ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

develop:
	pip install -U -r requirements_dev.txt
