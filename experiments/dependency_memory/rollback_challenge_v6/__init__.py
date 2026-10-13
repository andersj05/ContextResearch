"""Difficulty calibration and held-out rollback experiments; no implicit live calls."""


def load_tests(loader, tests, pattern):
    return loader.loadTestsFromName("experiments.dependency_memory.rollback_challenge_v6.test_challenge")
