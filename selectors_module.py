from dataclasses import dataclass
from typing import List, Tuple

from selenium.webdriver.common.by import By

LOGIN_URL = (
    "https://nfe.sefaz.ba.gov.br/servicos/NFENC/SSL/ASLibrary/Login?"
    "ReturnUrl=%2fservicos%2fnfenc%2fModulos%2fAutenticado%2fRestrito%2fNFENC_consulta_emitente.aspx"
)


@dataclass
class Selectors:
    username: List[Tuple[str, str]]
    password: List[Tuple[str, str]]
    login_button: List[Tuple[str, str]]
    filter_period_radio: List[Tuple[str, str]]
    period_start: List[Tuple[str, str]]
    period_end: List[Tuple[str, str]]
    consultar_button: List[Tuple[str, str]]
    captcha_image: List[Tuple[str, str]]
    captcha_input: List[Tuple[str, str]]
    razao_social: List[Tuple[str, str]]


DEFAULT_SELECTORS = Selectors(
    username=[
        (By.ID, "PHCentro_userLogin"),
        (By.NAME, "PHCentro$userLogin"),
    ],
    password=[
        (By.ID, "PHCentro_userPass"),
        (By.NAME, "PHCentro$userPass"),
    ],
    login_button=[
        (By.XPATH, "//label[@for='PHCentro_btnLogin']"),
        (By.CSS_SELECTOR, "label[for='PHCentro_btnLogin']"),
        (By.ID, "PHCentro_btnLogin"),
        (By.CSS_SELECTOR, "button[id$='btnLogin']"),
        (By.CSS_SELECTOR, "input[id$='btnLogin']"),
    ],
    filter_period_radio=[
        (By.ID, "rbt_filtro3"),
        (By.CSS_SELECTOR, "input#rbt_filtro3"),
        (By.XPATH, "//input[@name='filtro' and @value='rbt_filtro3']"),
    ],
    period_start=[
        (By.ID, "txtPeriodoInicial"),
        (By.CSS_SELECTOR, "input#txtPeriodoInicial"),
        (By.CSS_SELECTOR, "input[id$='txtDataAutorizacaoInicio']"),
        (By.CSS_SELECTOR, "input[id$='txtDataAutorizacaoInicial']"),
        (By.CSS_SELECTOR, "input[id$='txtDataPeriodoAutorizacaoInicio']"),
        (
            By.XPATH,
            (
                "//label[contains(translate(normalize-space(.),"
                " '\u00c1\u00c2\u00c3\u00c0\u00e1\u00e2\u00e3\u00e0"
                "\u00c9\u00ca\u00e9\u00ea\u00cd\u00ed\u00d3\u00d4"
                "\u00d5\u00f3\u00f4\u00f5\u00da\u00fa\u00c7\u00e7PERIOD',"
                " 'aaaaaaaaeeeiiooouuccperiod'), 'periodo de autorizacao')]"
                "/following::input[1]"
            ),
        ),
    ],
    period_end=[
        (By.ID, "txtPeriodoFinal"),
        (By.CSS_SELECTOR, "input#txtPeriodoFinal"),
        (By.CSS_SELECTOR, "input[id$='txtDataAutorizacaoFim']"),
        (By.CSS_SELECTOR, "input[id$='txtDataAutorizacaoFinal']"),
        (By.CSS_SELECTOR, "input[id$='txtDataPeriodoAutorizacaoFim']"),
        (
            By.XPATH,
            (
                "//label[contains(translate(normalize-space(.),"
                " '\u00c1\u00c2\u00c3\u00c0\u00e1\u00e2\u00e3\u00e0"
                "\u00c9\u00ca\u00e9\u00ea\u00cd\u00ed\u00d3\u00d4"
                "\u00d5\u00f3\u00f4\u00f5\u00da\u00fa\u00c7\u00e7PERIOD',"
                " 'aaaaaaaaeeeiiooouuccperiod'), 'periodo de autorizacao')]"
                "/following::input[2]"
            ),
        ),
    ],
    consultar_button=[
        (By.ID, "AplicarFiltro"),
        (By.CSS_SELECTOR, "input#AplicarFiltro"),
        (By.CSS_SELECTOR, "button[id$='btnConsultar']"),
        (By.CSS_SELECTOR, "input[id$='btnConsultar']"),
        (By.XPATH, "//button[normalize-space()='Consultar']"),
        (
            By.XPATH,
            (
                "//input[@type='submit' and "
                "contains(translate(@value, 'consultar', 'CONSULTAR'), 'CONSULTAR')]"
            ),
        ),
    ],
    captcha_image=[
        (By.ID, "img_captcha"),
        (By.CSS_SELECTOR, "img#img_captcha"),
    ],
    captcha_input=[
        (By.ID, "txt_cod_antirobo"),
        (By.CSS_SELECTOR, "input#txt_cod_antirobo"),
    ],
    razao_social=[
        (By.ID, "lblRazaoSocial_Emitente"),
        (By.CSS_SELECTOR, "#lblRazaoSocial_Emitente"),
    ],
)
