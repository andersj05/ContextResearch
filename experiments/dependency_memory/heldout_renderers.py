"""Offline semantics for the four reserved synthetic manifest families.

This module does not construct model requests or modify the development v1
serializer. Its static metadata is persistent public side information; the
selected manifest is disclosed only by the surrounding environment's timing
rule. A future adapter must preserve that distinction and pass its own wire
isolation checks before any launch.

The domain is deliberately fixed to six canonical job keys and two candidates.
No function accepts a fixture, target, receipt, seed, or evaluator label. The
catalogs cover every pair before a route is selected. They are controlled
relational templates, not observed workloads or evidence of model inference.
"""

from __future__ import annotations

from itertools import combinations


VERSION = "heldout_renderer_semantics_v1"
FAMILY_NAMES = ("alias_chain", "package_prerequisites", "validation_scope", "deployment_handoff")
RENDER_MODES = ("explicit_labels", "inferred_dependencies")
JOB_KEYS = tuple(f"job-{i}" for i in range(6))
ARTIFACTS = ("ledger-snapshot", "route-schema", "asset-index", "clock-profile", "quota-map", "trace-catalog")
_CATALOG_NAMES = ("aurora", "birch", "coral", "dune", "elm", "flint", "grove", "heather",
                  "iris", "juniper", "kelp", "linden", "meadow", "nectar", "orchid")
_TASKS = {
    "alias_chain": (
        "Resolve each requested alias through its intermediate name to its artifact. "
        "The eventual handoff requires a receipt for one of those two artifacts."
    ),
    "package_prerequisites": (
        "Trace the requested package's prerequisite components to their source artifacts. "
        "The eventual handoff requires a receipt for one of those two source artifacts."
    ),
    "validation_scope": (
        "The stated verification obligation covers every artifact in its named scope. "
        "The eventual handoff requires a receipt for one of those two scoped artifacts."
    ),
    "deployment_handoff": (
        "Resolve the stated deployment handoff's required delivery roles to the artifacts "
        "whose evidence they require. The eventual handoff requires a receipt for one of "
        "those two artifacts."
    ),
}
_CLUE_FIELDS = {"alias_chain": "requested_aliases", "package_prerequisites": "requested_package",
                "validation_scope": "verification_obligation", "deployment_handoff": "deployment_handoff"}


def public_metadata(family: str) -> dict:
    """Return a fresh, route-independent public catalog for exactly six jobs.

    Only the family chooses a catalog. All 15 possible candidate pairs are
    represented, and no target or opaque record value enters its construction.
    Numeric catalog order is not a revision schedule: only JOB_KEYS determines
    the public lexicographic refresh order.
    """
    if type(family) is not str or family not in FAMILY_NAMES:
        raise ValueError("Unknown held-out family")
    metadata = {"version": VERSION, "family": family,
                "jobs": [{"key": key, "artifact": artifact} for key, artifact in zip(JOB_KEYS, ARTIFACTS)]}
    pairs = tuple(combinations(ARTIFACTS, 2))
    # Fixed public names obscure neither the relations nor the revision rule.
    # The permutation only avoids using numeric pair labels as surface names.
    labels = tuple(_CATALOG_NAMES[(7 * index + 3) % 15] for index in range(15))
    if family == "alias_chain":
        names = ("lark", "bramble", "cinder", "marsh", "opal", "fern")
        aliases = ("westgate", "northstar", "lowtide", "sunrise", "highridge", "eastwind")
        metadata["aliases"] = [{"alias": alias, "intermediate_name": names[index]}
                               for alias, index in zip(aliases, (2, 5, 1, 4, 0, 3))]
        metadata["names"] = [{"intermediate_name": name, "artifact": ARTIFACTS[index]}
                             for name, index in zip(names, (4, 0, 5, 2, 1, 3))]
    elif family == "package_prerequisites":
        components = ("adapter", "catalogue", "resolver", "scheduler", "signer", "writer")
        metadata["components"] = [{"component": name, "source_artifact": ARTIFACTS[index]}
                                  for name, index in zip(components, (2, 4, 1, 5, 3, 0))]
        component_for = {row["source_artifact"]: row["component"] for row in metadata["components"]}
        metadata["packages"] = [{"package": f"bundle-{label}",
                                 "prerequisites": sorted(component_for[artifact] for artifact in pair)}
                                for label, pair in zip(labels, pairs)]
    elif family == "validation_scope":
        metadata["scopes"] = [{"scope": f"scope-{label}", "artifacts": sorted(pair)}
                              for label, pair in zip(labels, pairs)]
        # Obligation names and scope names have a different fixed ordering.
        metadata["obligations"] = [{"obligation": f"verify-{_CATALOG_NAMES[index]}",
                                   "scope": f"scope-{label}", "coverage": "all_scope_artifacts"}
                                  for index, label in enumerate(labels)]
    else:
        roles = ("publisher", "registrar", "dispatcher", "attestor", "operator", "curator")
        metadata["delivery_roles"] = [{"role": role, "evidence_artifact": ARTIFACTS[index]}
                                      for role, index in zip(roles, (3, 5, 0, 4, 2, 1))]
        role_for = {row["evidence_artifact"]: row["role"] for row in metadata["delivery_roles"]}
        metadata["handoffs"] = [{"handoff": f"handoff-{label}",
                                 "required_roles": sorted(role_for[artifact] for artifact in pair)}
                                for label, pair in zip(labels, pairs)]
    return metadata


