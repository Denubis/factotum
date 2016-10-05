import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "factotum",
    version = "0.1.0",
    author = "Brian Ballsun-Stanton",
    author_email = "factorio@drbbs.org",
    description = ("A tool to control a headless factorio server."),
    license = "GPLv3",
    keywords = "factorio rcon headless",
    url = "https://github.com/Denubis/factotum",
    py_modules=['factotum'],
    packages = find_packages(),
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Games/Entertainment :: Simulation",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
    install_requires=["click", "ptyprocess", "clint", "circus", "daemonocle", "requests", "python-valve", "factoirc", "pyfakefs"],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'factotum=factotum.factotum:cli'
        ]
    }

)

