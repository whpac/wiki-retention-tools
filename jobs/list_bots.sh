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
UG_DUMP=$(dump_path $WIKI $DUMP_DATE "user_groups.sql.gz")
UFG_DUMP=$(dump_path $WIKI $DUMP_DATE "user_former_groups.sql.gz")

toolforge jobs run list-bots \
    --command "cd $(pwd) && ~/.venv/bin/python ./scripts/list_bots.py $UG_DUMP $UFG_DUMP $BOTS_FILE -f 1000" \
    --image python3.11 \
    --mem 256Mi \
    --cpu 1 \
    --filelog-stdout $(pwd)/logs/list-bots.out \
    --filelog-stderr $(pwd)/logs/list-bots.err \
    --emails onfinish

popd > /dev/null