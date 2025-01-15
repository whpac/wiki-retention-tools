import argparse
import gzip
import mwxml
import phpserialize
import psutil
import re

parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='Path to the gzipped XML dump file')
parser.add_argument('output_file', help='Path to the output TSV file')
parser.add_argument('-f', '--report-freq', type=int, default=1000, help='How often to report the progress')
args = parser.parse_args()

dump = mwxml.Dump.from_file(gzip.open(args.input_file))

proc = psutil.Process() # For monitoring the memory usage

with open(args.output_file, 'w', encoding='utf-8') as f:
    f.write('user_id\ttimestamp\tlog_id\tmethod\n')
    items = 0
    user_creations = 0
    for log_item in dump.log_items:
        items += 1
        if items % args.report_freq == 0:
            mem_used = proc.memory_info().rss / (2**20)
            print(f'Processed {items} log items (including {user_creations} user creations); memory: {mem_used:.2f} MB')

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
        elif re.match(r'^\d+$', params):
            created_user_id = int(params)
        else:
            try:
                # That's not an optimal solution, let's ultimately find a deserializer for strings
                params = phpserialize.loads(params.encode('utf-8'), decode_strings=True)
                if '4::userid' in params:
                    created_user_id = params['4::userid']
            except Exception as e:
                print(f'Failed to unserialize params: `{params}`: {e}')

        if created_user_id is None:
            continue

        f.write(f'{created_user_id}\t{log_item.timestamp.long_format()}\t{log_item.id}\t{log_item.action}\n')

print(f'Processing complete.')
