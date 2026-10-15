import datetime
import tkinter as tk
from tkinter import ttk, messagebox

from modals.dialog_utils import prepare_modal
from theme import COLORS as C
from utils.ui_components import Tooltip
from utils.system_report import collect_computer_info, format_computer_report


class ComputerInfoDialog(tk.Toplevel):
    """Dialog that shows a hardware/software report for the computer."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.title("Informações do Computador")
        self.configure(bg=C["bg_dark"])
        self.minsize(800, 560)

        self._build_ui()
        self._refresh_report()
        prepare_modal(self, parent=parent, width=920, height=640, resizable=True)
        self.focus_force()

    def _build_ui(self):
        main = tk.Frame(self, bg=C["bg_dark"], padx=18, pady=18)
        main.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            main,
            text="Informações do Computador",
            font=("Arial", 15, "bold"),
            bg=C["bg_dark"],
            fg=C["accent_blue"],
        ).pack(anchor="w")

        tk.Label(
            main,
            text="Relatório local do sistema, CPU, memória, armazenamento e GPU.",
            font=("Arial", 10),
            bg=C["bg_dark"],
            fg=C["fg_secondary"],
        ).pack(anchor="w", pady=(6, 14))

        toolbar = tk.Frame(main, bg=C["bg_dark"])
        toolbar.pack(fill=tk.X, pady=(0, 10))

        refresh_btn = tk.Button(
            toolbar,
            text="Atualizar Relatório",
            font=("Arial", 10, "bold"),
            bg=C["accent_green"],
            fg="#ffffff",
            activebackground=C["accent_green_h"],
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._refresh_report,
        )
        refresh_btn.pack(side=tk.LEFT)
        Tooltip(refresh_btn, "Recolhe novamente as informações do computador")

        copy_btn = tk.Button(
            toolbar,
            text="Copiar Relatório",
            font=("Arial", 10),
            bg=C["accent_blue"],
            fg="#ffffff",
            activebackground=C["accent_blue_h"],
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._copy_report,
        )
        copy_btn.pack(side=tk.LEFT, padx=(8, 0))

        self.updated_label = tk.Label(
            toolbar,
            text="",
            font=("Arial", 9),
            bg=C["bg_dark"],
            fg=C["fg_muted"],
        )
        self.updated_label.pack(side=tk.RIGHT)

        text_frame = tk.Frame(main, bg=C["bg_dark"])
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.report_text = tk.Text(
            text_frame,
            wrap="word",
            font=("Courier New", 10),
            bg=C["bg_darkest"],
            fg=C["fg_primary"],
            insertbackground=C["fg_primary"],
            relief=tk.FLAT,
            padx=12,
            pady=12,
        )
        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.report_text.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_text.configure(yscrollcommand=scroll.set)

        footer = tk.Frame(main, bg=C["bg_dark"])
        footer.pack(fill=tk.X, pady=(10, 0))

        close_btn = tk.Button(
            footer,
            text="Fechar",
            font=("Arial", 10),
            bg=C["bg_button"],
            fg=C["fg_primary"],
            activebackground=C["bg_button_hover"],
            activeforeground=C["fg_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.destroy,
        )
        close_btn.pack(side=tk.RIGHT)

    def _set_report(self, text: str):
        self.report_text.config(state=tk.NORMAL)
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert("1.0", text)
        self.report_text.config(state=tk.DISABLED)

    def _refresh_report(self):
        report = collect_computer_info()
        text = format_computer_report(report)
        self._set_report(text)
        stamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.updated_label.config(text=f"Atualizado em {stamp}")

    def _copy_report(self):
        text = self.report_text.get("1.0", tk.END).strip()
        if not text:
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copiado", "Relatório copiado para a área de transferência.", parent=self)
