import logging
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Optional, Tuple

from openpyxl import load_workbook
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from config import ELEMENT_WAIT_SECONDS

try:
    import pyautogui

    pyautogui.FAILSAFE = False
except ImportError:  # pragma: no cover - ambiente sem pyautogui
    pyautogui = None  # type: ignore[assignment]


def configurar_logs() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )


def pausar(segundos: float) -> None:
    if segundos > 0:
        logging.debug("Pausa de %.2f segundos.", segundos)
        time.sleep(segundos)


def carregar_credenciais(
    xlsx_path: Path,
    sheet_name: Optional[str],
    row_number: int,
    col_user: int,
    col_password: int,
) -> Tuple[str, str]:
    logging.info("STEP 1 - Lendo credenciais em %s", xlsx_path)
    workbook = load_workbook(xlsx_path, data_only=True, read_only=True)
    worksheet = workbook[sheet_name] if sheet_name else workbook.active
    usuario = worksheet.cell(row=row_number, column=col_user).value
    senha = worksheet.cell(row=row_number, column=col_password).value
    if not usuario or not senha:
        raise ValueError(
            "Nao foi possivel encontrar usuario e senha na planilha. "
            "Verifique os parametros --linha, --coluna-usuario e --coluna-senha."
        )
    return str(usuario).strip(), str(senha).strip()


def periodo_mes_anterior(base: Optional[date] = None) -> Tuple[str, str]:
    hoje = base or date.today()
    primeiro_deste_mes = hoje.replace(day=1)
    ultimo_mes = primeiro_deste_mes - timedelta(days=1)
    primeiro = ultimo_mes.replace(day=1)
    ultimo = ultimo_mes
    inicio = primeiro.strftime("%d/%m/%Y")
    fim = ultimo.strftime("%d/%m/%Y")
    logging.info("STEP 2 - Periodo selecionado: %s ate %s (mes anterior).", inicio, fim)
    return inicio, fim


def pressionar_enter_certificado(headless: bool) -> None:
    if headless:
        logging.info("STEP 6 - Modo headless ativo; pulando envio automatico de ENTER.")
        return
    if pyautogui is None:
        logging.info("STEP 6 - pyautogui nao instalado; pulando envio automatico de ENTER.")
        return

    logging.info("STEP 6 - Aguardando 3 segundos e pressionando ENTER para fechar o certificado.")
    time.sleep(3)
    try:
        pyautogui.press("enter")
        logging.debug("STEP 6 - ENTER enviado via pyautogui.")
    except Exception as exc:
        logging.warning("STEP 6 - Falha ao enviar ENTER via pyautogui: %s", exc)


def detectar_captcha(driver: Chrome) -> bool:
    seletor_xpath = (
        "//*[contains(translate(@id, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'captcha')"
        " or contains(translate(@class, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'captcha')"
        " or contains(translate(@src, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'captcha')]"
    )
    captcha_elements = driver.find_elements(By.XPATH, seletor_xpath)
    return len(captcha_elements) > 0


def lidar_com_captcha(driver: Chrome, destino: Path, aguardar_usuario: bool) -> None:
    logging.info("STEP - Verificando presenca de CAPTCHA.")
    if not detectar_captcha(driver):
        return

    destino.mkdir(parents=True, exist_ok=True)
    screenshot_path = destino / f"captcha_{date.today().isoformat()}.png"
    driver.save_screenshot(str(screenshot_path))
    logging.warning(
        "CAPTCHA detectado. Screenshot salva em %s. "
        "Sera necessario resolver manualmente.",
        screenshot_path,
    )
    if aguardar_usuario:
        input("Resolva o CAPTCHA no navegador aberto e pressione Enter para continuar...")


def aguardar_pagina_carregada(driver: Chrome, timeout: int) -> None:
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    logging.info(
        "STEP 4 - Estado do documento apos carregamento: %s",
        driver.execute_script("return document.readyState"),
    )


def preencher_campo(driver: Chrome, elemento, valor: str) -> None:
    try:
        elemento.click()
        elemento.clear()
        elemento.send_keys(valor)
    except Exception as exc:
        logging.warning(
            "Falha ao preencher campo via send_keys (%s). Aplicando fallback JavaScript.",
            exc,
        )
        driver.execute_script(
            (
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
                "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));"
            ),
            elemento,
            valor,
        )
    else:
        driver.execute_script(
            (
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
                "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));"
            ),
            elemento,
            valor,
        )

    def _tem_valor(_: object) -> bool:
        try:
            return (elemento.get_attribute("value") or "").strip() == valor
        except Exception:
            return False

    WebDriverWait(driver, ELEMENT_WAIT_SECONDS).until(_tem_valor)
