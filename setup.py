# -*- coding: utf-8 -*-
# See here for more options:
# <http://pythonhosted.org/setuptools/setuptools.html>
import os
from setuptools import setup, find_packages

NAME = "kafkfa_extractor"
VERSION = "0.0.1"

REQUIRES = [
    "confluent-kafka==1.1.0",
    "pyyaml==5.1.2",
]

def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()

setup_dict = dict(
    name=NAME,
    version=VERSION,
    description="NI-Mon submodule",
    author_email="vantu.bkhn@gmail.com",
    url="",
    install_requires=REQUIRES,
    packages=find_packages(),
    # packages=find_packages(exclude=(TESTS_DIRECTORY,)),
    include_package_data=True,
    long_description=read('README.md'),
    zip_safe=False,  # don't use eggs
    entry_points={
        'console_scripts': [
            'kafka_extractor_cli = kafka_extractor.collectd_extractor:main'
        ],
    }
)

if __name__ == '__main__':
    setup(**setup_dict)
