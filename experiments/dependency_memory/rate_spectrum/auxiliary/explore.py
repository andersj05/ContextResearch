"""Post-hoc mathematical exploration; floats are not certificates."""
import json
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.dependency_memory.joint_coding import decoder_frontier as f

start = time.perf_counter()
orbits = list(f.decoder_orbits())
loss = np.asarray([f.loss_matrix(table) for _, table, _ in orbits], dtype=np.int8)
unsigned = next(i for i, (_, table, _) in enumerate(orbits) if table == f.UNSIGNED)
rows = []
for t in (0.15, 0.25, 0.4, 0.6, 0.8, 0.95):
    w = np.power(t, loss.astype(float))
    q = np.full((len(orbits), 16), 1/16)
    for iteration in range(4000):
        z = np.einsum('ixa,ia->ix', w, q)
        gradient = np.mean(w / z[:, :, None], axis=1)
        next_q = q * gradient
        next_q /= next_q.sum(axis=1, keepdims=True)
        if np.max(np.abs(next_q-q)) < 2e-13:
            q = next_q
            break
        q = next_q
    z = np.einsum('ixa,ia->ix', w, q)
    gradient = np.mean(w / z[:, :, None], axis=1)
    free = -np.mean(np.log2(z), axis=1)
    dual = free - np.log2(np.max(gradient, axis=1))
    posterior = q[:, None, :] * w / z[:, :, None]
    distortion = np.mean(np.sum(posterior * loss, axis=2), axis=1) / 12
    marginal = np.mean(posterior, axis=1)
    safe = np.maximum(marginal, 1e-300)
    with np.errstate(divide='ignore', invalid='ignore'):
        information = np.mean(np.sum(np.where(posterior > 0, posterior * (np.log2(posterior)-np.log2(safe[:, None, :])), 0), axis=2), axis=1)
    other = np.copy(dual)
    other[unsigned] = np.inf
    contender = int(np.argmin(other))
    row = {'t': str(t), 'iterations': iteration+1,
           'unsigned_free': float(free[unsigned]), 'unsigned_dual': float(dual[unsigned]),
           'unsigned_information': float(information[unsigned]), 'unsigned_distortion': float(distortion[unsigned]),
           'unsigned_q': q[unsigned].tolist(),
           'other_min_dual': float(other[contender]), 'other_index': orbits[contender][0],
           'other_table': list(orbits[contender][1]),
           'other_primal_free': float(free[contender]),
           'minimum_dual_gap_from_unsigned_free': float(other[contender]-free[unsigned])}
    rows.append(row)
    print(json.dumps(row), flush=True)
    # All floating weights are exploratory raw witness candidates, not proof.
    np.savez_compressed(ROOT / 'build/rate-spectrum' / ('weights-'+str(t)+'.npz'), q=q,
                        indices=np.asarray([index for index, _, _ in orbits]))
result = {'evidence_class': 'floating exploratory supporting-objective probes; no model calls',
          'orbits': len(orbits), 'tables': sum(size for _, _, size in orbits), 'points': rows,
          'elapsed_seconds': time.perf_counter()-start}
(ROOT / 'build/rate-spectrum/exploration.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
