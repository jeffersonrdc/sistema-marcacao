from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import base64
import re
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, NoSuchElementException, \
    InvalidSelectorException, WebDriverException
from selenium.common.exceptions import StaleElementReferenceException
from identificadores import *
from selenium.webdriver.chrome.service import Service
from tkinter import *
import tkinter as tk
from tkinter import font as tkfont
import pandas as pd
from datetime import datetime, date
import time as t
from dateutil.relativedelta import relativedelta, SU
import pytesseract
import cv2
import numpy as np
import os

# Uso de Condições de Espera

# presence_of_element_located: Aguarda até que o elemento esteja presente no DOM.
# visibility_of_element_located: Aguarda até que o elemento esteja presente no DOM e visível.
# element_to_be_clickable: Aguarda até que o elemento esteja presente, visível e clicável.
# Usar essas práticas ajudará a evitar exceções como NoSuchElementException e
# ElementNotInteractableException, garantindo que seu script aguarde adequadamente até que os elementos estejam
# prontos para interação.

timeout = 60


def acessar_site():
    # # Configuração do Chrome em modo headless
    # chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Executar em modo headless
    #
    # # Configuração do WebDriver
    # navegador = webdriver.Chrome(options=chrome_options)
    try:
        navegador = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    except Exception as e:
        print("Erro ao usar ChromeDriverManager:", e)
        # Caminho para o executável do ChromeDriver baixado manualmente
        chrome_driver_path = r"C:\Program Files\chromedriver\chromedriver.exe"
        navegador = webdriver.Chrome(service=Service(chrome_driver_path))
    navegador.maximize_window()

    # Conectar ao DevTools e simular a rede 3G
    # navegador.execute_cdp_cmd("Network.enable", {})
    # navegador.execute_cdp_cmd("Network.emulateNetworkConditions", {
    #     "offline": False,
    #     "latency": 100,  # Latência em milissegundos
    #     "downloadThroughput": 350 * 1024 / 8,  # Taxa de download em bytes por segundo (350 kbps)
    #     "uploadThroughput": 110 * 1024 / 8  # Taxa de upload em bytes por segundo (100 kbps)
    # })

    # navegador.implicitly_wait(1)
    link = "http://www.proeis.rj.gov.br/"
    navegador.get(link)

    select = Select(WebDriverWait(navegador, timeout).until(
        ec.element_to_be_clickable((By.ID, 'ddlTipoAcesso'))
    ))

    select.select_by_value(tipo_login)

    WebDriverWait(navegador, timeout).until(
        ec.element_to_be_clickable((By.ID, 'txtLogin'))
    ).send_keys(usuario)
    WebDriverWait(navegador, timeout).until(
        ec.element_to_be_clickable((By.ID, 'txtSenha'))
    ).send_keys(senha)
    # print(navegador.page_source)

    # Encontrar o campo de entrada
    input_field = WebDriverWait(navegador, timeout).until(
        ec.element_to_be_clickable((By.ID, 'TextCaptcha'))
    )
    input_field.click()

    texto = None
    while texto is None:
        imagem = gera_imagem_captcha_login(navegador)
        texto = resolver_captcha(imagem)
        if len(texto) >= 6:
            navegador.find_element(By.NAME, 'TextCaptcha').send_keys(texto)
            if is_visible(navegador):
                navegador.find_element(By.ID, 'txtSenha').send_keys(senha)
                navegador.find_element(By.NAME, 'TextCaptcha').clear()
                navegador.find_element(By.NAME, 'TextCaptcha').click()
                texto = None
        else:
            WebDriverWait(navegador, 3).until(ec.presence_of_element_located(
                (By.ID, 'lnkNewCaptcha'))).click()
            texto = None

    adicionar_mensagem(f"Aguardando usuário digitar o captcha...")
    janela.update()  # Atualiza a janela para exibir a mensagem

    # while True:
    #     try:
    #         input_field = WebDriverWait(navegador, timeout).until(
    #             ec.element_to_be_clickable((By.ID, 'TextCaptcha')))
    #         input_field.click()
    #         if check_input(input_field):
    #             # Encontrar e clicar no botão de login
    #             # navegador.find_element(By.ID, 'btnEntrar').click()
    #             WebDriverWait(navegador, timeout).until(
    #                 ec.element_to_be_clickable((By.ID, 'btnEntrar'))
    #             ).click()
    #             if is_visible(navegador):
    #                 adicionar_mensagem(f"captcha digitado é inválido, digite novamente!")
    #                 janela.update()  # Atualiza a janela para exibir a mensagem
    #                 # Manter o foco no campo de entrada se o texto for inválido
    #                 WebDriverWait(navegador, timeout).until(
    #                     ec.element_to_be_clickable((By.ID, 'txtSenha'))
    #                 ).send_keys(senha)
    #
    #                 WebDriverWait(navegador, timeout).until(
    #                     ec.element_to_be_clickable((By.ID, 'TextCaptcha'))).clear()
    #                 WebDriverWait(navegador, timeout).until(
    #                     ec.element_to_be_clickable((By.ID, 'TextCaptcha'))).click()
    #             else:
    #                 adicionar_mensagem(f"Login OK! Abrindo a página inicial...")
    #                 janela.update()  # Atualiza a janela para exibir a mensagem
    #                 break
    #     except StaleElementReferenceException:
    #         # Ignorar e continuar o loop se o elemento estiver obsoleto
    #         pass
    nova_inscricao(navegador)


