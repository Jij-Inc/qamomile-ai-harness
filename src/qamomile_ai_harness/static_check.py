from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


GATE_NAMES = {
    "h",
    "x",
    "y",
    "z",
    "s",
    "t",
    "rx",
    "ry",
    "rz",
    "p",
    "cx",
    "cy",
    "cz",
    "ccx",
    "swap",
    "rxx",
    "ryy",
    "rzz",
    "control",
    "pauli_evolve",
}

PARAMETERIZED_CONTROL_TARGETS = {"rx", "ry", "rz", "p", "rxx", "ryy", "rzz"}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    severity: str
    code: str
    message: str


def _is_qmc_attr(node: ast.AST, name: str | None = None) -> bool:
    if not isinstance(node, ast.Attribute):
        return False
    if name is not None and node.attr != name:
        return False
    return isinstance(node.value, ast.Name) and node.value.id == "qmc"


def _call_name(node: ast.AST) -> str | None:
    if not isinstance(node, ast.Call):
        return None
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    if isinstance(node.func, ast.Name):
        return node.func.id
    return None


def _is_qmc_gate_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    return isinstance(node.func, ast.Attribute) and _is_qmc_attr(node.func) and node.func.attr in GATE_NAMES


def _has_qkernel_decorator(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for dec in func.decorator_list:
        if _is_qmc_attr(dec, "qkernel"):
            return True
        if isinstance(dec, ast.Call) and _is_qmc_attr(dec.func, "qkernel"):
            return True
    return False


class QamomileChecker(ast.NodeVisitor):
    def __init__(self, path: Path):
        self.path = path
        self.findings: list[Finding] = []
        self.qkernel_depth = 0
        self.has_qkernel = False
        self.has_solve = False
        self.imports_qmc = False

    def add(self, node: ast.AST, severity: str, code: str, message: str) -> None:
        self.findings.append(
            Finding(
                path=str(self.path),
                line=getattr(node, "lineno", 1),
                severity=severity,
                code=code,
                message=message,
            )
        )

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name == "qamomile.circuit" and alias.asname == "qmc":
                self.imports_qmc = True
            if alias.name.startswith("qiskit"):
                self.add(node, "error", "QML001", "Do not import Qiskit in Qamomile solution files.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module and node.module.startswith("qiskit"):
            self.add(node, "error", "QML001", "Do not import Qiskit in Qamomile solution files.")
        if node.module == "qamomile.circuit":
            self.add(node, "warning", "QML002", "Prefer `import qamomile.circuit as qmc` for consistency.")
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        is_kernel = _has_qkernel_decorator(node)
        if node.name == "solve":
            self.has_solve = True
        if is_kernel:
            self.has_qkernel = True
            if not node.returns:
                self.add(node, "error", "QML003", "@qmc.qkernel functions should have Qamomile return annotations.")
            self.qkernel_depth += 1
            self.generic_visit(node)
            self.qkernel_depth -= 1
        else:
            self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        if self.qkernel_depth > 0 and isinstance(node.iter, ast.Name):
            self.add(
                node,
                "warning",
                "QML004",
                "Do not iterate directly over a Qamomile vector; use index-based `qmc.range(...)` loops.",
            )
        if self.qkernel_depth > 0 and isinstance(node.iter, ast.Call):
            if _call_name(node.iter) == "range":
                self.add(
                    node,
                    "warning",
                    "QML005",
                    "Python `range(...)` inside qkernels is only safe for concrete unrolled loops; use `qmc.range(...)` for `qmc.UInt` symbolic loops.",
                )
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:
        if self.qkernel_depth > 0 and _is_qmc_gate_call(node.value):
            self.add(
                node,
                "error",
                "QML006",
                "Qamomile gates return fresh handles; assign the return value instead of ignoring it.",
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if _is_qmc_attr(node.func, "control") and node.args:
            target = node.args[0]
            if isinstance(target, ast.Attribute) and _is_qmc_attr(target):
                if target.attr in PARAMETERIZED_CONTROL_TARGETS:
                    self.add(
                        node,
                        "warning",
                        "QML011",
                        "Parameterized `qmc.control(...)` gates can leave formal parameters such as `angle` unbound; run a Qamomile transpile/sample smoke test or use an explicit decomposition.",
                    )
        if self.qkernel_depth > 0 and isinstance(node.func, ast.Attribute):
            if _is_qmc_attr(node.func) and node.func.attr == "measure":
                self.add(
                    node,
                    "info",
                    "QML007",
                    "Measurement is fine for sampling tasks, but state-preparation benchmark cases usually require returning unmeasured qubits.",
                )
        self.generic_visit(node)


def check_file(path: Path) -> list[Finding]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        return [
            Finding(
                path=str(path),
                line=exc.lineno or 1,
                severity="error",
                code="QML000",
                message=f"SyntaxError: {exc.msg}",
            )
        ]

    checker = QamomileChecker(path)
    checker.visit(tree)
    if not checker.imports_qmc:
        checker.findings.append(
            Finding(str(path), 1, "warning", "QML008", "Expected `import qamomile.circuit as qmc`.")
        )
    if not checker.has_qkernel:
        checker.findings.append(Finding(str(path), 1, "error", "QML009", "No `@qmc.qkernel` function found."))
    if path.name.startswith("QPC") and not checker.has_solve:
        checker.findings.append(Finding(str(path), 1, "error", "QML010", "QCoder-style files should define `solve`."))
    return sorted(checker.findings, key=lambda item: (item.path, item.line, item.code))


def check_paths(paths: list[Path]) -> list[Finding]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.rglob("*.py")))
        else:
            files.append(path)
    findings: list[Finding] = []
    for file in files:
        findings.extend(check_file(file))
    return findings
