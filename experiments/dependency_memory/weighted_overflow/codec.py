"""C72 actors with the new public, pre-source allocation rule."""
from experiments.dependency_memory.tie_coding import codec as original
from . import bounds


def count(n, g=8, a=None):
    bounds.parameters(n, g, a)
    return bounds.select(n, g)[0] if a is None else a


def encode(blocks, g=8, a=None, *, diagnostics=False):
    blocks = tuple(blocks)
    if type(g) is not int or g not in bounds.GROUPS or not blocks or len(blocks) % g:
        raise ValueError('Nonempty source length must be a multiple of a supported public g')
    return original.encode(blocks, g, count(len(blocks)//g, g, a), diagnostics=diagnostics)


def decode_response(parent, block, n, g=8, a=None):
    return original.decode_response(parent, block, n, g, count(n, g, a))


def update(parent, block, omitted, n, g=8, a=None):
    return original.update(parent, block, omitted, n, g, count(n, g, a))


def predict(child, block, omitted, query):
    return original.predict(child, block, omitted, query)
