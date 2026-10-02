# Balanced-source complementary completion

October 2, 2026. A local analytic reduction, checked offline. No model calls.
For every fixed code in the stated balanced-source, average-Hamming-loss model,
some complementary final table has no larger mean error with exactly the same
parent encoder and capacity. Sorting endpoint labels changes each updater bit
only by a fixed public XOR. It does not change the information timing or add
state. This gives equality of unrestricted/complementary optima for every k/B.

The proof averages public completions while keeping the old code fixed, then
chooses one completion before the source. A constructive choice uses the modal
population value of X_j XOR old_child on formerly constant coordinates. Those
population statistics are offline design inputs, never actor observations.
Per-instance loss can increase. A biased two-source example has unrestricted
zero error versus complementary error at least 1/6, so source balance matters.
No general derandomization novelty or practical/LLM benefit is claimed.

The finite adapter enumerates one to three blocks and at most 64 public states;
the theorem is not limited to those examples. Checks include all 36 branch pairs
and 256 Boolean updaters on uniform three-bit inputs, eight already preserved
three-block books, and identity on the unchanged 40,529-error witness. Every
whole-code score executes actual final query routes. Optional nearest-parent
reassignment after completion is a separate achieved construction.

```powershell
python -m experiments.dependency_memory.decoder_completion.certificate
python -m unittest discover -s experiments/dependency_memory -p test_completion.py -v
```

The reduction lets the existing C62 complementary converse imply the same
unrestricted lower bound independently of C63's much larger complete-table
certificate. Both historical certificates remain unchanged. The remaining
asymptotic comparison has six complementary symmetry families. The complete
curve between C65's certified slopes still needs proof or a counterexample.
External correctness and source priority remain open.
