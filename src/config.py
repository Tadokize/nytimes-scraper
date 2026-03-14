import yaml
import os


def load_config():
    # lê o arquivo de configuração na raiz do projeto
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # retorna apenas os campos que o scraper precisa
    return {
        'search_phrase': config.get('search_phrase', ''),
        'categories': config.get('categories', []),
        'months': config.get('months', 1)
    }