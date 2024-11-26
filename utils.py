import tkinter as tk
from tkinter import Toplevel, Label, Button, ttk
from datetime import datetime
from cryptography.fernet import Fernet


def adicionar_mensagem(text_area, mensagem):
    text_area.config(state=tk.NORMAL)  # Habilita a edição do Text
    text_area.insert(tk.END, mensagem + "\n")  # Adiciona a mensagem ao final
    text_area.config(state=tk.DISABLED)  # Desabilita a edição do Text
    text_area.see(tk.END)  # Rolagem automática para a última mensagem


def check_input(input_field):
    input_value = input_field.get_attribute("value")
    return len(input_value) >= 6


def check_input_and_time(input_field, hora_limite_param):
    current_time = datetime.now().time()
    input_value = input_field.get_attribute("value")
    return (
        len(input_value) >= 6
        and current_time >= datetime.strptime(hora_limite_param, "%H:%M:%S").time()
    )


def mostrar_mensagem_centralizada(parent_window, titulo, mensagem):
    dialogo = Toplevel(parent_window)
    dialogo.title(titulo)
    dialogo.geometry("300x100")

    largura_tela = dialogo.winfo_screenwidth()
    altura_tela = dialogo.winfo_screenheight()
    pos_x = (largura_tela - 300) // 2
    pos_y = (altura_tela - 100) // 2
    dialogo.geometry(f"300x100+{pos_x}+{pos_y}")

    Label(dialogo, text=mensagem, wraplength=280, justify="center").pack(pady=10)
    Button(dialogo, text="OK", command=dialogo.destroy).pack(pady=10)

    dialogo.transient(parent_window)
    dialogo.grab_set()
    parent_window.wait_window(dialogo)


def mostrar_dialogo_carregamento(parent_window, mensagem="Aguarde..."):
    dialogo = Toplevel(parent_window)
    dialogo.title("Carregando")
    dialogo.geometry("200x100")

    largura_tela = dialogo.winfo_screenwidth()
    altura_tela = dialogo.winfo_screenheight()
    pos_x = (largura_tela - 200) // 2
    pos_y = (altura_tela - 100) // 2
    dialogo.geometry(f"200x100+{pos_x}+{pos_y}")

    Label(dialogo, text=mensagem).pack(pady=20)

    # Adiciona uma barra de progresso
    progress_bar = ttk.Progressbar(dialogo, mode="indeterminate", length=250)
    progress_bar.pack(pady=10)
    progress_bar.start()  # Inicia a animação da barra

    dialogo.transient(parent_window)
    dialogo.grab_set()
    return dialogo, progress_bar


def fechar_dialogo_carregamento(dialogo, progress_bar):
    progress_bar.stop()  # Para a animação da barra
    dialogo.destroy()


# Função para gerar uma chave secreta (apenas uma vez)
def gerar_chave():
    chave = Fernet.generate_key()
    with open("chave.key", "wb") as chave_arquivo:
        chave_arquivo.write(chave)


# Função para carregar a chave secreta
def carregar_chave():
    return open("chave.key", "rb").read()


# Função para criptografar o CPF
def criptografar(dado):
    chave = carregar_chave()  # Carrega a chave secreta
    fernet = Fernet(chave)  # Cria o objeto Fernet
    dado_criptografado = fernet.encrypt(dado.encode())  # Criptografa o CPF
    return dado_criptografado


# Função para descriptografar o CPF
def descriptografar(dado):
    chave = carregar_chave()  # Carrega a chave secreta
    fernet = Fernet(chave)  # Cria o objeto Fernet
    dado_descriptografado = fernet.decrypt(dado).decode()  # Descriptografa o CPF
    return dado_descriptografado


def salvar_pagina(navegador_param):
    with open("output.html", "w", encoding="utf-8") as file:
        file.write(navegador_param.page_source)

    print("Conteúdo salvo em output.html")
