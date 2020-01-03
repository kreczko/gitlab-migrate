#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import codecs
import os
import glob
import re
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    global here
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def _is_valid_command(file_name):
    with open(file_name) as f:
        return 'def cli(' in f.read()


with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'numpy',
    'python-gitlab>=1.7.0',
    'pyyaml',
    'pandas',
]

setup_requirements = [
    # 'pytest-runner',
]

test_requirements = ['flake8', 'hypothesis', 'pytest',]

setup(
    author="Luke Kreczko",
    author_email='kreczko@cern.ch',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Commands to migrate repositories between GitLab servers",
    entry_points={
        'console_scripts': [
            'gitlab-migrate=gitlab_migrate.migrate:cli',
            'gitlab-migrate-info=gitlab_migrate.server_info:cli',
        ]
    },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='gitlab,migrate',
    name='gitlab-migrate',
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/kreczko/gitlab-migrate',
    version=find_version("gitlab_migrate", '__init__.py'),
    zip_safe=False,
)