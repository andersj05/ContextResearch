"""User-authorized continuation of the v5 allocation without repeated identities."""


def load_tests(loader, tests, pattern):
    return loader.loadTestsFromName("experiments.dependency_memory.rollback_development_v5_continuation.test_continuation")