def nova_inscricao(navegador_param):
    adicionar_mensagem(f"Abrindo a página de marcação...")
    janela.update()  # Atualiza a janela para exibir a mensagem
    # navegador_param.find_element(By.ID, 'btnEscala').click()
    WebDriverWait(navegador_param, timeout).until(
        ec.element_to_be_clickable((By.ID, 'btnEscala'))).click()
    pesquisar_vaga(navegador_param)


def pesquisar_vaga(navegador_param):
    current_time = datetime.now().time()
    if current_time < datetime.strptime("06:00:00", "%H:%M:%S").time():
        adicionar_mensagem(f"Aguardando o horário para iniciar a marcação do RAS...")
        janela.update()  # Atualiza a janela para exibir a mensagem
        while True:
            current_time = datetime.now().time()
            if current_time >= datetime.strptime("06:00:00", "%H:%M:%S").time():
                WebDriverWait(navegador_param, timeout).until(
                    ec.element_to_be_clickable((By.ID, 'btnNovaInscricao'))).click()
                break
    else:
        WebDriverWait(navegador_param, timeout).until(
            ec.element_to_be_clickable((By.ID, 'btnNovaInscricao'))).click()
    tentativa = 0
    for informacao in informacoes_array:
        if tentativa > 0:
            is_alert(navegador_param)

        # SELECIONA A DATA
        select_data_evento = None
        tentativa = 1
        while not select_data_evento:
            try:
                select_data_evento = Select(WebDriverWait(navegador_param, timeout).until(ec.element_to_be_clickable(
                    (By.ID, 'ddlDataEvento'))))  # METODO QUE AGUARDA ATÉ X SEGUNDOS O ID SER CARREGADO NA PÁGINA
                select_data_evento.select_by_visible_text(informacao['data_servico'])
            except StaleElementReferenceException:
                select_data_evento = None
                print(f"Erro ao selecionar Data do evento: {tentativa}")
                tentativa = tentativa + 1

            # ________________________________________________________________________________________________________________________________________________________________#

        # CLICA NO LINK PARA EXIBIR O CAPTCHA
        adicionar_mensagem(f"Abrindo imagem do captcha, aguarde...")
        janela.update()  # Atualiza a janela para exibir a mensagem
        abri_captcha_click = None
        while not abri_captcha_click:
            try:
                abri_captcha_click = WebDriverWait(navegador_param, timeout).until(
                    ec.element_to_be_clickable((By.ID, 'lnkNewCaptcha')))
                if abri_captcha_click is not None:
                    abri_captcha_click.click()

                    while verifica_captcha_vaga_visivel(navegador_param):
                        break

                    adicionar_mensagem(f"Imagem do captcha aberta!")
                    janela.update()  # Atualiza a janela para exibir a mensagem

            except ElementClickInterceptedException:
                abri_captcha_click = None
                print(f"Erro ElementClickInterceptedException ao clicar para exibir imagem do captcha.")
            except StaleElementReferenceException:
                abri_captcha_click = None
                print(
                    f"Erro StaleElementReferenceException ao localizar elemento para clicar e exibir imagem do "
                    f"captcha.")

        # ________________________________________________________________________________________________________________________________________________________________#

        # SELECIONA A VAGA PELO CONVÊNIO
        if informacao['tipo_filtro'] == 1:
            select_convenio = None
            tentativa = 1
            while not select_convenio:
                try:
                    select_convenio = Select(WebDriverWait(navegador_param, timeout).until(ec.element_to_be_clickable(
                        (By.ID, 'ddlConvenios'))))  # METODO QUE AGUARDA ATÉ X SEGUNDOS O ID SER CARREGADO NA PÁGINA
                    select_convenio.select_by_visible_text(informacao['local_servico'])  # CARREGA PELA DESCRIÇÃO
                except StaleElementReferenceException:
                    select_convenio = None
                    print(f"Erro ao selecionar convênio: {tentativa}")
                    tentativa = tentativa + 1

        # SELECIONA A VAGA PELO CPA
        else:
            select_cpa = None
            tentativa = 1
            while not select_cpa:
                try:
                    select_cpa = Select(WebDriverWait(navegador_param, timeout).until(ec.element_to_be_clickable(
                        (By.ID, 'ddlCPAS'))))  # METODO QUE AGUARDA ATÉ X SEGUNDOS O ID SER CARREGADO NA PÁGINA
                    select_cpa.select_by_visible_text(informacao['local_servico'])  # CARREGA PELA DESCRIÇÃO
                except StaleElementReferenceException:
                    select_cpa = None
                    print(f"Erro ao selecionar CPA: {tentativa}")
                    tentativa = tentativa + 1

        tentativa = 1
        is_ok = False
        while not is_ok:
            try:
                # print(navegador.page_source)
                # Usar XPath para encontrar o campo de entrada
                input_field = WebDriverWait(navegador_param, timeout).until(
                    ec.element_to_be_clickable((By.XPATH, '//*[@id="TextCaptcha"]'))
                )
                input_field.clear()
                input_field.click()

                # Loop para monitorar continuamente a entrada e a hora
                tentativa = 1
                while True:
                    try:
                        current_time = datetime.now().time()
                        if current_time < datetime.strptime("07:00:00", "%H:%M:%S").time():
                            adicionar_mensagem(f"Aguardando o horário para iniciar a marcação do Proeis...")
                            janela.update()  # Atualiza a janela para exibir a mensagem
                        imagem = gera_imagem_captcha_vaga(navegador_param)
                        texto_captcha = resolver_captcha(imagem)
                        navegador_param.find_element(By.ID, 'TextCaptcha').send_keys(texto_captcha)
                        WebDriverWait(navegador_param, timeout).until(
                                                        ec.element_to_be_clickable((By.ID, 'btnConsultar'))).click()
                        while verifica_local_visivel(navegador_param):
                            break
                        alert = is_alert(navegador_param)
                        if alert == 0:
                            is_ok = True
                            break
                        else:
                            adicionar_mensagem(f"captcha é inválido, irei tentar novamente!")
                            janela.update()  # Atualiza a janela para exibir a mensagem


                        # input_field = WebDriverWait(navegador_param, timeout).until(
                        #     ec.element_to_be_clickable((By.XPATH, '//*[@id="TextCaptcha"]'))
                        # )
                        # current_time = datetime.now().time()
                        # if current_time < datetime.strptime("07:00:00", "%H:%M:%S").time():
                        #     adicionar_mensagem(f"Aguardando o horário para iniciar a marcação do Proeis...")
                        #     janela.update()  # Atualiza a janela para exibir a mensagem
                        # if check_input_and_time(input_field, hora_limite):
                        #     # Encontrar e clicar no botão de login
                        #     WebDriverWait(navegador_param, timeout).until(
                        #         ec.element_to_be_clickable((By.ID, 'btnConsultar'))).click()
                        #     while verifica_local_visivel(navegador_param):
                        #         break
                        #     alert = is_alert(navegador_param)
                        #     if alert == 0:
                        #         is_ok = True
                        #         break
                        #     else:
                        #         adicionar_mensagem(f"captcha digitado é inválido, digite novamente!")
                        #         janela.update()  # Atualiza a janela para exibir a mensagem
                    except StaleElementReferenceException:
                        print(f"Erro ao clicar no elemento para consultar as vagas: {tentativa}")
                        tentativa += 1
                        # Esperar por um curto período para evitar uso excessivo de CPU
            except Exception:
                print(f"Erro ao clicar no elemento para digitar o captcha. Tentavia {tentativa}")
                tentativa += 1
                if tentativa > 5:  # Número máximo de tentativas
                    print("Número máximo de tentativas atingido. Saindo...")
                    navegador_param.quit()
                    break

        if informacao['tipo_filtro'] == 2:
            tentativa = 1
            convenio_xcpa = None
            while not convenio_xcpa:
                try:
                    convenio_xcpa = WebDriverWait(navegador_param, timeout).until(ec.element_to_be_clickable(
                        (By.LINK_TEXT,
                         f"{informacao['localxcpa_servico']}")))  # METODO QUE AGUARDA ATÉ X SEGUNDOS O ID SER CARREGADO
                    # NA PÁGINA
                except StaleElementReferenceException:
                    print(f"Erro ao clicar no elemento de escolha do local onde possui os serviços: {tentativa}")
                    tentativa += 1

            # while verifica_local_visivel(navegador_param):
            #     break

            navegador_param.execute_script("arguments[0].click();", convenio_xcpa)
        # else:
        #     while verifica_local_visivel(navegador_param):
        #         break
        tentativa = 1

        while verifica_vaga_visivel(navegador_param):
            break

        while True:
            xpath_evento = f"//td[text()='{informacao['setor_servico']}' and following-sibling::td[text()='{informacao['hora_servico']}'] and following-sibling::td[text()='{informacao['turno_servico']}']]/following-sibling::td[@class='btnCollumn']/a"
            try:
                elementos_evento = WebDriverWait(navegador_param, 20).until(
                    ec.element_to_be_clickable((By.XPATH, xpath_evento))
                )

                # Verificar se o elemento é clicável e clicar nele
                if elementos_evento.is_displayed() and elementos_evento.is_enabled():
                    navegador_param.execute_script("arguments[0].click();", elementos_evento)
                    is_alert(navegador_param, 20)
                    adicionar_mensagem(f"Setor {informacao['setor_servico']} no dia {informacao['data_servico'][8:10]}/{informacao['data_servico'][5:7]}/{informacao['data_servico'][0:4]} às {informacao['hora_servico']} marcado com sucesso!")
                    janela.update()  # Atualiza a janela para exibir a mensagem
                    break
            except TimeoutException:
                print(f"Erro ao clicar no elemento de marcação da vaga: {tentativa}")
                tentativa += 1
                if tentativa > 5:  # Número máximo de tentativas
                    print("Número máximo de tentativas atingido. Saindo...")
                    break
            except WebDriverException as e:
                print(f"Erro ao clicar no elemento de marcação da vaga: {tentativa} - {str(e)}")
                tentativa += 1
                if tentativa > 5:  # Número máximo de tentativas
                    print("Número máximo de tentativas atingido. Saindo...")
                    break
        # ________________________________________________________________________________________________________________________________________________________________#

    # FECHA O NAVEGADOR AO TERMINAR DE INSERIR AS VAGAS
    adicionar_mensagem(f"Marcações finalizadas, fechando o navegador em 30 segundos...")
    janela.update()  # Atualiza a janela para exibir a mensagem
    t.sleep(30)
    navegador_param.quit()


