"""Inspected exact schedule bounds, before freezing a certificate."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from experiments.dependency_memory.entropy_coding import finite

records = []
for k in (96,192,384,768,1536,3072,6144,12288):
    data = finite.bound(k)
    record = {key:data[key] for key in ('k','oracle_blocks','two_word_blocks','binomial_cells_represented','frontier_steps')}
    record.update({key:str(float(data[key])) for key in ('base_error','failure_event_upper_probability','conditional_excess_upper','error_upper')})
    records.append(record)
    print(json.dumps(record),flush=True)
Path(__file__).with_name('probe.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
