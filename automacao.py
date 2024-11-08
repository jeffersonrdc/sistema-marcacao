from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
    NoSuchElementException,
    InvalidSelectorException,
    WebDriverException,
)
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from utils import adicionar_mensagem

timeout = 60

def acessar_site(informacoes_array, info_usuario, text_area, janela_marcacao):
    # # Configuração do Chrome em modo headless
    # chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Executar em modo headless
    #
    # # Configuração do WebDriver
    # navegador = webdriver.Chrome(options=chrome_options)
    chrome_driver_path = (
        ChromeDriverManager()
        .install()
        .replace("THIRD_PARTY_NOTICES.chromedriver", "chromedriver.exe")
    )
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

    select = Select(
        WebDriverWait(navegador, timeout).until(
            ec.element_to_be_clickable((By.ID, "ddlTipoAcesso"))
        )
    )

    select.select_by_value(info_usuario['tipo_login'])

    WebDriverWait(navegador, timeout).until(
        ec.element_to_be_clickable((By.ID, "txtLogin"))
    ).send_keys(info_usuario['usuario'])
    WebDriverWait(navegador, timeout).until(
        ec.element_to_be_clickable((By.ID, "txtSenha"))
    ).send_keys(info_usuario['senha'])
    # print(navegador.page_source)

    # Encontrar o campo de entrada
    input_field = WebDriverWait(navegador, timeout).until(
        ec.element_to_be_clickable((By.ID, "TextCaptcha"))
    )
    input_field.click()

    # texto = None
    # while texto is None:
    #     imagem = gera_imagem_captcha_login(navegador)
    #     texto = resolver_captcha(imagem)
    #     if len(texto) >= 6:
    #         navegador.find_element(By.NAME, 'TextCaptcha').send_keys(texto)
    #         if is_visible(navegador):
    #             navegador.find_element(By.ID, 'txtSenha').send_keys(senha)
    #             navegador.find_element(By.NAME, 'TextCaptcha').clear()
    #             navegador.find_element(By.NAME, 'TextCaptcha').click()
    #             texto = None
    #     else:
    #         WebDriverWait(navegador, 3).until(ec.presence_of_element_located(
    #             (By.ID, 'lnkNewCaptcha'))).click()
    #         texto = None

    adicionar_mensagem(text_area, f"Aguardando usuário digitar o captcha...")
    janela_marcacao.update()  # Atualiza a janela para exibir a mensagem

    while True:
        try:
            input_field = WebDriverWait(navegador, timeout).until(
                ec.element_to_be_clickable((By.ID, "TextCaptcha"))
            )
            input_field.click()
            if check_input(input_field):
                # Encontrar e clicar no botão de login
                WebDriverWait(navegador, timeout).until(
                    ec.element_to_be_clickable((By.ID, "btnEntrar"))
                ).click()
                if is_visible(navegador):
                    adicionar_mensagem(
                        f"captcha digitado é inválido, digite novamente!"
                    )
                    janela_marcacao.update()  # Atualiza a janela para exibir a mensagem
                    # Manter o foco no campo de entrada se o texto for inválido
                    WebDriverWait(navegador, timeout).until(
                        ec.element_to_be_clickable((By.ID, "txtSenha"))
                    ).send_keys(senha)

                    WebDriverWait(navegador, timeout).until(
                        ec.element_to_be_clickable((By.ID, "TextCaptcha"))
                    ).clear()
                    WebDriverWait(navegador, timeout).until(
                        ec.element_to_be_clickable((By.ID, "TextCaptcha"))
                    ).click()
                else:
                    adicionar_mensagem(f"Login OK! Abrindo a página inicial...")
                    janela_marcacao.update()  # Atualiza a janela para exibir a mensagem
                    break
        except StaleElementReferenceException:
            # Ignorar e continuar o loop se o elemento estiver obsoleto
            pass
    nova_inscricao(navegador)


def nova_inscricao(navegador_param):
    adicionar_mensagem(f"Abrindo a página de marcação...")
    janela.update()  # Atualiza a janela para exibir a mensagem
    WebDriverWait(navegador_param, timeout).until(
        ec.element_to_be_clickable((By.ID, "btnEscala"))
    ).click()
    pesquisar_vaga(navegador_param)
    """ processar_informacoes(navegador_param) """

