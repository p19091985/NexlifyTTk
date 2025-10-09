# teste_ambiente.py
import ttkbootstrap as bstrap
import sys

def run_test():
    print(" INICIANDO TESTE DE AMBIENTE TTKBOOTSTRAP ")
    print(f"Versão do Python: {sys.version}")
    try:
        # 1. Criar a janela principal
        print("Passo 1: Criando a janela (bstrap.Window)...")
        window = bstrap.Window(themename="litera")
        window.title("Teste de Ambiente")
        window.geometry("400x200")
        print("Passo 1: Sucesso.")

        # 2. Adicionar um widget simples
        print("Passo 2: Adicionando um Label...")
        label = bstrap.Label(window, text="Se esta janela é visível, o ambiente está OK.", font=("Segoe UI", 12))
        label.pack(expand=True)
        print("Passo 2: Sucesso.")

        # 3. Iniciar o loop da aplicação
        print("Passo 3: Iniciando o mainloop()...")
        window.mainloop()
        print(" TESTE FINALIZADO COM SUCESSO ")

    except Exception as e:
        print(f"\n OCORREU UM ERRO DURANTE O TESTE ")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()