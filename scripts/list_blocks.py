import argparse
from datetime import datetime
from gnu_time_parser import parseRelativeTime
import gzip
import mwxml
import phpserialize
import psutil
import re

def monthToNumber(monthMatch):
    month = monthMatch.group(1).lower()
    months = {
        'jan': '01',
        'feb': '02',
        'mar': '03',
        'apr': '04',
        'may': '05',
        'jun': '06',
        'jul': '07',
        'aug': '08',
        'sep': '09',
        'oct': '10',
        'nov': '11',
        'dec': '12'
    }
    return months.get(month, '00')

INFINITE_DESIGNATORS = ['infinite', 'indefinite', 'infinity', 'never']

parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='Path to the gzipped XML dump file')
parser.add_argument('output_file', help='Path to the output TSV file')
parser.add_argument('-f', '--report-freq', type=int, default=1000, help='How often to report the progress')
args = parser.parse_args()

dump = mwxml.Dump.from_file(gzip.open(args.input_file))

proc = psutil.Process() # For monitoring the memory usage

with open(args.output_file, 'w', encoding='utf-8') as f:
    f.write('user_name\ttimestamp\tblock_duration\tlog_id\tmethod\n')
    items = 0
    blocks = 0
    for log_item in dump.log_items:
        items += 1
        if items % args.report_freq == 0:
            mem_used = proc.memory_info().rss / (2**20)
            print(f'Processed {items} log items (including {blocks} blocks); memory: {mem_used:.2f} MB')

        # We want only blocks
        if log_item.type != 'block':
            continue

        blocks += 1

        if log_item.user is None or log_item.timestamp is None or log_item.page is None:
            continue

        blocked_username = log_item.page.title

        params = log_item.params

        block_duration = ''
        if params is None or params == '':
            block_duration = ''
        else:
            try:
                # That's not an optimal solution, let's ultimately find a deserializer for strings
                params = phpserialize.loads(params.encode('utf-8'), decode_strings=True)
                if '5::duration' in params:
                    block_duration = params['5::duration']
            except Exception as e:
                block_duration = params.split('\n')[0]

        if block_duration == '':
            block_end_date = ''
        elif block_duration in INFINITE_DESIGNATORS:
            block_end_date = 'infinity'
        else:
            try:
                block_end_date = datetime.strptime(block_duration, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                try:
                    # Working with locales is non-trivial, so replace some words with numbers
                    # to make life easier on non-English machines
                    block_duration_sanitized = re.sub(r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s*', '', block_duration)
                    block_duration_sanitized = re.sub(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', monthToNumber, block_duration_sanitized)
                    block_end_date = datetime.strptime(block_duration_sanitized, '%d %m %Y %H:%M:%S %Z')
                except ValueError:
                    block_span = parseRelativeTime(block_duration)
                    block_start_date = datetime.fromtimestamp(log_item.timestamp.unix())
                    block_end_date = block_start_date + block_span
                block_end_date = block_end_date.strftime('%Y-%m-%dT%H:%M:%SZ')

        f.write(f'{blocked_username}\t{log_item.timestamp.long_format()}\t{block_duration}\t{block_end_date}\t{log_item.id}\t{log_item.action}\n')

print(f'Processing complete.')
