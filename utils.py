import tkinter as tk


def adicionar_mensagem(text_area, mensagem):
    text_area.config(state=tk.NORMAL)  # Habilita a edição do Text
    text_area.insert(tk.END, mensagem + "\n")  # Adiciona a mensagem ao final
    text_area.config(state=tk.DISABLED)  # Desabilita a edição do Text
    text_area.see(tk.END)  # Rolagem automática para a última mensagem
