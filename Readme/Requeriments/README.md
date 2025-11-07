# Automatizacao de Consulta NF-e (SEFAZ Bahia)

Este projeto inclui um script em Python que automatiza o login no portal da SEFAZ Bahia, preenche o periodo de autorizacao com o primeiro e o ultimo dia do mes anterior e aciona a consulta.

## Dependencias

- Google Chrome instalado
- Python 3.10 ou superior (para o script em Python)
- Node.js 18+ (para a versao em TypeScript)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) instalado e acessível no PATH (necessário para o OCR do CAPTCHA).

Instale as bibliotecas necessarias para cada opcao:

- Python:
  ```bash
  pip install -r requirements.txt
  ```
  (Inclui `pyautogui` e `pywinauto`, utilizados para interagir com janelas nativas do Windows.)
- TypeScript:
  ```bash
  npm install
  ```

## Estrutura da planilha

O arquivo `usuario-senha-nfe.xlsx`, localizado na raiz do projeto, deve ser utilizado pela automacao. Por padrao ele considera:

- Aba: primeira aba (use `--aba` para escolher outra).
- Linha: `2` (primeira linha apos o cabecalho).
- Coluna do usuario: `3`.
- Coluna da senha: `4`.

Use os parametros de linha/coluna caso a planilha seja alterada.

## Execucao

### Script em Python

```bash
python main.py --planilha usuario-senha-nfe.xlsx
```

### Script em TypeScript

```bash
npm run start -- --planilha usuario-senha-nfe.xlsx
```

Parametros uteis (ambos os scripts):

- `--headless`: executa o Chrome sem interface grafica.
- `--linha`, `--coluna-usuario`, `--coluna-senha`, `--aba`: personalizam a leitura da planilha.
- `--espera`: tempo maximo de espera (segundos) para elementos (padrao `20`).
- `--diretorio-captcha`: pasta onde screenshots de CAPTCHA serao salvos.
- `--sequencia-captcha`: pausa a execucao para que o usuario resolva o CAPTCHA manualmente.
- `--fechar-navegador`: fecha o navegador automaticamente ao final (por padrão ele permanece aberto até você confirmar).
- `--ocr-captcha`: tenta ler o CAPTCHA automaticamente (requer Tesseract instalado; falhas voltam para o modo manual).

## Ajustando seletores

- Python: edite `DEFAULT_SELECTORS` em `automacao_selenium.py`.
- TypeScript: ajuste o objeto `SELECTORS` em `src/steps.ts`.

## Observacoes

- O script nao resolve CAPTCHA automaticamente. Use `--sequencia-captcha` para pausar a execucao e concluir manualmente.
- A automacao abre o navegador real (ou modo headless, se configurado). Acompanhe a execucao para validar o resultado.
- Tanto a versao em Python quanto em TypeScript aceitam certificados inseguros automaticamente, ignorando alertas de site nao seguro.
- Caso a janela nativa de certificado apareca, confirme manualmente (o script envia um `ENTER` apos o login, mas nao controla a caixa automaticamente).

## Estrutura do codigo Python

- `main.py`: ponto de entrada e parsing de argumentos.
- `browser.py`: inicializacao do WebDriver e utilitarios de espera.
- `steps.py`: implementa as etapas de acesso, login e preenchimento do periodo.
- `selectors.py`: centraliza os seletores utilizados na automacao.
- `utils.py`: funcoes auxiliares (logs, leitura de planilha, pausa, captcha, etc.).
- `automacao_selenium.py`: atalho de compatibilidade que apenas encaminha para `main.py`.