# Função para verificar o comprimento da entrada
def check_input_and_time(input_field, hora_limite_param):
    current_time = datetime.now().time()
    input_value = input_field.get_attribute('value')
    return len(input_value) >= 6 and current_time >= datetime.strptime(hora_limite_param, "%H:%M:%S").time()


def check_input(input_field):
    input_value = input_field.get_attribute('value')
    return len(input_value) >= 6


def resolver_captcha(caminho_imagem_origem):
    # Leitura da imagem
    imagem = cv2.imread(caminho_imagem_origem)

    if imagem is None:
        print(f"Erro ao ler a imagem: {caminho_imagem_origem}")

    # Conversão para escala de cinza
    imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

    # Aplicação de uma operação de morfologia para remover ruídos
    kernel = np.ones((2, 2), np.uint8)
    imagem_morf = cv2.morphologyEx(imagem_cinza, cv2.MORPH_CLOSE, kernel)

    # Aplicação de um método de limiarização
    _, imagem_tratada = cv2.threshold(imagem_morf, 127, 255, cv2.THRESH_BINARY or cv2.THRESH_OTSU)

    # Caminho para o executável do Tesseract (necessário apenas no Windows)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # Determinar o caminho absoluto para o diretório tessdata
    caminho_tessdata = os.path.join(os.getcwd(), 'tessdata')

    # Configuração do diretório tessdata para Tesseract no Windows
    config_tessdata = f'--tessdata-dir "{caminho_tessdata}" --psm 7 -c tessedit_char_whitelist=0123456789aAbBcCdDeEfFgG'
    texto = pytesseract.image_to_string(imagem_tratada, lang='por', config=config_tessdata)  # 'por' para português

    return texto


