# Here are defined common variables that
# denote eg. files shared by the jobs.
# Paths are to be relative to the root of the project.
REGISTRATIONS_FILE="./data/registration_dates.tsv"
FIRST_EDITS_FILE="./data/first_edits.tsv"
COUNTS_FILE_REG1D="./data/edit_counts.reg1d.tsv"
COUNTS_FILE_REGM2="./data/edit_counts.regm2.tsv"
COUNTS_FILE_1EM2="./data/edit_counts.1em2.tsv"
BOTS_FILE="./data/bots.tsv"
BLOCKS_FILE="./data/blocks.tsv"
BLOCKS_FILE_USERS="./data/blocks_users.tsv"
BLOCKS_FILE_USERIDS="./data/blocks_userids.tsv"
BLOCKS_FILE_AGG="./data/blocks_agg.tsv"
BLOCKS_FILE_1EM2="./data/blocks.1em2.tsv"
RENAMES_FILE="./data/user_renames.tsv"


# Ensures that all the required directories exist.
make_dirs () {
    mkdir -p ./data
    mkdir -p ./logs
}

# Returns the date of the dump to use.
# This is set to be the beginning of the current of last month.
# Dumps younger than 14 days are not used, since they may still
# be in progress.
dump_date () {
    date --date='-14 days' +%Y%m01
}

# Makes the path to the dump file.
# Accepts three arguments:
# 1. The wiki name. (eg. enwiki)
# 2. The date of the dump. (eg. 20250101)
# 3. The base filename of the dump. (eg. pages-logging.xml.gz)
dump_path () {
    local WIKI=$1
    local DATE=$2
    local FILENAME=$3
    echo "/public/dumps/public/$WIKI/$DATE/$WIKI-$DATE-$FILENAME"
}
