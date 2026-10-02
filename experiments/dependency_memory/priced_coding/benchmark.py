"""One local sample per public plan/input; separate from deterministic grading."""
from hashlib import sha256
import json
from pathlib import Path
import platform
from time import perf_counter_ns, process_time_ns

from . import design, bounds, codec, tables
from experiments.dependency_memory.tie_coding import bounds as roots, design as logarithms
from experiments.dependency_memory.weighted_overflow import certificate as previous

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def measure(action):
    wall, cpu = perf_counter_ns(), process_time_ns()
    result = action()
    return result, {'wall_ns':perf_counter_ns()-wall, 'process_cpu_ns':process_time_ns()-cpu}


def main():
    name, _ = tables.names()
    book = tables.load(name)
    losses, error = tables.weights(name)
    records = []
    for k in (384, 768, 12288):
        # Public tables are already loaded. Cold planning includes root/log
        # computation, but excludes JSON loading and historical discovery.
        bounds.moments.cache_clear()
        bounds.allocation.cache_clear()
        bounds.select.cache_clear()
        roots.root_bounds.cache_clear()
        design.entropies.cache_clear()
        logarithms.log2_bounds.cache_clear()
        (a, degree), timing = measure(lambda:bounds.select(k//book.g, book, losses, error))
        records.append({'stage':'cold_public_planning','book':name,'k':k,'a':a,'degree':degree,**timing})
        design.compiled(book)
        for family in ('zeros','cycle','balanced'):
            xs=((0,)*k if family=='zeros' else (3,)*k if family=='balanced'
                else tuple((11*j+5)%16 for j in range(k)))
            common={'book':name,'k':k,'a':a,'degree':degree,'family':family,
                    'constructed_input_sha256':sha256(bytes(xs)).hexdigest()}
            parent, timing = measure(lambda:codec.encode(xs,book,a))
            if parent >= 1 << (2*k):
                raise ValueError('Measured parent exceeds its charged cap')
            records.append({'stage':'warm_encode',**common,'parent_bit_length':parent.bit_length(),
                            'parent_sha256':previous.digest_integer(parent),**timing})
            child, timing = measure(lambda:codec.update(parent,k-1,2,k,book,a))
            records.append({'stage':'update_last_block',**common,'child':child,**timing})
            prediction, timing = measure(lambda:codec.predict(child,k-1,2,1))
            records.append({'stage':'predict',**common,'prediction':prediction,**timing})
        print({'k':k,'a':a,'degree':degree,'completed_samples':len(records)},flush=True)
    files=[HERE/name for name in ('benchmark.py','design.py','bounds.py','codec.py','tables.py','tables.json')]
    files += [HERE.parent/'tie_coding'/name for name in ('bounds.py','design.py')]
    files += [HERE.parent/'entropy_coding/codec.py']
    result={'date':'2026-10-02','python':platform.python_version(),'platform':platform.platform(),
            'samples_per_plan_or_input_stage':1,
            'planning_scope':'Loaded fixed public descriptor/weights; cold moment/root/log/allocation caches. File loading and original discovery excluded.',
            'actor_scope':'Compiled public book cached before encode; source-dependent values are never cached across boundaries.',
            'limits':'Single local wall/process CPU samples on constructed inputs; no population latency, portable speed, optimized actor, model or provider cost claim.',
            'source_sha256':{p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in files},
            'samples':records}
    (HERE/'local_timings_2026-10-02.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':
    main()
