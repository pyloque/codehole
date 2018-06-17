# pylint: disable=all

import os

from setuptools import setup, find_packages

f = open(os.path.join(os.path.dirname(__file__), 'version.txt'))
version = f.read().strip()
f.close()

setup(
    name="codehole",
    version=version,
    description="codehole site",
    author="qianwp",
    author_email="holycoder@163.com",
    license="MIT",
    packages=find_packages(),
    keywords=['codehole'])
