import os
import requests
import jwt
import tkinter as tk
from tkinter import Toplevel, Label, Button, messagebox, ttk
from frm_marcacao import MarcacaoWindow
import threading
from utils import criptografar, descriptografar
from utils import (
    mostrar_mensagem_centralizada,
    mostrar_dialogo_carregamento,
    fechar_dialogo_carregamento,
)
import identificadores


class LoginWindow:
    def __init__(self):
        self.janela_login = tk.Tk()
        self.janela_login.title("Login")
        self.janela_login.geometry("300x200")

        # Centraliza a janela
        largura_tela = self.janela_login.winfo_screenwidth()
        altura_tela = self.janela_login.winfo_screenheight()
        pos_x = (largura_tela - 300) // 2
        pos_y = (altura_tela - 200) // 2
        self.janela_login.geometry(f"300x200+{pos_x}+{pos_y}")

        # Cria os widgets de login
        tk.Label(self.janela_login, text="Usuário:").pack(pady=5)
        self.entry_usuario = tk.Entry(self.janela_login)
        self.entry_usuario.pack(pady=5)

        tk.Label(self.janela_login, text="Senha:").pack(pady=5)
        self.entry_senha = tk.Entry(self.janela_login, show="*")
        self.entry_senha.pack(pady=5)

        tk.Button(self.janela_login, text="Login", command=self.fazer_login).pack(
            pady=20
        )

        # Associa a tecla Enter ao botão de login
        self.janela_login.bind("<Return>", lambda event: self.fazer_login())

    def validar_login(self, usuario, senha):
        url = "http://localhost:8000/login"
        response = requests.post(url, json={"usuario": usuario, "senha": senha})

        if response.status_code == 200:
            identificadores.token = response.json().get("token")
            secret_key = os.getenv("SECRET_KEY")
            decoded_data = jwt.decode(
                identificadores.token,
                secret_key,
                algorithms=["HS256"],
                options={"verify_exp": False},
            )
            return True
        return False

    def fazer_login(self):
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()

        if not usuario or not senha:
            mostrar_mensagem_centralizada(
                self.janela_login,
                "Erro",
                "Por favor, preencha os campos de usuário e senha.",
            )
            return

        # Mostrar o diálogo de carregamento
        dialogo_carregamento, progress_bar = mostrar_dialogo_carregamento(
            self.janela_login, "Fazendo login..."
        )

        # Função para processar o login
        def processar_login():
            try:
                sucesso = self.validar_login(usuario, senha)

                # Fechar o diálogo na thread principal
                self.janela_login.after(
                    0,
                    fechar_dialogo_carregamento,
                    dialogo_carregamento,
                    progress_bar,
                )

                if sucesso:
                    # Navegar para a próxima janela na thread principal
                    self.janela_login.after(0, self.iniciar_marcacao)
                else:
                    # Mostrar mensagem de erro na thread principal
                    self.janela_login.after(
                        0,
                        lambda: mostrar_mensagem_centralizada(
                            self.janela_login, "Erro", "Usuário ou senha incorretos."
                        ),
                    )
            except requests.RequestException as e:
                # Fechar o diálogo e mostrar erro na thread principal
                self.janela_login.after(
                    0,
                    fechar_dialogo_carregamento,
                    dialogo_carregamento,
                    progress_bar,
                )
                self.janela_login.after(
                    0,
                    lambda: messagebox.showerror("Erro", f"Erro de conexão: {e}"),
                )

        # Inicia o processamento do login em uma thread separada
        threading.Thread(target=processar_login, daemon=True).start()

    def iniciar_marcacao(self):
        self.janela_login.destroy()  # Fecha a janela de login
        frm_marcacao = MarcacaoWindow()  # Inicia a janela principal
        frm_marcacao.start()

    def start(self):
        self.janela_login.mainloop()
