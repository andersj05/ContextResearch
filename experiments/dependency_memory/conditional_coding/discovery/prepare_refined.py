import json
from pathlib import Path

here = Path(__file__).resolve().parent
rows = [json.loads(line) for line in (here / 'refine.jsonl').read_text().splitlines()]
last = rows[-1]
assert last['kind'] == 'refined_final' and last['one_swap_zero_screen']
header = 'static const uint16_t BASE[64]={' + ','.join(map(str, last['book'])) + '};\n'
(here / 'refined.h').write_bytes(header.encode())
source = (here / 'swap.c').read_bytes()
assert source.count(b'#include "base.h"') == 1
(here / 'couple.c').write_bytes(source.replace(b'#include "base.h"', b'#include "refined.h"', 1))
print(json.dumps({'refined_three_errors': last['errors'], 'swaps': last['accepted']}))
