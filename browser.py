import logging
import time
from contextlib import contextmanager
from typing import Iterable, List, Tuple

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from config import ELEMENT_WAIT_SECONDS


@contextmanager
def criar_driver(headless: bool, manter_aberto: bool) -> Iterable[Chrome]:
    logging.info("STEP 3 - Inicializando Chrome (headless=%s).", headless)
    options = ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--allow-insecure-localhost")
    options.set_capability("acceptInsecureCerts", True)
    if headless:
        options.add_argument("--headless=new")

    driver_path = ChromeDriverManager().install()
    service = ChromeService(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    try:
        yield driver
    finally:
        if manter_aberto:
            try:
                input(
                    "Automacao concluida. Revise o navegador e pressione Enter para encerra-lo..."
                )
            except EOFError:
                time.sleep(5)
        logging.info("Encerrando navegador.")
        driver.quit()


class Browser:
    def __init__(self, driver: Chrome, wait_seconds: int = ELEMENT_WAIT_SECONDS) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_seconds)

    def navigate(self, url: str) -> None:
        self.driver.get(url)

    def wait_for(
        self,
        selectors: List[Tuple[str, str]],
        description: str,
        condition=EC.presence_of_element_located,
    ):
        last_error: TimeoutException | None = None
        for by_strategy, value in selectors:
            try:
                logging.debug("Tentando localizar %s usando %s = %s", description, by_strategy, value)
                return self.wait.until(condition((by_strategy, value)))
            except TimeoutException as exc:
                last_error = exc
        raise TimeoutException(f"Nao foi possivel localizar {description}.") from last_error
