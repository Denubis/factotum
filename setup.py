import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "FactoryFactotum",
    version = "0.0.10",
    author = "Brian Ballsun-Stanton",
    author_email = "factorio@drbbs.org",
    description = ("A tool to control a headless factorio server."),
    license = "GPLv3",
    keywords = "factorio rcon headless",
    url = "https://github.com/Denubis/headlessFactorio",
    packages=['FactoryFactotum'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Games/Entertainment :: Simulation",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
    install_requires=["click", "ptyprocess", "clint", "circus", "daemonocle", "requests", "python-valve", "factoirc"],
    include_package_data=True,
    scripts=['bin/FactoryFactotum'],

)

