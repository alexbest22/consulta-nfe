from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from browser import Browser
from selectors_module import DEFAULT_SELECTORS, LOGIN_URL
from utils import (
    aguardar_pagina_carregada,
    lidar_com_captcha,
    pausar,
    preencher_campo,
    pressionar_enter_certificado,
)


DEFAULT_PAUSE_SECONDS = 1.0


class ConsultaNFeSteps:
    def __init__(
        self,
        browser: Browser,
        diretorio_captcha: Path,
        aguardar_captcha: bool,
        pausa: float = DEFAULT_PAUSE_SECONDS,
    ) -> None:
        self.browser = browser
        self.pausa = pausa
        self.diretorio_captcha = diretorio_captcha
        self.aguardar_captcha = aguardar_captcha

    def acessar_login(self, timeout: int) -> None:
        self.browser.navigate(LOGIN_URL)
        aguardar_pagina_carregada(self.browser.driver, timeout)
        self.browser.wait_for(
            [
                (By.ID, "PHCentro_pnllogin"),
                (By.CSS_SELECTOR, "div#PHCentro_pnllogin"),
                (By.CSS_SELECTOR, "form#frmPControle"),
            ],
            "container de login",
        )

    def autenticar(self, usuario: str, senha: str, headless: bool) -> None:
        campo_usuario = self.browser.wait_for(
            DEFAULT_SELECTORS.username,
            "campo de usuario",
            condition=EC.element_to_be_clickable,
        )
        campo_senha = self.browser.wait_for(
            DEFAULT_SELECTORS.password,
            "campo de senha",
            condition=EC.element_to_be_clickable,
        )
        botao_login = self.browser.wait_for(
            DEFAULT_SELECTORS.login_button,
            "botao de login",
            condition=EC.element_to_be_clickable,
        )

        preencher_campo(self.browser.driver, campo_usuario, usuario)
        preencher_campo(self.browser.driver, campo_senha, senha)
        pausar(self.pausa)

        botao_login.click()
        pressionar_enter_certificado(headless)
        pausar(self.pausa)

    def definir_periodo(self, periodo_inicio: str, periodo_fim: str) -> None:
        filtro_periodo = self.browser.wait_for(
            DEFAULT_SELECTORS.filter_period_radio,
            "radio 'Periodo de Autorizacao'",
            condition=EC.element_to_be_clickable,
        )
        try:
            filtro_periodo.click()
        except Exception:
            self.browser.driver.execute_script("arguments[0].click();", filtro_periodo)
        self.browser.driver.execute_script(
            "arguments[0].checked = true;"
            "if (typeof script_rbt_filtro === 'function') { script_rbt_filtro(); }",
            filtro_periodo,
        )
        pausar(self.pausa)

        campo_periodo_inicio = self.browser.wait_for(
            DEFAULT_SELECTORS.period_start,
            "campo 'Periodo de Autorizacao' (inicial)",
            condition=EC.element_to_be_clickable,
        )
        campo_periodo_fim = self.browser.wait_for(
            DEFAULT_SELECTORS.period_end,
            "campo 'Periodo de Autorizacao' (final)",
            condition=EC.element_to_be_clickable,
        )

        preencher_campo(self.browser.driver, campo_periodo_inicio, periodo_inicio)
        preencher_campo(self.browser.driver, campo_periodo_fim, periodo_fim)
        pausar(self.pausa)

        lidar_com_captcha(
            self.browser.driver,
            self.diretorio_captcha,
            self.aguardar_captcha,
        )
