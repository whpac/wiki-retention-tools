import argparse

parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='Path to the TSV file with blocks')
parser.add_argument('output_file', help='Path to the output TSV file')
parser.add_argument('registrations_file', help='Path to the TSV file with list of user registrations')
args = parser.parse_args()

users = {}
with open(args.registrations_file, 'r', encoding='utf-8') as f:
    i = 0
    for line in f:
        i += 1
        if i == 1:
            continue # Skip the header

        fields = line.strip().split('\t')
        user_id = int(fields[0])
        user_name = fields[4]

        if user_name in users:
            print(f'Duplicate user name: {user_name}')
            continue

        users[user_name] = user_id

with open(args.output_file, 'w', encoding='utf-8') as f_out:
    with open(args.input_file, 'r', encoding='utf-8') as f_in:
        i = 0
        for line in f_in:
            i += 1
            fields = line.strip().split('\t')

            if i == 1:
                f_out.write(f'user_id\t{'\t'.join(fields[1:])}\n')
                continue # Skip the header

            user_name = fields[0]

            user_id = users.get(user_name, None)
            if user_id is None:
                print(f'User not found: {user_name}')
                continue

            f_out.write(f'{user_id}\t{'\t'.join(fields[1:])}\n')
