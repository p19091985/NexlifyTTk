# teste_tkinter.py
import tkinter as tk

try:
    root = tk.Tk()
    root.title("Teste de Ambiente Tkinter")
    root.geometry("400x200")
    label = tk.Label(root, text="Se esta janela apareceu,\no seu ambiente Tkinter está funcionando.", font=("Helvetica", 14))
    label.pack(pady=40)
    root.mainloop()
except Exception as e:
    print(f"Ocorreu um erro ao tentar criar a janela de teste: {e}")