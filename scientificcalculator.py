#!/usr/bin/env python3
"""
Advanced Modern Scientific Calculator with Compact and Full Modes
Author: [Your Name]
Date: [Current Date]
Description:
    This script implements an advanced scientific calculator using Tkinter.
    It features a dedicated number pad, an advanced functions panel (with memory
    functions, scientific operations, backspace, clear entry, Deg/Rad toggle, Ans,
    and percentage), a history panel, and a toggle between full (advanced) and compact modes.
    The UI uses a modern, flat, dark-themed design with responsive grids and hover effects.
"""

import tkinter as tk
from tkinter import ttk
import math

# Helper functions for degree-based trigonometry
def deg_sin(x):
    return math.sin(math.radians(x))

def deg_cos(x):
    return math.cos(math.radians(x))

def deg_tan(x):
    return math.tan(math.radians(x))

class AdvancedCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Scientific Calculator")
        self.geometry("520x750")
        self.resizable(False, False)
        self.configure(bg="#2E2E2E")  # Dark background

        # Internal states
        self.operator = ""      # Current expression
        self.memory = 0         # Memory value (M+, M-, etc.)
        self.last_result = 0    # Last evaluated result (for Ans button)
        self.history = []       # List of history entries
        self.angle_mode = "rad" # "rad" or "deg" mode for trig functions
        self.full_mode = True   # True = Full mode (advanced panel & history visible), False = Compact mode

        # Setup ttk style for modern flat UI
        self.style = ttk.Style(self)
        self.setup_style()

        # Create main widgets and layout
        self.create_widgets()

        # Bind keyboard input
        self.bind_keys()

    def setup_style(self):
        """Setup ttk style for a modern, flat UI."""
        self.style.theme_use("clam")
        self.style.configure("TButton",
                             background="#4A4A4A",
                             foreground="white",
                             font=("Segoe UI", 16, "bold"),
                             borderwidth=0,
                             focusthickness=3,
                             focuscolor="none")
        self.style.map("TButton",
                       background=[("active", "#5A5A5A")])

    def create_widgets(self):
        """Create and place all main widgets, including display, mode toggle, button panels, and history."""
        # Top Display Frame
        self.display_frame = tk.Frame(self, bg="#2E2E2E")
        self.display_frame.pack(pady=(15, 10), fill=tk.X)
        self.display_var = tk.StringVar()
        self.display = tk.Entry(self.display_frame, textvariable=self.display_var,
                                font=("Segoe UI", 28, "bold"),
                                relief=tk.FLAT, bd=0, justify='right',
                                bg="#2E2E2E", fg="white", insertbackground="white")
        self.display.config(highlightthickness=2, highlightbackground="#4A4A4A")
        self.display.pack(ipady=10, padx=20, fill=tk.X)

        # Mode Toggle Frame (Compact / Full)
        self.mode_toggle_frame = tk.Frame(self, bg="#2E2E2E")
        self.mode_toggle_frame.pack(pady=(0,10))
        self.mode_toggle_btn = ttk.Button(self.mode_toggle_frame, text="Switch to Compact Mode",
                                          command=self.toggle_mode)
        self.mode_toggle_btn.pack()

        # Main Container Frame for Advanced and Basic Panels
        self.container_frame = tk.Frame(self, bg="#2E2E2E")
        self.container_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=False)

        # Advanced Panel Frame (left side in full mode)
        self.advanced_frame = tk.Frame(self.container_frame, bg="#2E2E2E")
        self.create_advanced_buttons(self.advanced_frame)

        # Basic Panel Frame with Number Pad and Basic Operators (right side)
        self.basic_frame = tk.Frame(self.container_frame, bg="#2E2E2E")
        self.create_basic_buttons(self.basic_frame)

        # In full mode, arrange panels side by side; in compact mode, hide advanced panel.
        if self.full_mode:
            self.advanced_frame.grid(row=0, column=0, sticky="nsew", padx=5)
            self.basic_frame.grid(row=0, column=1, sticky="nsew", padx=5)
            self.container_frame.columnconfigure(0, weight=1)
            self.container_frame.columnconfigure(1, weight=1)
        else:
            self.basic_frame.grid(row=0, column=0, sticky="nsew")
            self.container_frame.columnconfigure(0, weight=1)

        # History Panel (only in full mode)
        self.history_frame = tk.Frame(self, bg="#2E2E2E")
        if self.full_mode:
            self.history_frame.pack(pady=10, fill=tk.BOTH, expand=True)
            history_label = tk.Label(self.history_frame, text="History", font=("Segoe UI", 16, "bold"),
                                     bg="#2E2E2E", fg="white")
            history_label.pack(anchor="w", padx=20)
            self.history_list = tk.Listbox(self.history_frame, font=("Segoe UI", 14),
                                          bg="#3E3E3E", fg="white", activestyle="none",
                                          highlightthickness=0, bd=0)
            self.history_list.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
            scrollbar = tk.Scrollbar(self.history_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.history_list.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=self.history_list.yview)

    def create_advanced_buttons(self, parent):
        """Create the advanced functions panel with memory, scientific functions, and extra controls."""
        # Define advanced buttons layout: each sublist is a row.
        adv_buttons = [
            ['MC', 'MR', 'M+', 'M-'],
            ['CE', 'C', '⌫', 'Rad'],  # 'Rad' button toggles between Rad and Deg
            ['sin', 'cos', 'tan', '%'],
            ['ln', 'exp', '√', 'Ans'],
            ['π', 'e', '', '']  # Two constants; empty placeholders for alignment
        ]
        for r, row in enumerate(adv_buttons):
            for c, char in enumerate(row):
                if char == '':
                    continue  # Skip placeholders
                btn = ttk.Button(parent, text=char, style="TButton")
                btn.grid(row=r, column=c, padx=4, pady=4, ipadx=8, ipady=8, sticky="nsew")
                # Map commands for advanced buttons
                if char == 'C':
                    btn.config(command=self.clear_all)
                elif char == 'CE':
                    btn.config(command=self.clear_entry)
                elif char == '⌫':
                    btn.config(command=self.backspace)
                elif char == 'MC':
                    btn.config(command=self.memory_clear)
                elif char == 'MR':
                    btn.config(command=self.memory_recall)
                elif char == 'M+':
                    btn.config(command=self.memory_add)
                elif char == 'M-':
                    btn.config(command=self.memory_subtract)
                elif char == 'Rad':
                    btn.config(command=self.toggle_angle_mode)
                elif char == 'Ans':
                    btn.config(command=self.append_ans)
                elif char == '%':
                    btn.config(command=lambda: self.append_to_operator('%'))
                elif char in ('sin', 'cos', 'tan', 'ln', 'exp', '√'):
                    btn.config(command=lambda op=char: self.append_function(op))
                elif char in ('π', 'e'):
                    constant = math.pi if char == 'π' else math.e
                    btn.config(command=lambda const=constant: self.append_constant(const))
                # Hover effects
                btn.bind("<Enter>", lambda e, b=btn: b.state(["active"]))
                btn.bind("<Leave>", lambda e, b=btn: b.state(["!active"]))
        # Configure grid to expand evenly in the advanced panel
        for i in range(4):
            parent.columnconfigure(i, weight=1)
        for i in range(len(adv_buttons)):
            parent.rowconfigure(i, weight=1)

    def create_basic_buttons(self, parent):
        """Create the basic number pad and arithmetic operator panel."""
        # Define basic buttons layout in a typical number pad style:
        # Rows with 4 columns; last row has '=' spanning across.
        basic_buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', '±', '+']
        ]
        for r, row in enumerate(basic_buttons):
            for c, char in enumerate(row):
                btn = ttk.Button(parent, text=char, style="TButton")
                btn.grid(row=r, column=c, padx=4, pady=4, ipadx=10, ipady=10, sticky="nsew")
                # Map basic commands
                if char == '±':
                    btn.config(command=self.plus_minus)
                else:
                    btn.config(command=lambda ch=char: self.append_to_operator(ch))
                btn.bind("<Enter>", lambda e, b=btn: b.state(["active"]))
                btn.bind("<Leave>", lambda e, b=btn: b.state(["!active"]))
        # Last row: '=' button spanning all 4 columns
        eq_btn = ttk.Button(parent, text='=', style="TButton", command=self.calculate)
        eq_btn.grid(row=4, column=0, columnspan=4, padx=4, pady=4, ipadx=10, ipady=10, sticky="nsew")
        eq_btn.bind("<Enter>", lambda e, b=eq_btn: b.state(["active"]))
        eq_btn.bind("<Leave>", lambda e, b=eq_btn: b.state(["!active"]))
        # Configure grid weights for the basic panel
        for i in range(4):
            parent.columnconfigure(i, weight=1)
        for i in range(5):
            parent.rowconfigure(i, weight=1)

    def bind_keys(self):
        """Bind keyboard events for input."""
        self.bind("<Key>", self.key_event)

    def key_event(self, event):
        """Handle keyboard events to allow direct input."""
        char = event.char
        keysym = event.keysym
        if char in "0123456789.+-*/()%":
            self.append_to_operator(char)
        elif keysym == "Return":
            self.calculate()
        elif keysym == "BackSpace":
            self.backspace()
        elif keysym.lower() == "c":
            self.clear_all()

    def toggle_mode(self):
        """Toggle between full (advanced) mode and compact mode."""
        self.full_mode = not self.full_mode
        # Remove both panels from container frame
        for widget in self.container_frame.winfo_children():
            widget.grid_forget()
        # Remove history frame if exists
        if hasattr(self, 'history_frame'):
            self.history_frame.pack_forget()
        # Re-pack panels based on mode
        if self.full_mode:
            # Show advanced panel and basic panel side by side
            self.advanced_frame.grid(row=0, column=0, sticky="nsew", padx=5)
            self.basic_frame.grid(row=0, column=1, sticky="nsew", padx=5)
            self.container_frame.columnconfigure(0, weight=1)
            self.container_frame.columnconfigure(1, weight=1)
            # Show history panel
            self.history_frame.pack(pady=10, fill=tk.BOTH, expand=True)
            self.mode_toggle_btn.config(text="Switch to Compact Mode")
        else:
            # Hide advanced functions and history panel; expand basic panel
            self.basic_frame.grid(row=0, column=0, sticky="nsew")
            self.container_frame.columnconfigure(0, weight=1)
            self.mode_toggle_btn.config(text="Switch to Full Mode")

    def toggle_angle_mode(self):
        """Toggle the angle mode between radians and degrees and update the button text."""
        if self.angle_mode == "rad":
            self.angle_mode = "deg"
            # Change the button label to reflect mode; find button by text "Rad"
            for child in self.advanced_frame.winfo_children():
                if child.cget("text") in ("Rad", "Deg"):
                    child.config(text="Deg")
                    break
        else:
            self.angle_mode = "rad"
            for child in self.advanced_frame.winfo_children():
                if child.cget("text") in ("Rad", "Deg"):
                    child.config(text="Rad")
                    break

    def append_to_operator(self, value):
        """Append a character or operator to the current expression."""
        # For percentage, convert to division by 100 (if user presses % in basic panel)
        if value == '%':
            self.operator += "/100"
        else:
            self.operator += str(value)
        self.display_var.set(self.operator)

    def append_function(self, func):
        """Append a scientific function call to the expression."""
        # For trigonometric functions, check angle mode
        if func in ('sin', 'cos', 'tan'):
            if self.angle_mode == "deg":
                # Use custom degree functions
                self.operator += f"deg_{func}("
            else:
                self.operator += f"math.{func}("
        elif func == '√':
            self.operator += "math.sqrt("
        else:
            # For ln and exp
            self.operator += f"math.{func}("
        self.display_var.set(self.operator)

    def append_constant(self, const_value):
        """Append a constant value (π or e) to the expression."""
        self.operator += str(const_value)
        self.display_var.set(self.operator)

    def append_ans(self):
        """Append the last result to the current expression."""
        self.operator += str(self.last_result)
        self.display_var.set(self.operator)

    def clear_all(self):
        """Clear the entire expression."""
        self.operator = ""
        self.display_var.set("")

    def clear_entry(self):
        """Clear only the current entry (display)."""
        self.operator = ""
        self.display_var.set("")

    def backspace(self):
        """Remove the last character from the expression."""
        self.operator = self.operator[:-1]
        self.display_var.set(self.operator)

    def calculate(self):
        """Evaluate the expression, update history, and display the result."""
        try:
            # Prepare a safe evaluation context with math functions and custom degree functions.
            safe_dict = {
                "math": math,
                "deg_sin": deg_sin,
                "deg_cos": deg_cos,
                "deg_tan": deg_tan,
                "__builtins__": None
            }
            # Replace percentage symbol if left unprocessed
            expression = self.operator
            result = eval(expression, safe_dict, {})
            self.last_result = result
            self.display_var.set(result)
            # Update history
            history_entry = f"{self.operator} = {result}"
            self.history.append(history_entry)
            if self.full_mode and hasattr(self, 'history_list'):
                self.history_list.insert(tk.END, history_entry)
            self.operator = str(result)
        except Exception:
            self.display_var.set("Error")
            self.operator = ""

    def memory_clear(self):
        """Clear stored memory."""
        self.memory = 0
        self.display_var.set("Memory Cleared")

    def memory_recall(self):
        """Recall the stored memory value."""
        self.operator += str(self.memory)
        self.display_var.set(self.operator)

    def memory_add(self):
        """Add the current evaluated expression to memory."""
        try:
            safe_dict = {"math": math, "deg_sin": deg_sin, "deg_cos": deg_cos, "deg_tan": deg_tan, "__builtins__": None}
            current_value = eval(self.operator, safe_dict, {}) if self.operator else 0
            self.memory += current_value
            self.display_var.set(f"M: {self.memory}")
            self.operator = ""
        except Exception:
            self.display_var.set("Error")
            self.operator = ""

    def memory_subtract(self):
        """Subtract the current evaluated expression from memory."""
        try:
            safe_dict = {"math": math, "deg_sin": deg_sin, "deg_cos": deg_cos, "deg_tan": deg_tan, "__builtins__": None}
            current_value = eval(self.operator, safe_dict, {}) if self.operator else 0
            self.memory -= current_value
            self.display_var.set(f"M: {self.memory}")
            self.operator = ""
        except Exception:
            self.display_var.set("Error")
            self.operator = ""

    def plus_minus(self):
        """Toggle the sign of the current expression."""
        if self.operator:
            try:
                if self.operator[0] == '-':
                    self.operator = self.operator[1:]
                else:
                    self.operator = '-' + self.operator
                self.display_var.set(self.operator)
            except Exception:
                self.display_var.set("Error")
                self.operator = ""

if __name__ == "__main__":
    calc = AdvancedCalculator()
    calc.mainloop()
