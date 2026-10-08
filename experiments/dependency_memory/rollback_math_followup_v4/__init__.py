"""Separately frozen mathematical development follow-up with failure diagnostics."""


def load_tests(loader,tests,pattern):
    return loader.loadTestsFromName('experiments.dependency_memory.rollback_math_followup_v4.test_followup')