def verifica_captcha_vaga_visivel(navegador_param):
    try:
        WebDriverWait(navegador_param, timeout).until(
            ec.presence_of_element_located(
                (By.XPATH, "//div[contains(@style, 'width: 300px; height: 91px; background: url')]")))
    except InvalidSelectorException:
        return False

    return True


def verifica_local_visivel(navegador_param):
    try:
        WebDriverWait(navegador_param, timeout).until(
            ec.invisibility_of_element_located((By.ID, 'aguarde'))
        )
    except TimeoutException:
        return False
    except NoSuchElementException:
        return False
    except InvalidSelectorException:
        return False

    return True


def verifica_vaga_visivel(navegador_param):
    try:
        elemento = WebDriverWait(navegador_param, timeout).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "div[role='status'][aria-hidden='true']"))
        )
        style = elemento.get_attribute("style")
        if "display:none" in style:
            return False
        else:
            return True
    except TimeoutException:
        return False
    except NoSuchElementException:
        return False


def is_dialog_invisible(navegador_param):
    try:
        elemento = WebDriverWait(navegador_param, 1).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "div[role='status'][aria-hidden='true']"))
        )
        style = elemento.get_attribute("style")
        if "display:none" in style:
            return True
        else:
            return False
    except TimeoutException:
        return False
    except NoSuchElementException:
        return False


def gera_imagem_captcha_login(navegador_param):
    div = navegador_param.find_element(By.XPATH, '//*[@id="captcha"]/div')
    bg_url = div.value_of_css_property('background')
    bg_url = re.split('[()]', bg_url)[3]
    bg_url = bg_url[23:]

    image_path = "imagelogin.png"
    with open("imagelogin.png", "wb") as fh:
        fh.write(base64.urlsafe_b64decode(bg_url))

    return image_path


def gera_imagem_captcha_vaga(navegador_param):
    div = None
    bg_url = None
    while not div:
        try:
            div = navegador_param.find_element(By.XPATH, '//*[@id="captcha"]/div')
            bg_url = div.value_of_css_property('background')
            bg_url = re.split('[()]', bg_url)[3]
            bg_url = bg_url[23:]

        except NoSuchElementException:
            ""
    image_path = "imagevaga.png"
    with open(image_path, "wb") as fh:
        fh.write(base64.urlsafe_b64decode(bg_url))

    return image_path


def is_alert(navegador_param, timeoutalert=1):
    try:
        alert = WebDriverWait(navegador_param, timeoutalert).until(ec.alert_is_present())
        if alert is not None:
            alert.accept()
            return 1
    except Exception as err:
        print(f"retrying after {type(err)}: {err}")

    return 0


def is_visible(navegador_param):
    try:
        erro_captcha = WebDriverWait(navegador_param, 0).until(ec.presence_of_element_located(
            (By.ID, 'lblLogin')))
        if erro_captcha.is_displayed():
            return True
        else:
            return False
    except TimeoutException:
        return False


def adicionar_mensagem(mensagem):
    text_area.config(state=tk.NORMAL)  # Habilita a edição do Text
    text_area.insert(tk.END, mensagem + "\n")  # Adiciona mensagem ao final
    text_area.config(state=tk.DISABLED)  # Desabilita a edição do Text
    text_area.see(tk.END)  # Rolagem automática para a última mensagem


