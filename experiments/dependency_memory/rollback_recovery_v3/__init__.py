"""Prospective harder-task rollback development study; earlier launches stay sealed."""


def load_tests(loader,tests,pattern):
    # Repository discovery starts at dependency_memory without a package prefix.
    # Load the canonical namespace so typed records never gain duplicate identities.
    return loader.loadTestsFromName('experiments.dependency_memory.rollback_recovery_v3.test_study')
