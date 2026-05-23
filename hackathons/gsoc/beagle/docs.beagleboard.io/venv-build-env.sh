#!/bin/sh -ex
# Source this script like `. ./venv-build-env.sh`
if [ ! -e ./.venv ]; then
   python3 -m venv .venv
fi
. ./.venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
