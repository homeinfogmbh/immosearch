#! /usr/bin/env python3
"""Install script."""

from setuptools import setup

setup(
    name="immosearch",
    use_scm_version={"local_scheme": "node-and-timestamp"},
    setup_requires=["setuptools_scm"],
    install_requires=[
        "boolparse",
        "configlib",
        "flask",
        "mdb",
        "openimmo",
        "openimmodb",
        "openimmolib",
        "peewee",
        "peeweeplus",
        "pyxb",
        "wsgilib",
    ],
    author="HOMEINFO - Digitale Informationssysteme GmbH",
    author_email="info@homeinfo.de",
    maintainer="Richard Neumann",
    maintainer_email="r.neumann@homeinfo.de",
    packages=["immosearch"],
    license=open("LICENSE.txt").read(),
    description="Real estate search engine.",
)
