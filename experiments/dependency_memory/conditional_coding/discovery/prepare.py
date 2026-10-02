import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
old = root / 'experiments/dependency_memory/joint_coding_finite3/discovery.json'
book = json.loads(old.read_text())['runs']['greedy']['codeword_ids']
(Path(__file__).parent / 'base.h').write_bytes(('static const uint16_t BASE[64]={' + ','.join(map(str, book)) + '};\n').encode())
