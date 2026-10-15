"""Small helpers for consistent Tk modal dialog behavior."""

import tkinter as tk

from utils.ui_components import center_window


def prepare_modal(
    window,
    *,
    parent=None,
    width=None,
    height=None,
    resizable=False,
    grab=True,
    wait_visibility=True,
):
    """Apply consistent transient, centering and grab behavior to a Toplevel."""
    if width is not None or height is not None:
        center_window(window, width, height, parent=parent)

    if parent is not None:
        try:
            window.transient(parent)
        except tk.TclError:
            pass

    try:
        if isinstance(resizable, tuple):
            window.resizable(*resizable)
        else:
            window.resizable(resizable, resizable)
    except tk.TclError:
        pass

    if wait_visibility:
        try:
            window.wait_visibility()
        except tk.TclError:
            pass

    if grab:
        try:
            window.grab_set()
        except tk.TclError:
            pass

    return window


def wait_for_modal(owner, window):
    """Wait for a modal dialog without leaking Tcl errors during teardown."""
    try:
        owner.wait_window(window)
    except tk.TclError:
        pass
