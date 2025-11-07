import logging
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
from openpyxl import load_workbook
from PIL import Image
from pytesseract import pytesseract

pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import pytesseract
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


def resolver_captcha_ocr(driver: Chrome) -> bool:
    from selectors_module import DEFAULT_SELECTORS

    logging.info("STEP - Tentando resolver CAPTCHA por OCR.")
    try:
        imagem_elemento = driver.find_element(*DEFAULT_SELECTORS.captcha_image[0])
        campo_entrada = driver.find_element(*DEFAULT_SELECTORS.captcha_input[0])
    except Exception:
        logging.info("STEP - Elementos de CAPTCHA nao encontrados para OCR.")
        return False

    imagem_b64 = imagem_elemento.screenshot_as_png
    texto = extrair_texto_captcha_from_bytes(imagem_b64)
    if texto:
        logging.info("STEP - OCR retornou '%s'.", texto)
        preencher_campo(driver, campo_entrada, texto)
        return True

    logging.warning("STEP - OCR nao conseguiu decodificar o CAPTCHA.")
    return False


def lidar_com_captcha(driver: Chrome, destino: Path, aguardar_usuario: bool) -> None:
    logging.info("STEP - Verificando presenca de CAPTCHA.")
    if not detectar_captcha(driver):
        return

    logging.warning(
        "STEP - CAPTCHA detectado. Informe manualmente caso o OCR nao esteja ativado."
    )
    if aguardar_usuario:
        input("Digite o CAPTCHA no navegador e pressione Enter para continuar...")


def extrair_texto_captcha_from_bytes(image_bytes: bytes) -> str:
    np_array = np.frombuffer(image_bytes, np.uint8)
    imagem = cv2.imdecode(np_array, cv2.IMREAD_GRAYSCALE)
    if imagem is None:
        return ""

    blur = cv2.medianBlur(imagem, 3)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = np.ones((2, 2), np.uint8)
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    dilate = cv2.dilate(close, kernel, iterations=1)
    erode = cv2.erode(dilate, kernel, iterations=1)
    ampliada = cv2.resize(erode, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

    pil_image = Image.fromarray(ampliada)
    texto = pytesseract.image_to_string(
        pil_image,
        config="--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    )
    return "".join(ch for ch in texto.upper() if ch.isalnum())


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
