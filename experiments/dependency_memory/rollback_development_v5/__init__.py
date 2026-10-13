"""Prospective staged rollback development: 48 tasks, no implicit model launch."""


def load_tests(loader, tests, pattern):
    return loader.loadTestsFromName("experiments.dependency_memory.rollback_development_v5.test_design")
