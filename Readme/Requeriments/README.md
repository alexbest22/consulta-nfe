# Automatizacao de Consulta NF-e (SEFAZ Bahia)

Este projeto automatiza o login no portal da SEFAZ Bahia, preenche o periodo de autorizacao (mês anterior) e baixa a planilha de resultados para cada par usuario/senha listado na planilha de entrada.

## Dependencias

- Google Chrome instalado
- Python 3.10 ou superior
- Node.js 18+ (somente se for usar a versão em TypeScript)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) instalado e acessivel no PATH (necessario para o OCR do CAPTCHA)

### Instalacao das bibliotecas

- Python:
  ```bash
  pip install -r requirements.txt
  ```
  (Inclui `pyautogui`, `pywinauto`, `pytesseract`, OpenCV e Pillow.)

- TypeScript:
  ```bash
  npm install
  ```

## Estrutura da planilha

Arquivo padrão: `usuario-senha-nfe.xlsx` (raiz do projeto).

- Aba: primeira aba (use `--aba` para definir outra).
- Linha inicial: `2` (primeira linha apos o cabecalho).
- Coluna do usuario: `3`.
- Coluna da senha: `4`.

Todas as linhas a partir do indice informado sao processadas ate encontrar uma linha vazia.

## Execucao (Python)

```bash
python main.py --planilha usuario-senha-nfe.xlsx --ocr-captcha
```

Use `--ocr-captcha` para ativar a tentativa automatica de leitura do CAPTCHA. Se preferir digitar manualmente, omita essa opcao ou acrescente `--sequencia-captcha` para forcar a pausa aguardando o usuario.

### Principais opcoes

- `--headless`: executa o Chrome sem interface grafica.
- `--linha`, `--coluna-usuario`, `--coluna-senha`, `--aba`: personalizam o mapeamento da planilha.
- `--espera`: tempo maximo de espera (segundos) para elementos (padrao `20`).
- `--diretorio-captcha`: pasta usada para arquivos auxiliares do CAPTCHA (padrao `captchas`).
- `--downloads-temporarios`: pasta temporaria para downloads antes de mover (padrao `.downloads_temp`).
- `--saida-planilhas`: pasta raiz onde as planilhas sao organizadas (padrao `planilhas`); os arquivos sao renomeados para `.xls` caso venham como `.tmp`.
- `--sequencia-captcha`: pausa a execucao para que o usuario resolva o CAPTCHA manualmente caso o OCR nao seja utilizado.
- `--ocr-captcha`: tenta ler o CAPTCHA automaticamente (requer Tesseract instalado).
- `--manter-navegador`: mantem o navegador aberto ao final de cada execucao para inspecao manual (por padrao o navegador e fechado assim que a planilha e baixada para seguir com a proxima credencial).

## Fluxo automatizado

1. Para cada linha valida da planilha:
   - Abre o portal, realiza o login e identifica a razao social exibida na tela.
   - Seleciona o filtro de periodo, preenche as datas do mes anterior e resolve o CAPTCHA via OCR (caso habilitado) ou aguarda digitacao manual.
   - Clica em **Consultar**. Se o portal apresentar um alerta de CAPTCHA invalido, aceita o alerta, envia `ENTER`, resolve o CAPTCHA novamente e repete o processo.
   - Ao obter o resultado, clica em **Gerar Planilha** e aguarda o fim do download.
   - Move o arquivo baixado para `saida-planilhas/<ano>/<RAZAO_SOCIAL>/<mes_por_extenso>/`.
   - Encerra o navegador e passa para a proxima credencial.
2. Ao terminar todas as credenciais, o script aguarda uma confirmacao manual para encerrar.

## Ajustando seletores

- Python: edite `selectors_module.py`.
- TypeScript: ajuste o objeto `SELECTORS` em `src/steps.ts`.

## Observacoes

- O OCR depende da instalacao local do Tesseract (`tesseract.exe`). Ajuste o caminho em `utils.py` caso o executavel esteja em outro diretorio.
- Caso deseje resolver o CAPTCHA manualmente, use `--sequencia-captcha`. Com `--ocr-captcha`, o script tenta decodifica-lo automaticamente; se falhar, volta ao fluxo manual.
- O navegador e fechado apos cada credencial para iniciar o proximo processamento. Use `--manter-navegador` para inspecionar manualmente antes de fechar.
- Certifique-se de que o Chrome permita downloads automaticos (as configuracoes de download sao ajustadas dinamicamente pelo script).

## Estrutura dos arquivos Python

- `main.py`: ponto de entrada, parsing de argumentos e loop sobre todas as credenciais.
- `browser.py`: inicializacao/configuracao do WebDriver.
- `steps.py`: etapas de acesso, login, preenchimento, resolucao do CAPTCHA e acionamento de botoes.
- `selectors_module.py`: definicao centralizada dos seletores utilizados.
- `utils.py`: funcoes auxiliares (OCR do CAPTCHA, leitura da planilha, pausas, organizacao de arquivos etc.).
- `automacao_selenium.py`: atalho de compatibilidade que simplesmente chama `main.py`.
