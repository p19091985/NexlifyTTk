import tkinter as tk
from tkinter import ttk
from theme import COLORS as C

def center_window(window: tk.Toplevel, width: int = None, height: int = None, parent: tk.Widget = None):
    """
    Centers a Toplevel window relative to its parent (or the screen if no parent).
    If width and height are provided, it sets the geometry explicitly.
    Otherwise, it forces an update to calculate the required size.
    """
    if width is None or height is None:
        window.update_idletasks()

    # Determine dimensions
    w = width if width is not None else window.winfo_width()
    h = height if height is not None else window.winfo_height()

    if parent is None:
        parent = window.master

    if parent:
        parent = parent.winfo_toplevel()

    # Determine position
    if parent and parent.winfo_viewable():
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
    else:
        # Fallback to screen center
        screen_w = window.winfo_screenwidth()
        screen_h = window.winfo_screenheight()
        x = (screen_w // 2) - (w // 2)
        y = (screen_h // 2) - (h // 2)

    # Ensure it's not off-screen
    x = max(0, x)
    y = max(0, y)

    window.geometry(f"{w}x{h}{x:+d}{y:+d}")

class Tooltip:
    """Lightweight hover tooltip for any tkinter widget."""

    def __init__(self, widget, text, delay=400):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._tipwindow = None
        self._id = None
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)

    def _on_enter(self, event=None):
        self._id = self.widget.after(self.delay, self._show)

    def _on_leave(self, event=None):
        if self._id:
            self.widget.after_cancel(self._id)
            self._id = None
        self._hide()

    def _show(self):
        if self._tipwindow:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"{x:+d}{y:+d}")
        tw.configure(bg=C["bg_toolbar"])
        tk.Label(tw, text=self.text, justify=tk.LEFT,
                 bg=C["bg_toolbar"], fg=C["fg_primary"], relief=tk.SOLID, borderwidth=1,
                 font=("Arial", 9), padx=8, pady=4).pack()
        self._tipwindow = tw

    def _hide(self):
        if self._tipwindow:
            self._tipwindow.destroy()
            self._tipwindow = None
