#!/usr/bin/env python

import os
from setuptools import find_packages, setup

execfile('llama/version.py')

with open('requirements.txt') as fh:
    required = fh.read().splitlines()

setup(
    name='llama',
    version=str(__version__),
    description='LLAMA - Loss & LAtency MAtrix',
    url='https://github.com/dropbox/llama',
    author='Bryan Reed',
    maintainer='Bryan Reed',
    author_email='breed@dropbox.com',
    maintainer_email='breed@dropbox.com.',
    license='Apache',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Networking :: Monitoring',
    ],
    keywords='llama udp loss latency matrix probe packet',
    scripts=['bin/llama_collector'],
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=required,
)
