import argparse
import gzip
import psutil
from sql_reader import readSqlDump

parser = argparse.ArgumentParser()
parser.add_argument('input_files', help='Path to the gzipped SQL dump file', nargs='+')
parser.add_argument('output_file', help='Path to the output TSV file')
parser.add_argument('-f', '--report-freq', type=int, default=1000, help='How often to report the progress')
args = parser.parse_args()

proc = psutil.Process() # For monitoring the memory usage

bot_users = set()
records = 0

for input_file in args.input_files:
    with gzip.open(input_file, 'rt', encoding='utf-8') as dump_file:
        for record in readSqlDump(dump_file):
            records += 1
            if record.get('ug_group') == 'bot':
                bot_users.add(record['ug_user'])
            elif record.get('ufg_group') == 'bot':
                bot_users.add(record['ufg_user'])

            if records % args.report_freq == 0:
                mem_used = proc.memory_info().rss / (2**20)
                print(f'Processed {records} records; found {len(bot_users)} bot users; memory: {mem_used:.2f} MB')

with open(args.output_file, 'w', encoding='utf-8') as f:
    f.write('user_id\tuser_bot\n')
    for user_id in bot_users:
        f.write(f'{user_id}\tbot\n')

print(f'Processing complete.')
