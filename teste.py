def acessar_site():
    chrome_driver_path = (
        ChromeDriverManager()
        .install()
        .replace("THIRD_PARTY_NOTICES.chromedriver", "chromedriver.exe")
    )
    navegador = webdriver.Chrome(service=Service(chrome_driver_path))
    navegador.maximize_window()

    link = "http://www.proeis.rj.gov.br/"
    navegador.get(link)

    select = Select(
        WebDriverWait(navegador, timeout).until(
            ec.element_to_be_clickable((By.ID, "ddlTipoAcesso"))
        )
    )

    select.select_by_value(tipo_login)

    WebDriverWait(navegador, timeout).until(
        ec.element_to_be_clickable((By.ID, "txtLogin"))
    ).send_keys(usuario)
    WebDriverWait(navegador, timeout).until(
        ec.element_to_be_clickable((By.ID, "txtSenha"))
    ).send_keys(senha)
    # print(navegador.page_source)

    # Encontrar o campo de entrada
    input_field = WebDriverWait(navegador, timeout).until(
        ec.element_to_be_clickable((By.ID, "TextCaptcha"))
    )
    input_field.click()

    adicionar_mensagem(f"Aguardando usuário digitar o captcha...")
    janela.update()  # Atualiza a janela para exibir a mensagem

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
                    janela.update()  # Atualiza a janela para exibir a mensagem
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
                    janela.update()  # Atualiza a janela para exibir a mensagem
                    break
        except StaleElementReferenceException:
            # Ignorar e continuar o loop se o elemento estiver obsoleto
            pass
    nova_inscricao(navegador)