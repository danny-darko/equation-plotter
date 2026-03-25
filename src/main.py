import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import sympy as sp
import re
import tkinter.font as tkfont
from matplotlib.ticker import MultipleLocator


class GraphPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Equation Plotter")

        # Make font size bigger
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=15)
        self.root.option_add("*Font", default_font)

        # Starter functions
        self.examples = [
            "x^2",
            "sin(x)",
            "cos(x)",
            "tan(x)",
            "log(x)",
            "sqrt(x)",
            "exp(-x)",
            "abs(x)",
            "x*sin(x) + log(x)"
        ]

        # Dropdown Label
        tk.Label(root, text="Choose a sample function ('^' is power notation for the computer to understand):").pack()

        # Dropdown Menu
        self.selected_example = tk.StringVar()
        self.selected_example.set(self.examples[0])  # default
        example_menu = tk.OptionMenu(root, self.selected_example, *self.examples, command=self.fill_entry)
        example_menu.pack(pady=5)

        # Entry for custom input
        tk.Label(root, text="Or enter your own equation in terms of x:").pack()
        self.entry = tk.Entry(root, width=40)
        self.entry.pack(pady=5)

        # 2nd optional equation
        tk.Label(root, text="Second equation (optional, for simultaneous plotting):").pack()
        self.entry2 = tk.Entry(root, width=40)
        self.entry2.pack(pady=5)

        # Plot Button
        tk.Button(root, text="Plot Graph", command=self.plot_graph).pack(pady=5)

        # Graph Display Area Frame (resizable container)
        plot_frame = tk.Frame(root)
        plot_frame.pack(expand=True, fill='both')

        # Create matplotlib figure and canvas
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()

        # Add navigation toolbar inside the plot frame
        self.toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        self.toolbar.update()
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Pack canvas and allow it to expand with window
        self.canvas.get_tk_widget().pack(side=tk.TOP, expand=True, fill='both')

        # Proper exit on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def fill_entry(self, selected):
        """Fill the input box with selected example"""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, selected)

    def plot_graph(self):
        original_input = self.entry.get()
        expr_input = original_input.replace('^', '**')
        expr_input = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', expr_input)

        x = sp.Symbol('x')

        allowed_locals = {
            'x': x,
            'sin': sp.sin,
            'cos': sp.cos,
            'tan': sp.tan,
            'log': sp.log,
            'ln': sp.log,
            'sqrt': sp.sqrt,
            'exp': sp.exp,
            'pi': sp.pi,
            'e': sp.E,
            'abs': sp.Abs,
        }

        try:
            expr = sp.sympify(expr_input, locals=allowed_locals)
            f = sp.lambdify(x, expr, modules=["numpy"])

            x_vals = np.linspace(-10, 10, 400)
            y_vals = f(x_vals)

            # Remove undefined values (e.g., log(x<0))
            mask = np.isfinite(y_vals)
            x_vals = x_vals[mask]
            y_vals = y_vals[mask]

            self.ax.clear()
            label_tex = r"$y = " + original_input.replace("^", "^") + "$"
            self.ax.plot(x_vals, y_vals, label=label_tex)

            # Clamp Y-axis range for better viewing
            if y_vals.size > 0:
                y_min, y_max = np.min(y_vals), np.max(y_vals)
                y_min = max(y_min, -10)
                y_max = min(y_max, 20)
                self.ax.set_ylim(y_min, y_max)

            # Set smaller grid intervals
            self.ax.xaxis.set_major_locator(MultipleLocator(1))
            self.ax.yaxis.set_major_locator(MultipleLocator(1))

            self.ax.set_title(label_tex, fontsize=20)
            self.ax.set_xlabel("x", fontsize=17)
            self.ax.set_ylabel("y", fontsize=17)
            self.ax.tick_params(axis='both', which='major', labelsize=17)

            self.ax.grid(True)

            # === Intercepts and turning point ===

            # 1. Y-intercept (f(0))
            try:
                y_intercept = f(0)
                if np.isfinite(y_intercept):
                    self.ax.plot(0, y_intercept, 'go', label="Y-Intercept")
                    self.ax.annotate(f"({0:.2f}, {y_intercept:.2f})", (0, y_intercept),
                                     textcoords="offset points", xytext=(10, 10), fontsize=12, color='green')
            except:
                pass

            # 2. X-intercepts (solve f(x) = 0)
            try:
                x_intercepts = sp.solve(expr, x)
                for xi in x_intercepts:
                    if xi.is_real:
                        xi_val = float(xi.evalf())
                        if -10 <= xi_val <= 10:
                            self.ax.plot(xi_val, 0, 'ro', label="X-Intercept")
                            self.ax.annotate(f"({xi_val:.2f}, 0)", (xi_val, 0),
                                             textcoords="offset points", xytext=(10, -20), fontsize=12, color='red')
            except:
                pass

            # 3. Turning point (only for quadratics)
            try:
                poly = sp.Poly(expr, x)
                if poly.degree() == 2:
                    a, b, c = poly.all_coeffs()
                    a = float(a)
                    b = float(b)
                    vertex_x = -b / (2 * a)
                    vertex_y = float(f(vertex_x))
                    self.ax.plot(vertex_x, vertex_y, 'bo', label="Turning Point")
                    self.ax.annotate(f"({vertex_x:.2f}, {vertex_y:.2f})", (vertex_x, vertex_y),
                                     textcoords="offset points", xytext=(-60, -10), fontsize=12, color='blue')
            except:
                pass

            # Check if a second equation was provided
            second_input = self.entry2.get().strip()
            if second_input:
                expr_input2 = second_input.replace('^', '**')
                expr_input2 = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', expr_input2)

                try:
                    expr2 = sp.sympify(expr_input2, locals=allowed_locals)
                    f2 = sp.lambdify(x, expr2, modules=["numpy"])
                    y_vals2 = f2(x_vals)
                    mask2 = np.isfinite(y_vals2)
                    x_vals2 = x_vals[mask2]
                    y_vals2 = y_vals2[mask2]
                    label_tex2 = r"$y = " + second_input + "$"
                    self.ax.plot(x_vals2, y_vals2, label=label_tex2, linestyle='--')

                    # === Solve for point of intersection ===
                    solution = sp.solve(sp.Eq(expr, expr2), x)
                    if solution:
                        for sol in solution:
                            if sol.is_real:
                                y_val = expr.subs(x, sol).evalf()
                                self.ax.plot(float(sol), float(y_val), 'mo')  # magenta circle
                                self.ax.annotate(f"({sol.evalf():.2f}, {y_val:.2f})",
                                                 (float(sol), float(y_val)),
                                                 textcoords="offset points", xytext=(10, 10),
                                                 fontsize=12, color='purple')

                except Exception as e:
                    messagebox.showerror("Error", f"Second equation invalid:\n{e}")

            self.ax.legend(fontsize=17)
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Error", f"Invalid equation:\n{e}")

    def on_close(self):
        """Properly close the app"""
        self.root.quit()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphPlotterApp(root)
    root.mainloop()