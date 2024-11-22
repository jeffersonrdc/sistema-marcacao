import tkinter as tk
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
