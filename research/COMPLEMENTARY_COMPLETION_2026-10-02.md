# Complementary final decoders suffice under the balanced source

October 2, 2026. **Local analytic deduction with exact branch and whole-code
checks.** Claim C66. The argument is elementary averaging/bitwise decoder
design, not a new derandomization principle. External correctness and
publication priority remain open. No model call or natural workflow is added.

In the stated uniform delayed-query model, for **every** number of blocks k
and parent capacity B,

\[
\boxed{D_k(B)=D_k^{\mathrm{complementary}}(B).}
\]

Every fixed code with arbitrary, possibly repeated endpoint pairs has a
complementary completion with no larger population-average error. The parent
encoder and its capacity stay unchanged. Each one-bit updater output changes
only by a fixed public label swap. This is a reduction of the decoder search
space, not a new error bound or preservation of each source instance.

It also reduces every positive-slope supporting optimization to the six
complementary symmetry families. The [C62 converse](COMPLEMENTARY_DECODER_COVER_2026-10-01.md)
therefore supplies a short alternative proof of the unchanged unrestricted
three-block lower bound 40,072/147,456. The independent, much larger
[C63 certificate](ALL_DECODER_THREE_BLOCK_COVER_2026-10-01.md) is preserved.

## 1. Information contract and theorem

Start with any fixed encoder E and updater U. Parent M is produced before
public R/O and disappears after U emits one bit Z. Only then is J revealed.
The final decoder receives Z,R,O,J and fixed public tables; it has no parent,
source, archive, provider history or extra instance-dependent channel.

For each r,o, write the two three-bit prediction endpoints as v^0,v^1.
Endpoint coordinates correspond to the three possible late queries j != o.
The endpoints need not be complementary or distinct. The public query law
is independent of the source, and every queried source coordinate is balanced:
P(X_rj=0)=P(X_rj=1)=1/2. The current independent uniform block/query law meets
these assumptions. Independence among the source coordinates is not needed
for this particular lemma.

**Completion theorem.** There is a fixed complementary table and fixed public
bit relabeling of U whose average Hamming error is no larger, with the same E,
the same parent states and the same information timing. Completion is chosen
from the population law and the old code before an actual source is drawn.
The theorem is not an online rule that reads forgotten source values.

## 2. Averaging proof

For each endpoint coordinate where v^0_j != v^1_j, leave both bits unchanged.
Where they agree, choose an independent fair design bit C_r,o,j for the new
zero endpoint and its complement for the new one endpoint. Keep the original
E and U fixed while averaging over these design choices.

On disagreeing coordinates, predictions stay identical pointwise. On agreeing
coordinates, the old prediction is the constant v^0_j, so its expected error
is 1/2 by source balance and source-independent queries. Before sorting the
new endpoints, the new prediction is C_r,o,j XOR Z. Conditional on the source
and old Z, averaging over the independent fair C gives error 1/2. Thus the
average over all public completions equals the original code's average error.

There are finitely many completions for each finite k. At least one has no
larger error than that average. Fix it before the source. It is a legal code:
E is unchanged and U still produces one bit before J.

If canonical endpoint ordering swaps the new zero/one words, replace U's
output by Z XOR h_r,o, where h_r,o is a fixed public bit. This is a bijection
on the child alphabet, requires only the already public R/O, and makes the
actual prediction agree with the unsorted completion. It adds no state and
does not make J available earlier. Random design bits are only a proof device;
the resulting operating code has a fixed public decoder.

Complementary codes are already a subset of unrestricted codes. Applying the
construction to every unrestricted code proves equality of the two optima for
every k/B, including arbitrary joint parent encoders and heterogeneous block
tables. Independent source-free random tapes can be fixed before this argument;
undeclared source-correlated tapes would be another information channel.

## 3. Constructive population design and information objective

On an originally agreeing coordinate, choose the new zero-endpoint bit to be
the modal population value of X_rj XOR old_Z_r,o, breaking ties toward zero.
The new prediction's error is then at most 1/2. This directly chooses a good
completion coordinate by coordinate. Originally disagreeing bits stay fixed.
Computing these correlations may require the whole source population and
existing code; no efficient practical design algorithm is implied.

The [finite adapter](../experiments/dependency_memory/decoder_completion/README.md)
computes these design statistics offline. The operating updater receives only
M,R,O and the fixed codebook; the final predictor receives only Z,R,O,J and the
fixed endpoint table. Tests independently execute every reported query route.
This is a trusted-function mathematical adapter, not a physical process sandbox
or a provider-native compaction experiment.

