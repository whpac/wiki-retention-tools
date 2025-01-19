#!/bin/bash

# Go into the root of the project
pushd "$(dirname $0)/.." > /dev/null

# Load the utility functions and common variables
source ./jobs/utils.sh
make_dirs

PYTHON=~/.venv/bin/python

$PYTHON ./scripts/drop_anon_blocks.py $BLOCKS_FILE $BLOCKS_FILE_USERS
$PYTHON ./scripts/attach_blocks_to_ids.py $BLOCKS_FILE_USERS $BLOCKS_FILE_USERIDS $REGISTRATIONS_FILE
$PYTHON ./scripts/aggregate_blocks.py $BLOCKS_FILE_USERIDS $BLOCKS_FILE_AGG
$PYTHON ./scripts/sum_blocks.py $BLOCKS_FILE_AGG $BLOCKS_FILE_1EM2 $FIRST_EDITS_FILE -u 60

popd > /dev/null