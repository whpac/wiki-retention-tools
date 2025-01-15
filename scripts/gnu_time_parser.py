from datetime import timedelta
import re
from sys import stderr

def parseRelativeTime(time_expr: str):
    time = {
        'days': 0,
        'seconds': 0,
        'minutes': 0,
        'hours': 0,
        'weeks': 0
    }

    keywords = {
        'years': ('days', 365), # Not precisely aligned with GNU
        'months': ('days', 30), # Not precisely aligned with GNU
        'fortnights': ('weeks', 2),
        'weeks': ('weeks', 1),
        'days': ('days', 1),
        'hours': ('hours', 1),
        'minutes': ('minutes', 1),
        'mins': ('minutes', 1),
        'seconds': ('seconds', 1),
        'secs': ('seconds', 1),

        'now': ('seconds', 0),
        'today': ('days', 0),
        'yesterday': ('days', -1),
        'tomorrow': ('days', 1),
    }

    currMultiplier = 0
    currUnit = None

    for word in (time_expr + ' 0').lower().split(): # Add a dummy 0 to the end to ensure the last part is processed
        if re.match(r'^[\-+]?\d+$', word):
            if currUnit is not None:
                unitName, unitValue = keywords[currUnit]
                time[unitName] += currMultiplier * unitValue

            currMultiplier = int(word)
            currUnit = None
        elif word in keywords:
            currUnit = word
        elif word + 's' in keywords:
            currUnit = word + 's'
        elif word == 'ago':
            currMultiplier *= -1
        else:
            # Unknown part, ignore
            print(f'Unknown part for relative GNU time: `{word}` in `{time_expr}`.', file=stderr)

    td = timedelta(**time)
    return td
