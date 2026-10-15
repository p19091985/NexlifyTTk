import tkinter as tk
from tkinter import ttk
import logging
from theme import C, apply_dark_theme, scaled, scaled_font
from utils.window_icon import apply_window_icon

class StartupSplash:
    """Small themed splash window shown while the app is bootstrapping."""

    def __init__(self, project_root: str, logger: logging.Logger) -> None:
        self.project_root = project_root
        self.logger = logger
        self.cancelled = False

        self.root = tk.Tk()
        self.root.title("NexlifyTTk")
        self.root.configure(bg=C["bg_dark"])
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._handle_close_request)

        apply_window_icon(self.root, self.project_root, default=True, logger=self.logger)

        self.style = ttk.Style(self.root)
        apply_dark_theme(self.style)
        self.style.configure(
            "Startup.Horizontal.TProgressbar",
            troughcolor=C["bg_darkest"],
            background=C["accent_blue"],
            lightcolor=C["accent_blue"],
            darkcolor=C["accent_blue"],
            bordercolor=C["bg_darkest"],
            thickness=scaled(10),
        )

        self.status_var = tk.StringVar(value="Preparando ambiente inicial...")

        shell = tk.Frame(
            self.root,
            bg=C["accent_blue"],
            padx=1,
            pady=1,
            bd=0,
            highlightthickness=0,
        )
        shell.pack(fill="both", expand=True)

        card = tk.Frame(
            shell,
            bg=C["bg_darker"],
            padx=scaled(22),
            pady=scaled(20),
            bd=0,
            highlightthickness=0,
        )
        card.pack(fill="both", expand=True)

        title = tk.Label(
            card,
            text="NexlifyTTk",
            bg=C["bg_darker"],
            fg=C["accent_blue"],
            font=scaled_font("Segoe UI", 18, "bold"),
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            card,
            text="Preparando o ambiente e a interface do template.",
            bg=C["bg_darker"],
            fg=C["fg_secondary"],
            font=scaled_font("Segoe UI", 10),
        )
        subtitle.pack(anchor="w", pady=(scaled(6), scaled(18)))

        self.status_label = tk.Label(
            card,
            textvariable=self.status_var,
            bg=C["bg_darker"],
            fg=C["fg_primary"],
            font=scaled_font("Segoe UI", 10, "bold"),
        )
        self.status_label.pack(anchor="w", pady=(0, scaled(10)))

        self.progress = ttk.Progressbar(
            card,
            mode="indeterminate",
            length=scaled(340),
            style="Startup.Horizontal.TProgressbar",
        )
        self.progress.pack(fill="x")

        note = tk.Label(
            card,
            text="A janela principal sera aberta quando o ambiente minimo estiver pronto para uso.",
            bg=C["bg_darker"],
            fg=C["fg_muted"],
            font=scaled_font("Segoe UI", 9),
            wraplength=scaled(360),
            justify="left",
        )
        note.pack(anchor="w", pady=(scaled(12), 0))

        self.root.update_idletasks()
        width = max(scaled(420), card.winfo_reqwidth() + scaled(2))
        height = max(scaled(180), card.winfo_reqheight() + scaled(2))
        self._center_window(width, height)
        try:
            self.root.attributes("-topmost", True)
        except tk.TclError:
            pass
        self.progress.start(11)
        self.pump()

    def _center_window(self, width: int, height: int) -> None:
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _handle_close_request(self) -> None:
        self.cancelled = True
        self.close()

    def set_status(self, text: str) -> None:
        self.status_var.set(text)
        self.pump()

    def pump(self) -> None:
        try:
            self.root.update_idletasks()
            self.root.update()
        except tk.TclError:
            self.cancelled = True

    def close(self) -> None:
        try:
            self.progress.stop()
        except Exception:
            pass

        try:
            self.root.destroy()
        except tk.TclError:
            pass