# Função para criar o efeito de alto relevo
def create_embossed_frame(parent, row, column, bg_color="lightgray", bd=3, padx=5, pady=5):
    frame = tk.Frame(parent, bg=bg_color, relief="raised", bd=bd)
    frame.grid(row=row, column=column, padx=padx, pady=pady, sticky="nsew")

    # Configuração para centralizar os widgets dentro do frame
    # frame.pack_propagate(False)  # Impede que o frame se expanda para ajustar o conteúdo
    # frame.grid_rowconfigure(0, weight=1)  # Ajusta o peso da única linha do frame
    frame.grid_columnconfigure(0, weight=1)  # Ajusta o peso da única coluna do frame

    return frame


# Criar uma lista vazia para armazenar as informações
# informacoes_array = []

# Definindo a variável global no nível do módulo
janela = None
usuario = None
senha = None
tipo_login = None
hora_limite = None
text_area = None


def abrir_janela():
    global janela
    janela = Tk()
    janela.title('Sistema de Marcação')
    # Obtém a largura e altura da tela
    screen_width = janela.winfo_screenwidth()
    screen_height = janela.winfo_screenheight()

    # Ajusta a geometria da janela para preencher toda a tela
    janela.geometry(f"{screen_width}x{screen_height}")

    # Verificar se hoje é quinta-feira
    today = date.today()
    if today.weekday() == 3:  # 3 representa quinta-feira
        second_sunday = today + relativedelta(weekday=SU(1)) + relativedelta(weeks=1)
        periods = (second_sunday - today).days + 1
    else:  # Se hoje for antes de quinta-feira (segunda a quarta)
        next_sunday = today + relativedelta(weekday=SU(1))
        periods = (next_sunday - today).days + 1

    # Gerar a lista de datas
    list_of_date = pd.date_range(today, periods=periods)

    # Converter as datas para strings e adicionar à lista de opções
    data = ["Selecione a data"] + [str(day.date()) for day in list_of_date]

    i = 1
    row = 0
    column = 0

    convenio_vars = []
    cpa_vars = []
    checkbuttons_convenio = []
    checkbuttons_cpa = []
    select_convenio = []
    select_vagas_convenio = []
    select_cpa = []
    select_locais_cpa = []
    select_vagas_locais_cpa = []
    variable_convenio = []
    variable_vagas_convenio = []
    variable_cpa = []
    variable_locais_cpa = []
    variable_data_servico = []
    variable_vaga_servico = []
    variable_horario_servico = []
    variable_turno_servico = []

    # Função para adicionar mensagem ao Text
    def adicionar_mensagem(mensagem):
        text_area.config(state=tk.NORMAL)  # Habilita a edição do Text
        text_area.insert(tk.END, mensagem + "\n")  # Adiciona mensagem ao final
        text_area.config(state=tk.DISABLED)  # Desabilita a edição do Text
        text_area.see(tk.END)  # Rolagem automática para a última mensagem

    # Exemplo de uso da função de validação
    def validar_campos():
        global usuario, senha, tipo_login

        tipo_login = OPTIONS_IDENTIFICACAO.index(tipo_identificacao.get())
        if tipo_login == 0:
            show_alert("Erro", "Informe o tipo de login")
            return False
        else:
            if tipo_login == 1:
                tipo_login = "CPF"
            else:
                tipo_login = "ID"

        usuario = entry_usuario.get()
        senha = entry_senha.get()
        if not usuario or not senha:
            show_alert("Erro", "Usuário e senha não podem ser vazios.")
            return False

        if OPTIONS_IDENTIFICACAO.index(tipo_identificacao.get()) == 1 and len(usuario) != 11:
            show_alert("Erro", "Login do tipo CPF, o usuário deve ter exatamente 11 caracteres.")
            return False

        horario_maracacao = OPTIONS_HORAMARCACAO.index(variable_horariomarcacao.get())
        if horario_maracacao == 0:
            show_alert("Erro", "Informe o horário da marcação")
            return False
        is_servico_selecionado = False
        for i in range(7):
            data_servico = data.index(variable_data_servico[i].get())
            horario_servico = OPTIONS_HORARIO.index(variable_horario_servico[i].get())
            turno_servico = OPTIONS_TURNOSERVICO.index(variable_turno_servico[i].get())
            if convenio_vars[i].get():
                indice_convenio = OPTIONS_CONVENIO.index(variable_convenio[i].get())
                convenio = OPTIONS_VAGASXCONVENIO[variable_convenio[i].get()]
                vaga_convenio = convenio.index(variable_vagas_convenio[i].get())
                if indice_convenio == 0:
                    show_alert("Erro", f"Convênio da linha {i + 1} não informado")
                    return False
                if vaga_convenio == 0:
                    show_alert("Erro", f"Vaga do convênio da linha {i + 1} não informado")
                    return False
                if data_servico == 0:
                    show_alert("Erro", f"Data do serviço da linha {i + 1} não informado")
                    return False
                if horario_servico == 0:
                    show_alert("Erro", f"Horario do serviço da linha {i + 1} não informado")
                    return False
                if turno_servico == 0:
                    show_alert("Erro", f"Turno do serviço da linha {i + 1} não informado")
                    return False
                is_servico_selecionado = True
            elif cpa_vars[i].get():
                cpa = OPTIONS_CPA.index(variable_cpa[i].get())
                if cpa == 0:
                    show_alert("Erro", f"CPA da linha {i + 1} não informado")
                    return False
                locais_cpa = OPTIONS_LOCAISXCPA[variable_cpa[i].get()]
                indice_local_selecionado = locais_cpa.index(variable_locais_cpa[i].get())
                local_selecionado = OPTIONS_VAGASXLOCAIS_CPA[variable_locais_cpa[i].get()]
                vaga_servico = local_selecionado.index(variable_vaga_servico[i].get())
                if indice_local_selecionado == 0:
                    show_alert("Erro", f"Local da linha {i + 1} não informado")
                    return False
                if data_servico == 0:
                    show_alert("Erro", f"Data do serviço da linha {i + 1} não informado")
                    return False
                if vaga_servico == 0:
                    show_alert("Erro", f"Vaga do serviço da linha {i + 1} não informado")
                    return False
                if horario_servico == 0:
                    show_alert("Erro", f"Horario do serviço da linha {i + 1} não informado")
                    return False
                if turno_servico == 0:
                    show_alert("Erro", f"Turno do serviço da linha {i + 1} não informado")
                    return False
                is_servico_selecionado = True
        if not is_servico_selecionado:
            show_alert("Erro", f"Nenhum serviço informado!")
            return False

        return True

    def show_alert(title, message):
        alert_window = tk.Toplevel(janela)
        alert_window.title(title)

        # Calcula a largura e altura da mensagem
        default_font = tkfont.Font()
        message_width = default_font.measure(message) + 20  # Adiciona padding

        # Conta o número de linhas na mensagem
        lines = message.count("\n") + 1
        message_height = default_font.metrics("linespace") * lines + 80  # Adiciona espaço para botões

        # Calcula as coordenadas para centralizar a janela de alerta
        janela.update_idletasks()
        x = (janela.winfo_screenwidth() // 2) - (message_width // 2)
        y = (janela.winfo_screenheight() // 2) - (message_height // 2)

        # Configura a geometria da janela de alerta para centralizá-la
        alert_window.geometry(f'{message_width}x{message_height}+{x}+{y}')

        tk.Label(alert_window, text=message).pack(padx=10, pady=10)
        tk.Button(alert_window, text="OK", command=alert_window.destroy).pack(pady=10)

    # Função de callback para checkboxes de Convênio e CPA
    def on_checkbox_click(index, is_convenio):
        if is_convenio:
            if convenio_vars[index].get() == 1:
                cpa_vars[index].set(0)  # Desativa a checkbox de CPA
                select_convenio[index].config(state='normal')
                select_vagas_convenio[index].config(state='normal')
                checkbuttons_cpa[index].config(state='disabled')
                select_cpa[index].config(state='disabled')
                select_locais_cpa[index].config(state='disabled')
                select_vagas_locais_cpa[index].config(state='disabled')
                variable_cpa[index].set(OPTIONS_CPA[0])  # Reseta o OptionMenu de CPA
            else:
                checkbuttons_cpa[index].config(state='normal')  # Ativa a checkbox de CPA
                variable_convenio[index].set(OPTIONS_CONVENIO[0])  # Reseta o OptionMenu de Convênio
                select_convenio[index].config(state='disabled')
                select_vagas_convenio[index].config(state='disabled')
                variable_vaga_servico[index].set("Selecione uma vaga")  # Reseta o OptionMenu de Convênio
        else:
            if cpa_vars[index].get() == 1:
                convenio_vars[index].set(0)  # Desativa a checkbox de Convênio
                checkbuttons_convenio[index].config(state='disabled')
                select_convenio[index].config(state='disabled')
                select_vagas_convenio[index].config(state='disabled')
                select_cpa[index].config(state='normal')
                select_vagas_locais_cpa[index].config(state='normal')
                variable_convenio[index].set(OPTIONS_CONVENIO[0])  # Reseta o OptionMenu de Convênio
                variable_vagas_convenio[index].set("Selecione uma vaga")  # Reseta o OptionMenu de Convênio
            else:
                checkbuttons_convenio[index].config(state='normal')  # Ativa a checkbox de Convênio
                variable_cpa[index].set(OPTIONS_CPA[0])  # Reseta o OptionMenu de CPA
                select_cpa[index].config(state='disabled')
                select_locais_cpa[index].config(state='disabled')
                select_vagas_locais_cpa[index].config(state='disabled')
                select_vagas_locais_cpa[index].config(state='disabled')
                variable_convenio[index].set(OPTIONS_CONVENIO[0])  # Reseta o OptionMenu de Convênio
                variable_locais_cpa[index].set("Selecione o local")  # Reseta o OptionMenu de Convênio
                variable_vaga_servico[index].set("Selecione uma vaga")  # Reseta o OptionMenu de Convênio

    def btn_abrir_site_click():
        adicionar_mensagem(f"Validando as informações...")
        janela.update()  # Atualiza a janela para exibir a mensagem
        if validar_campos():
            global informacoes_array
            informacoes_array = []
            adicionar_mensagem(f"Salvando os registros para marcações...")
            janela.update()  # Atualiza a janela para exibir a mensagem
            for index in range(7):
                if convenio_vars[index].get():
                    # Adicionar as informações à lista
                    informacoes_array.append({
                        'local_servico': variable_convenio[index].get(),
                        'tipo_filtro': 1,
                        'data_servico': variable_data_servico[index].get(),
                        'hora_servico': variable_horario_servico[index].get(),
                        'setor_servico': variable_vagas_convenio[index].get(),
                        'turno_servico': variable_turno_servico[index].get(),
                    })
                elif cpa_vars[index].get():
                    # Adicionar as informações à lista
                    informacoes_array.append({
                        'local_servico': variable_cpa[index].get(),
                        'tipo_filtro': 2,
                        'data_servico': variable_data_servico[index].get(),
                        'hora_servico': variable_horario_servico[index].get(),
                        'setor_servico': variable_vaga_servico[index].get(),
                        'turno_servico': variable_turno_servico[index].get(),
                        'localxcpa_servico': variable_locais_cpa[index].get()
                    })

            adicionar_mensagem(f"Abrindo a página do site...")
            janela.update()  # Atualiza a janela para exibir a mensagem
            acessar_site()

    def update_locais_cpa(texto, index):
        locais_options = OPTIONS_LOCAISXCPA.get(texto, [])
        variable_locais_cpa[index].set(locais_options[0] if locais_options else "Selecione um local")
        menu = select_locais_cpa[index]['menu']
        menu.delete(0, 'end')
        if len(locais_options) > 0:
            select_locais_cpa[index].config(state='normal')
            for local in locais_options:
                menu.add_command(label=local, command=lambda l=local, idx=index: (
                    variable_locais_cpa[idx].set(l),
                    update_vagas_locais_cpa(l, idx)
                ))
        else:
            variable_locais_cpa[index].set(
                locais_options[0] if locais_options else "Selecione um local")  # Reseta o OptionMenu de Locais do CPA
            select_locais_cpa[index].config(state='disabled')

    def update_vagas_locais_cpa(texto, index):
        vagas_options = OPTIONS_VAGASXLOCAIS_CPA.get(texto, [])
        variable_vaga_servico[index].set(vagas_options[0] if vagas_options else "Selecione um local")
        menu = select_vagas_locais_cpa[index]['menu']
        menu.delete(0, 'end')
        if len(vagas_options) > 0:
            select_vagas_locais_cpa[index].config(state='normal')
            for local in vagas_options:
                menu.add_command(label=local, command=lambda l=local: variable_vaga_servico[index].set(l))
        else:
            variable_vaga_servico[index].set(
                vagas_options[0] if vagas_options else "Selecione um local")  # Reseta o OptionMenu de Locais do CPA
            select_locais_cpa[index].config(state='disabled')

    def update_locais_convenio(texto, index):
        locais_options = OPTIONS_VAGASXCONVENIO.get(texto, [])
        variable_vagas_convenio[index].set(locais_options[0] if locais_options else "Selecione uma vaga")
        menu = select_vagas_convenio[index]['menu']
        menu.delete(0, 'end')

        for local in locais_options:
            menu.add_command(label=local, command=lambda l=local: variable_vagas_convenio[index].set(l))

    def search(event, options, combobox):
        value = event.widget.get()
        if value == '':
            combobox['values'] = options
        else:
            data = []
            for item in options:
                if value.lower() in item.lower():
                    data.append(item)
            combobox['values'] = data

    # Função para atualizar a variável hora_limite
    def update_hora_limite(value):
        global hora_limite
        hora_limite = value
        print(f"Hora limite selecionada: {hora_limite}")

    # Função para validar que o usuário é apenas números
    def validar_entrada(texto):
        return texto.isdigit() or texto == ""

    # OptionMenu para tipo de identificação
    tipo_identificacao = StringVar()
    tipo_identificacao.set(OPTIONS_IDENTIFICACAO[0])  # Valor padrão
    tk.Label(janela, text="Tipo de Login:").grid(column=4, row=row, padx=5, pady=5, sticky='w')
    option_identificacao = OptionMenu(janela, tipo_identificacao, *OPTIONS_IDENTIFICACAO)
    option_identificacao.grid(column=5, row=row, padx=5, pady=5)
    option_identificacao.config(width=20)  # Define um tamanho fixo para o OptionMenu

    row += 1

    # Validação para garantir que o usuário seja apenas números
    vcmd = (janela.register(validar_entrada), '%P')

    # Label e Entry para Usuário
    tk.Label(janela, text="Usuário:").grid(column=4, row=row, padx=5, pady=5, sticky='w')
    entry_usuario = tk.Entry(janela, validate="key", validatecommand=vcmd, width=26)
    entry_usuario.grid(column=5, row=row, padx=5, pady=5)

    row += 1

    # Label e Entry para Senha
    tk.Label(janela, text="Senha:").grid(column=4, row=row, padx=5, pady=5, sticky='w')
    entry_senha = tk.Entry(janela, show="*", width=26)
    entry_senha.grid(column=5, row=row, padx=5, pady=5)

    row += 1

    # Criação do OptionMenu para horário de marcação fora do loop
    tk.Label(janela, text="Horario de marcação:").grid(column=4, row=row, padx=5, pady=5, sticky='w')
    variable_horariomarcacao = StringVar(janela)
    variable_horariomarcacao.set(OPTIONS_HORAMARCACAO[0])
    hora_limite = OPTIONS_HORAMARCACAO[0]  # Inicializa hora_limite com o primeiro valor de OPTIONS_HORAMARCACAO

    # OptionMenu para horário de marcação
    w_horariomarcacao = OptionMenu(janela, variable_horariomarcacao, *OPTIONS_HORAMARCACAO, command=update_hora_limite)
    w_horariomarcacao.grid(column=5, row=row, padx=5, pady=5)
    w_horariomarcacao.config(width=20)  # Define um tamanho fixo para o OptionMenu

    row += 1
    # Cria um frame com efeito de alto relevo
    # embossed_frame_convenio = create_embossed_frame(janela, row, 0, padx=10, pady=10)
    # embossed_frame_cpa = create_embossed_frame(janela, row, 1, padx=10, pady=10)
    for i in range(7):
        convenio_vars.append(IntVar())
        convenio_check = Checkbutton(janela, text='Convênio:', onvalue=1, offvalue=0, variable=convenio_vars[i])
        convenio_check.grid(column=column, row=row, padx=5, pady=5)
        checkbuttons_convenio.append(convenio_check)
        convenio_check.config(command=lambda index=i: on_checkbox_click(index, True))
        column += 1

        variable_convenio.append(StringVar(janela))
        variable_convenio[i].set(OPTIONS_CONVENIO[0])
        w_convenio = OptionMenu(janela, variable_convenio[i], *OPTIONS_CONVENIO,
                                command=lambda value, idx=i: update_locais_convenio(value, idx))
        w_convenio.config(state='disabled')
        w_convenio.grid(column=column, row=row, padx=5, pady=5)
        select_convenio.append(w_convenio)

        column += 1

        variable_vagas_convenio.append(StringVar(janela))
        variable_vagas_convenio[i].set("Selecione uma vaga")
        w_vagas_convenio = OptionMenu(janela, variable_vagas_convenio[i], "")
        w_vagas_convenio.config(state='disabled')
        w_vagas_convenio.grid(column=column, row=row, padx=5, pady=5)
        select_vagas_convenio.append(w_vagas_convenio)
        column += 1

        cpa_vars.append(IntVar())
        cpa_check = Checkbutton(janela, text='CPA: ', onvalue=1, offvalue=0, variable=cpa_vars[i])
        cpa_check.grid(column=column, row=row, padx=5, pady=5)
        checkbuttons_cpa.append(cpa_check)
        cpa_check.config(command=lambda index=i: on_checkbox_click(index, False))
        column += 1

        variable_cpa.append(StringVar(janela))
        variable_cpa[i].set(OPTIONS_CPA[0])
        w_cpa = OptionMenu(janela, variable_cpa[i], *OPTIONS_CPA,
                           command=lambda value, idx=i: update_locais_cpa(value, idx))
        w_cpa.config(state='disabled')
        w_cpa.grid(column=column, row=row, padx=5, pady=5)
        select_cpa.append(w_cpa)
        column += 1

        variable_locais_cpa.append(StringVar(janela))
        variable_locais_cpa[i].set("Selecione o local")
        w_locaiscpa = OptionMenu(janela, variable_locais_cpa[i], "")
        w_locaiscpa.config(state='disabled')
        w_locaiscpa.grid(column=column, row=row, padx=5, pady=5)
        select_locais_cpa.append(w_locaiscpa)
        column += 1

        variable_vaga_servico.append(StringVar(janela))
        variable_vaga_servico[i].set("Selecione uma vaga")
        w_vaga = OptionMenu(janela, variable_vaga_servico[i], *OPTIONS_VAGASXLOCAIS_CPA)
        w_vaga.config(state='disabled')
        w_vaga.grid(column=column, row=row, padx=5, pady=5)
        select_vagas_locais_cpa.append(w_vaga)
        column += 1

        variable_data_servico.append(StringVar(janela))
        variable_data_servico[i].set(data[0])
        w_data = OptionMenu(janela, variable_data_servico[i], *data)
        w_data.grid(column=column, row=row, padx=5, pady=5)
        column += 1

        variable_horario_servico.append(StringVar(janela))
        variable_horario_servico[i].set(OPTIONS_HORARIO[0])
        w_horario = OptionMenu(janela, variable_horario_servico[i], *OPTIONS_HORARIO)
        w_horario.grid(column=column, row=row, padx=5, pady=5)
        column += 1

        variable_turno_servico.append(StringVar(janela))
        variable_turno_servico[i].set(OPTIONS_TURNOSERVICO[0])
        w_turnoservico = OptionMenu(janela, variable_turno_servico[i], *OPTIONS_TURNOSERVICO)
        w_turnoservico.grid(column=column, row=row, padx=5, pady=5)

        row += 1
        i += 1
        column = 0

    btn_abrir_siste = Button(janela, text='Iniciar marcação', command=btn_abrir_site_click)
    btn_abrir_siste.grid(column=5, row=row, padx=10, pady=10)

    row += 1

    global text_area
    # Área de texto para exibir mensagens
    text_area = Text(janela, height=10, width=100, wrap=tk.WORD)
    text_area.grid(row=row, column=0, padx=10, pady=10, sticky="nsew", columnspan=12)

    # Barra de rolagem para a área de texto
    scrollbar = Scrollbar(janela, command=text_area.yview)
    scrollbar.grid(row=row, column=12, sticky='nsew')
    text_area.config(yscrollcommand=scrollbar.set)

    # Impede que o usuário edite a área de texto diretamente
    text_area.config(state=tk.DISABLED)

    # Ajuste do grid para expandir a área de texto conforme a janela redimensiona
    janela.grid_rowconfigure(row, weight=1)
    janela.grid_columnconfigure(0, weight=1)

    janela.mainloop()


if __name__ == '__main__':
    abrir_janela()