"""Certify a fixed three-block codebook by executing every delayed query.

Discovery is optional and separate. This file never runs the native heuristic.
The finite witness uses six parent bits, then one child bit, with no reread.
"""
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path

from experiments.dependency_memory.joint_coding.coding import CODEBOOK as PAIR_BOOK

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DISCOVERY = HERE / "discovery.json"
OUTPUT = HERE.parent / "results/joint_three_block_certificate_2026-10-01.json"
VERSION = "finite3_unsigned_witness_v1"


def loss(source, decision):
    weight = source.bit_count()
    return sum((3 - (weight - ((source >> o) & 1))) if ((decision >> o) & 1)
               else weight - ((source >> o) & 1) for o in range(4))


def decode_id(number):
    return (number & 15, (number >> 4) & 15, number >> 8)


def validate_book(book):
    if type(book) not in (tuple, list) or not 1 <= len(book) <= 64:
        raise ValueError("Expected 1..64 distinct branch-decision triples")
    if any(type(row) is not tuple or len(row) != 3 or
           any(type(a) is not int or not 0 <= a < 16 for a in row) for row in book):
        raise ValueError("Each codeword contains three four-bit decision words")
    if len(set(book)) != len(book):
        raise ValueError("Duplicate decision triple")


def parent_table(book):
    validate_book(book)
    one = [[loss(x, a) for a in range(16)] for x in range(16)]
    table = []
    for source in range(4096):
        x, y, z = decode_id(source)
        table.append(min(range(len(book)), key=lambda m:
                     one[x][book[m][0]] + one[y][book[m][1]] + one[z][book[m][2]]))
    return table


def update(message, block, omitted, book):
    # Called before the late coordinate is known; no source or archive argument.
    if type(message) is not int or not 0 <= message < len(book):
        raise ValueError("Invalid six-bit parent")
    if type(block) is not int or not 0 <= block < 3 or type(omitted) is not int or not 0 <= omitted < 4:
        raise ValueError("Invalid public branch")
    return (book[message][block] >> omitted) & 1


def predict(child, block, omitted, query):
    # The public decoder is fixed before the source. It cannot see the parent.
    if type(child) is not int or child not in (0, 1) or type(block) is not int or not 0 <= block < 3:
        raise ValueError("Invalid one-bit child or public block")
    if type(omitted) is not int or not 0 <= omitted < 4 or type(query) is not int or not 0 <= query < 4 or query == omitted:
        raise ValueError("Invalid late coordinate")
    return child


def grade(table, book):
    """Actual route execution independent of the popcount generator formula."""
    validate_book(book)
    if len(table) != 4096 or any(type(m) is not int or not 0 <= m < len(book) for m in table):
        raise ValueError("Expected one legal parent message for every source")
    branches = [[0] * 4 for _ in range(3)]
    histogram = Counter()
    for source, message in enumerate(table):
        # Truth labels are used only by the evaluator after actor prediction.
        truth = list(reversed(f"{source:012b}"))
        errors = 0
        for block in range(3):
            for omitted in range(4):
                child = update(message, block, omitted, book)
                for query in range(4):
                    if query == omitted:
                        continue
                    answer = predict(child, block, omitted, query)
                    wrong = answer != int(truth[4 * block + query])
                    branches[block][omitted] += wrong
                    errors += wrong
        histogram[errors] += 1
    errors = sum(k * v for k, v in histogram.items())
    ratio = Fraction(errors, 147456)
    return {"errors": errors, "outcomes": 147456,
            "distortion": {"numerator": ratio.numerator, "denominator": ratio.denominator},
            "branch_errors": branches, "per_source_error_histogram": dict(sorted(histogram.items())),
            "message_occupancies": [table.count(m) for m in range(len(book))]}


def selected_book():
    discovery = json.loads(DISCOVERY.read_text(encoding="utf-8"))
    ids = discovery["runs"]["greedy"]["codeword_ids"]
    if len(ids) != 64 or ids != sorted(set(ids)) or any(type(i) is not int or not 0 <= i < 4096 for i in ids):
        raise ValueError("Invalid fixed discovery witness")
    book = tuple(decode_id(i) for i in ids)
    validate_book(book)
    return book


def concatenation_book():
    return tuple(sorted((a, b, c) for (a, b), c in product(PAIR_BOOK, (0, 1, 14, 15))))


def certificate():
    discovery = json.loads(DISCOVERY.read_text(encoding="utf-8"))
    book = selected_book()
    table = parent_table(book)
    witness = grade(table, book)
    if witness["errors"] != discovery["runs"]["greedy"]["errors"]:
        raise ValueError("Native search and direct route grading disagree")
    control = concatenation_book()
    baseline = grade(parent_table(control), control)
    if baseline["errors"] != discovery["runs"]["concatenation"]["errors"]:
        raise ValueError("Historical concatenation and native control disagree")
    files = (HERE / "search.c", HERE / "witness.py", HERE / "test_finite3.py", DISCOVERY,
             HERE.parent / "joint_coding/coding.py")
    return {"version": VERSION, "date": "2026-10-01", "new_model_requests": 0,
        "evidence_class": "explicit finite construction and exhaustive route grading; heuristic discovery",
        "source_sha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "information_contract": {"independent_uniform_four_bit_blocks": 3, "parent_bits": 6, "child_bits": 1,
            "parent_before_block_and_omission": True, "child_before_query": True,
            "final_inputs": ["child_bit", "block", "omission", "query"], "archives_or_rereads": False,
            "codebook_fixed_before_source": True, "charged_as_instance_memory": False},
        "codebook": book, "parent_table": table, "witness": witness,
        "concatenation_control": baseline,
        "independent_two_bit_blocks": {"errors": 41472, "outcomes": 147456, "distortion": "9/32"},
        "errors_avoided_against_concatenation": baseline["errors"] - witness["errors"],
        "limits": "Upper bound only; unsigned fixed decoder. No proof of finite optimum, search completeness, scalable runtime, model gain or publication priority. Existing asymptotic results unchanged."}


def main():
    data = certificate()
    OUTPUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"witness_errors": data["witness"]["errors"], "outcomes": data["witness"]["outcomes"],
                      "concatenation_errors": data["concatenation_control"]["errors"],
                      "errors_avoided": data["errors_avoided_against_concatenation"]}))


if __name__ == "__main__":
    main()