def pesquisar_vaga(navegador_param):
    is_mensagem = False
    current_time = datetime.now().time()
    if current_time < datetime.strptime("06:00:00", "%H:%M:%S").time():
        adicionar_mensagem(f"Aguardando o horário para iniciar a marcação do RAS...")
        janela.update()  # Atualiza a janela para exibir a mensagem
        while True:
            current_time = datetime.now().time()
            if current_time >= datetime.strptime("06:00:00", "%H:%M:%S").time():
                WebDriverWait(navegador_param, timeout).until(
                    ec.element_to_be_clickable((By.ID, "btnNovaInscricao"))
                ).click()
                break
    else:
        WebDriverWait(navegador_param, timeout).until(
            ec.element_to_be_clickable((By.ID, "btnNovaInscricao"))
        ).click()
    tentativa = 0

    iterator = iter(informacoes_array)
    for informacao in informacoes_array:
        next_item = next(iterator, None)
        if tentativa > 0:
            is_alert(navegador_param)

        # SELECIONA A DATA
        select_data_evento = None
        tentativa = 1
        while not select_data_evento:
            try:
                select_data_evento = Select(
                    WebDriverWait(navegador_param, timeout).until(
                        ec.element_to_be_clickable((By.ID, "ddlDataEvento"))
                    )
                )  # METODO QUE AGUARDA ATÉ X SEGUNDOS O ID SER CARREGADO NA PÁGINA
                select_data_evento.select_by_visible_text(informacao["data_servico"])
            except StaleElementReferenceException:
                select_data_evento = None
                tentativa = tentativa + 1

            # ________________________________________________________________________________________________________________________________________________________________#

        # CLICA NO LINK PARA EXIBIR O CAPTCHA
        adicionar_mensagem(f"Abrindo imagem do captcha, aguarde...")
        janela.update()  # Atualiza a janela para exibir a mensagem
        abri_captcha_click = None
        while not abri_captcha_click:
            try:
                abri_captcha_click = WebDriverWait(navegador_param, timeout).until(
                    ec.element_to_be_clickable((By.ID, "lnkNewCaptcha"))
                )
                if abri_captcha_click is not None:
                    abri_captcha_click.click()

                    while verifica_captcha_vaga_visivel(navegador_param):
                        break

                    adicionar_mensagem(f"Imagem do captcha aberta!")
                    janela.update()  # Atualiza a janela para exibir a mensagem

            except ElementClickInterceptedException:
                abri_captcha_click = None
            except StaleElementReferenceException:
                abri_captcha_click = None

        # ________________________________________________________________________________________________________________________________________________________________#

        # SELECIONA A VAGA PELO CONVÊNIO
        if informacao["tipo_filtro"] == 1:
            select_convenio = None
            tentativa = 1
            while not select_convenio:
                try:
                    select_convenio = Select(
                        WebDriverWait(navegador_param, timeout).until(
                            ec.element_to_be_clickable((By.ID, "ddlConvenios"))
                        )
                    )  # METODO QUE AGUARDA ATÉ X SEGUNDOS O ID SER CARREGADO NA PÁGINA
                    select_convenio.select_by_visible_text(
                        informacao["local_servico"]
                    )  # CARREGA PELA DESCRIÇÃO
                except StaleElementReferenceException:
                    select_convenio = None
                    tentativa = tentativa + 1

        # SELECIONA A VAGA PELO CPA
        else:
            select_cpa = None
            tentativa = 1
            while not select_cpa:
                try:
                    select_cpa = Select(
                        WebDriverWait(navegador_param, timeout).until(
                            ec.element_to_be_clickable((By.ID, "ddlCPAS"))
                        )
                    )  # METODO QUE AGUARDA ATÉ X SEGUNDOS O ID SER CARREGADO NA PÁGINA
                    select_cpa.select_by_visible_text(
                        informacao["local_servico"]
                    )  # CARREGA PELA DESCRIÇÃO
                except StaleElementReferenceException:
                    select_cpa = None
                    tentativa = tentativa + 1

        tentativa = 1
        is_ok = False
        while not is_ok:
            try:
                # print(navegador.page_source)
                # Garante que o elemento seja visível e clicável
                input_field = WebDriverWait(navegador_param, timeout).until(
                    ec.visibility_of_element_located(
                        (By.XPATH, '//*[@id="TextCaptcha"]')
                    )
                )

                WebDriverWait(navegador_param, timeout).until(
                    ec.element_to_be_clickable((By.XPATH, '//*[@id="TextCaptcha"]'))
                )
                input_field.clear()
                # Executa o clique via JavaScript e coloca o foco no campo
                navegador_param.execute_script(
                    "arguments[0].click(); arguments[0].focus();", input_field
                )

                # Loop para monitorar continuamente a entrada e a hora
                tentativa = 1
                while True:
                    try:
                        # current_time = datetime.now().time()
                        # if current_time < datetime.strptime("07:00:00", "%H:%M:%S").time():
                        #     adicionar_mensagem(f"Aguardando o horário para iniciar a marcação do Proeis...")
                        #     janela.update()  # Atualiza a janela para exibir a mensagem
                        # imagem = gera_imagem_captcha_vaga(navegador_param)
                        # texto_captcha = resolver_captcha(imagem)
                        # navegador_param.find_element(By.ID, 'TextCaptcha').send_keys(texto_captcha)
                        # WebDriverWait(navegador_param, timeout).until(
                        #                                 ec.element_to_be_clickable((By.ID, 'btnConsultar'))).click()
                        # while verifica_local_visivel(navegador_param):
                        #     break
                        # alert = is_alert(navegador_param)
                        # if alert == 0:
                        #     is_ok = True
                        #     break
                        # else:
                        #     adicionar_mensagem(f"captcha é inválido, irei tentar novamente!")
                        #     janela.update()  # Atualiza a janela para exibir a mensagem

                        input_field = WebDriverWait(navegador_param, timeout).until(
                            ec.element_to_be_clickable(
                                (By.XPATH, '//*[@id="TextCaptcha"]')
                            )
                        )

                        current_time = datetime.now().time()
                        if (
                            current_time
                            < datetime.strptime("07:00:00", "%H:%M:%S").time()
                        ):
                            if not is_mensagem:
                                is_mensagem = True
                                adicionar_mensagem(
                                    f"Aguardando o horário para iniciar a marcação do Proeis..."
                                )
                                janela.update()  # Atualiza a janela para exibir a mensagem
                        # if check_input_and_time(input_field, hora_limite):
                        if (
                            hora_limite
                            and check_input_and_time(input_field, hora_limite)
                        ) or (
                            not hora_limite and check_input_and_time(input_field, None)
                        ):
                            # Encontrar e clicar no botão de login
                            WebDriverWait(navegador_param, timeout).until(
                                ec.element_to_be_clickable((By.ID, "btnConsultar"))
                            ).click()
                            while verifica_local_visivel(navegador_param):
                                break
                            alert = is_alert(navegador_param)
                            if alert == 0:
                                is_ok = True
                                break
                            else:
                                adicionar_mensagem(
                                    f"captcha digitado é inválido, digite novamente!"
                                )
                                janela.update()  # Atualiza a janela para exibir a mensagem
                    except StaleElementReferenceException:
                        tentativa += 1
                        # Esperar por um curto período para evitar uso excessivo de CPU
            except Exception as e:
                tentativa += 1
                if tentativa > 5:  # Número máximo de tentativas
                    navegador_param.quit()
                    break

        if informacao["tipo_filtro"] == 2:
            tentativa = 1
            convenio_xcpa = None
            while not convenio_xcpa:
                try:
                    convenio_xcpa = WebDriverWait(navegador_param, timeout).until(
                        ec.element_to_be_clickable(
                            (By.LINK_TEXT, f"{informacao['localxcpa_servico']}")
                        )
                    )  # METODO QUE AGUARDA ATÉ X SEGUNDOS O ID SER CARREGADO
                    # NA PÁGINA
                except StaleElementReferenceException:
                    tentativa += 1

            # while verifica_local_visivel(navegador_param):
            #     break

            navegador_param.execute_script("arguments[0].click();", convenio_xcpa)
        tentativa = 1

        while verifica_vaga_visivel(navegador_param):
            break

        while True:
            xpath_evento = f"//td[text()='{informacao['setor_servico']}' and following-sibling::td[text()='{informacao['hora_servico']}'] and following-sibling::td[text()='{informacao['turno_servico']}']]/following-sibling::td[@class='btnCollumn']/a"
            try:
                elementos_evento = WebDriverWait(navegador_param, 5).until(
                    ec.element_to_be_clickable((By.XPATH, xpath_evento))
                )

                # Verificar se o elemento é clicável e clicar nele
                if elementos_evento.is_displayed() and elementos_evento.is_enabled():
                    navegador_param.execute_script(
                        "arguments[0].click();", elementos_evento
                    )
                    is_alert(navegador_param, 20)
                    adicionar_mensagem(
                        f"{informacao['setor_servico']} dia {informacao['data_servico'][8:10]}/{informacao['data_servico'][5:7]}/{informacao['data_servico'][0:4]} às {informacao['hora_servico']} marcado com sucesso!"
                    )
                    janela.update()  # Atualiza a janela para exibir a mensagem
                    break
                else:
                    adicionar_mensagem(
                        f"{informacao['setor_servico']} dia {informacao['data_servico'][8:10]}/{informacao['data_servico'][5:7]}/{informacao['data_servico'][0:4]} às {informacao['hora_servico']} não encontrado!"
                    )
                    janela.update()  # Atualiza a janela para exibir a mensagem
                    break
            except TimeoutException:
                tentativa += 1
                if (
                    tentativa > 2
                    and next_item is not None
                    and next_item != informacoes_array[-1]
                ):
                    adicionar_mensagem(
                        f"Setor {informacao['setor_servico']} no dia {informacao['data_servico'][8:10]}/{informacao['data_servico'][5:7]}/{informacao['data_servico'][0:4]} às {informacao['hora_servico']} não encontrado! Buscando próxima vaga..."
                    )
                    janela.update()  # Atualiza a janela para exibir a mensagem
                    break
                else:
                    continue
            except WebDriverException as e:
                tentativa += 1
                if tentativa > 5:  # Número máximo de tentativas
                    break
        # ________________________________________________________________________________________________________________________________________________________________#

    # FECHA O NAVEGADOR AO TERMINAR DE INSERIR AS VAGAS
    adicionar_mensagem(f"Marcações finalizadas, fechando o navegador em 30 segundos...")
    janela.update()  # Atualiza a janela para exibir a mensagem
    t.sleep(30)
    navegador_param.quit()
