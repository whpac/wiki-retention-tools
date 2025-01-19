#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <wiki>" >&2
    exit 1
fi

# Go into the root of the project
pushd "$(dirname $0)/.." > /dev/null

# Load the utility functions and common variables
source ./jobs/utils.sh

make_dirs

WIKI=$1
DUMP_DATE=$(dump_date)
PAGES_DUMP=$(dump_path $WIKI $DUMP_DATE "stub-meta-history.xml.gz")

toolforge jobs run first-edits \
    --command "cd $(pwd) && ~/.venv/bin/python ./scripts/first_edit.py $PAGES_DUMP $FIRST_EDITS_FILE -f 5000" \
    --image python3.11 \
    --mem 2Gi \
    --cpu 1 \
    --filelog-stdout $(pwd)/logs/first-edits.out \
    --filelog-stderr $(pwd)/logs/first-edits.err \
    --emails onfinish

popd > /dev/null