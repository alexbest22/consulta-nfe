import argparse
from pathlib import Path

from browser import Browser, criar_driver
from steps import ConsultaNFeSteps
from utils import (
    carregar_credenciais,
    configurar_logs,
    pausar,
    periodo_mes_anterior,
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
        help="Diretorio onde screenshots de CAPTCHA serao salvos.",
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
        "--fechar-navegador",
        action="store_true",
        help="Fecha o navegador automaticamente ao final (padrao: manter aberto ate confirmacao).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configurar_logs()

    planilha = Path(args.planilha).expanduser().resolve()
    usuario, senha = carregar_credenciais(
        planilha,
        args.aba,
        args.linha,
        args.coluna_usuario,
        args.coluna_senha,
    )
    periodo_inicio, periodo_fim = periodo_mes_anterior()

    with criar_driver(args.headless, not args.fechar_navegador) as driver:
        browser = Browser(driver)
        steps = ConsultaNFeSteps(
            browser=browser,
            diretorio_captcha=Path(args.diretorio_captcha),
            aguardar_captcha=args.sequencia_captcha,
        )

        steps.acessar_login(args.espera)
        steps.autenticar(usuario, senha, args.headless)
        steps.definir_periodo(periodo_inicio, periodo_fim)


if __name__ == "__main__":
    main()
