"""Save one local timing sample; never replay timings as deterministic evidence."""
from hashlib import sha256
import json
from pathlib import Path
import platform
import sys
from time import perf_counter_ns, process_time_ns

from . import bounds, codec
from experiments.dependency_memory.tie_coding import design
from experiments.dependency_memory.tie_coding import bounds as roots

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE/'local_timings_2026-10-02.json'


def measured(function):
    wall, cpu = perf_counter_ns(), process_time_ns()
    value = function()
    return value, {'wall_ns':perf_counter_ns()-wall, 'process_cpu_ns':process_time_ns()-cpu}


def main():
    plans, actors = [], []
    for k in (384, 768, 12288):
        for method in (bounds.select, bounds.allocation, bounds.moments,
                       bounds.loss_weights, design.prepare, design.log2_bounds,
                       roots.root_bounds, roots.moment_upper):
            method.cache_clear()
        (a, degree), elapsed = measured(lambda:bounds.select(k//8, 8))
        plans.append({'k':k, 'a':a, 'degree':degree, **elapsed})
        for family in ('zeros', 'cycle', 'balanced'):
            xs = ((0,)*k if family == 'zeros' else (3,)*k if family == 'balanced'
                  else tuple((11*r+5)%16 for r in range(k)))
            parent, encoding = measured(lambda:codec.encode(xs))
            child, updating = measured(lambda:codec.update(parent, k-1, 0, k//8))
            answer, predicting = measured(lambda:codec.predict(child, k-1, 0, 1))
            if answer != child:
                raise ValueError('Final actor needs extra information')
            actors.append({'k':k, 'a':a, 'family':family,
                'constructed_input_sha256':sha256(bytes(xs)).hexdigest(),
                'parent_bit_length':parent.bit_length(),
                'fallback':parent == 0,
                'encode':encoding, 'update_last_block':updating, 'predict':predicting})
    files = (HERE/'bounds.py', HERE/'codec.py', HERE/'benchmark.py',
             HERE.parent/'tie_coding/codec.py', HERE.parent/'tie_coding/design.py',
             HERE.parent/'tie_coding/bounds.py')
    result = {'date':'2026-10-02', 'python_version':sys.version.split()[0],
        'platform':platform.platform(), 'repeats_per_input':1,
        'public_plan_cache':'All relevant public-only caches cleared before each length; plans then shared by that length actors',
        'source_sha256':{p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in files},
        'planning':plans, 'constructed_actors':actors,
        'scope':'Single local samples of cold public planning and warm actors, not population latency, portable speed, LLM/model calls or token/credit accounting.'}
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps({'planning':plans, 'actor_rows':len(actors)}, indent=2))


if __name__ == '__main__':
    main()
