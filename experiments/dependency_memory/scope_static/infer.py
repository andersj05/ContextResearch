"""AST-only access-use heuristic with conservative whole-input fallback.

This is not a universal Python soundness certificate. The evaluator checks
finite catalogs separately. The analyzer reads public source and formal names,
never instances, evaluator answers, authored contracts or model responses.
"""
import ast
from dataclasses import dataclass
import re

from experiments.dependency_memory.scope_inference import codec


@dataclass(frozen=True)
class Value:
    paths: frozenset = frozenset()
    literals: frozenset = frozenset()
    items: tuple | None = None
    unknown: bool = False


UNKNOWN = Value(unknown=True)


def merge(*values):
    if not values:
        return Value()
    items = values[0].items
    if any(v.items != items for v in values[1:]):
        items = None
    return Value(frozenset().union(*(v.paths for v in values)),
                 frozenset().union(*(v.literals for v in values)), items, any(v.unknown for v in values))


class Analyzer:
    def __init__(self, source):
        tree = ast.parse(source)
        self.functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        self.values, self.presence, self.nonempty = set(), set(), set()
        self.issues, self.stack = [], []
        self.globals = {}
        for n in tree.body:
            if isinstance(n, (ast.Assign, ast.AnnAssign)):
                self.statement(n, self.globals)
        shadowed = {"type", "isinstance", "bool", "dict"} & (self.functions.keys() | self.globals.keys())
        if shadowed:
            self.fallback(tree, "shadowed structural builtin")

    def fallback(self, node, reason):
        self.values.add("$")
        item = {"line": getattr(node, "lineno", None), "reason": reason}
        if item not in self.issues:
            self.issues.append(item)

    def retain(self, value, mode="value"):
        if mode == "value" and value.items is not None:
            for part in value.items:
                self.retain(part)
        for path in value.paths:
            if mode == "type" and not path:
                # JSON projection preserves the root type, even for malformed
                # nondictionary roots. No root key set or truth claim follows.
                continue
            if mode == "truth" and not path:
                self.values.add("$")
            elif mode in ("type", "truth"):
                self.nonempty.add(path)
            else:
                self.values.add(path or "$")

    def keys(self, value):
        if (value.unknown or not value.literals or any(type(k) is not str or not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", k)
                                                     or k == codec.MARKER for k in value.literals)):
            return None
        return value.literals

    def access(self, base, key, node, subscript=False):
        self.retain(base, "type")
        self.retain(key)
        keys = self.keys(key)
        if keys is None:
            self.retain(base)
            self.issues.append({"line": node.lineno, "reason": "dynamic or unrepresentable key: retain its whole base"})
            return UNKNOWN
        paths = frozenset((p + "." if p else "") + k for p in base.paths for k in keys)
        if subscript:
            self.presence.update(paths)
        return Value(paths, unknown=base.unknown)

    def bind(self, target, value, env):
        if isinstance(target, ast.Name):
            env[target.id] = value
        elif isinstance(target, (ast.Tuple, ast.List)):
            if value.items is None or len(value.items) != len(target.elts):
                self.fallback(target, "unresolved destructuring")
                for child in target.elts:
                    self.bind(child, UNKNOWN, env)
            else:
                for child, part in zip(target.elts, value.items):
                    self.bind(child, part, env)
        else:
            self.fallback(target, "mutation or unsupported assignment")

    def expression(self, node, env):
        if node is None:
            return Value(literals=frozenset({None}))
        if isinstance(node, ast.Constant):
            return Value(literals=frozenset({node.value}))
        if isinstance(node, ast.Name):
            return env.get(node.id, self.globals.get(node.id, UNKNOWN))
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            items = tuple(self.expression(x, env) for x in node.elts)
            return Value(items=items)
        if isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                self.retain(self.expression(k, env))
                self.retain(self.expression(v, env))
            return UNKNOWN
        if isinstance(node, ast.Subscript):
            return self.access(self.expression(node.value, env), self.expression(node.slice, env), node, True)
        if isinstance(node, ast.UnaryOp):
            self.retain(self.expression(node.operand, env), "truth" if isinstance(node.op, ast.Not) else "value")
            return UNKNOWN
        if isinstance(node, ast.BoolOp):
            values = [self.expression(v, env) for v in node.values]
            for v in values:
                self.retain(v, "truth")
            return merge(*values)
        if isinstance(node, ast.BinOp):
            self.retain(self.expression(node.left, env))
            self.retain(self.expression(node.right, env))
            return UNKNOWN
        if isinstance(node, ast.Compare):
            values = [self.expression(n, env) for n in [node.left, *node.comparators]]
            for left, right, op in zip(values, values[1:], node.ops):
                keys = self.keys(left)
                if isinstance(op, (ast.In, ast.NotIn)) and right.paths and keys is not None:
                    self.retain(right, "type")
                    self.presence.update((p + "." if p else "") + k for p in right.paths for k in keys)
                else:
                    self.retain(left)
                    self.retain(right)
            return UNKNOWN
        if isinstance(node, ast.IfExp):
            self.retain(self.expression(node.test, env), "truth")
            return merge(self.expression(node.body, env), self.expression(node.orelse, env))
        if isinstance(node, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
            local = dict(env)
            for g in node.generators:
                iterable = self.expression(g.iter, local)
                if g.is_async or iterable.items is None:
                    self.fallback(node, "nonliteral comprehension iteration")
                    self.bind(g.target, UNKNOWN, local)
                else:
                    self.bind(g.target, merge(*iterable.items), local)
                for condition in g.ifs:
                    self.retain(self.expression(condition, local), "truth")
            self.retain(self.expression(node.elt, local), "truth" if isinstance(node, ast.GeneratorExp) else "value")
            return UNKNOWN
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "get":
                base = self.expression(node.func.value, env)
                if not 1 <= len(node.args) <= 2 or node.keywords:
                    self.fallback(node, "unsupported get signature")
                    return UNKNOWN
                result = self.access(base, self.expression(node.args[0], env), node)
                return merge(result, self.expression(node.args[1], env)) if len(node.args) == 2 else result
            arguments = [self.expression(v, env) for v in node.args]
            keywords = {v.arg: self.expression(v.value, env) for v in node.keywords}
            if None in keywords:
                self.fallback(node, "unresolved keyword expansion")
            name = node.func.id if isinstance(node.func, ast.Name) else None
            if name in {"eval", "exec", "globals", "locals", "getattr", "setattr", "vars", "__import__", "dir", "compile"}:
                self.fallback(node, "reflection or dynamic execution")
                return UNKNOWN
            if name in ("type", "isinstance", "bool") and arguments:
                self.retain(arguments[0], "truth" if name == "bool" else "type")
                for v in arguments[1:]:
                    self.retain(v)
                return UNKNOWN
            if name in self.functions:
                return self.function(name, arguments, keywords)
            if isinstance(node.func, ast.Attribute):
                self.retain(self.expression(node.func.value, env))
            for v in [*arguments, *keywords.values()]:
                self.retain(v)
            return UNKNOWN
        if isinstance(node, ast.Attribute):
            self.retain(self.expression(node.value, env))
            return UNKNOWN
        if isinstance(node, (ast.JoinedStr, ast.FormattedValue)):
            for n in (node.values if isinstance(node, ast.JoinedStr) else [node.value]):
                self.retain(self.expression(n, env))
            return UNKNOWN
        self.fallback(node, "unsupported expression: " + type(node).__name__)
        return UNKNOWN

    def statements(self, nodes, env):
        returns = []
        for node in nodes:
            returns += self.statement(node, env)
        return returns

    def statement(self, node, env):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = self.expression(node.value, env)
            for target in (node.targets if isinstance(node, ast.Assign) else [node.target]):
                self.bind(target, value, env)
        elif isinstance(node, ast.Expr):
            self.expression(node.value, env)
        elif isinstance(node, ast.Return):
            return [self.expression(node.value, env)]
        elif isinstance(node, ast.Raise):
            self.retain(self.expression(node.exc, env))
            self.retain(self.expression(node.cause, env))
        elif isinstance(node, ast.If):
            self.retain(self.expression(node.test, env), "truth")
            left, right = dict(env), dict(env)
            returns = self.statements(node.body, left) + self.statements(node.orelse, right)
            for name in left.keys() | right.keys():
                env[name] = merge(left.get(name, UNKNOWN), right.get(name, UNKNOWN))
            return returns
        elif isinstance(node, ast.For):
            iterable = self.expression(node.iter, env)
            if iterable.items is None:
                self.fallback(node, "nonliteral loop iteration")
                self.bind(node.target, UNKNOWN, env)
            else:
                self.bind(node.target, merge(*iterable.items), env)
            return self.statements(node.body, env) + self.statements(node.orelse, env)
        elif isinstance(node, ast.Try):
            branches, returns = [], []
            for body in [node.body, *(h.body for h in node.handlers), node.orelse, node.finalbody]:
                local = dict(env)
                returns += self.statements(body, local)
                branches.append(local)
            for name in set().union(*(b.keys() for b in branches)):
                env[name] = merge(*(b.get(name, UNKNOWN) for b in branches))
            return returns
        elif not isinstance(node, ast.Pass):
            self.fallback(node, "unsupported statement: " + type(node).__name__)
        return []

    def function(self, name, arguments, keywords):
        if name in self.stack or len(self.stack) >= 12:
            self.fallback(self.functions[name], "recursive or deep helper calls")
            return UNKNOWN
        node = self.functions[name]
        formals = [*node.args.posonlyargs, *node.args.args]
        if node.args.vararg or node.args.kwarg or len(arguments) > len(formals):
            self.fallback(node, "unsupported function signature")
        env = dict(self.globals)
        env.update({a.arg: v for a, v in zip(formals, arguments)})
        for formal, default in zip(formals[-len(node.args.defaults):] if node.args.defaults else [], node.args.defaults):
            env.setdefault(formal.arg, self.expression(default, env))
        for formal, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
            env[formal.arg] = self.expression(default, env) if default is not None else UNKNOWN
        env.update(keywords)
        self.stack.append(name)
        result = merge(*self.statements(node.body, env))
        self.stack.pop()
        return result

    def result(self):
        if "$" in self.values:
            contract = {"value_paths": ["$"], "presence_paths": [], "nonempty_paths": []}
        else:
            def beneath(path, roots):
                return any(path == p or path.startswith(p + ".") for p in roots)
            values = {p for p in self.values if not beneath(p, self.values - {p})}
            nonempty = {p for p in self.nonempty if not beneath(p, values)}
            presence = {p for p in self.presence if not beneath(p, values) and p not in nonempty}
            contract = {"value_paths": sorted(values), "presence_paths": sorted(presence), "nonempty_paths": sorted(nonempty)}
        try:
            codec.validate(contract)
        except ValueError:
            self.fallback(ast.Module(), "contract outside the existing projection DSL")
            contract = {"value_paths": ["$"], "presence_paths": [], "nonempty_paths": []}
        return {"contract": contract, "issues": self.issues, "whole_input_fallback": "$" in contract["value_paths"],
                "limits": "AST-only heuristic; finite checks are separate. No universal Python soundness, minimal scope or slicing novelty claim."}


def infer(source, entry, record_parameter, *, public_arguments=None):
    analyzer = Analyzer(source)
    if entry not in analyzer.functions or record_parameter not in [a.arg for a in analyzer.functions[entry].args.args]:
        raise ValueError("Unknown public entry or record parameter")
    keywords = {record_parameter: Value(paths=frozenset({""}))}
    for name, value in (public_arguments or {}).items():
        if name == record_parameter:
            raise ValueError("No record instance may enter source analysis")
        keywords[name] = Value(literals=frozenset({value}))
    analyzer.retain(analyzer.function(entry, [], keywords))
    return analyzer.result()
