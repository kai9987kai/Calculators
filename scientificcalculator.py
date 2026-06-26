#!/usr/bin/env python3
"""
Modern Scientific Calculator
============================
A responsive Tkinter scientific calculator with:

- Safe AST-based expression evaluation (no eval / exec)
- Radian and degree trigonometry
- Memory, answer recall, result history, and compact/full layouts
- Keyboard controls, copy support, friendly errors, and input safeguards
- Scientific functions: trig/inverse trig, roots, powers, logs, exponentials,
  reciprocal, factorial, constants, and percentages

Requires: Python 3.9+ with Tkinter (included with most Python installers).
"""

from __future__ import annotations

import ast
import math
import operator
import tkinter as tk
from dataclasses import dataclass
from typing import Callable


APP_BG = "#171A21"
PANEL_BG = "#20242D"
DISPLAY_BG = "#0E1117"
TEXT = "#F3F5F7"
MUTED = "#AAB2BF"
ACCENT = "#4F8CFF"
ACCENT_HOVER = "#6A9DFF"
OPERATOR = "#303847"
OPERATOR_HOVER = "#3C4658"
DANGER = "#B8495B"
DANGER_HOVER = "#D15B6E"
NUMBER = "#272D38"
NUMBER_HOVER = "#343D4B"
SCIENCE = "#252A34"
SCIENCE_HOVER = "#343B48"


class CalculatorError(ValueError):
    """A user-facing calculation error."""


@dataclass(frozen=True)
class HistoryEntry:
    expression: str
    result: str


