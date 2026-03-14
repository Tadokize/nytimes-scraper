import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from config import load_config
from scraper import scrape_nytimes
from excel_writer import save_to_excel


def init_state():
    # carrega configurações e exibe resumo antes de iniciar
    print('=== NYTimes Scraper - REFramework ===')
    config = load_config()
    print(f'Configurações carregadas:')
    print(f'  Frase: {config["search_phrase"]}')
    print(f'  Categorias: {config["categories"]}')
    print(f'  Meses: {config["months"]}')
    return config


def process(config: dict):
    # garante que a pasta de saída existe antes de começar
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
    os.makedirs(f'{output_dir}/images', exist_ok=True)

    print('\nIniciando scraping...')
    results = scrape_nytimes(config, output_dir)
    print(f'{len(results)} notícias encontradas.')

    if results:
        excel_path = os.path.join(output_dir, 'news.xlsx')
        save_to_excel(results, excel_path)
    else:
        print('Nenhuma notícia encontrada no período.')

    return results


def end_state(results: list):
    # resumo final após a execução
    print(f'\n=== Finalizado ===')
    print(f'Total de notícias salvas: {len(results)}')


if __name__ == '__main__':
    # ponto de entrada seguindo a estrutura REFramework: init → process → end
    config = init_state()
    results = process(config)
    end_state(results)