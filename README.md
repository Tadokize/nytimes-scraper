# nytimes-scraper

Script de automação para extração de notícias do New York Times. Desenvolvido em Python com Playwright para navegação, openpyxl para geração do Excel e Docker para execução isolada.

## O que faz

- Busca notícias por frase de pesquisa
- Filtra por categoria e período (meses)
- Ordena os resultados por mais recentes
- Salva título, data, descrição e imagem de cada notícia
- Gera um arquivo Excel com contagem da frase pesquisada e detecção de valores monetários

## Configuração

Edite o `config.yaml` antes de rodar:
```yaml
search_phrase: "artificial intelligence"  # frase que será buscada
categories:                               # deixe vazio [] para sem filtro
  - "Technology"
months: 2                                 # 1 = mês atual, 2 = atual + anterior
```

## Rodando com Docker
```bash
docker build -t nytimes-scraper .
docker run -v $(pwd)/output:/app/output nytimes-scraper
```

O resultado fica disponível na pasta `output/` do seu sistema.

## Rodando localmente
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
python3 src/main.py
```

## Output

Após a execução, a pasta `output/` conterá:

- `news.xlsx` — planilha com todas as notícias coletadas
- `images/` — imagens baixadas de cada notícia

## Requisitos

- Docker, ou
- Python 3.12+ com WSL2/Linux