import argparse
import gzip
import mwxml
import re

parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='Path to the gzipped XML dump file')
parser.add_argument('output_file', help='Path to the output TSV file')
parser.add_argument('-f', '--report-freq', type=int, default=1000, help='How often to report the progress')
args = parser.parse_args()

dump = mwxml.Dump.from_file(gzip.open(args.input_file))

with open(args.output_file, 'w', encoding='utf-8') as f:
    f.write('user_id\ttimestamp\tlog_id\tmethod\n')
    items = 0
    user_creations = 0
    for log_item in dump.log_items:
        items += 1
        if items % args.report_freq == 0:
            print(f'Processed {items} log items (including {user_creations} user creations)')

        # We want only user creations
        if log_item.type != 'newusers':
            continue

        user_creations += 1

        if log_item.user is None or log_item.timestamp is None:
            continue

        params = log_item.params

        created_user_id = None
        if params is None or params == '':
            created_user_id = log_item.user.id
        elif ':' not in params:
            created_user_id = int(params)
        else:
            match = re.search(r'::userid";i:(\d+);', params)
            if match:
                created_user_id = int(match.group(1))

        if created_user_id is None:
            continue

        f.write(f'{created_user_id}\t{log_item.timestamp.long_format()}\t{log_item.id}\t{log_item.action}\n')

print(f'Processing complete.')
