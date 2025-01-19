#!/bin/bash

if [ $# -lt 2 ]; then
    echo "Usage: $0 <wiki> <reg1d|regm2|1em2>" >&2
    exit 1
fi

# Go into the root of the project
pushd "$(dirname $0)/.." > /dev/null

# Load the utility functions and common variables
source ./jobs/utils.sh

case $2 in
    "reg1d")
        SCRIPT_OPTIONS="$COUNTS_FILE_REG1D $REGISTRATIONS_FILE -l 0 -u 1"
        ;;
    "regm2")
        SCRIPT_OPTIONS="$COUNTS_FILE_REGM2 $REGISTRATIONS_FILE -l 30 -u 60"
        ;;
    "1em2")
        SCRIPT_OPTIONS="$COUNTS_FILE_1EM2 $FIRST_EDITS_FILE -l 30 -u 60"
        ;;
    *)
        echo "Invalid edit counting mode: $2" >&2
        echo "Allowed modes" >&2
        echo "    reg1d: edits done within 24 hours from registration" >&2
        echo "    regm2: edits done between 30 and 60 days from registration" >&2
        echo "    1em2: edits done between 30 and 60 days from first edit" >&2
        popd > /dev/null
        exit 2
        ;;
esac

make_dirs

WIKI=$1
DUMP_DATE=$(dump_date)
PAGES_DUMP=$(dump_path $WIKI $DUMP_DATE "stub-meta-history.xml.gz")

toolforge jobs run edit-counter \
    --command "cd $(pwd) && ~/.venv/bin/python ./scripts/count_edits.py $PAGES_DUMP $SCRIPT_OPTIONS -f 5000" \
    --image python3.11 \
    --mem 2Gi \
    --cpu 1 \
    --filelog-stdout $(pwd)/logs/edit-counter.out \
    --filelog-stderr $(pwd)/logs/edit-counter.err \
    --emails onfinish

popd > /dev/null