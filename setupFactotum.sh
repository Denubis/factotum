#!/bin/bash

type virtualenv >/dev/null 2>&1 || { echo >&2 "I require virtualenv but it's not installed. Please sudo apt install virtualenv. Aborting."; exit 1; }

virtualenv venv
virtualenv -p /usr/bin/python2.7 venv
source venv/bin/activate
pip install click daemonocle

