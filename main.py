import argparse
import logging
import shutil
import time
from pathlib import Path

from browser import Browser, criar_driver
from steps import ConsultaNFeSteps
from utils import (
    ajustar_extensao_planilha,
    aguardar_download_conclusao,
    carregar_lista_credenciais,
    configurar_logs,
    normalizar_nome_pasta,
    periodo_mes_anterior_info,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automatiza login e consulta no portal SEFAZ-BA (NF-e)."
    )
    parser.add_argument(
        "--planilha",
        required=True,
        help="Caminho para a planilha Excel contendo usuario e senha.",
    )
    parser.add_argument(
        "--linha",
        type=int,
        default=2,
        help="Linha da planilha (1-index) onde estao usuario e senha. Padrao: 2.",
    )
    parser.add_argument(
        "--coluna-usuario",
        type=int,
        default=3,
        help="Numero da coluna (1-index) para o usuario. Padrao: 3.",
    )
    parser.add_argument(
        "--coluna-senha",
        type=int,
        default=4,
        help="Numero da coluna (1-index) para a senha. Padrao: 4.",
    )
    parser.add_argument(
        "--aba",
        help="Nome da aba dentro da planilha. Se omitido, usa a primeira aba.",
    )
    parser.add_argument(
        "--espera",
        type=int,
        default=20,
        help="Tempo maximo de espera (segundos) para elementos da pagina.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Executa o Chrome em modo headless.",
    )
    parser.add_argument(
        "--diretorio-captcha",
        default="captchas",
        help="Diretorio onde arquivos relacionados ao CAPTCHA serao armazenados.",
    )
    parser.add_argument(
        "--downloads-temporarios",
        default=".downloads_temp",
        help="Diretorio temporario para receber os downloads antes de mover para o destino final.",
    )
    parser.add_argument(
        "--saida-planilhas",
        default="planilhas",
        help="Diretorio raiz onde as planilhas consolidadas serao salvas.",
    )
    parser.add_argument(
        "--sequencia-captcha",
        action="store_true",
        help=(
            "Mantem execucao aguardando o usuario resolver o CAPTCHA manualmente."
            " Ao detectar um CAPTCHA, o script pausa ate o usuario confirmar."
        ),
    )
    parser.add_argument(
        "--ocr-captcha",
        action="store_true",
        help="Ativa tentativa automatica de leitura do CAPTCHA via OCR (requer Tesseract instalado).",
    )
    parser.add_argument(
        "--manter-navegador",
        action="store_true",
        help="Mantem o navegador aberto ao final de cada execucao para inspecao manual.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configurar_logs()

    planilha = Path(args.planilha).expanduser().resolve()
    credenciais = carregar_lista_credenciais(
        planilha,
        args.aba,
        args.linha,
        args.coluna_usuario,
        args.coluna_senha,
    )
    if not credenciais:
        raise SystemExit("Nenhuma credencial encontrada na planilha.")

    periodo_inicio, periodo_fim, ano_referencia, mes_extenso = periodo_mes_anterior_info()
    base_saida = Path(args.saida_planilhas).expanduser().resolve()
    base_downloads = Path(args.downloads_temporarios).expanduser().resolve()
    diretorio_captcha = Path(args.diretorio_captcha).expanduser().resolve()

    total = len(credenciais)
    for indice, (usuario, senha) in enumerate(credenciais, start=1):
        logging.info("===== Processando credencial %s/%s =====", indice, total)
        temp_dir = base_downloads / f"exec_{indice}_{int(time.time())}"
        temp_dir.mkdir(parents=True, exist_ok=True)

        with criar_driver(args.headless, args.manter_navegador, temp_dir) as driver:
            browser = Browser(driver)
            steps = ConsultaNFeSteps(
                browser=browser,
                diretorio_captcha=diretorio_captcha,
                aguardar_captcha=args.sequencia_captcha,
                usar_ocr=args.ocr_captcha,
                headless=args.headless,
            )

            steps.acessar_login(args.espera)
            steps.autenticar(usuario, senha, args.headless)
            razao_social = steps.obter_razao_social()
            steps.definir_periodo(periodo_inicio, periodo_fim)
            steps.enviar_consulta()

            arquivo_download = aguardar_download_conclusao(temp_dir)
            arquivo_download = ajustar_extensao_planilha(arquivo_download)

        destino_final = (
            base_saida
            / str(ano_referencia)
            / mes_extenso
            / normalizar_nome_pasta(razao_social, f"empresa_{indice}")
        )
        destino_final.mkdir(parents=True, exist_ok=True)
        destino_arquivo = destino_final / arquivo_download.name
        shutil.move(str(arquivo_download), destino_arquivo)
        shutil.rmtree(temp_dir, ignore_errors=True)
        logging.info("Arquivo movido para %s", destino_arquivo)

    input("Processamento concluido. Pressione Enter para encerrar...")


if __name__ == "__main__":
    main()
