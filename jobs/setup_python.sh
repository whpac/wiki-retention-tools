#!/bin/bash

# This script, if run without arguments, creates a Toolforge job with
# an image inside of which the initialization is done.
# Don't invoke the script manually with any arguments, as it won't work.

if [ $# -eq 0 ]; then
    JOB_NAME="setup-python"
    echo "Starting a Toolforge job for Python initialization."
    toolforge jobs run $JOB_NAME \
        --command "cd $(pwd) && $(dirname $0)/setup_python.sh dummyarg" \
        --image python3.11 \
        --wait \
        --filelog-stdout $(pwd)/logs/setup-python.out \
        --filelog-stderr $(pwd)/logs/setup-python.err
    exit 0
fi

# The actual initialization code starts here.
# See https://wikitech.wikimedia.org/wiki/Help:Toolforge/Python

# use bash strict mode
set -euo pipefail

# delete the venv, if it already exists
rm -rf ~/.venv

# create the venv
python3 -m venv ~/.venv

# activate it
source ~/.venv/bin/activate

# upgrade pip inside the venv and add support for the wheel package format
pip install -U pip wheel

pip install -r "$(dirname $0)/../requirements.txt"