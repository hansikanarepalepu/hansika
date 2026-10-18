"""Static checks for common Python mistakes. Pure standard library."""
import ast
import builtins

HINTS = {
    "syntax_error": "Python can't parse this line. Check brackets, colons and indentation.",
    "bare_except": "Catch specific errors, e.g. `except ValueError:`. A bare `except:` hides real bugs.",
    "mutable_default": "Use `None` as the default and create the list/dict inside the function.",
    "none_compare": "Use `is None` / `is not None` instead of `== None`.",
    "unused_import": "Remove the import, or use it. Unused imports clutter the file.",
    "builtin_shadow": "Rename the variable. It hides a built-in (list, str, id...) you may need later.",
    "long_function": "Split this function into smaller ones. Aim for under 50 lines.",
}
MAX_FUNCTION_LINES = 50
BUILTINS = {n for n in dir(builtins) if not n.startswith("_")}


def _issue(rule, node_or_line, message, lines):
    line = node_or_line if isinstance(node_or_line, int) else node_or_line.lineno
    code = lines[line - 1].strip() if 0 < line <= len(lines) else ""
    return {"rule": rule, "line": line, "message": message, "hint": HINTS[rule], "code": code}


def analyze(source):
    lines = source.splitlines()
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return [_issue("syntax_error", e.lineno or 1, f"Syntax error: {e.msg}", lines)]

    issues = []
    imported, used = {}, set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append(_issue("bare_except", node, "Bare `except:` clause", lines))

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in node.args.defaults + [d for d in node.args.kw_defaults if d]:
                if isinstance(d, (ast.List, ast.Dict, ast.Set)):
                    issues.append(_issue("mutable_default", d, "Mutable default argument", lines))
            end = getattr(node, "end_lineno", node.lineno)
            if end - node.lineno + 1 > MAX_FUNCTION_LINES:
                issues.append(_issue("long_function", node, f"Function `{node.name}` is too long", lines))

        elif isinstance(node, ast.Compare):
            for op, comp in zip(node.ops, node.comparators):
                if isinstance(op, (ast.Eq, ast.NotEq)) and isinstance(comp, ast.Constant) and comp.value is None:
                    issues.append(_issue("none_compare", node, "Comparison to None with ==", lines))

        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in BUILTINS:
                    issues.append(_issue("builtin_shadow", node, f"`{t.id}` shadows a built-in", lines))

        elif isinstance(node, ast.Import):
            for a in node.names:
                imported[(a.asname or a.name).split(".")[0]] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                if a.name != "*":
                    imported[a.asname or a.name] = node.lineno

        elif isinstance(node, ast.Name):
            used.add(node.id)

    for name, line in imported.items():
        if name not in used and name != "__future__":
            issues.append(_issue("unused_import", line, f"`{name}` imported but unused", lines))
    return sorted(issues, key=lambda i: i["line"])
