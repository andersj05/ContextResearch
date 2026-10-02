"""Only frozen public descriptors are exposed to the coding actors."""
from functools import cache
from fractions import Fraction as F
import json
from pathlib import Path
from .design import Book


@cache
def load(name):
    data = json.loads(Path(__file__).with_name('tables.json').read_text(encoding='utf-8'))
    row = data['books'][name]
    return Book(row['g'], tuple(row['price']), tuple(row['words']),
                tuple(row['proposal_counts']), tuple(row['counts']))


def names():
    data = json.loads(Path(__file__).with_name('tables.json').read_text(encoding='utf-8'))
    return data['finite_book'], data['slack_family_book']


@cache
def weights(name):
    data = json.loads(Path(__file__).with_name('tables.json').read_text(encoding='utf-8'))
    losses = tuple(data['books'][name]['loss_sums'])
    book = load(name)
    error = F(1, 2)-F(sum(losses), 12*book.g*16**book.g)
    return losses, error
