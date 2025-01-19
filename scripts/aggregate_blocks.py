import argparse
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='Path to the TSV blocks list file')
parser.add_argument('output_file', help='Path to the output TSV file')
args = parser.parse_args()

blocks = defaultdict(list) # user_name -> (block_start, block_end)[]

with open(args.input_file, 'r', encoding='utf-8') as f:
    i = 0
    for line in f:
        i += 1
        if i == 1:
            continue # Skip the header

        fields = line.strip().split('\t')

        if len(fields) < 6:
            print(f'Invalid line: {line}')
            continue

        user_name = fields[0]
        action = fields[5]
        timestamp = fields[1]
        block_end = fields[3]

        if action == 'unblock':
            user_blocks = blocks[user_name]
            if len(user_blocks) == 0:
                print(f'Unblocking user {user_name} without a block')
                continue

            # Update the block end time
            last_block = user_blocks[-1]
            if last_block[1] < timestamp and last_block[1] != 'infinity':
                print(f'Unblocking user {user_name} with no active block')
                continue

            user_blocks[-1] = (last_block[0], timestamp)
        elif action == 'reblock':
            user_blocks = blocks[user_name]
            if len(user_blocks) == 0:
                print(f'Reblocking user {user_name} without a block')
                continue

            # Update the block end time
            last_block = user_blocks[-1]
            if last_block[1] < timestamp and last_block[1] != 'infinity':
                print(f'Reblocking user {user_name} with no active block')
                continue

            user_blocks[-1] = (last_block[0], block_end)
        elif action == 'block':
            user_blocks = blocks[user_name]
            user_blocks.append((timestamp, block_end))
        else:
            print(f'Unknown block action: {action}')


with open(args.output_file, 'w', encoding='utf-8') as f:
    for user_name, blocks in blocks.items():
        f.write(user_name)
        for block_start, block_end in blocks:
            f.write(f'\t{block_start}\t{block_end}')
        f.write('\n')
