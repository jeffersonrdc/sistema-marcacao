import tkinter as tk
from tkinter import (
    StringVar,
    OptionMenu,
    Checkbutton,
    IntVar,
    Text,
    Scrollbar,
    Button,
    messagebox,
)
from identificadores import *  # Supondo que essas variáveis sejam definidas em identificadores
from datetime import datetime, date
from dateutil.relativedelta import relativedelta, SU
import pandas as pd
from automacao import acessar_site
from utils import adicionar_mensagem


def validar_entrada(texto):
    return texto.isdigit() or texto == ""


class MarcacaoWindow:
    def __init__(self):
        # Inicializa a janela
        self.janela_marcacao = tk.Tk()
        self.janela_marcacao.title("Sistema de Marcação")

        # Inicialização das variáveis
        self.convenio_vars = []
        self.cpa_vars = []
        self.checkbuttons_convenio = []
        self.checkbuttons_cpa = []
        self.select_convenio = []
        self.select_vagas_convenio = []
        self.select_cpa = []
        self.select_locais_cpa = []
        self.select_vagas_locais_cpa = []
        self.variable_convenio = []
        self.variable_vagas_convenio = []
        self.variable_cpa = []
        self.variable_locais_cpa = []
        self.variable_data_servico = []
        self.variable_vaga_servico = []
        self.variable_horario_servico = []
        self.variable_turno_servico = []
        self.hora_limite = None

        # Aqui está a definição do método update_hora_limite
        def update_hora_limite(value):
            self.hora_limite = value

        # Função que será chamada quando a checkbox for clicada

        def on_checkbox_click(index, is_convenio):
            if is_convenio:
                if self.convenio_vars[index].get() == 1:
                    self.cpa_vars[index].set(0)  # Desativa a checkbox de CPA
                    self.select_convenio[index].config(state="normal")
                    self.select_vagas_convenio[index].config(state="normal")
                    self.checkbuttons_cpa[index].config(state="disabled")
                    self.select_cpa[index].config(state="disabled")
                    self.select_locais_cpa[index].config(state="disabled")
                    self.select_vagas_locais_cpa[index].config(state="disabled")
                    self.variable_cpa[index].set(
                        OPTIONS_CPA[0]
                    )  # Reseta o OptionMenu de CPA
                else:
                    self.checkbuttons_cpa[index].config(
                        state="normal"
                    )  # Ativa a checkbox de CPA
                    self.variable_convenio[index].set(
                        OPTIONS_CONVENIO[0]
                    )  # Reseta o OptionMenu de Convênio
                    self.select_convenio[index].config(state="disabled")
                    self.select_vagas_convenio[index].config(state="disabled")
                    self.variable_vaga_servico[index].set(
                        "Selecione uma vaga"
                    )  # Reseta o OptionMenu de Convênio
            else:
                if self.cpa_vars[index].get() == 1:
                    self.convenio_vars[index].set(0)  # Desativa a checkbox de Convênio
                    self.checkbuttons_convenio[index].config(state="disabled")
                    self.select_convenio[index].config(state="disabled")
                    self.select_vagas_convenio[index].config(state="disabled")
                    self.select_cpa[index].config(state="normal")
                    self.select_vagas_locais_cpa[index].config(state="normal")
                    self.variable_convenio[index].set(
                        OPTIONS_CONVENIO[0]
                    )  # Reseta o OptionMenu de Convênio
                    self.variable_vagas_convenio[index].set(
                        "Selecione uma vaga"
                    )  # Reseta o OptionMenu de Convênio
                else:
                    self.checkbuttons_convenio[index].config(
                        state="normal"
                    )  # Ativa a checkbox de Convênio
                    self.variable_cpa[index].set(
                        OPTIONS_CPA[0]
                    )  # Reseta o OptionMenu de CPA
                    self.select_cpa[index].config(state="disabled")
                    self.select_locais_cpa[index].config(state="disabled")
                    self.select_vagas_locais_cpa[index].config(state="disabled")
                    self.select_vagas_locais_cpa[index].config(state="disabled")
                    self.variable_convenio[index].set(
                        OPTIONS_CONVENIO[0]
                    )  # Reseta o OptionMenu de Convênio
                    self.variable_locais_cpa[index].set(
                        "Selecione o local"
                    )  # Reseta o OptionMenu de Convênio
                    self.variable_vaga_servico[index].set(
                        "Selecione uma vaga"
                    )  # Reseta o OptionMenu de Convênio

        def update_locais_convenio(texto, index):
            locais_options = OPTIONS_VAGASXCONVENIO.get(texto, [])
            self.variable_vagas_convenio[index].set(
                locais_options[0] if locais_options else "Selecione uma vaga"
            )
            menu = self.select_vagas_convenio[index]["menu"]
            menu.delete(0, "end")

            for local in locais_options:
                menu.add_command(
                    label=local,
                    command=lambda l=local: self.variable_vagas_convenio[index].set(l),
                )

        def update_locais_cpa(texto, index):
            locais_options = OPTIONS_LOCAISXCPA.get(texto, [])
            self.variable_locais_cpa[index].set(
                locais_options[0] if locais_options else "Selecione um local"
            )
            menu = self.select_locais_cpa[index]["menu"]
            menu.delete(0, "end")
            if len(locais_options) > 0:
                self.select_locais_cpa[index].config(state="normal")
                for local in locais_options:
                    menu.add_command(
                        label=local,
                        command=lambda l=local, idx=index: (
                            self.variable_locais_cpa[idx].set(l),
                            update_vagas_locais_cpa(l, idx),
                        ),
                    )
            else:
                self.variable_locais_cpa[index].set(
                    locais_options[0] if locais_options else "Selecione um local"
                )  # Reseta o OptionMenu de Locais do CPA
                self.select_locais_cpa[index].config(state="disabled")

        def update_vagas_locais_cpa(texto, index):
            vagas_options = OPTIONS_VAGASXLOCAIS_CPA.get(texto, [])
            self.variable_vaga_servico[index].set(
                vagas_options[0] if vagas_options else "Selecione um local"
            )
            menu = self.select_vagas_locais_cpa[index]["menu"]
            menu.delete(0, "end")
            if len(vagas_options) > 0:
                self.select_vagas_locais_cpa[index].config(state="normal")
                for local in vagas_options:
                    menu.add_command(
                        label=local,
                        command=lambda l=local: self.variable_vaga_servico[index].set(
                            l
                        ),
                    )
            else:
                self.variable_vaga_servico[index].set(
                    vagas_options[0] if vagas_options else "Selecione um local"
                )  # Reseta o OptionMenu de Locais do CPA
                self.select_locais_cpa[index].config(state="disabled")

        # Verificar se hoje é quinta-feira
        today = date.today()
        if today.weekday() == 3:  # 3 representa quinta-feira
            second_sunday = (
                today + relativedelta(weekday=SU(1)) + relativedelta(weeks=1)
            )
            periods = (second_sunday - today).days + 1
        else:  # Se hoje for antes de quinta-feira (segunda a quarta)
            next_sunday = today + relativedelta(weekday=SU(1))
            periods = (next_sunday - today).days + 1

        # Gerar a lista de datas
        list_of_date = pd.date_range(today, periods=periods)

        # Converter as datas para strings e adicionar à lista de opções
        data = ["Selecione a data"] + [str(day.date()) for day in list_of_date]

        # Exemplo de uso da função de validação
        def validar_campos():
            global usuario, senha, tipo_login

            tipo_login = OPTIONS_IDENTIFICACAO.index(tipo_identificacao.get())
            if tipo_login == 0:
                messagebox.showerror("Erro", "Informe o tipo de login")
                return False
            else:
                if tipo_login == 1:
                    tipo_login = "CPF"
                else:
                    tipo_login = "ID"

            usuario = entry_usuario.get()
            usuarios_validos = ["12220864766", "51040425", "11325438782", "50952790"]
            if usuario not in usuarios_validos:
                messagebox.showerror("Erro", "Usuário não habilitado. Verifique!")
                return False

            senha = entry_senha.get()
            if not usuario or not senha:
                messagebox.showerror("Erro", "Usuário e senha não podem ser vazios.")
                return False

            if (
                OPTIONS_IDENTIFICACAO.index(tipo_identificacao.get()) == 1
                and len(usuario) != 11
            ):
                messagebox.showerror(
                    "Erro",
                    "Login do tipo CPF, o usuário deve ter exatamente 11 caracteres.",
                )
                return False

            """ horario_maracacao = OPTIONS_HORAMARCACAO.index(variable_horariomarcacao.get())
            if horario_maracacao == 0:
                show_alert("Erro", "Informe o horário da marcação")
                return False """
            is_servico_selecionado = False
            for i in range(7):
                data_servico = data.index(self.variable_data_servico[i].get())
                horario_servico = OPTIONS_HORARIO.index(
                    self.variable_horario_servico[i].get()
                )
                turno_servico = OPTIONS_TURNOSERVICO.index(
                    self.variable_turno_servico[i].get()
                )
                if self.convenio_vars[i].get():
                    indice_convenio = OPTIONS_CONVENIO.index(
                        self.variable_convenio[i].get()
                    )
                    convenio = OPTIONS_VAGASXCONVENIO[self.variable_convenio[i].get()]
                    vaga_convenio = convenio.index(
                        self.variable_vagas_convenio[i].get()
                    )
                    if indice_convenio == 0:
                        messagebox.showerror(
                            "Erro", f"Convênio da linha {i + 1} não informado"
                        )
                        return False
                    if vaga_convenio == 0:
                        messagebox.showerror(
                            "Erro", f"Vaga do convênio da linha {i + 1} não informado"
                        )
                        return False
                    if data_servico == 0:
                        messagebox.showerror(
                            "Erro", f"Data do serviço da linha {i + 1} não informado"
                        )
                        return False
                    if horario_servico == 0:
                        messagebox.showerror(
                            "Erro", f"Horario do serviço da linha {i + 1} não informado"
                        )
                        return False
                    if turno_servico == 0:
                        messagebox.showerror(
                            "Erro", f"Turno do serviço da linha {i + 1} não informado"
                        )
                        return False
                    is_servico_selecionado = True
                elif self.cpa_vars[i].get():
                    cpa = OPTIONS_CPA.index(self.variable_cpa[i].get())
                    if cpa == 0:
                        messagebox.showerror(
                            "Erro", f"CPA da linha {i + 1} não informado"
                        )
                        return False
                    locais_cpa = OPTIONS_LOCAISXCPA[self.variable_cpa[i].get()]
                    indice_local_selecionado = locais_cpa.index(
                        self.variable_locais_cpa[i].get()
                    )
                    local_selecionado = OPTIONS_VAGASXLOCAIS_CPA[
                        self.variable_locais_cpa[i].get()
                    ]
                    vaga_servico = local_selecionado.index(
                        self.variable_vaga_servico[i].get()
                    )
                    if indice_local_selecionado == 0:
                        messagebox.showerror(
                            "Erro", f"Local da linha {i + 1} não informado"
                        )
                        return False
                    if data_servico == 0:
                        messagebox.showerror(
                            "Erro", f"Data do serviço da linha {i + 1} não informado"
                        )
                        return False
                    if vaga_servico == 0:
                        messagebox.showerror(
                            "Erro", f"Vaga do serviço da linha {i + 1} não informado"
                        )
                        return False
                    if horario_servico == 0:
                        messagebox.showerror(
                            "Erro", f"Horario do serviço da linha {i + 1} não informado"
                        )
                        return False
                    if turno_servico == 0:
                        messagebox.showerror(
                            "Erro", f"Turno do serviço da linha {i + 1} não informado"
                        )
                        return False
                    is_servico_selecionado = True
            if not is_servico_selecionado:
                messagebox.showerror("Erro", f"Nenhum serviço informado!")
                return False

            return True

        def btn_abrir_site_click():
            adicionar_mensagem(self.text_area, f"Validando as informações...")
            self.janela_marcacao.update()  # Atualiza a janela para exibir a mensagem
            if validar_campos():
                info_marcacao = []
                info_usuario = {
                    "tipo_login": tipo_login,
                    "usuario": usuario,
                    "senha": senha,
                    "hora_limite": self.hora_limite,
                }
                adicionar_mensagem(
                    self.text_area, f"Salvando os registros para marcações..."
                )
                self.janela_marcacao.update()  # Atualiza a janela para exibir a mensagem
                for index in range(7):
                    if self.convenio_vars[index].get():
                        # Adicionar as informações à lista
                        info_marcacao.append(
                            {
                                "local_servico": self.variable_convenio[index].get(),
                                "tipo_filtro": 1,
                                "data_servico": self.variable_data_servico[index].get(),
                                "hora_servico": self.variable_horario_servico[
                                    index
                                ].get(),
                                "setor_servico": self.variable_vagas_convenio[
                                    index
                                ].get(),
                                "turno_servico": self.variable_turno_servico[
                                    index
                                ].get(),
                            }
                        )
                    elif self.cpa_vars[index].get():
                        # Adicionar as informações à lista
                        info_marcacao.append(
                            {
                                "local_servico": self.variable_cpa[index].get(),
                                "tipo_filtro": 2,
                                "data_servico": self.variable_data_servico[index].get(),
                                "hora_servico": self.variable_horario_servico[
                                    index
                                ].get(),
                                "setor_servico": self.variable_vaga_servico[
                                    index
                                ].get(),
                                "turno_servico": self.variable_turno_servico[
                                    index
                                ].get(),
                                "localxcpa_servico": self.variable_locais_cpa[
                                    index
                                ].get(),
                            }
                        )

                adicionar_mensagem(self.text_area, f"Abrindo a página do site...")
                self.janela_marcacao.update()  # Atualiza a janela para exibir a mensagem
                acessar_site(
                    info_marcacao, info_usuario, self.text_area, self.janela_marcacao
                )

        # Obtém a largura e altura da tela
        screen_width = self.janela_marcacao.winfo_screenwidth()
        screen_height = self.janela_marcacao.winfo_screenheight()

        # Ajusta a geometria da janela para preencher toda a tela
        self.janela_marcacao.geometry(f"{screen_width}x{screen_height}")

        # Variáveis para a criação dos componentes
        row = 0
        column = 0

        # OptionMenu para tipo de identificação
        tipo_identificacao = StringVar()
        tipo_identificacao.set(OPTIONS_IDENTIFICACAO[0])  # Valor padrão
        tk.Label(self.janela_marcacao, text="Tipo de Login:").grid(
            column=4, row=row, padx=5, pady=5, sticky="w"
        )
        option_identificacao = OptionMenu(
            self.janela_marcacao, tipo_identificacao, *OPTIONS_IDENTIFICACAO
        )
        option_identificacao.grid(column=5, row=row, padx=5, pady=5)
        option_identificacao.config(width=20)

        row += 1

        # Validação para garantir que o usuário seja apenas números
        vcmd = (self.janela_marcacao.register(validar_entrada), "%P")

        # Label e Entry para Usuário
        tk.Label(self.janela_marcacao, text="Usuário:").grid(
            column=4, row=row, padx=5, pady=5, sticky="w"
        )
        entry_usuario = tk.Entry(
            self.janela_marcacao, validate="key", validatecommand=vcmd, width=26
        )
        entry_usuario.grid(column=5, row=row, padx=5, pady=5)

        row += 1

        # Label e Entry para Senha
        tk.Label(self.janela_marcacao, text="Senha:").grid(
            column=4, row=row, padx=5, pady=5, sticky="w"
        )
        entry_senha = tk.Entry(self.janela_marcacao, show="*", width=26)
        entry_senha.grid(column=5, row=row, padx=5, pady=5)

        row += 1

        # Criação do OptionMenu para horário de marcação
        tk.Label(self.janela_marcacao, text="Horário de marcação:").grid(
            column=4, row=row, padx=5, pady=5, sticky="w"
        )
        variable_horariomarcacao = StringVar(self.janela_marcacao)
        variable_horariomarcacao.set(OPTIONS_HORAMARCACAO[0])

        # OptionMenu para horário de marcação
        w_horariomarcacao = OptionMenu(
            self.janela_marcacao,
            variable_horariomarcacao,
            *OPTIONS_HORAMARCACAO,
            command=update_hora_limite,
        )
        w_horariomarcacao.grid(column=5, row=row, padx=5, pady=5)
        w_horariomarcacao.config(width=20)

        row += 1

        # Criação dos checkbuttons e OptionMenus para os convênios
        for i in range(7):
            self.convenio_vars.append(IntVar())
            convenio_check = Checkbutton(
                self.janela_marcacao,
                text="Convênio:",
                onvalue=1,
                offvalue=0,
                variable=self.convenio_vars[i],
            )
            convenio_check.grid(column=column, row=row, padx=(5, 2), pady=5, sticky="w")
            self.checkbuttons_convenio.append(convenio_check)
            convenio_check.config(
                command=lambda index=i: on_checkbox_click(index, True)
            )
            column += 1

            self.variable_convenio.append(StringVar(self.janela_marcacao))
            self.variable_convenio[i].set(OPTIONS_CONVENIO[0])
            w_convenio = OptionMenu(
                self.janela_marcacao,
                self.variable_convenio[i],
                *OPTIONS_CONVENIO,
                command=lambda value, idx=i: update_locais_convenio(value, idx),
            )
            w_convenio.config(state="disabled")
            w_convenio.grid(column=column, row=row, padx=(5, 2), pady=5, sticky="w")
            self.select_convenio.append(w_convenio)

            column += 1

            self.variable_vagas_convenio.append(StringVar(self.janela_marcacao))
            self.variable_vagas_convenio[i].set("Selecione uma vaga")
            w_vagas_convenio = OptionMenu(
                self.janela_marcacao, self.variable_vagas_convenio[i], ""
            )
            w_vagas_convenio.config(state="disabled")
            w_vagas_convenio.grid(column=column, row=row, padx=5, pady=5)
            self.select_vagas_convenio.append(w_vagas_convenio)

            column += 1

            self.cpa_vars.append(IntVar())
            cpa_check = Checkbutton(
                self.janela_marcacao,
                text="CPA: ",
                onvalue=1,
                offvalue=0,
                variable=self.cpa_vars[i],
            )
            cpa_check.grid(column=column, row=row, padx=5, pady=5)
            self.checkbuttons_cpa.append(cpa_check)
            cpa_check.config(command=lambda index=i: on_checkbox_click(index, False))
            column += 1

            self.variable_cpa.append(StringVar(self.janela_marcacao))
            self.variable_cpa[i].set(OPTIONS_CPA[0])
            w_cpa = OptionMenu(
                self.janela_marcacao,
                self.variable_cpa[i],
                *OPTIONS_CPA,
                command=lambda value, idx=i: update_locais_cpa(value, idx),
            )
            w_cpa.config(state="disabled")
            w_cpa.grid(column=column, row=row, padx=5, pady=5)
            self.select_cpa.append(w_cpa)

            column += 1

            self.variable_locais_cpa.append(StringVar(self.janela_marcacao))
            self.variable_locais_cpa[i].set("Selecione o local")
            w_locaiscpa = OptionMenu(
                self.janela_marcacao, self.variable_locais_cpa[i], ""
            )
            w_locaiscpa.config(state="disabled")
            w_locaiscpa.grid(column=column, row=row, padx=5, pady=5)
            self.select_locais_cpa.append(w_locaiscpa)

            column += 1

            self.variable_vaga_servico.append(StringVar(self.janela_marcacao))
            self.variable_vaga_servico[i].set("Selecione uma vaga")
            w_vaga = OptionMenu(
                self.janela_marcacao,
                self.variable_vaga_servico[i],
                *OPTIONS_VAGASXLOCAIS_CPA,
            )
            w_vaga.config(state="disabled")
            w_vaga.grid(column=column, row=row, padx=5, pady=5)
            self.select_vagas_locais_cpa.append(w_vaga)

            column += 1

            self.variable_data_servico.append(StringVar(self.janela_marcacao))
            self.variable_data_servico[i].set(data[0])
            w_data = OptionMenu(
                self.janela_marcacao, self.variable_data_servico[i], *data
            )
            w_data.grid(column=column, row=row, padx=5, pady=5)

            column += 1

            self.variable_horario_servico.append(StringVar(self.janela_marcacao))
            self.variable_horario_servico[i].set(OPTIONS_HORARIO[0])
            w_horario = OptionMenu(
                self.janela_marcacao, self.variable_horario_servico[i], *OPTIONS_HORARIO
            )
            w_horario.grid(column=column, row=row, padx=5, pady=5)

            column += 1

            self.variable_turno_servico.append(StringVar(self.janela_marcacao))
            self.variable_turno_servico[i].set(OPTIONS_TURNOSERVICO[0])
            w_turnoservico = OptionMenu(
                self.janela_marcacao,
                self.variable_turno_servico[i],
                *OPTIONS_TURNOSERVICO,
            )
            w_turnoservico.grid(column=column, row=row, padx=5, pady=5)

            row += 1
            column = 0

        # Botão para iniciar a marcação
        btn_abrir_siste = Button(
            self.janela_marcacao, text="Iniciar marcação", command=btn_abrir_site_click
        )
        btn_abrir_siste.grid(column=5, row=row, padx=10, pady=10)

        row += 1

        # Área de texto para exibir mensagens
        self.text_area = Text(self.janela_marcacao, height=10, width=100, wrap=tk.WORD)
        self.text_area.grid(
            row=row, column=0, padx=10, pady=10, sticky="nsew", columnspan=11
        )

    def start(self):
        self.janela_marcacao.mainloop()
