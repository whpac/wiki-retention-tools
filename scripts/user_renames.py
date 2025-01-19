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
    f.write('old_name\ttimestamp\tnew_name\n')
    items = 0
    user_renames = 0
    for log_item in dump.log_items:
        items += 1
        if items % args.report_freq == 0:
            mem_used = proc.memory_info().rss / (2**20)
            print(f'Processed {items} log items (including {user_renames} user renames); memory: {mem_used:.2f} MB')

        # We want only user creations
        if log_item.type != 'renameuser':
            continue

        user_renames += 1

        if log_item.timestamp is None:
            continue

        params = log_item.params

        user_old_name = None
        user_new_name = None
        if params is None or params == '':
            matches = re.findall(r'\[\[User:(.+?)\|', log_item.comment)
            if len(matches) == 2:
                user_old_name = matches[0]
                user_new_name = matches[1]
        elif not params.startswith('a:'):
            user_old_name = log_item.page.title
            user_new_name = params
        else:
            try:
                # That's not an optimal solution, let's ultimately find a deserializer for strings
                params = phpserialize.loads(params.encode('utf-8'), decode_strings=True)
                if '4::olduser' in params and '5::newuser' in params:
                    user_old_name = params['4::olduser']
                    user_new_name = params['5::newuser']
            except Exception as e:
                user_old_name = log_item.page.title
                user_new_name = params

        if user_old_name is None:
            continue

        f.write(f'{user_old_name}\t{log_item.timestamp.long_format()}\t{user_new_name}\n')

print(f'Processing complete.')
