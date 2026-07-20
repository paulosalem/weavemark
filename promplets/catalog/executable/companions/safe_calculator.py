"""Safe local arithmetic binding for executable catalog promplets."""

from __future__ import annotations

import ast
import operator
from collections.abc import Callable
from decimal import Decimal, InvalidOperation, localcontext

_BINARY_OPERATORS: dict[type[ast.operator], Callable[[Decimal, Decimal], Decimal]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_UNARY_OPERATORS: dict[type[ast.unaryop], Callable[[Decimal], Decimal]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
_FORMATS = {"currency", "number", "percentage"}


def calculate(expression: str, format: str = "number") -> str:
    """Evaluate bounded arithmetic without exposing Python execution."""

    normalized = expression.replace("$", "").replace(",", "").replace("^", "**").strip()
    if not normalized or len(normalized) > 300:
        raise ValueError("Expression must contain between 1 and 300 characters.")
    if format not in _FORMATS:
        raise ValueError(f"Unsupported result format: {format}")

    tree = ast.parse(normalized, mode="eval")
    with localcontext() as context:
        context.prec = 50
        value = _evaluate(tree)
    if not value.is_finite() or abs(value) > Decimal("1e100"):
        raise ValueError("Result is outside the supported finite range.")

    if format == "currency":
        return f"${value:,.2f}"
    rendered = _render_decimal(value)
    return f"{rendered}%" if format == "percentage" else rendered


def _evaluate(node: ast.AST) -> Decimal:
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)
    if isinstance(node, ast.Constant) and type(node.value) in {int, float}:
        return Decimal(str(node.value))
    if isinstance(node, ast.UnaryOp):
        operation = _UNARY_OPERATORS.get(type(node.op))
        if operation is None:
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
        return operation(_evaluate(node.operand))
    if isinstance(node, ast.BinOp):
        left = _evaluate(node.left)
        right = _evaluate(node.right)
        if isinstance(node.op, ast.Pow):
            if right != right.to_integral_value() or abs(right) > 500:
                raise ValueError("Exponent must be an integer between -500 and 500.")
            try:
                return left ** int(right)
            except (InvalidOperation, OverflowError) as exc:
                raise ValueError(
                    "Power operation is outside the supported range."
                ) from exc
        operation = _BINARY_OPERATORS.get(type(node.op))
        if operation is None:
            raise ValueError(f"Unsupported binary operator: {type(node.op).__name__}")
        try:
            return operation(left, right)
        except (InvalidOperation, ZeroDivisionError) as exc:
            raise ValueError("Invalid arithmetic operation.") from exc
    raise ValueError(f"Unsupported expression element: {type(node).__name__}")


def _render_decimal(value: Decimal) -> str:
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"


__all__ = ["calculate"]
