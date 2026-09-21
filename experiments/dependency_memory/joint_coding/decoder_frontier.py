"""Decoder-complete, exact-arithmetic bounds for the delayed-query block model.

Enumerates all 36**4 unordered decoder tables through their 4,751 orbits.
No numerical optimizer, third-party package, provider, or floating-point
comparison is used to certify a bound. See the accompanying research note
for the analytic reduction from arbitrary joint encoders to these checks.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
from itertools import combinations_with_replacement, permutations
import json
from math import prod
from pathlib import Path


PAIRS = tuple(combinations_with_replacement(range(8), 2))
PAIR_INDEX = {pair: i for i, pair in enumerate(PAIRS)}
UNSIGNED = (PAIR_INDEX[(0, 7)],) * 4
# Chosen by exploration, then treated solely as exact rational witnesses.
T = Fraction(116328784, 10**9)
UNSIGNED_WEIGHTS = tuple(
    1009489803807342 if a in (0, 15) else
    163503398730886 if a.bit_count() == 2 else 0
    for a in range(16)
)
# Sum = 3*10**15. The six middle weights are equal; no optimizer is needed.
GRADIENT_SCALE = 2**160
LOG_BITS = 192
LOG_TERMS = 100
LOWER_TARGET = Fraction(2618989799, 10**10)
UPPER_TARGET = Fraction(2618989801, 10**10)


def ceil_div(n: int, d: int) -> int:
    return -(-n // d)


def _ln_unit_interval(n: int, d: int) -> tuple[int, int]:
    """Bounds on 2**LOG_BITS * ln(n/d), for 1 <= n/d <= 2.

    Use ln(y)=2*sum z**(2j+1)/(2j+1), z=(y-1)/(y+1).
    Every arithmetic operation rounds outward. Since 0 <= z <= 1/3,
    the omitted tail is at most 3**(-2*LOG_TERMS).
    """
    if not 0 < d <= n <= 2*d:
        raise ValueError("Expected a ratio in [1,2]")
    scale = 1 << LOG_BITS
    if n == d:
        return 0, 0
    low = (n-d)*scale // (n+d)
    high = ceil_div((n-d)*scale, n+d)
    square_low = low*low // scale
    square_high = ceil_div(high*high, scale)
    power_low, power_high = low, high
    total_low = total_high = 0
    for j in range(LOG_TERMS):
        total_low += power_low // (2*j+1)
        total_high += ceil_div(power_high, 2*j+1)
        power_low = power_low*square_low // scale
        power_high = ceil_div(power_high*square_high, scale)
    return (2*total_low,
            2*total_high + ceil_div(scale, 3**(2*LOG_TERMS)))


@lru_cache(maxsize=256, typed=True)
def log2_bounds(n: int, d: int = 1) -> tuple[Fraction, Fraction]:
    """Rigorous rational bounds on log2(n/d); no floating-point logarithm."""
    if type(n) is not int or type(d) is not int or n <= 0 or d <= 0:
        raise ValueError("Expected positive integers")
    exponent = n.bit_length() - d.bit_length()
    if exponent >= 0:
        denominator, numerator = d << exponent, n
    else:
        numerator, denominator = n << -exponent, d
    if numerator < denominator:
        numerator *= 2
        exponent -= 1
    low, high = _ln_unit_interval(numerator, denominator)
    two_low, two_high = _ln_unit_interval(2, 1)
    return (exponent + Fraction(low, two_high),
            exponent + Fraction(high, two_low))


def decimal_enclosure(low: Fraction, high: Fraction, places: int = 16) -> list[str]:
    """Outward rounded decimal endpoints, as strings (never JSON floats)."""
    scale = 10**places
    first = low.numerator*scale // low.denominator
    last = ceil_div(high.numerator*scale, high.denominator)
    def format_integer(value):
        sign = "-" if value < 0 else ""
        whole, decimal = divmod(abs(value), scale)
        return f"{sign}{whole}.{decimal:0{places}d}"
    return [format_integer(first), format_integer(last)]


def fraction_record(value: Fraction) -> dict:
    return {"numerator": value.numerator, "denominator": value.denominator}


def project(source: int, omitted: int) -> int:
    return ((source >> (omitted+1)) << omitted) | (source & ((1 << omitted)-1))


def loss_matrix(table: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    """L[x][a] counts errors on the 12 equally weighted omission/query routes."""
    if len(table) != 4 or any(type(p) is not int or not 0 <= p < 36 for p in table):
        raise ValueError("Expected four decoder-pair indices in 0..35")
    branches = [[[(project(x, o) ^ PAIRS[table[o]][b]).bit_count()
                  for b in range(2)] for x in range(16)] for o in range(4)]
    return tuple(tuple(sum(branches[o][x][(a >> o) & 1] for o in range(4))
                       for a in range(16)) for x in range(16))


def nearest_weights(loss: tuple) -> tuple[int, ...]:
    """Marginal of a uniformly tie-broken nearest word, with denominator 256.

    Every tie set is a Cartesian product of four one/two-choice sets, hence
    has size 1,2,4,8,16. This is a witness, not assumed RD-optimal.
    """
    weights = [0]*16
    for row in loss:
        best = min(row)
        winners = [a for a in range(16) if row[a] == best]
        if 16 % len(winners):
            raise ValueError("Loss does not have branch-product tie sets")
        for a in winners:
            weights[a] += 16 // len(winners)
    return tuple(weights)


def symmetry_maps() -> tuple:
    """All 16 bit flips times 24 coordinate permutations, on decoder tables.

    Each entry stores its new omitted coordinate and all 36 transformed
    unordered pairs. Sorting a pair may flip that branch's child-bit label.
    Such a relabeling is free and merely permutes decision-word columns.
    """
    maps = []
    for permutation in permutations(range(4)):
        for mask in range(16):
            branches = []
            for old_o in range(4):
                new_o = permutation[old_o]
                old_coordinates = [j for j in range(4) if j != old_o]
                new_coordinates = [j for j in range(4) if j != new_o]
                words = []
                for word in range(8):
                    full = sum(((word >> i) & 1) << permutation[j]
                               for i, j in enumerate(old_coordinates)) ^ mask
                    words.append(sum(((full >> j) & 1) << i
                                     for i, j in enumerate(new_coordinates)))
                pairs = tuple(PAIR_INDEX[tuple(sorted((words[a], words[b])))]
                              for a, b in PAIRS)
                branches.append((new_o, pairs))
            maps.append(tuple(branches))
    return tuple(maps)


def encode_table(table: tuple) -> int:
    return sum(value*36**o for o, value in enumerate(table))


def decode_table(index: int) -> tuple[int, ...]:
    return tuple(index // 36**o % 36 for o in range(4))


def decoder_orbits():
    """Disjoint complete cover; no assumption about orbit sizes or stabilizers."""
    transforms = tuple(tuple(tuple(value*36**new_o for value in pairs)
                             for new_o, pairs in mapping)
                       for mapping in symmetry_maps())
    seen = bytearray(36**4)
    covered = 0
    for index in range(36**4):
        if seen[index]:
            continue
        table = decode_table(index)
        orbit = {sum(mapping[o][table[o]] for o in range(4))
                 for mapping in transforms}
        if min(orbit) != index or any(seen[member] for member in orbit):
            raise ArithmeticError("Orbit partition overlaps or is not canonical")
        for member in orbit:
            seen[member] = 1
        covered += len(orbit)
        yield index, table, len(orbit)
    if covered != 36**4 or not all(seen):
        raise ArithmeticError("Incomplete decoder enumeration")


def kernel(loss: tuple, t: Fraction = T) -> tuple:
    """Integer kernel K=b**12*t**L for t=a/b."""
    if not 0 < t < 1:
        raise ValueError("Expected 0 < t < 1")
    powers = [t.numerator**l * t.denominator**(12-l) for l in range(13)]
    return tuple(tuple(powers[l] for l in row) for row in loss)


def dual_product(loss: tuple, weights: tuple, t: Fraction = T) -> tuple[int, int]:
    """An upper bound G on product(z_x)*g**16, represented by N/D.

    q_a=w_a/Q, z_x=sum_a q_a*t**L[x,a],
    g=max_a (1/16)*sum_x t**L[x,a]/z_x.
    Thus every channel satisfies I+s*E[L] >= -log2(G)/16, s=-log2(t).
    Ceilings give a rigorous upper bound on g. Q cancels algebraically.
    """
    if len(weights) != 16 or any(type(w) is not int or w < 0 for w in weights) or not sum(weights):
        raise ValueError("Expected sixteen nonnegative integer weights with positive sum")
    values = kernel(loss, t)
    totals = [sum(w*k for w, k in zip(weights, row)) for row in values]
    maximum = max(sum(ceil_div(GRADIENT_SCALE*values[x][a], totals[x])
                      for x in range(16)) for a in range(16))
    numerator = prod(totals) * maximum**16
    denominator = (16*GRADIENT_SCALE*t.denominator**12)**16
    return numerator, denominator


def primal_bounds(loss: tuple, weights: tuple, t: Fraction = T) -> dict:
    """Exact Gibbs channel loss and a rigorous upper bound on its information.

    P(a|x)=w_a*K[x,a]/Z_x. Its information is at most
    -E log2(z_x) + E[L]*log2(t), with equality only if q is its marginal.
    """
    values = kernel(loss, t)
    totals = [sum(w*k for w, k in zip(weights, row)) for row in values]
    normalizer = sum(weights)*t.denominator**12
    distortion = sum(Fraction(sum(weights[a]*values[x][a]*loss[x][a]
                                  for a in range(16)), totals[x])
                     for x in range(16)) / 192
    logs = [log2_bounds(z, normalizer) for z in totals]
    free_low = -sum(high for low, high in logs) / 16
    free_high = -sum(low for low, high in logs) / 16
    t_low, t_high = log2_bounds(t.numerator, t.denominator)
    return {"distortion": distortion, "free_low": free_low, "free_high": free_high,
            "cross_information_low": free_low + 12*distortion*t_low,
            "information_upper": free_high + 12*distortion*t_high}


@lru_cache(maxsize=1)
def certificate() -> dict:
    histogram = Counter()
    digest = sha256()
    largest = second = None
    total = orbits = 0
    for index, table, size in decoder_orbits():
        loss = loss_matrix(table)
        weights = UNSIGNED_WEIGHTS if table == UNSIGNED else nearest_weights(loss)
        numerator, denominator = dual_product(loss, weights)
        # The denominator is common to all tables, including the special q.
        row = (numerator, index, size)
        if largest is None or row > largest:
            second, largest = largest, row
        elif second is None or row > second:
            second = row
        digest.update(f"{index}:{size}:{numerator:x}\n".encode("ascii"))
        histogram[size] += 1
        total += size
        orbits += 1
    if orbits != 4751 or total != 36**4 or largest[1] != encode_table(UNSIGNED):
        raise ArithmeticError("Decoder coverage or worst dual witness changed")
    # Every other class has a uniform, exactly checked objective separation.
    if second[0] * 2**190 >= denominator:
        raise ArithmeticError("Non-unsigned lower bound must exceed 95/8")
    log_low, log_high = log2_bounds(largest[0], denominator)
    free_lower = -log_high / 16
    t_low, t_high = log2_bounds(T.numerator, T.denominator)
    distortion_lower = (free_lower-2) / (-12*t_low)
    primal = primal_bounds(loss_matrix(UNSIGNED), UNSIGNED_WEIGHTS)
    if not (distortion_lower > LOWER_TARGET
            and primal["distortion"] < UPPER_TARGET
            and primal["information_upper"] < 2):
        raise ArithmeticError("Requested strict rate/distortion bounds failed")
    return {
        "schema_version": 1,
        "evidence_status": "exact finite certificate plus analytic block-coding argument; external review open",
        "source_symbols": 16, "decision_words": 16,
        "unordered_branch_pairs_including_repeats": 36,
        "decoder_tables_covered": total, "symmetry_group_size": 384,
        "decoder_orbits": orbits,
        "orbit_size_histogram": {str(k): v for k, v in sorted(histogram.items())},
        "orbit_dual_products_sha256": digest.hexdigest(),
        "t": fraction_record(T), "gradient_scale_bits": 160,
        "log_interval_bits": LOG_BITS, "log_series_terms": LOG_TERMS,
        "unsigned_weights": list(UNSIGNED_WEIGHTS),
        "worst_dual_orbit": {"index": largest[1], "size": largest[2],
                             "pairs": [list(PAIRS[p]) for p in decode_table(largest[1])]},
        "runner_up_dual_orbit": {"index": second[1], "size": second[2],
                                 "pairs": [list(PAIRS[p]) for p in decode_table(second[1])]},
        "other_orbits_free_energy_strict_lower": "95/8",
        "universal_free_energy_lower_enclosure": decimal_enclosure(free_lower, -log_low/16),
        "finite_all_k_distortion_lower_enclosure": decimal_enclosure(distortion_lower, distortion_lower),
        "achievable_asymptotic_distortion_enclosure": decimal_enclosure(primal["distortion"], primal["distortion"]),
        "test_channel_information_upper_enclosure": decimal_enclosure(primal["information_upper"], primal["information_upper"]),
        "certified_strict_interval": {"lower": str(LOWER_TARGET), "upper": str(UPPER_TARGET),
                                       "decimal": ["0.2618989799", "0.2618989801"]},
        "finite_lower_bound": "D_k(2k) > 0.2618989799 for every k >= 1",
        "asymptotic_upper_bound": "lim_k D_k(2k) < 0.2618989801",
        "exact_closed_form_or_finite_optimal_code_claimed": False,
        "model_requests": 0,
    }


def report(result: dict) -> str:
    return f"""# Certified unrestricted rate-two interval