def _family(metadata):
    if type(metadata) is not dict:
        raise ValueError("Public metadata must be an object")
    family = metadata.get("family")
    if metadata != public_metadata(family):
        raise ValueError("Public metadata must equal the static canonical family catalog")
    return family


def _pair(candidates):
    if (type(candidates) not in (list, tuple) or len(candidates) != 2
            or any(type(key) is not str or key not in JOB_KEYS for key in candidates)
            or tuple(candidates) != tuple(sorted(set(candidates)))):
        raise ValueError("Manifest requires two distinct sorted canonical job keys")
    return tuple(candidates)


def render_manifest(candidates, metadata: dict, render_mode: str) -> dict:
    """Render the clue from the candidate pair and public catalog only.

    The final target is deliberately absent from the signature. Inferred clues
    reference public relations, never stable job keys or receipt values.
    """
    family = _family(metadata)
    candidates = _pair(candidates)
    if render_mode not in RENDER_MODES:
        raise ValueError("Unknown render mode")
    if render_mode == "explicit_labels":
        return {"kind": "manifest", "candidate_keys": list(candidates)}
    artifact_for = {row["key"]: row["artifact"] for row in metadata["jobs"]}
    wanted = {artifact_for[key] for key in candidates}
    if family == "alias_chain":
        names = {row["intermediate_name"] for row in metadata["names"] if row["artifact"] in wanted}
        clue = sorted(row["alias"] for row in metadata["aliases"] if row["intermediate_name"] in names)
    elif family == "package_prerequisites":
        needed = {row["component"] for row in metadata["components"] if row["source_artifact"] in wanted}
        clue = next(row["package"] for row in metadata["packages"] if set(row["prerequisites"]) == needed)
    elif family == "validation_scope":
        scope = next(row["scope"] for row in metadata["scopes"] if set(row["artifacts"]) == wanted)
        clue = next(row["obligation"] for row in metadata["obligations"] if row["scope"] == scope)
    else:
        needed = {row["role"] for row in metadata["delivery_roles"] if row["evidence_artifact"] in wanted}
        clue = next(row["handoff"] for row in metadata["handoffs"] if set(row["required_roles"]) == needed)
    return {"kind": "manifest", "task": _TASKS[family], _CLUE_FIELDS[family]: clue}


def infer_candidates(manifest: dict, metadata: dict) -> tuple[str, str]:
    """Resolve a canonical clue using its public relational semantics.

    This is a scripted semantic oracle, not a model output repair mechanism.
    It rejects added fields and modified catalogs rather than accepting hidden
    channels or ambiguous relations. It does not call render_manifest.
    """
    family = _family(metadata)
    if type(manifest) is not dict or manifest.get("kind") != "manifest":
        raise ValueError("Expected a manifest object")
    if "candidate_keys" in manifest:
        if set(manifest) != {"kind", "candidate_keys"} or type(manifest["candidate_keys"]) is not list:
            raise ValueError("Explicit manifest contains undeclared content")
        return _pair(manifest["candidate_keys"])
    field = _CLUE_FIELDS[family]
    if set(manifest) != {"kind", "task", field} or manifest.get("task") != _TASKS[family]:
        raise ValueError("Inferred manifest contains missing or undeclared content")
    clue = manifest[field]
    try:
        if family == "alias_chain":
            if (type(clue) is not list or len(clue) != 2 or any(type(alias) is not str for alias in clue)
                    or clue != sorted(set(clue))):
                raise ValueError("Expected two distinct canonical aliases")
            aliases = {row["alias"]: row["intermediate_name"] for row in metadata["aliases"]}
            names = {row["intermediate_name"]: row["artifact"] for row in metadata["names"]}
            artifacts = [names[aliases[alias]] for alias in clue]
        else:
            if type(clue) is not str:
                raise ValueError("Expected a catalog name")
            if family == "package_prerequisites":
                packages = {row["package"]: row["prerequisites"] for row in metadata["packages"]}
                sources = {row["component"]: row["source_artifact"] for row in metadata["components"]}
                artifacts = [sources[component] for component in packages[clue]]
            elif family == "validation_scope":
                obligations = {row["obligation"]: row["scope"] for row in metadata["obligations"]}
                scopes = {row["scope"]: row["artifacts"] for row in metadata["scopes"]}
                artifacts = scopes[obligations[clue]]
            else:
                handoffs = {row["handoff"]: row["required_roles"] for row in metadata["handoffs"]}
                evidence = {row["role"]: row["evidence_artifact"] for row in metadata["delivery_roles"]}
                artifacts = [evidence[role] for role in handoffs[clue]]
    except KeyError as error:
        raise ValueError("Manifest refers to an unknown public relation") from error
    key_for = {row["artifact"]: row["key"] for row in metadata["jobs"]}
    return _pair(sorted(key_for[artifact] for artifact in artifacts))
