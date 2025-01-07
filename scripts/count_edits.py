import argparse
import gzip
import mwxml
import psutil
from collections import defaultdict
from datetime import datetime, timedelta
from mwtypes import Timestamp
from typing import Tuple

parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='Path to the gzipped XML dump file')
parser.add_argument('output_file', help='Path to the output TSV file')
parser.add_argument('bounds_ref_file', help='Path to the TSV file with reference for bounds calculation')
parser.add_argument('-f', '--report-freq', type=int, default=1000, help='How often to report the progress')
parser.add_argument('-l', '--lower-bound', type=int, default=0, help='How many days after the reference date to start counting edits')
parser.add_argument('-u', '--upper-bound', type=int, default=30, help='How many days after the reference date to stop counting edits')
args = parser.parse_args()

def makeBounds(refPointFile: str, startOffset: timedelta, endOffset: timedelta) -> dict[int, Tuple[datetime, datetime]]:
    """
    Creates a bounds dictionary from a file with reference points for each user.
    The bounds are calculated as the reference point plus the start and end offsets.
    """
    bounds = {}
    with open(refPointFile, 'r') as f:
        curr_line = 0
        for line in f:
            curr_line += 1
            if curr_line == 1: # Skip the header
                continue

            row = line.strip().split('\t')
            user_id = int(row[0])
            timestamp = datetime.strptime(row[1], '%Y-%m-%dT%H:%M:%SZ')
            lowerBound = Timestamp(timestamp + startOffset)
            upperBound = Timestamp(timestamp + endOffset)

            bounds[user_id] = (lowerBound, upperBound)
    return bounds


bounds = makeBounds(args.bounds_ref_file, timedelta(days=args.lower_bound), timedelta(days=args.upper_bound))
dump = mwxml.Dump.from_file(gzip.open(args.input_file))

proc = psutil.Process() # For monitoring the memory usage

edit_counts = defaultdict(int)
pages = 0
revisions = 0
for page in dump.pages:
    pages += 1
    for revision in page:
        revisions += 1
        # Skip pages without the information we need
        if revision.user is None or revision.timestamp is None:
            continue

        user_id = revision.user.id
        # Skip IPs
        if user_id is None:
            continue

        if user_id not in bounds:
            continue

        lower_bound, upper_bound = bounds[user_id]
        if revision.timestamp < lower_bound or revision.timestamp > upper_bound:
            continue

        edit_counts[user_id] += 1
    
    if pages % args.report_freq == 0:
        mem_used = proc.memory_info().rss / (2**20)
        print(f'Processed {pages} pages ({revisions} revisions in total); memory: {mem_used:.2f} MB')

with open(args.output_file, 'w', encoding='utf-8') as f:
    f.write('user_id\tnum_edits\n')
    for user_id, num_edits in edit_counts.items():
        f.write(f'{user_id}\t{num_edits}\n')

print(f'Processing complete.')