Generated by `joint_coding/decoder_frontier.py`, using only Python's standard
library and exact integers/rationals. No optimizer is trusted by this check.

**0.2618989799 < lim_k D_k(2k) < 0.2618989801.**

The lower inequality also holds at every finite positive k. The upper
inequality uses standard asymptotic coding; it is not a supplied finite code.

| Check | Certified result |
|---|---|
| Unordered decoder tables, including repeated and noncomplementary pairs | {result['decoder_tables_covered']:,} |
| Bit-flip / coordinate-permutation group | 384 |
| Disjoint decoder orbits | {result['decoder_orbits']:,} |
| Universal supporting-objective lower bound | {result['universal_free_energy_lower_enclosure']} |
| All-k distortion lower bound | {result['finite_all_k_distortion_lower_enclosure']} |
| Rational test-channel distortion | {result['achievable_asymptotic_distortion_enclosure']} |
| Upper bound on test-channel mutual information (bits) | {result['test_channel_information_upper_enclosure']} |

Every interval displayed above is rounded outward. The strict final interval
has width 0.0000000002 in error probability (0.00000002 percentage points).
The resulting excess over the isolated one-bit child optimum is about
1.189898 percentage points. The earlier interval was [129/512, 101/384].

The certificate covers arbitrary joint parent encoders, different decoder
tables across blocks, and source-independent randomization by the analytic
reduction in the [proof](../../../research/DECODER_COMPLETE_FRONTIER_2026-09-21.md).
No exact closed form, finite two-block optimum, or native-agent benefit is
claimed. The numerical exploratory optimizer is unnecessary for reproduction.
External correctness and publication novelty remain open; no model calls.
"""


def main() -> None:
    result = certificate()
    output = Path(__file__).parent.parent / "results"
    (output / "decoder_frontier_certificate.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    (output / "decoder_frontier_report.md").write_text(
        report(result), encoding="utf-8", newline="\n")
    print("Certified: 0.2618989799 < limiting rate-two error < 0.2618989801")
    print(f"Covered {result['decoder_tables_covered']} tables in {result['decoder_orbits']} orbits")


if __name__ == "__main__":
    main()
