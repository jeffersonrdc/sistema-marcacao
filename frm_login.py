import os
import requests
import jwt
import tkinter as tk
from tkinter import Toplevel, Label, Button, messagebox
from frm_marcacao import MarcacaoWindow

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
        
        tk.Button(self.janela_login, text="Login", command=self.fazer_login).pack(pady=20)
        
    def mostrar_mensagem_centralizada(self, titulo, mensagem):
        dialogo = Toplevel(self.janela_login)
        dialogo.title(titulo)
        dialogo.geometry("300x100")
        
        largura_tela = dialogo.winfo_screenwidth()
        altura_tela = dialogo.winfo_screenheight()
        pos_x = (largura_tela - 300) // 2
        pos_y = (altura_tela - 100) // 2
        dialogo.geometry(f"300x100+{pos_x}+{pos_y}")
        
        Label(dialogo, text=mensagem, wraplength=280, justify="center").pack(pady=10)
        Button(dialogo, text="OK", command=dialogo.destroy).pack(pady=10)
        
        dialogo.transient(self.janela_login)
        dialogo.grab_set()
        self.janela_login.wait_window(dialogo)

    def validar_login(self, usuario, senha):
        url = "http://localhost:8000/login"
        response = requests.post(url, json={"usuario": usuario, "senha": senha})

        if response.status_code == 200:
            token = response.json().get("token")
            secret_key = os.getenv("SECRET_KEY")
            decoded_data = jwt.decode(
                token, secret_key, algorithms=["HS256"], options={"verify_exp": False}
            )
            return True
        return False

    def fazer_login(self):
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()

        if not usuario or not senha:
            self.mostrar_mensagem_centralizada("Erro", "Por favor, preencha os campos de usuário e senha.")
            return
        
        try:
            if self.validar_login(usuario, senha):
                self.janela_login.destroy()  # Fecha a janela de login
                frm_marcacao = MarcacaoWindow()  # Inicia a janela principal
                frm_marcacao.start()
            else:
                self.mostrar_mensagem_centralizada("Erro", "Usuário ou senha incorretos.")
        except requests.RequestException as e:
            messagebox.showerror("Erro", f"Erro de conexão: {e}")

    def start(self):
        self.janela_login.mainloop()
