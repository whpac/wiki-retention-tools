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
LOG_DUMP=$(dump_path $WIKI $DUMP_DATE "pages-logging.xml.gz")

toolforge jobs run registration-dates \
    --command "cd $(pwd) && ~/.venv/bin/python ./scripts/registration.py $LOG_DUMP $REGISTRATIONS_FILE -f 5000" \
    --image python3.11 \
    --mem 4Gi \
    --cpu 1 \
    --filelog-stdout $(pwd)/logs/registration-dates.out \
    --filelog-stderr $(pwd)/logs/registration-dates.err \
    --emails onfinish

popd > /dev/null