def format_number(value: float | int) -> str:
    """Format a numerical value clearly without unnecessary trailing zeros."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CalculatorError("The result is not a real number.")

    value = float(value)
    if not math.isfinite(value):
        raise CalculatorError("The result is outside the supported range.")

    if abs(value) < 1e-14:
        value = 0.0
    if value.is_integer() and abs(value) < 1e15:
        return str(int(value))
    return f"{value:.12g}"


class SafeExpressionEvaluator:
    """Evaluate only a small, explicitly approved mathematical expression language."""

    MAX_EXPRESSION_LENGTH = 250
    MAX_FACTORIAL = 170
    MAX_EXPONENT = 10_000

    def __init__(self, angle_mode: str = "RAD", ans: float = 0.0) -> None:
        self.angle_mode = angle_mode
        self.ans = ans

    def evaluate(self, expression: str) -> float:
        expression = self._normalise(expression)
        if not expression:
            raise CalculatorError("Enter a calculation first.")
        if len(expression) > self.MAX_EXPRESSION_LENGTH:
            raise CalculatorError("That expression is too long.")

        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as exc:
            raise CalculatorError("Check the expression and any brackets.") from exc

        result = self._visit(tree.body)
        if isinstance(result, bool) or not isinstance(result, (int, float)):
            raise CalculatorError("Only real-number calculations are supported.")
        if not math.isfinite(float(result)):
            raise CalculatorError("The result is outside the supported range.")
        return float(result)

    @staticmethod
    def _normalise(expression: str) -> str:
        return (
            expression.strip()
            .replace("×", "*")
            .replace("÷", "/")
            .replace("−", "-")
            .replace("^", "**")
            .replace("π", "pi")
            .replace("√", "sqrt")
        )

    def _visit(self, node: ast.AST) -> float:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                raise CalculatorError("Only numbers are allowed.")
            return float(node.value)

        if isinstance(node, ast.Name):
            constants = {"pi": math.pi, "e": math.e, "ans": self.ans}
            if node.id not in constants:
                raise CalculatorError(f"'{node.id}' is not an available value.")
            return constants[node.id]

        if isinstance(node, ast.UnaryOp):
            operand = self._visit(node.operand)
            if isinstance(node.op, ast.UAdd):
                return operand
            if isinstance(node.op, ast.USub):
                return -operand
            raise CalculatorError("That unary operation is not supported.")

        if isinstance(node, ast.BinOp):
            left = self._visit(node.left)
            right = self._visit(node.right)
            return self._binary_operation(node.op, left, right)

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.keywords or len(node.args) != 1:
                raise CalculatorError("Use one argument inside each function.")
            return self._call_function(node.func.id, self._visit(node.args[0]))

        raise CalculatorError("That part of the expression is not supported.")

    def _binary_operation(self, op: ast.operator, left: float, right: float) -> float:
        try:
            if isinstance(op, ast.Add):
                result = operator.add(left, right)
            elif isinstance(op, ast.Sub):
                result = operator.sub(left, right)
            elif isinstance(op, ast.Mult):
                result = operator.mul(left, right)
            elif isinstance(op, ast.Div):
                if right == 0:
                    raise CalculatorError("Division by zero is not possible.")
                result = operator.truediv(left, right)
            elif isinstance(op, ast.Pow):
                if abs(right) > self.MAX_EXPONENT:
                    raise CalculatorError("That exponent is too large.")
                result = operator.pow(left, right)
            else:
                raise CalculatorError("That operation is not supported.")
        except CalculatorError:
            raise
        except OverflowError as exc:
            raise CalculatorError("The result is outside the supported range.") from exc
        except ValueError as exc:
            raise CalculatorError("That operation has no real-number result.") from exc

        if not math.isfinite(float(result)):
            raise CalculatorError("The result is outside the supported range.")
        return float(result)

    def _call_function(self, name: str, value: float) -> float:
        direct_functions: dict[str, Callable[[float], float]] = {
            "sqrt": self._sqrt,
            "ln": self._ln,
            "log": self._log10,
            "exp": self._exp,
            "abs": abs,
            "floor": math.floor,
            "ceil": math.ceil,
            "fact": self._factorial,
        }
        if name in direct_functions:
            return float(direct_functions[name](value))

        trig_functions: dict[str, Callable[[float], float]] = {
            "sin": self._sin,
            "cos": self._cos,
            "tan": self._tan,
            "asin": self._asin,
            "acos": self._acos,
            "atan": self._atan,
        }
        if name in trig_functions:
            return float(trig_functions[name](value))

        raise CalculatorError(f"'{name}' is not an available function.")

    @staticmethod
    def _sqrt(value: float) -> float:
        if value < 0:
            raise CalculatorError("Square roots of negative values are not real.")
        return math.sqrt(value)

    @staticmethod
    def _ln(value: float) -> float:
        if value <= 0:
            raise CalculatorError("ln needs a positive value.")
        return math.log(value)

    @staticmethod
    def _log10(value: float) -> float:
        if value <= 0:
            raise CalculatorError("log needs a positive value.")
        return math.log10(value)

    @staticmethod
    def _exp(value: float) -> float:
        try:
            return math.exp(value)
        except OverflowError as exc:
            raise CalculatorError("The result is outside the supported range.") from exc

    def _factorial(self, value: float) -> float:
        if not value.is_integer() or value < 0:
            raise CalculatorError("Factorial needs a non-negative whole number.")
        if value > self.MAX_FACTORIAL:
            raise CalculatorError(f"Factorial is limited to {self.MAX_FACTORIAL}.")
        return float(math.factorial(int(value)))

    def _to_radians(self, value: float) -> float:
        return math.radians(value) if self.angle_mode == "DEG" else value

    def _from_radians(self, value: float) -> float:
        return math.degrees(value) if self.angle_mode == "DEG" else value

    def _sin(self, value: float) -> float:
        return math.sin(self._to_radians(value))

    def _cos(self, value: float) -> float:
        return math.cos(self._to_radians(value))

    def _tan(self, value: float) -> float:
        return math.tan(self._to_radians(value))

    def _asin(self, value: float) -> float:
        if not -1 <= value <= 1:
            raise CalculatorError("asin needs a value from -1 to 1.")
        return self._from_radians(math.asin(value))

    def _acos(self, value: float) -> float:
        if not -1 <= value <= 1:
            raise CalculatorError("acos needs a value from -1 to 1.")
        return self._from_radians(math.acos(value))

    def _atan(self, value: float) -> float:
        return self._from_radians(math.atan(value))


class CalculatorEngine:
    """Owns calculator state and provides safe input-friendly operations."""

    def __init__(self) -> None:
        self.expression = ""
        self.answer = 0.0
        self.memory = 0.0
        self.angle_mode = "RAD"
        self.history: list[HistoryEntry] = []

    @property
    def display_expression(self) -> str:
        """Return a friendlier visual representation while retaining parseable state."""
        return (
            self.expression.replace("**", "^")
            .replace("*", "×")
            .replace("/", "÷")
            .replace("pi", "π")
            .replace("sqrt", "√")
        )

    def append_digit(self, digit: str) -> None:
        if digit not in "0123456789":
            return
        self.expression += digit

    def append_decimal(self) -> None:
        if not self.expression or self.expression[-1] in "+-*/(":
            self.expression += "0."
            return

        current = self._current_token()
        if "." not in current:
            self.expression += "."

    def append_operator(self, operator_text: str) -> None:
        operator_text = {"×": "*", "÷": "/", "^": "**"}.get(operator_text, operator_text)
        if operator_text not in {"+", "-", "*", "/", "**"}:
            return

        if not self.expression:
            if operator_text == "-":
                self.expression = "-"
            return

        if self.expression.endswith("."):
            self.expression += "0"

        # A minus after another operator is allowed as a negative-number sign.
        if operator_text == "-" and self.expression[-1] in "*/":
            self.expression += "-"
            return

        if self.expression.endswith("**"):
            self.expression = self.expression[:-2] + operator_text
        elif self.expression[-1] in "+-*/":
            self.expression = self.expression[:-1] + operator_text
        else:
            self.expression += operator_text

    def open_parenthesis(self) -> None:
        if self._ends_in_operand():
            self.expression += "*"
        self.expression += "("

    def close_parenthesis(self) -> None:
        if self.expression.count("(") > self.expression.count(")") and self.expression:
            if self.expression[-1] in "+-*/(":
                return
            self.expression += ")"

    def append_function(self, function_name: str) -> None:
        if function_name not in {
            "sin", "cos", "tan", "asin", "acos", "atan",
            "sqrt", "ln", "log", "exp", "fact",
        }:
            return
        if self._ends_in_operand():
            self.expression += "*"
        self.expression += f"{function_name}("

    def append_constant(self, constant_name: str) -> None:
        if constant_name not in {"pi", "e", "ans"}:
            return
        if self._ends_in_operand():
            self.expression += "*"
        self.expression += constant_name

    def append_percent(self) -> None:
        """Convert the current operand to a fraction of one hundred."""
        if not self.expression or self.expression[-1] in "+-*/(":
            return

        start = self._last_operand_start()
        operand = self.expression[start:]
        if operand:
            self.expression = f"{self.expression[:start]}({operand}/100)"

    def square(self) -> None:
        if self.expression and self.expression[-1] not in "+-*/(":
            self.expression = f"({self.expression})**2"

    def reciprocal(self) -> None:
        if self.expression and self.expression[-1] not in "+-*/(":
            self.expression = f"1/({self.expression})"

    def toggle_sign(self) -> None:
        if not self.expression:
            self.expression = "-"
        elif self.expression.startswith("-(") and self.expression.endswith(")"):
            self.expression = self.expression[2:-1]
        else:
            self.expression = f"-({self.expression})"

    def backspace(self) -> None:
        self.expression = self.expression[:-1]

    def clear_all(self) -> None:
        self.expression = ""

    def clear_entry(self) -> None:
        """Clear the latest top-level entry, retaining earlier completed terms."""
        if not self.expression:
            return

        depth = 0
        split_at = -1
        for index, char in enumerate(self.expression):
            if char == "(":
                depth += 1
            elif char == ")":
                depth = max(0, depth - 1)
            elif depth == 0 and char in "+-*/":
                # Keep a leading negative sign attached to the current operand.
                if index == 0:
                    continue
                split_at = index

        self.expression = self.expression[: split_at + 1] if split_at >= 0 else ""
        while self.expression.endswith("**"):
            self.expression = self.expression[:-2]

    def calculate(self) -> tuple[str, str]:
        expression_before = self.expression
        evaluator = SafeExpressionEvaluator(self.angle_mode, self.answer)
        result = evaluator.evaluate(expression_before)
        result_text = format_number(result)
        expression_text = self.display_expression
        self.answer = result
        self.expression = result_text

        entry = HistoryEntry(expression_text, result_text)
        self.history.append(entry)
        if len(self.history) > 150:
            self.history.pop(0)
        return expression_text, result_text

    def memory_clear(self) -> None:
        self.memory = 0.0

    def memory_add(self) -> None:
        value = self._value_for_memory()
        self.memory += value

    def memory_subtract(self) -> None:
        value = self._value_for_memory()
        self.memory -= value

    def memory_recall(self) -> None:
        text = format_number(self.memory)
        if self._ends_in_operand():
            self.expression += "*"
        self.expression += text

    def toggle_angle_mode(self) -> None:
        self.angle_mode = "DEG" if self.angle_mode == "RAD" else "RAD"

    def _value_for_memory(self) -> float:
        if not self.expression:
            return self.answer
        evaluator = SafeExpressionEvaluator(self.angle_mode, self.answer)
        return evaluator.evaluate(self.expression)

    def _current_token(self) -> str:
        token = []
        for char in reversed(self.expression):
            if char in "+-*/(":
                break
            token.append(char)
        return "".join(reversed(token))

    def _last_operand_start(self) -> int:
        """Find the beginning of the final top-level operand."""
        depth = 0
        start = 0
        for index, char in enumerate(self.expression):
            if char == "(":
                depth += 1
            elif char == ")":
                depth = max(0, depth - 1)
            elif depth == 0 and char in "+-*/":
                is_unary_minus = char == "-" and (
                    index == 0 or self.expression[index - 1] in "+-*/"
                )
                if not is_unary_minus:
                    start = index + 1
        return start

    def _ends_in_operand(self) -> bool:
        return bool(
            self.expression
            and (
                self.expression[-1].isdigit()
                or self.expression[-1] == ")"
                or self.expression.endswith(("pi", "ans", "e"))
            )
        )


class CalculatorButton(tk.Button):
    """A button with simple high-contrast hover behaviour."""

    def __init__(
        self,
        parent: tk.Misc,
        text: str,
        command: Callable[[], None],
        bg: str = NUMBER,
        hover_bg: str = NUMBER_HOVER,
        **kwargs: object,
    ) -> None:
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=TEXT,
            activebackground=hover_bg,
            activeforeground=TEXT,
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 12, "bold"),
            padx=8,
            pady=10,
            highlightthickness=0,
            **kwargs,
        )
        self._base_bg = bg
        self._hover_bg = hover_bg
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _event: tk.Event) -> None:
        self.configure(bg=self._hover_bg)

    def _on_leave(self, _event: tk.Event) -> None:
        self.configure(bg=self._base_bg)


class ScientificCalculator(tk.Tk):
    """Tkinter application shell for the calculator engine."""

    FULL_GEOMETRY = "820x730"
    COMPACT_GEOMETRY = "390x610"

    def __init__(self) -> None:
        super().__init__()
        self.engine = CalculatorEngine()
        self.full_mode = True

        self.title("Scientific Calculator")
        self.geometry(self.FULL_GEOMETRY)
        self.minsize(390, 560)
        self.configure(bg=APP_BG)
        self.option_add("*tearOff", False)

        self.expression_var = tk.StringVar()
        self.result_var = tk.StringVar(value="0")
        self.status_var = tk.StringVar()

        self._build_ui()
        self._bind_keys()
        self._refresh()

    def _build_ui(self) -> None:
        root = tk.Frame(self, bg=APP_BG)
        root.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        self._build_display(root)
        self._build_toolbar(root)

        self.body = tk.Frame(root, bg=APP_BG)
        self.body.pack(fill=tk.BOTH, expand=True, pady=(12, 0))
        self.body.columnconfigure(0, weight=1)
        self.body.columnconfigure(1, weight=1)
        self.body.rowconfigure(0, weight=1)
        self.body.rowconfigure(1, weight=1)

        self.advanced_panel = self._make_panel(self.body, "Scientific")
        self.basic_panel = self._make_panel(self.body, "Calculator")
        self.history_panel = self._make_history_panel(self.body)

        self._build_advanced_buttons()
        self._build_basic_buttons()
        self._apply_layout()

    def _build_display(self, parent: tk.Misc) -> None:
        display = tk.Frame(parent, bg=DISPLAY_BG, highlightbackground="#2E3543", highlightthickness=1)
        display.pack(fill=tk.X)

        tk.Label(
            display,
            textvariable=self.expression_var,
            anchor="e",
            bg=DISPLAY_BG,
            fg=MUTED,
            font=("Segoe UI", 12),
            padx=16,
            pady=8,
        ).pack(fill=tk.X)

        output = tk.Entry(
            display,
            textvariable=self.result_var,
            state="readonly",
            justify="right",
            readonlybackground=DISPLAY_BG,
            fg=TEXT,
            relief=tk.FLAT,
            font=("Segoe UI", 28, "bold"),
            bd=0,
            takefocus=False,
        )
        output.pack(fill=tk.X, padx=12, pady=(0, 8), ipady=6)

        tk.Label(
            display,
            textvariable=self.status_var,
            anchor="w",
            bg=DISPLAY_BG,
            fg=MUTED,
            font=("Segoe UI", 10),
            padx=16,
            pady=(0, 8),
        ).pack(fill=tk.X)

    def _build_toolbar(self, parent: tk.Misc) -> None:
        toolbar = tk.Frame(parent, bg=APP_BG)
        toolbar.pack(fill=tk.X, pady=(10, 0))

        self.mode_button = CalculatorButton(
            toolbar,
            text="Compact mode",
            command=self._toggle_mode,
            bg=OPERATOR,
            hover_bg=OPERATOR_HOVER,
            font=("Segoe UI", 10, "bold"),
            pady=7,
        )
        self.mode_button.pack(side=tk.RIGHT)

        self.copy_button = CalculatorButton(
            toolbar,
            text="Copy result",
            command=self._copy_result,
            bg=OPERATOR,
            hover_bg=OPERATOR_HOVER,
            font=("Segoe UI", 10, "bold"),
            pady=7,
        )
        self.copy_button.pack(side=tk.RIGHT, padx=(0, 8))

    def _make_panel(self, parent: tk.Misc, title: str) -> tk.Frame:
        panel = tk.Frame(parent, bg=PANEL_BG, padx=10, pady=10)
        tk.Label(
            panel,
            text=title,
            anchor="w",
            bg=PANEL_BG,
            fg=MUTED,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 8))
        for column in range(4):
            panel.columnconfigure(column, weight=1, uniform=f"{title}_buttons")
        return panel

    def _make_history_panel(self, parent: tk.Misc) -> tk.Frame:
        panel = tk.Frame(parent, bg=PANEL_BG, padx=10, pady=10)
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)

        header = tk.Frame(panel, bg=PANEL_BG)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        header.columnconfigure(0, weight=1)

        tk.Label(
            header,
            text="History",
            anchor="w",
            bg=PANEL_BG,
            fg=MUTED,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="ew")

        CalculatorButton(
            header,
            text="Clear",
            command=self._clear_history,
            bg=OPERATOR,
            hover_bg=OPERATOR_HOVER,
            font=("Segoe UI", 9, "bold"),
            pady=5,
        ).grid(row=0, column=1, sticky="e")

        list_container = tk.Frame(panel, bg=PANEL_BG)
        list_container.grid(row=1, column=0, sticky="nsew")
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)

        self.history_list = tk.Listbox(
            list_container,
            bg=DISPLAY_BG,
            fg=TEXT,
            selectbackground=ACCENT,
            selectforeground=TEXT,
            activestyle="none",
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            font=("Cascadia Mono", 10),
            exportselection=False,
        )
        self.history_list.grid(row=0, column=0, sticky="nsew")
        self.history_list.bind("<Double-Button-1>", self._restore_history)

        scrollbar = tk.Scrollbar(list_container, command=self.history_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.history_list.configure(yscrollcommand=scrollbar.set)
        return panel

    def _build_advanced_buttons(self) -> None:
        buttons: list[tuple[str, Callable[[], None], str, str]] = [
            ("MC", self._memory_clear, OPERATOR, OPERATOR_HOVER),
            ("MR", self._memory_recall, OPERATOR, OPERATOR_HOVER),
            ("M+", self._memory_add, OPERATOR, OPERATOR_HOVER),
            ("M−", self._memory_subtract, OPERATOR, OPERATOR_HOVER),
            ("sin", lambda: self._function("sin"), SCIENCE, SCIENCE_HOVER),
            ("cos", lambda: self._function("cos"), SCIENCE, SCIENCE_HOVER),
            ("tan", lambda: self._function("tan"), SCIENCE, SCIENCE_HOVER),
            ("%", self._percent, SCIENCE, SCIENCE_HOVER),
            ("sin⁻¹", lambda: self._function("asin"), SCIENCE, SCIENCE_HOVER),
            ("cos⁻¹", lambda: self._function("acos"), SCIENCE, SCIENCE_HOVER),
            ("tan⁻¹", lambda: self._function("atan"), SCIENCE, SCIENCE_HOVER),
            ("x²", self._square, SCIENCE, SCIENCE_HOVER),
            ("ln", lambda: self._function("ln"), SCIENCE, SCIENCE_HOVER),
            ("log", lambda: self._function("log"), SCIENCE, SCIENCE_HOVER),
            ("eˣ", lambda: self._function("exp"), SCIENCE, SCIENCE_HOVER),
            ("xʸ", lambda: self._operator("^"), SCIENCE, SCIENCE_HOVER),
            ("√x", lambda: self._function("sqrt"), SCIENCE, SCIENCE_HOVER),
            ("1/x", self._reciprocal, SCIENCE, SCIENCE_HOVER),
            ("x!", lambda: self._function("fact"), SCIENCE, SCIENCE_HOVER),
            ("Ans", lambda: self._constant("ans"), SCIENCE, SCIENCE_HOVER),
            ("π", lambda: self._constant("pi"), SCIENCE, SCIENCE_HOVER),
            ("e", lambda: self._constant("e"), SCIENCE, SCIENCE_HOVER),
            ("RAD", self._toggle_angle, ACCENT, ACCENT_HOVER),
            ("CE", self._clear_entry, DANGER, DANGER_HOVER),
        ]

        for index, (label, command, bg, hover) in enumerate(buttons, start=1):
            row, column = divmod(index - 1, 4)
            CalculatorButton(
                self.advanced_panel,
                text=label,
                command=command,
                bg=bg,
                hover_bg=hover,
            ).grid(row=row + 1, column=column, sticky="nsew", padx=3, pady=3)

        for row in range(1, 7):
            self.advanced_panel.rowconfigure(row, weight=1)

    def _build_basic_buttons(self) -> None:
        buttons: list[tuple[str, Callable[[], None], str, str]] = [
            ("AC", self._clear_all, DANGER, DANGER_HOVER),
            ("⌫", self._backspace, OPERATOR, OPERATOR_HOVER),
            ("(", self._open_parenthesis, OPERATOR, OPERATOR_HOVER),
            (")", self._close_parenthesis, OPERATOR, OPERATOR_HOVER),
            ("7", lambda: self._digit("7"), NUMBER, NUMBER_HOVER),
            ("8", lambda: self._digit("8"), NUMBER, NUMBER_HOVER),
            ("9", lambda: self._digit("9"), NUMBER, NUMBER_HOVER),
            ("÷", lambda: self._operator("÷"), OPERATOR, OPERATOR_HOVER),
            ("4", lambda: self._digit("4"), NUMBER, NUMBER_HOVER),
            ("5", lambda: self._digit("5"), NUMBER, NUMBER_HOVER),
            ("6", lambda: self._digit("6"), NUMBER, NUMBER_HOVER),
            ("×", lambda: self._operator("×"), OPERATOR, OPERATOR_HOVER),
            ("1", lambda: self._digit("1"), NUMBER, NUMBER_HOVER),
            ("2", lambda: self._digit("2"), NUMBER, NUMBER_HOVER),
            ("3", lambda: self._digit("3"), NUMBER, NUMBER_HOVER),
            ("−", lambda: self._operator("-"), OPERATOR, OPERATOR_HOVER),
            ("±", self._toggle_sign, NUMBER, NUMBER_HOVER),
            ("0", lambda: self._digit("0"), NUMBER, NUMBER_HOVER),
            (".", self._decimal, NUMBER, NUMBER_HOVER),
            ("+", lambda: self._operator("+"), OPERATOR, OPERATOR_HOVER),
        ]
        for index, (label, command, bg, hover) in enumerate(buttons, start=1):
            row, column = divmod(index - 1, 4)
            CalculatorButton(
                self.basic_panel,
                text=label,
                command=command,
                bg=bg,
                hover_bg=hover,
            ).grid(row=row + 1, column=column, sticky="nsew", padx=3, pady=3)

        CalculatorButton(
            self.basic_panel,
            text="=",
            command=self._calculate,
            bg=ACCENT,
            hover_bg=ACCENT_HOVER,
            font=("Segoe UI", 14, "bold"),
        ).grid(row=6, column=0, columnspan=4, sticky="nsew", padx=3, pady=(6, 3))

        for row in range(1, 7):
            self.basic_panel.rowconfigure(row, weight=1)

    def _apply_layout(self) -> None:
        for widget in (self.advanced_panel, self.basic_panel, self.history_panel):
            widget.grid_forget()

        if self.full_mode:
            self.advanced_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
            self.basic_panel.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
            self.history_panel.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(12, 0))
            self.body.rowconfigure(1, weight=1)
            self.mode_button.configure(text="Compact mode")
            self.geometry(self.FULL_GEOMETRY)
        else:
            self.basic_panel.grid(row=0, column=0, columnspan=2, sticky="nsew")
            self.body.rowconfigure(1, weight=0)
            self.mode_button.configure(text="Full mode")
            self.geometry(self.COMPACT_GEOMETRY)

    def _refresh(self, result: str | None = None, message: str | None = None) -> None:
        self.expression_var.set(self.engine.display_expression)
        self.result_var.set(result if result is not None else (self.engine.display_expression or "0"))
        memory_text = f"M: {format_number(self.engine.memory)}"
        mode_text = self.engine.angle_mode
        self.status_var.set(message or f"{mode_text}  •  {memory_text}")

    def _show_error(self, error: Exception) -> None:
        self.result_var.set("Error")
        self.status_var.set(str(error))
        self.bell()

    def _digit(self, digit: str) -> None:
        self.engine.append_digit(digit)
        self._refresh()

    def _decimal(self) -> None:
        self.engine.append_decimal()
        self._refresh()

    def _operator(self, operator_text: str) -> None:
        self.engine.append_operator(operator_text)
        self._refresh()

    def _open_parenthesis(self) -> None:
        self.engine.open_parenthesis()
        self._refresh()

    def _close_parenthesis(self) -> None:
        self.engine.close_parenthesis()
        self._refresh()

    def _function(self, name: str) -> None:
        self.engine.append_function(name)
        self._refresh()

    def _constant(self, name: str) -> None:
        self.engine.append_constant(name)
        self._refresh()

    def _percent(self) -> None:
        self.engine.append_percent()
        self._refresh()

    def _square(self) -> None:
        self.engine.square()
        self._refresh()

    def _reciprocal(self) -> None:
        self.engine.reciprocal()
        self._refresh()

    def _toggle_sign(self) -> None:
        self.engine.toggle_sign()
        self._refresh()

    def _backspace(self) -> None:
        self.engine.backspace()
        self._refresh()

    def _clear_all(self) -> None:
        self.engine.clear_all()
        self._refresh(message="Cleared")

    def _clear_entry(self) -> None:
        self.engine.clear_entry()
        self._refresh(message="Entry cleared")

    def _calculate(self) -> None:
        try:
            expression, result = self.engine.calculate()
        except CalculatorError as exc:
            self._show_error(exc)
            return

        self.history_list.insert(tk.END, f"{expression} = {result}")
        self.history_list.yview_moveto(1.0)
        self._refresh(result=result, message=f"Calculated  •  {self.engine.angle_mode}")
        self.expression_var.set(expression)

    def _memory_clear(self) -> None:
        self.engine.memory_clear()
        self._refresh(message="Memory cleared")

    def _memory_recall(self) -> None:
        self.engine.memory_recall()
        self._refresh(message="Memory recalled")

    def _memory_add(self) -> None:
        try:
            self.engine.memory_add()
            self._refresh(message="Added to memory")
        except CalculatorError as exc:
            self._show_error(exc)

    def _memory_subtract(self) -> None:
        try:
            self.engine.memory_subtract()
            self._refresh(message="Subtracted from memory")
        except CalculatorError as exc:
            self._show_error(exc)

    def _toggle_angle(self) -> None:
        self.engine.toggle_angle_mode()
        for widget in self.advanced_panel.winfo_children():
            if isinstance(widget, CalculatorButton) and widget.cget("text") in {"RAD", "DEG"}:
                widget.configure(text=self.engine.angle_mode)
                break
        self._refresh(message=f"Angle mode: {self.engine.angle_mode}")

    def _toggle_mode(self) -> None:
        self.full_mode = not self.full_mode
        self._apply_layout()
        self._refresh()

    def _clear_history(self) -> None:
        self.engine.history.clear()
        self.history_list.delete(0, tk.END)
        self._refresh(message="History cleared")

    def _restore_history(self, _event: tk.Event) -> None:
        selection = self.history_list.curselection()
        if not selection:
            return
        entry = self.engine.history[selection[0]]
        # History expressions are display-formatted, which the evaluator normalises safely.
        self.engine.expression = entry.expression
        self._refresh(message="History entry restored")

    def _copy_result(self) -> None:
        value = self.result_var.get()
        if value and value != "Error":
            self.clipboard_clear()
            self.clipboard_append(value)
            self.update()
            self._refresh(message="Result copied")

    def _bind_keys(self) -> None:
        self.bind_all("<Key>", self._on_key, add="+")
        self.bind_all("<Control-c>", self._on_copy_shortcut, add="+")
        self.bind_all("<Control-C>", self._on_copy_shortcut, add="+")

    def _on_copy_shortcut(self, _event: tk.Event) -> str:
        self._copy_result()
        return "break"

    def _on_key(self, event: tk.Event) -> str | None:
        char = event.char
        keysym = event.keysym

        if char in "0123456789":
            self._digit(char)
        elif char == ".":
            self._decimal()
        elif char in "+-*/":
            self._operator(char)
        elif char == "^":
            self._operator("^")
        elif char == "(":
            self._open_parenthesis()
        elif char == ")":
            self._close_parenthesis()
        elif char == "%":
            self._percent()
        elif keysym in {"Return", "KP_Enter"}:
            self._calculate()
        elif keysym == "BackSpace":
            self._backspace()
        elif keysym == "Delete":
            self._clear_entry()
        elif keysym == "Escape":
            self._clear_all()
        else:
            return None
        return "break"


if __name__ == "__main__":
    app = ScientificCalculator()
    app.mainloop()
