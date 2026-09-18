# Local audit of the compatibility scaling arguments

September 18, 2026. Scope: mathematical validity and independent computational formulations for claims C11-C13 in the [research memo](CREATIVE_RESEARCH_DIRECTIONS_2026-09-18.md). This is a local audit by the same research assistant, not independent external review, formal verification, or novelty certification.

## Outcome

The block-family conclusions survive this audit: exactly 3k parent bits are necessary and sufficient at error 1/4, and 2k parent bits force error strictly greater than 1/4 + 1/512 for every k >= 1. The argument allows arbitrary joint encoders across blocks. The finite entropy lemma admits an analytic proof, given below; its validity no longer depends solely on enumeration.

One scope error was corrected: the strict leave-one-out gap needs even n >= 4. At n=2, the two-bit parent can preserve both source bits, then pass the selected singleton through the one-bit child with zero error. The code already excluded n=2; the prose now agrees. No exact two-bit chain optimum has been computed.

## Assumption audit

| Item | Required condition | What breaks if changed |
|---|---|---|
| Source | k independent uniform four-bit blocks | The signature entropy and sum-information inequality need not have the stated values. |
| Timing | M precedes R,O; one-bit Z precedes J | Early relevance can remove the obstruction. |
| Decoder access | Only Z,R,O,J at the end | Reading M or any old source channel bypasses the child bottleneck. |
| Side information | R,O,J independent of source values and public at their stated stages | Instance-dependent public labels can carry uncharged information. |
| Capacity | At most 2^(2k) parent states and two child states in every execution | An entropy or average-length budget is a different model. |
| Randomization | Coins independent of source, fixed programs, hard capacities per realization | Fixing coins would not preserve an expected-only capacity constraint. |
| Loss | Uniform block, uniform omission, uniform remaining coordinate, average bit error | Worst-case loss or different branch weights require a new calculation. |

## Analytic entropy lemma

For any choice of complementary decoder pairs on the four triples, write the optimal branch functions as f_i(x) = maj(s_ij x_j : j != i), with x uniform on {-1,+1}^4. The signed-majority expansion has a nonzero cubic coefficient on the triple omitting i. No other branch contains that cubic monomial, so the four functions are linearly independent. Their joint range spans R^4.

All four functions are odd. The range therefore consists of antipodal pairs, and spanning R^4 requires at least four such pairs. For each output pair y,-y, the bijection x -> -x gives equally sized preimages. Denote the size of each member of pair i by a_i. Then a_i are positive integers, their sum is 8, and their number r is at least 4.

The entropy of the joint signature Y is

\[
H(Y)=4-\frac18\sum_{i=1}^r a_i\log_2 a_i.
\]

For fixed r, convexity of a log(a) means that transferring a unit from any smaller component greater than one to the largest component cannot decrease the sum. Its maximum occurs at (9-r,1,...,1). Among r=4,...,8 this is largest at r=4, giving (5,1,1,1). Consequently

\[
H(Y)\ge4-\frac58\log_2 5>\frac52,
\]

where the final inequality is equivalent to 5^10 < 2^24. Ordinary unsigned majorities have fibers (5,5,1,1,1,1,1,1), so the first bound is attained. This proof uses the same rank premise as the existing analytic eight-state proof but a separate extremal argument for entropy.

## Audit of the scaling steps

1. **Exact target.** Each branch has minimum error 1/4 and positive sampling weight. Equality of their average requires equality in every branch. Unique nearest complementary codewords force the full branch signature. Independent block inputs realize the Cartesian product of their signature ranges, requiring at least 8^k parent states even for joint encoders. Concatenating the eight-state construction attains this count.
2. **Noncomplementary branches.** Directly checking all 64 ordered decoder pairs, including repeated words, gives minimum error 1/3 among noncomplementary pairs. One such branch raises its block's error by at least (1/3-1/4)/4=1/48. This is a bound on fixed decoder types, not an assumption about how memory is allocated.
3. **Wrong signature decisions.** A wrong branch choice increases three-coordinate Hamming loss by at least one. Average branch mistake probability q_r is at most 3 delta_r; a union bound gives signature error p_r <= 12 delta_r. No independence of these mistakes is required.
4. **Conditional entropy.** Given M, reveal the signature-error indicator, then one of at most 15 alternatives. This gives H(Y_r|M) <= h2(p_r)+4p_r, whether or not Y_r is uniform. The reconstructed signature may lie outside the range; the 16-word alphabet still makes the bound valid.
5. **Averaging.** Assign auxiliary p_r=0 to blocks using a noncomplementary branch. Concavity bounds the average binary entropy by the entropy of the average p_r. Individual p_r need not lie below 1/2: only their average must, and delta <= 1/512 guarantees this.
6. **Joint encoding.** Source independence and conditional entropy subadditivity imply sum_r I(X^(r);M) <= I(X^(1),...,X^(k);M) <= 2k. Conditional independence is not assumed. Reversing this inequality would invalidate the proof.
7. **Strict endpoint.** At delta=1/512, the lower information bound is 5/2-168/512-h2(3/128). The exact integer inequality 3^3*125^125 > 2^874 implies h2(3/128)<11/64, making that information bound strictly greater than two bits per block. It also excludes every smaller delta by monotonicity on this interval.

## Independent finite checks

The [audit implementation](../experiments/dependency_memory/audit_scaling.py) does not import the original projection, decoder search, or scaling implementation. It uses explicit sign tuples and directly counts coordinate disagreements.

- All 64 ordered three-coordinate decoders, including constant decoders.
- All 8^4=4,096 oriented signed-majority assignments, without quotienting by output flips.
- Cubic Fourier coefficients of every branch function, including zero coefficients on the other branches' full triples.
- Equal antipodal fiber sizes and the maximum entropy product for every assignment.
- All 99 ordered positive compositions of 8 into at least four parts as a separate extremal-fiber check.
- Exact integer checks for both logarithmic inequalities.

The [certificate](../experiments/dependency_memory/results/scaling_audit_certificate.json) agrees with the original 256-assignment enumeration. Tests compare these independent formulations and enforce the corrected n-domain. These computations check finite ingredients; the general k argument is analytic.

## Literature boundary checked during the audit

[Equitz and Cover, Sections II-III](https://isl.stanford.edu/~cover/papers/transIT/0269equi.pdf) study compatible optimal descriptions in a progressive coding setup and give a Markov characterization. Their long-block rate-distortion setting does not directly instantiate our fixed one-bit child with a late block/omission choice. This is a distinction of models, not proof that our result is novel.

[Ahmadi et al., Sections II-A and III-A](https://arxiv.org/pdf/1207.2793v1) define cascade encoders with side information and costed actions. In their cascade-broadcast model, the intermediate encoder uses received messages and local observations to form a downstream message. That is close prior art for a memory update that cannot reread the source. The particular side-information timing, broadcast access, asymptotic rates, and reconstruction targets require an explicit reduction before transferring a theorem.

[Wang, Lim, and Gastpar, Section II](https://arxiv.org/abs/1504.00553v2) study caching before requests are known and request-dependent updates. Their update encoder sees both the source sequence and request sequence, whereas our updater cannot reread the source. This difference must be retained in any reduction. Their result is another reason to avoid claiming that delayed queries or a cache/update decomposition are new.

This targeted comparison does not establish a priority claim. A broader functional-compression and direct-sum literature review remains separate work. The mathematical result can be used as a locally audited diagnostic theorem while that comparison proceeds.

## Reproduce

```powershell
python experiments/dependency_memory/audit_scaling.py
python -m unittest discover -s experiments/dependency_memory -v
python scripts/validate_context_repo.py
```
