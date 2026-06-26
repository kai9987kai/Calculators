# BasicCalc

A clean, desktop calculator built with Python and Tkinter.

BasicCalc supports everyday arithmetic while avoiding Python’s unsafe `eval()` function. Expressions are parsed safely and only approved mathematical operations are allowed.

## Features

- Safe expression evaluation using Python’s `ast` module
- Addition, subtraction, multiplication, division, and modulo
- Decimal number support
- Parentheses and nested expressions
- Positive and negative numbers
- Previous-answer memory with the **Ans** button
- Automatic multiplication before parentheses  
  - Example: `2(3 + 4)` becomes `2*(3 + 4)`
- Backspace and clear controls
- Helpful error handling, including divide-by-zero protection
- Keyboard support
- Modern dark-themed Tkinter interface
- No external packages required

## Supported Operations

| Operation | Symbol | Example |
|---|---:|---|
| Addition | `+` | `7 + 3` |
| Subtraction | `-` | `10 - 4` |
| Multiplication | `*` or `×` | `6 * 8` |
| Division | `/` or `÷` | `20 / 5` |
| Modulo | `%` | `10 % 3` |
| Parentheses | `()` | `(2 + 3) * 4` |
| Negative values | `-` | `-12 + 5` |

## Requirements

- Python 3
- Tkinter

Tkinter is included with most standard Python installations.

On Debian or Ubuntu, install it with:

```bash
sudo apt install python3-tk
```

## Installation

Clone the repository:

```bash
git clone https://github.com/kai9987kai/Calculators.git
cd Calculators
```

## Running the Calculator

Run the script with Python:

```bash
python BasicCalc
```

On some systems, use:

```bash
python3 BasicCalc
```

## Keyboard Controls

| Key | Action |
|---|---|
| `0–9` | Enter numbers |
| `+ - * / %` | Enter operators |
| `(` `)` | Enter parentheses |
| `.` | Enter a decimal point |
| `Enter` | Calculate the expression |
| `Backspace` | Delete the last character |
| `Escape` | Clear the calculator |

## Example Calculations

```text
2 + 2
```

```text
(10 + 5) * 3
```

```text
25 % 7
```

```text
-8 + 12.5
```

```text
2(4 + 3)
```

## Safety

BasicCalc does not use `eval()`.

Instead, it parses expressions using Python’s Abstract Syntax Tree (`ast`) module and only permits numbers plus these operations:

```text
+  -  *  /  %  ( )
```

Unsupported expressions, invalid input, and division by zero are handled safely and shown in the calculator status area.

## Future Ideas

- Calculation history panel
- Copy result button
- Light and dark theme switcher
- Scientific functions
- Keyboard shortcut help screen
- Export calculation history
- Responsive window resizing

## License

This project does not currently include a licence file. Add a licence such as MIT if you want others to reuse or modify the code.
