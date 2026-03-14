import re
import requests
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from playwright.sync_api import sync_playwright


def get_date_limit(months: int) -> date:
    # 0 ou 1 = mês atual, 2 = mês atual + anterior, e assim por diante
    if months <= 1:
        months = 1
    today = date.today()
    return (today - relativedelta(months=months - 1)).replace(day=1)


def contains_money(text: str) -> bool:
    # detecta valores como $11,1 | US$ 111.111,11 | 11 dollars | 11 dólares
    pattern = r'(\$[\d,\.]+)|(\bUS\$[\d,\.]+)|\b(\d+)\s*(dollars?|dólares?)\b'
    return bool(re.search(pattern, text, re.IGNORECASE))


def count_phrase(text: str, phrase: str) -> int:
    # contagem simples case-insensitive
    return text.lower().count(phrase.lower())


def download_image(url: str, path: str) -> str:
    # salva a imagem localmente, ignora silenciosamente se falhar
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
            return path
    except Exception:
        pass
    return ''


def scrape_nytimes(config: dict, output_dir: str) -> list:
    search_phrase = config['search_phrase']
    categories = config['categories']
    months = config['months']
    date_limit = get_date_limit(months)
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # abre o site
        page.goto('https://www.nytimes.com', timeout=60000)
        page.wait_for_timeout(3000)

        # fecha popup de cookies/privacidade se aparecer
        try:
            page.click('button[data-testid="Accept all-btn"]', timeout=5000)
            page.wait_for_timeout(1000)
        except Exception:
            pass
        try:
            page.click('#fides-button-group button.fides-accept-all-button', timeout=5000)
            page.wait_for_timeout(1000)
        except Exception:
            pass
        try:
            page.evaluate("document.getElementById('fides-overlay')?.remove()")
            page.wait_for_timeout(500)
        except Exception:
            pass

        # abre o campo de busca e pesquisa a frase configurada
        page.click('button[data-testid="search-button"]', timeout=15000)
        page.wait_for_timeout(1000)
        page.fill('input[data-testid="search-input"]', search_phrase)
        page.keyboard.press('Enter')
        page.wait_for_timeout(3000)

        # ordena por mais recente
        page.wait_for_selector('[data-testid="SearchForm-sortBy"]', timeout=10000)
        page.select_option('[data-testid="SearchForm-sortBy"]', 'newest')
        page.wait_for_timeout(2000)

        # aplica filtros de categoria se definidos no config
        if categories:
            try:
                page.click('button[data-testid="search-multiselect-button"]')
                page.wait_for_timeout(1000)
                for category in categories:
                    try:
                        page.click(f'span[data-testid="DropdownLabel"]:has-text("{category}")')
                        page.wait_for_timeout(500)
                    except Exception:
                        pass
                page.keyboard.press('Escape')
                page.wait_for_timeout(2000)
            except Exception:
                pass

        # percorre as páginas de resultado até atingir o limite de data
        while True:
            page.wait_for_selector('[data-testid="search-bodega-result"]', timeout=10000)
            articles = page.query_selector_all('[data-testid="search-bodega-result"]')
            stop = False

            for article in articles:
                try:
                    title_el = article.query_selector('h4')
                    title = title_el.inner_text() if title_el else ''

                    desc_el = article.query_selector('[data-testid="summary-atom"]')
                    description = desc_el.inner_text() if desc_el else ''

                    date_el = article.query_selector('[data-testid="todays-date"]')
                    date_str = date_el.inner_text() if date_el else ''
                    try:
                        article_date = datetime.strptime(date_str, '%B %d, %Y').date()
                    except Exception:
                        article_date = date.today()

                    # para quando a notícia é mais antiga que o período configurado
                    if article_date < date_limit:
                        stop = True
                        break

                    # baixa a imagem e gera um nome de arquivo baseado no título
                    img_el = article.query_selector('img')
                    img_url = img_el.get_attribute('src') if img_el else ''
                    img_filename = ''
                    if img_url:
                        safe_title = re.sub(r'[^a-zA-Z0-9]', '_', title[:40])
                        img_filename = f'{safe_title}.jpg'
                        img_path = f'{output_dir}/images/{img_filename}'
                        download_image(img_url, img_path)

                    combined = f'{title} {description}'
                    phrase_count = count_phrase(combined, search_phrase)
                    has_money = contains_money(combined)

                    results.append({
                        'title': title,
                        'date': str(article_date),
                        'description': description,
                        'image_filename': img_filename,
                        'phrase_count': phrase_count,
                        'has_money': has_money
                    })

                except Exception:
                    continue

            if stop:
                break

            # carrega mais resultados se disponível
            try:
                next_btn = page.query_selector('button[data-testid="search-show-more-button"]')
                if next_btn:
                    next_btn.click()
                    page.wait_for_timeout(3000)
                else:
                    break
            except Exception:
                break

        browser.close()

    return results