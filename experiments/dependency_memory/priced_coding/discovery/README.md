# Preserved exact-priced quantizer discovery

Completed October 2, 2026; post-hoc mathematics, not independent model trials.
Both search processes and both complete tensor checks exited zero.
metadata.json binds original files and upstream C69/C72/C74/C67 evidence.

protocol.json predates eight g=5 starts at prices 2/5 and 1/2. All eight fail
the declared 12288-block finite C74 target. sampled_extension.json is a
post-hoc amendment made after those failures and before either g=6 launch.
It preserves the conditional extension while explicitly replacing full
design updates by one fixed pseudorandom sample of 131072 sources.
Every final six-block descriptor receives a full exact price pass on 16^6.

Five-block original JSON: 33837446 bytes. Six-block: 161330919 bytes.
The gzip files restore those exact bytes and original SHA-256 hashes.
All complete maps, proposal/actual counts, trajectories, sample source IDs,
stability flags, comparison counts and exploratory native clocks survive.
Raw six-block training trajectory/change values describe the fixed sample;
final losses/counts and exact minima describe the complete population.
The fixed xorshift sample is not an independent uniform or held-out trial.

priced.c is the original full-population program; sampled_priced.c is its
separate executed sample-design variant. make_sampled.py preserves the
transformation. base.h retains the actual C69 warm-start chain. None of
these original snapshots is edited to match later interpretations.
Compile flags were -O3 -std=c99 with Clang 19.1.0 on Windows x86_64.
No executable is committed.

The native base-array estimate omitted a transient uniqueness bitmap.
metadata.json adds N bytes, a possible renumber array and sample buffers
conservatively: 42041344 / 221446144 bytes. These are array bounds within
256 MiB; allocator/library/stack/RSS and Python grading RAM are separate.

calibrate.c/calibrate.json.gz preserve 1294947 machine price comparisons
and all 256 scalar costs; unrestricted integer products and literal routed
losses independently check them. transform.c uses a separate tensor
min-plus algorithm with literal query costs, certified 32-bit log floors,
exact near-score crossproducts and smallest-book-index ties.
Four tiny complete Fraction/literal controls are in transform_calibration.json.
All ten original label maps match its full independent minima. The
*_row*.txt descriptors and complete-label hashes bind exactly what was checked.
Original native per-row outputs and the driver's aggregate records survive.

analyse.py retains the first literal source/CDF/loss grading. The five-block
analysis originally used initial_bounds.py. Forty large original bounds
reproduce after exact product cancellation; recheck_five.py preserves that
check. Current production bounds additionally use unreduced integer signs
during binary comparisons without changing the rational objective.
These preserved scripts imported then-current production code; copying
them into another environment is not a pinned historical runtime image.

Default repository validation decompresses and grades original data,
checks descriptor log floors, calibration populations, hashes and source
loss/count consistency. It grades recorded complete native minima, rather
than claiming a fresh native tensor run or repeating 199 billion discovery
comparisons. The original native checker was actually run in this phase.

For an optional fresh tensor run, work from the repository root, create
ignored build/priced-vector/, decompress five.json.gz and six.json.gz there,
and compile transform.c to build/priced-vector/transform.exe. Set PYTHONPATH
to the repository root, then run the preserved check_transform.py with those
two JSON paths. It recreates public descriptors and temporary expected-label
files in that ignored directory. Compare its scientific fields and complete
label hashes; elapsed clock values may differ. Keep the original snapshots
and outputs intact.

Actors and public planners receive frozen selected descriptors, not these
grading maps or sample sources. No instance histogram, source/old-parent
reread, archive/environment/provider history or cached source value is an
allowed memory channel. Zero model calls and natural workflow episodes.
