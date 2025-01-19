import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='Path to the TSV blocks list file')
parser.add_argument('output_file', help='Path to the output TSV file')
args = parser.parse_args()

with open(args.output_file, 'w', encoding='utf-8') as f:
    with open(args.input_file, 'r', encoding='utf-8') as f_in:
        for line in f_in:
            fields = line.strip().split('\t')
            user_name = fields[0]

            # Drop IPv4 blocks
            # It seems that MediaWiki uses a similar regex, as 256.0.0.0 is not
            # a valid username, even though it's not a valid IPv4 address
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(/\d+)?$', user_name):
                continue

            # Drop IPv6 blocks
            # Colon is forbidden in usernames since 2015, but this regex makes
            # the check slightly more robust
            # It's not strictly what makes the IPv6 but it's a good heuristic
            if re.match(r'^[0-9a-fA-F:]+(/\d+)?$', user_name):
                continue

            # Drop temporary accounts
            # Checking for the tilde should be enough, but all the temp accounts
            # begin with the year, so make it a bit more specific
            if user_name.startswith('~20'):
                continue

            # Drop what seems to be a reminiscent of old autoblocks that were unblocked
            if user_name.startswith('#'):
                continue

            f.write(line)