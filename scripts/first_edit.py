import argparse
import gzip
import mwxml
import psutil

parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='Path to the gzipped XML dump file')
parser.add_argument('output_file', help='Path to the output TSV file')
parser.add_argument('-f', '--report-freq', type=int, default=1000, help='How often to report the progress')
args = parser.parse_args()

dump = mwxml.Dump.from_file(gzip.open(args.input_file))

proc = psutil.Process() # For monitoring the memory usage

first_edits = {}
pages = 0
revisions = 0
for page in dump.pages:
    pages += 1
    for revision in page:
        revisions += 1
        # Skip pages without the information we need
        if revision.user is None or revision.timestamp is None:
            continue

        # Skip IPs
        if revision.user.id is None:
            continue

        if revision.user.id not in first_edits:
            first_edits[revision.user.id] = (revision.timestamp, revision.id)

        if revision.timestamp < first_edits[revision.user.id][0]:
            first_edits[revision.user.id] = (revision.timestamp, revision.id)
    
    if pages % args.report_freq == 0:
        mem_used = proc.memory_info().rss / (2**20)
        print(f'Processed {pages} pages ({revisions} revisions in total); memory: {mem_used:.2f} MB')

with open(args.output_file, 'w', encoding='utf-8') as f:
    f.write('user_id\ttimestamp\trev_id\n')
    for user_id, (timestamp, rev_id) in first_edits.items():
        f.write(f'{user_id}\t{timestamp.long_format()}\t{rev_id}\n')

print(f'Processing complete.')
