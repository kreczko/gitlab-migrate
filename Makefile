.PHONY: clean clean-test clean-pyc clean-build docs help
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

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	@rm -fr build/
	@rm -fr dist/
	@rm -fr .eggs/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	@rm -fr .tox/
	@rm -f .coverage
	@rm -fr htmlcov/
	@rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 gitlab_migrate tests --ignore=D301,D400,E302,E402,D100,D103,D104,Q000,I001,I003,I004,N806 --max-line-length=120

test: ## run tests quickly with the default Python
	@python -m pytest -vv

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source gitlab_migrate -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -fr docs/reference
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

pypi-release: dist ## package and upload a release
	twine upload dist/*


changelog:
	@echo "Updating CHANGELOG.md"
	@github_changelog_generator -u kreczko -p gitlab-migrate -t ${CHANGELOG_GITHUB_TOKEN}
	@echo "Updating HISTORY.rst"
	#@gitchangelog ^v`<gitlab-migrate-version>` HEAD | cat - HISTORY.rst > HISTORY.tmp
	@mv HISTORY.tmp HISTORY.rst

update_release:
	@python update_release.py
	@echo "Check everything and if OK, execute"
	@echo "git add -u"
	@echo "git commit -m 'tagged version ${RELEASE}'"
	@echo "git push upstream master"
	@echo "git tag v${RELEASE}"
	@echo "git push upstream v${RELEASE}"


release: changelog update_release

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	@python setup.py -q install

install-dev: clean
	python -m pip install -U -e .