import argparse
from datetime import datetime, timedelta
from itertools import batched

parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='Path to the TSV file with aggregated blocks')
parser.add_argument('output_file', help='Path to the output TSV file')
parser.add_argument('bounds_ref_file', help='Path to the TSV file with reference for bounds calculation')
parser.add_argument('-u', '--upper-bound', type=int, default=30, help='How many days after the reference date to stop counting blocks')
parser.add_argument('-s', '--skip-missing', action='store_true', help='Skip users that are not in the reference file')
args = parser.parse_args()

def makeBounds(refPointFile: str, endOffset: timedelta) -> dict[int, datetime]:
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
            upperBound = timestamp + endOffset

            bounds[user_id] = upperBound
    return bounds


bounds = makeBounds(args.bounds_ref_file, timedelta(days=args.upper_bound))

with open(args.output_file, 'w', encoding='utf-8') as f_out:
    f_out.write('user_id\tblock_days\n')
    with open(args.input_file, 'r', encoding='utf-8') as f_in:
        for line in f_in:
            fields = line.strip().split('\t')

            if len(fields) < 2:
                print(f'Invalid line: {line}')
                continue

            user_id = int(fields[0])
            upper_bound = bounds.get(user_id, None)
            if upper_bound is None:
                if args.skip_missing:
                    print(f'User not found in bounds: {user_id}')
                    continue
                # Take all edits for users that did not edit
                upper_bound = datetime.max

            total_duration = timedelta()
            for i in range(1, len(fields), 2):
                block_start = fields[i]
                block_end = fields[i + 1]

                block_start = datetime.strptime(block_start, '%Y-%m-%dT%H:%M:%SZ')
                if block_start > upper_bound:
                    break

                if block_end == 'infinity':
                    total_duration = 'infinity'
                    break
                else:
                    block_end = datetime.strptime(block_end, '%Y-%m-%dT%H:%M:%SZ')
                    total_duration += block_end - block_start
            
            total_duration = total_duration if total_duration == 'infinity' else round(total_duration.total_seconds() / 86400, 2)
            f_out.write(f'{user_id}\t{total_duration}\n')
