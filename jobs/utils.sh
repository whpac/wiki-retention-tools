# Here are defined common variables that
# denote eg. files shared by the jobs.
# Paths are to be relative to the root of the project.
REGISTRATIONS_FILE="./data/registration_dates.tsv"


# Ensures that all the required directories exist.
make_dirs () {
    mkdir -p ./data
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
