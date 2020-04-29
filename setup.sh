#!/usr/bin/env bash

# I had to do the following, but you probably don't
# pip3 install --upgrade setuptools
# pip3 install wheel
# pip3 install virtualenv

virtualenv venv
source venv/bin/activate

pip3 install flask
pip3 install "graphene>=2.0"
pip3 install python-dateutil