The same argument applies to any channel P(A|X), where A lists the four old
updater responses. Canonicalization sends A to A XOR a fixed four-bit mask, so
I(X;A) is exactly unchanged. Choose a completion with no larger E L. Therefore,
for every s>=0,

\[
\min_{g,\,P(A|X)}\{I(X;A)+s\mathbb E L_g\}
=\min_{g\ \mathrm{complementary},\,P(A|X)}
\{I(X;A)+s\mathbb E L_g\}.
\]

This uses a fixed channel while choosing decoder bits; it does not assume an
optimal channel or discard output words outside a witness's support. Under
the existing uniform block/query symmetries, 256 complementary tables have
six orbits, in place of 4,751 orbits covering all 36^4 unrestricted tables.
The remaining full-curve comparison is between those six families. Completion
alone does not prove unsigned dominance at every slope.

## 4. Finite evidence and limits

The [source-bound certificate](../experiments/dependency_memory/results/decoder_completion_2026-10-02.json)
checks all 36 unordered branch pairs and all 256 Boolean updaters on eight
uniform three-bit sources: 9,216 branch/policy cases and 35,840 oriented
completion scores. Every average identity holds. These are individually checked
finite examples, not model trials or the proof of arbitrary k. An updater's
dependence on omitted bits or other blocks is allowed by the averaging proof,
which keeps the whole old code fixed.

Eight preserved C63 auxiliary books are completed without changing their
parents. Optional nearest-parent reassignment afterward is a separate legal
construction; it is not needed for the theorem. All three score stages execute
every source and final route. Identity on the existing C59 complementary witness
adds another 147,456 route checks. Total executed routes: 3,686,400.

| Preserved source file | Original errors | Completed, same parent | Completed, reassigned parent |
|---|---:|---:|---:|
| `search_144121.json` | 41,589 | 41,393 | 41,050 |
| `search_144526.json` | 41,589 | 41,393 | 41,050 |
| `search_146713.json` | 41,678 | 41,397 | 41,206 |
| `search_147118.json` | 41,678 | 41,397 | 41,206 |
| `search_149225.json` | 41,168 | 41,168 | 41,138 |
| `search_149227.json` | 41,088 | 41,088 | 40,738 |
| `search_149240.json` | 41,168 | 41,168 | 41,138 |
| `search_149312.json` | 41,088 | 41,088 | 40,738 |

Every denominator is 147,456. These already inspected mathematical cases include
symmetry-related examples and are not independent replications. The best new
score, 40,738, does **not** beat the existing 40,529-error witness. The finite
optimum and numerical frontier stay unchanged; the advance is the reduction and
alternative proof. Original books, parent assignments and source bytes remain
preserved in their old locations.

### Why the hypotheses and loss metric matter

Source balance cannot simply be removed. Let X be 0000 or 0011 with probability
1/2 each, with the existing uniform O/J law. A two-state parent and one-bit child
can distinguish them; noncomplementary projection endpoints give zero error.
Enumerating all 256 complementary tables gives at least four errors among the
24 equally weighted source/query outcomes, or **1/6**. The generator and a
separate coordinate calculation both verify that minimum. This is a biased-source
counterexample to extending complementary optimality, not the active source law.

Nor is this pointwise preservation. For a single uniform three-bit branch,
old endpoints (000,001) and child equal to its least significant bit have the same
mean error as completed endpoints (000,111). Yet source 001 goes from zero
errors to two errors. Average Hamming loss does not supply individual semantic
safety, tail-risk or worst-case guarantees.

Eight tests separately check coordinate completions, Boolean policies, whole
joint codes, unchanged complementary inputs, exact joint-count relabeling,
the biased counterexample, individual harm and independent full-route grading.
No general derandomization novelty, efficient encoder, publication priority,
new natural task, model improvement or token/production-cost result is claimed.

## 5. Reproduce and continue

```powershell
python -m experiments.dependency_memory.decoder_completion.certificate
python -m unittest discover -s experiments/dependency_memory -v
python scripts/validate_context_repo.py
python scripts/build_paper.py
```

The next mathematical target is a proof or counterexample for unsigned dominance
over the other five complementary families for all 0<t<1. A finite float grid
is discovery only. The C65 eight-point certificates and its all-slope restricted
unsigned algebra remain unchanged and provide checks for a prospective full
curve proof. Actual workflow intake and stronger model controls remain separate.
