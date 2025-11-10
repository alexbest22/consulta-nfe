import logging
from pathlib import Path
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException

from browser import Browser
from selectors_module import DEFAULT_SELECTORS
from utils import (
    aguardar_pagina_carregada,
    lidar_com_captcha,
    resolver_captcha_ocr,
    pausar,
    preencher_campo,
    pressionar_enter,
)


DEFAULT_PAUSE_SECONDS = 1.0


class ConsultaNFeSteps:
    def __init__(
        self,
        browser: Browser,
        diretorio_captcha: Path,
        aguardar_captcha: bool,
        usar_ocr: bool,
        headless: bool,
        login_url: str,
        subpasta: str,
        pausa: float = DEFAULT_PAUSE_SECONDS,
    ) -> None:
        self.browser = browser
        self.pausa = pausa
        self.diretorio_captcha = diretorio_captcha
        self.aguardar_captcha = aguardar_captcha
        self.usar_ocr = usar_ocr
        self.headless = headless
        self.login_url = login_url
        self.subpasta = subpasta
        self._razao_social: Optional[str] = None

    def acessar_login(self, timeout: int) -> None:
        self.browser.navigate(self.login_url)
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
        pressionar_enter(headless, delay=3.0, contexto="certificado")
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

        self._resolver_captcha()

    def obter_razao_social(self) -> str:
        if self._razao_social:
            return self._razao_social
        elemento = self.browser.wait_for(
            DEFAULT_SELECTORS.razao_social,
            "label de razao social",
        )
        self._razao_social = elemento.text.strip()
        logging.info("STEP - Razao social identificada: %s", self._razao_social)
        return self._razao_social

    def enviar_consulta(self) -> None:
        tentativas = 0
        while True:
            botao_consultar = self.browser.wait_for(
                DEFAULT_SELECTORS.consultar_button,
                "botao 'Consultar'",
                condition=EC.element_to_be_clickable,
            )
            pausar(self.pausa)
            botao_consultar.click()
            pausar(self.pausa)
            if self._tratar_alerta_captcha():
                tentativas += 1
                logging.warning("STEP - CAPTCHA invalido. Tentativa %s.", tentativas)
                self._resolver_captcha()
                continue
            break
        self._aguardar_resultados()

    def _resolver_captcha(self) -> None:
        if self.usar_ocr and resolver_captcha_ocr(self.browser.driver):
            return
        lidar_com_captcha(
            self.browser.driver,
            self.diretorio_captcha,
            self.aguardar_captcha,
        )

    def _tratar_alerta_captcha(self) -> bool:
        try:
            alert = WebDriverWait(self.browser.driver, 2).until(EC.alert_is_present())
        except TimeoutException:
            return False

        mensagem = alert.text
        logging.warning("STEP - Alerta apos consulta: %s", mensagem)
        alert.accept()
        pressionar_enter(self.headless, delay=3.0, contexto="alerta captcha")
        return True

    def _aguardar_resultados(self) -> None:
        try:
            gerar_planilha = self.browser.wait_for(
                [
                    (By.ID, "btn_GeraPlanilha"),
                    (By.ID, "btn_GerarPlanilha"),
                    (By.CSS_SELECTOR, "input#btn_GerarPlanilha"),
                    (By.XPATH, "//input[@value='Gerar Planilha']"),
                ],
                "botao 'Gerar Planilha'",
                condition=EC.element_to_be_clickable,
            )
            pausar(self.pausa)
            gerar_planilha.click()
            logging.info("STEP - Botao 'Gerar Planilha' acionado.")
        except TimeoutException:
            logging.warning("STEP - Botao 'Gerar Planilha' nao foi localizado apos a consulta.")
