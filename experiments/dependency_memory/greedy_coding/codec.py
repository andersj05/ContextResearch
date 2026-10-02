"""Exactly 2*k parent bits; public group code and scalar tail, then one bit."""
from . import design
from experiments.dependency_memory.entropy_coding.codec import predict


def public_group(k,g=None):
    if type(k) is not int or k < 1:
        raise ValueError('Expected a positive public source length')
    if g is None:
        g = design.group_size(k)
    if type(g) is not int or not 1 <= g <= k:
        raise ValueError('Public group size must be in 1..k')
    return g


def nearest(blocks,book):
    return min(range(len(book)),key=lambda m:
               sum(design.LOSS[x][(book[m] >> (4*r))&15]
                   for r,x in enumerate(blocks)))


def encode(blocks,g=None):
    blocks = tuple(blocks)
    k = len(blocks)
    g = public_group(k,g)
    if any(type(x) is not int or not 0 <= x < 16 for x in blocks):
        raise ValueError('Expected four-bit source blocks')
    table = design.book(g)
    groups,tail = divmod(k,g)
    parent = 0
    for group in range(groups):
        segment = blocks[group*g:(group+1)*g]
        parent |= nearest(segment,table) << (2*g*group)
    for r in range(tail):
        x = blocks[groups*g+r]
        message = min(range(4),key=lambda m:design.LOSS[x][design.BASE[m]])
        parent |= message << (2*g*groups+2*r)
    return parent


def decode_response(parent,block,k,g=None):
    g = public_group(k,g)
    if type(parent) is not int or not 0 <= parent < (1 << (2*k)):
        raise ValueError('Parent exceeds 2*k charged bits')
    if type(block) is not int or not 0 <= block < k:
        raise ValueError('Invalid public block')
    groups = k//g
    if block < groups*g:
        group,coordinate = divmod(block,g)
        message = (parent >> (2*g*group))&((1 << (2*g))-1)
        table = design.book(g)
        if message >= len(table):
            raise ValueError('Unused public group message')
        return (table[message] >> (4*coordinate))&15
    tail = block-groups*g
    return design.BASE[(parent >> (2*g*groups+2*tail))&3]


def update(parent,block,omitted,k,g=None):
    if type(omitted) is not int or not 0 <= omitted < 4:
        raise ValueError('Invalid public omission')
    return (decode_response(parent,block,k,g) >> omitted)&1
