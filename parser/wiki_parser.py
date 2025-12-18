from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import os
import time

BASE_URL = "https://r2online.ru"
WIKI_DIR = os.path.join(os.path.dirname(__file__), '..')

driver = None


def get_driver():
    global driver
    if driver is None:
        print("🌐 Запускаю браузер...")
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-infobars')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def close_driver():
    global driver
    if driver:
        driver.quit()
        driver = None



def make_absolute_url(url):
    if not url:
        return url
    if url.startswith('http'):
        return url
    if url.startswith('//'):
        return 'https:' + url
    if url.startswith('/'):
        return BASE_URL + url
    return BASE_URL + '/' + url


def transliterate(text):
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        ' ': '_', '-': '_', '.': '', '«': '', '»': '', '"': '', "'": '',
        '(': '', ')': '', ':': '', '/': '_', '\\': '_'
    }
    result = ''
    for char in text.lower():
        result += translit_dict.get(char, char)
    result = re.sub(r'[^a-z0-9_]', '', result)
    result = re.sub(r'_+', '_', result)
    return result.strip('_')


def fetch_page(url):
    print(f"  📥 Загружаю: {url}")
    try:
        browser = get_driver()
        browser.get(url)
        try:
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.article, .catalog-item, .functional-table, table, .post-item'))
            )
        except:
            pass
        time.sleep(2)
        return browser.page_source
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return None


def save_file(filename, content, output_dir):
    full_dir = os.path.join(WIKI_DIR, output_dir)
    os.makedirs(full_dir, exist_ok=True)
    path = os.path.join(full_dir, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✅ Сохранено: {output_dir}/{filename}")
    return path



GUIDE_CATALOG_TEMPLATE = '''<!DOCTYPE html>
<html lang="ru" class="js">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — База знаний R2 Online</title>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap" rel="stylesheet">

    <link href="../css/wiki.css" rel="stylesheet">
    <link href="../css/core.css" rel="stylesheet">
    <link href="../css/bootstrap.min.css" rel="stylesheet">
    <link href="../css/style.css" rel="stylesheet">
    <link href="../css/addition.css" rel="stylesheet">
    
    <style>
        .guide-grid {{ display: flex; flex-wrap: wrap; gap: 20px; margin-top: 20px; }}
        .guide-card {{ 
            background: rgba(255,255,255,0.03); 
            border-radius: 8px; 
            overflow: hidden; 
            width: calc(50% - 10px);
            transition: all 0.3s;
        }}
        .guide-card:hover {{ background: rgba(255,255,255,0.06); transform: translateY(-2px); }}
        .guide-card a {{ display: flex; text-decoration: none; color: inherit; }}
        .guide-card__img {{ width: 200px; min-height: 120px; flex-shrink: 0; }}
        .guide-card__img img {{ width: 100%; height: 100%; object-fit: cover; }}
        .guide-card__content {{ padding: 15px; flex: 1; }}
        .guide-card__title {{ font-size: 16px; font-weight: bold; color: #fff; margin-bottom: 8px; }}
        .guide-card__desc {{ font-size: 13px; color: #aaa; line-height: 1.4; }}
        @media (max-width: 900px) {{
            .guide-card {{ width: 100%; }}
        }}
    </style>
</head>

<body>
    <div class="wrapper wrapper--forum">
        <main class="main">
            <div class="content-area flex-sbs">
                <div class="wiki">
                    <div class="wiki__nav flex-sbc">
                        <div class="colfort-backlink">
                            <a href="../wiki.html">База знаний</a> &gt; {breadcrumbs}
                        </div>
                    </div>

                    <div class="inner-page__title wiki-page__title">
                        <h1 class="inner-page__title-text">{title_upper}</h1>
                    </div>

                    <div class="wiki__container flex-sbs">
                        <div class="wiki__content" style="width: 100%; padding: 20px 30px;">
                            <div class="guide-grid">
{cards}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
'''

GUIDE_CARD_TEMPLATE = '''                                <div class="guide-card">
                                    <a href="{link}">
                                        <div class="guide-card__img">
                                            <img src="{img}" alt="{title}">
                                        </div>
                                        <div class="guide-card__content">
                                            <div class="guide-card__title">{title}</div>
                                            <div class="guide-card__desc">{desc}</div>
                                        </div>
                                    </a>
                                </div>'''

GUIDE_PAGE_TEMPLATE = '''<!DOCTYPE html>
<html lang="ru" class="js">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — База знаний R2 Online</title>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap" rel="stylesheet">

    <link href="../css/wiki.css" rel="stylesheet">
    <link href="../css/core.css" rel="stylesheet">
    <link href="../css/bootstrap.min.css" rel="stylesheet">
    <link href="../css/style.css" rel="stylesheet">
    <link href="../css/addition.css" rel="stylesheet">
    
    <style>
        .guide-content {{ padding: 20px 0; line-height: 1.7; color: #ddd; }}
        .guide-content h2 {{ font-size: 22px; margin: 30px 0 15px; color: #fff; border-bottom: 1px solid #444; padding-bottom: 10px; }}
        .guide-content h3 {{ font-size: 18px; margin: 25px 0 12px; color: #fff; }}
        .guide-content p {{ margin: 12px 0; }}
        .guide-content ul, .guide-content ol {{ margin: 12px 0 12px 25px; }}
        .guide-content li {{ margin: 6px 0; }}
        .guide-content a {{ color: #4a9eff; }}
        .guide-content a:hover {{ text-decoration: underline; }}
        .guide-content img {{ max-width: 100%; height: auto; border-radius: 4px; }}
        
        /* Спойлеры */
        .spoiler {{ margin: 20px 0; background: rgba(0,0,0,0.3); border-radius: 8px; overflow: hidden; }}
        .spoiler__title {{ 
            padding: 12px 20px; 
            background: rgba(255,255,255,0.1); 
            cursor: pointer; 
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .spoiler__title:hover {{ background: rgba(255,255,255,0.15); }}
        .spoiler__title::after {{ content: '▼'; font-size: 12px; transition: transform 0.3s; }}
        .spoiler.open .spoiler__title::after {{ transform: rotate(180deg); }}
        .spoiler__content {{ display: none; padding: 20px; }}
        .spoiler.open .spoiler__content {{ display: block; }}
        
        /* Таблицы */
        .guide-content table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        .guide-content th, .guide-content td {{ padding: 10px 12px; border: 1px solid #444; text-align: left; }}
        .guide-content th {{ background: rgba(255,255,255,0.1); }}
        .guide-content tr:hover {{ background: rgba(255,255,255,0.03); }}
        .guide-content .tr-header {{ background: rgba(74, 158, 255, 0.15); }}
        .guide-content .tr-odd {{ background: rgba(255,255,255,0.05); }}
        
        /* Item icons */
        .layout-item-icon {{ display: inline-flex; align-items: center; margin: 2px; }}
        .layout-item-icon img {{ width: 32px; height: 32px; border-radius: 4px; }}
        .base-item-icon {{ width: 32px; height: 32px; }}
        .small-icon {{ width: 24px; height: 24px; }}
        .item-text {{ margin-left: 5px; }}
        
        /* Списки контента */
        .content-list {{ list-style: decimal; margin: 15px 0 15px 30px; }}
        .content-list li {{ margin: 8px 0; }}
        .link-in-top {{ color: #4a9eff; }}
        
        /* Таблицы квестов */
        .table-quest {{ width: 100%; }}
        .table-quest td {{ vertical-align: top; }}
        
        /* Кнопка наверх */
        .back-to-top {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            background: rgba(74, 158, 255, 0.8);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            text-decoration: none;
            opacity: 0.7;
            transition: opacity 0.3s;
        }}
        .back-to-top:hover {{ opacity: 1; }}
    </style>
</head>

<body>
    <div class="wrapper wrapper--forum">
        <main class="main">
            <div class="content-area flex-sbs">
                <div class="wiki">
                    <div class="wiki__nav flex-sbc">
                        <div class="colfort-backlink">
                            <a href="../wiki.html">База знаний</a> &gt; {breadcrumbs}
                        </div>
                    </div>

                    <div class="inner-page__title wiki-page__title">
                        <h1 class="inner-page__title-text">{title}</h1>
                    </div>

                    <div class="wiki__container flex-sbs">
                        <div class="wiki__content" style="width: 100%; padding: 20px 30px;">
                            <div class="guide-content">
{content}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
    
    <script>
        // Спойлеры
        document.querySelectorAll('.spoiler__title').forEach(function(title) {{
            title.addEventListener('click', function() {{
                this.parentElement.classList.toggle('open');
            }});
        }});
    </script>
</body>
</html>
'''


def parse_guides_catalog(soup):
    guides = []
    
    for item in soup.select('.post-item.location-item'):
        link_el = item.select_one('h3 a, .post-layout h3 a')
        img_el = item.select_one('img')
        desc_el = item.select_one('.post-description')
        
        if link_el:
            title = link_el.get_text(strip=True)
            href = link_el.get('href', '')
            img = make_absolute_url(img_el.get('src')) if img_el else ''
            desc = desc_el.get_text(strip=True) if desc_el else ''
            
            if title:
                guides.append({
                    'title': title,
                    'img': img,
                    'desc': desc[:100] + '...' if len(desc) > 100 else desc,
                    'original_link': href,
                    'filename': transliterate(title) + '.html'
                })
    
    return guides


def parse_guide_content(soup):
    content_el = soup.select_one('.article__text, .blog-content-page')
    
    if not content_el:
        return ''
    
    html = str(content_el)
    
    def fix_img_src(match):
        src = match.group(1)
        return f'src="{make_absolute_url(src)}"'
    
    html = re.sub(r'src="([^"]+)"', fix_img_src, html)
    
    def fix_href(match):
        href = match.group(1)
        if href.startswith('#') or href.startswith('javascript:'):
            return match.group(0)
        if href.startswith('/wiki/') or href.startswith('http'):
            return f'href="{make_absolute_url(href)}"'
        return match.group(0)
    
    html = re.sub(r'href="([^"]+)"', fix_href, html)
    
    return html


def scrape_guides_with_pagination(url):
    all_guides = []
    browser = get_driver()
    current_page = 1
    
    while True:
        page_url = f"{url}?page={current_page}" if current_page > 1 else url
        print(f"  📄 Страница {current_page}: {page_url}")
        
        browser.get(page_url)
        time.sleep(2)
        
        soup = BeautifulSoup(browser.page_source, 'lxml')
        guides = parse_guides_catalog(soup)
        
        if not guides:
            break
        
        all_guides.extend(guides)
        print(f"     Найдено: {len(guides)} гайдов")
        
        next_link = soup.select_one('.pagination a[rel="next"], .pagination__num:last-child:not(.active)')
        if not next_link:
            break
        
        current_page += 1
        
        if current_page > 20:
            break
    
    return all_guides


def scrape_guide_page(url, title, filename, breadcrumb_path, output_dir='guids'):
    html = fetch_page(url)
    if not html:
        return False
    
    soup = BeautifulSoup(html, 'lxml')
    
    title_el = soup.select_one('.article__title')
    if title_el:
        title = title_el.get_text(strip=True)
    
    content = parse_guide_content(soup)
    
    if not content:
        print(f"   ⚠️ Контент не найден")
        return False
    
    page_html = GUIDE_PAGE_TEMPLATE.format(
        title=title,
        breadcrumbs=breadcrumb_path,
        content=content
    )
    
    save_file(filename, page_html, output_dir)
    return True


def scrape_guides_section(url, title, output_filename, breadcrumb_path, output_dir='guids'):
    print(f"\n{'='*60}")
    print(f"РАЗДЕЛ ГАЙДОВ: {title}")
    print(f"URL: {url}")
    print('='*60)
    
    guides = scrape_guides_with_pagination(url)
    
    if not guides:
        print("❌ Гайды не найдены!")
        return False
    
    print(f"\n📋 Найдено всего {len(guides)} гайдов:")
    for g in guides:
        print(f"   • {g['title']}")
    
    cards = []
    for g in guides:
        cards.append(GUIDE_CARD_TEMPLATE.format(
            link=g['filename'],
            img=g['img'],
            title=g['title'],
            desc=g['desc']
        ))
    
    catalog_html = GUIDE_CATALOG_TEMPLATE.format(
        title=title,
        title_upper=title.upper(),
        breadcrumbs=breadcrumb_path,
        cards='\n'.join(cards)
    )
    
    save_file(output_filename, catalog_html, output_dir)
    
    print(f"\n🔄 Обрабатываю гайды...")
    for i, guide in enumerate(guides, 1):
        print(f"\n[{i}/{len(guides)}] {guide['title']}")
        guide_url = make_absolute_url(guide['original_link'])
        new_breadcrumb = f'{breadcrumb_path} &gt; <a href="{output_filename}">{title}</a>'
        scrape_guide_page(guide_url, guide['title'], guide['filename'], new_breadcrumb, output_dir)
        time.sleep(1)
    
    print(f"\n✅ Раздел '{title}' готов!")
    return True



ITEMS_CATALOG_TEMPLATE = '''<!DOCTYPE html>
<html lang="ru" class="js">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — База знаний R2 Online</title>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap" rel="stylesheet">

    <link href="../css/wiki.css" rel="stylesheet">
    <link href="../css/core.css" rel="stylesheet">
    <link href="../css/bootstrap.min.css" rel="stylesheet">
    <link href="../css/style.css" rel="stylesheet">
    <link href="../css/addition.css" rel="stylesheet">
</head>

<body>
    <div class="wrapper wrapper--forum">
        <main class="main">
            <div class="content-area flex-sbs">
                <div class="wiki">
                    <div class="wiki__nav flex-sbc">
                        <div class="colfort-backlink">
                            <a href="../wiki.html">База знаний</a> &gt; {breadcrumbs}
                        </div>
                    </div>

                    <div class="inner-page__title wiki-page__title">
                        <h1 class="inner-page__title-text">{title_upper}</h1>
                    </div>

                    <div class="wiki__container flex-sbs">
                        <div class="wiki__content" style="width: 100%; padding: 20px 30px;">
                            <div class="row">
{cards}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
'''

ITEMS_CARD_TEMPLATE = '''                                <div class="col col-1-4">
                                    <a href="{link}" class="dungeon-card item-card">
                                        <div class="dungeon-card__img">
                                            <img src="{img}" alt="{title}">
                                        </div>
                                        <div class="dungeon-card__title">{title}</div>
                                    </a>
                                </div>'''

ITEMS_LIST_TEMPLATE = '''<!DOCTYPE html>
<html lang="ru" class="js">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — База знаний R2 Online</title>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap" rel="stylesheet">

    <link href="../css/wiki.css" rel="stylesheet">
    <link href="../css/core.css" rel="stylesheet">
    <link href="../css/bootstrap.min.css" rel="stylesheet">
    <link href="../css/style.css" rel="stylesheet">
    <link href="../css/addition.css" rel="stylesheet">
    
    <style>
        .items-table {{ width: 100%; border-collapse: collapse; }}
        .items-table th {{ padding: 12px 10px; border-bottom: 2px solid #444; text-align: left; color: #888; font-weight: normal; }}
        .items-table td {{ padding: 10px; border-bottom: 1px solid #333; vertical-align: middle; }}
        .items-table tr:hover {{ background: rgba(255,255,255,0.03); }}
        .item-icon {{ width: 40px; height: 40px; border-radius: 4px; }}
        .item-name {{ font-size: 14px; }}
        .item-desc {{ font-size: 12px; color: #999; line-height: 1.4; }}
        .status-1 {{ color: #fff; }}
        .status-2 {{ color: #4a9eff; }}
        .status-3 {{ color: #b048f8; }}
        .icon-class {{ width: 24px; height: 24px; display: inline-block; background-size: contain; background-repeat: no-repeat; }}
        .cl-1 {{ background-image: url('https://r2online.ru/images/icons/class-1.png'); }}
        .cl-2 {{ background-image: url('https://r2online.ru/images/icons/class-2.png'); }}
        .cl-3 {{ background-image: url('https://r2online.ru/images/icons/class-3.png'); }}
        .cl-4 {{ background-image: url('https://r2online.ru/images/icons/class-4.png'); }}
        .cl-all {{ background-image: url('https://r2online.ru/images/icons/class-all.png'); }}
        .total-count {{ margin: 20px 0; padding: 10px 15px; background: rgba(255,255,255,0.05); border-radius: 4px; display: inline-block; }}
    </style>
</head>

<body>
    <div class="wrapper wrapper--forum">
        <main class="main">
            <div class="content-area flex-sbs">
                <div class="wiki">
                    <div class="wiki__nav flex-sbc">
                        <div class="colfort-backlink">
                            <a href="../wiki.html">База знаний</a> &gt; {breadcrumbs}
                        </div>
                    </div>

                    <div class="inner-page__title wiki-page__title">
                        <h1 class="inner-page__title-text">{title_upper}</h1>
                    </div>

                    <div class="wiki__container flex-sbs">
                        <div class="wiki__content" style="width: 100%; padding: 20px 30px;">
                            
                            <div class="total-count">📦 Всего предметов: {total}</div>

                            <div class="table-box">
                                <table class="table items-table">
                                    <thead>
                                        <tr>
                                            <th style="width: 50px;"></th>
                                            <th style="min-width: 150px;">Название</th>
                                            <th>Описание</th>
                                            <th style="width: 60px; text-align: center;">Вес</th>
                                            <th style="width: 50px; text-align: center;">Класс</th>
                                        </tr>
                                    </thead>
                                    <tbody>
{items}
                                    </tbody>
                                </table>
                            </div>

                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
'''

ITEM_ROW_TEMPLATE = '''                                        <tr>
                                            <td><img class="item-icon" src="{icon}" alt="{name}"></td>
                                            <td class="item-name"><span class="{status_class}">{name}</span></td>
                                            <td class="item-desc">{desc}</td>
                                            <td style="text-align:center;">{weight}</td>
                                            <td style="text-align:center;"><div class="icon-class {class_icon}"></div></td>
                                        </tr>'''



def parse_items_catalog(soup):
    categories = []
    
    for item in soup.select('.col-md-3.col-xs-3'):
        link = item.select_one('a.catalog-item')
        img = item.select_one('img')
        span = item.select_one('span')
        
        if link and span:
            title = span.get_text(strip=True)
            if title and title.strip() and title != '\xa0':
                categories.append({
                    'title': title,
                    'img': make_absolute_url(img.get('src')) if img else '',
                    'original_link': link.get('href'),
                    'filename': transliterate(title) + '.html'
                })
    
    return categories


def parse_items_from_table(soup):
    items = []
    
    for row in soup.select('table.functional-table tbody tr, table.mobs-list tbody tr'):
        cells = row.select('td')
        if len(cells) >= 4:
            item = {
                'icon': '',
                'name': '',
                'desc': '',
                'weight': '',
                'class': 'cl-all',
                'status_class': 'status-1'
            }
            
            icon_img = cells[0].select_one('img')
            if icon_img:
                item['icon'] = make_absolute_url(icon_img.get('src'))
            
            name_span = cells[1].select_one('span')
            if name_span:
                item['name'] = name_span.get_text(strip=True)
                classes = name_span.get('class', [])
                if 'status-3' in classes:
                    item['status_class'] = 'status-3'
                elif 'status-2' in classes:
                    item['status_class'] = 'status-2'
            
            if len(cells) > 2:
                desc = cells[2].get_text(strip=True)
                item['desc'] = desc[:200] + '...' if len(desc) > 200 else desc
            
            if len(cells) > 3:
                item['weight'] = cells[3].get_text(strip=True)
            
            if len(cells) > 4:
                class_div = cells[4].select_one('.icon-class')
                if class_div:
                    for c in class_div.get('class', []):
                        if c.startswith('cl-'):
                            item['class'] = c
                            break
            
            if item['name']:
                items.append(item)
    
    return items


def scrape_items_with_pagination(url):
    all_items = []
    browser = get_driver()
    
    print(f"  📥 Загружаю: {url}")
    browser.get(url)
    time.sleep(2)
    
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'table.functional-table, table.mobs-list'))
        )
    except:
        print("   ⚠️ Таблица не найдена")
        return []
    
    soup = BeautifulSoup(browser.page_source, 'lxml')
    page_buttons = soup.select('.dataTables_paginate .pagination .paginate_button:not(.previous):not(.next)')
    total_pages = len(page_buttons) if page_buttons else 1
    print(f"   📄 Найдено страниц: {total_pages}")
    
    page = 1
    while True:
        soup = BeautifulSoup(browser.page_source, 'lxml')
        items = parse_items_from_table(soup)
        
        if items:
            all_items.extend(items)
            print(f"   📄 Страница {page}: {len(items)} предметов")
        
        try:
            next_btn = browser.find_element(By.CSS_SELECTOR, '.dataTables_paginate .next:not(.disabled)')
            if not next_btn:
                break
            
            next_btn.click()
            time.sleep(1.5)
            page += 1
            
            if page > 100:
                print("   ⚠️ Достигнут лимит страниц (100)")
                break
                
        except Exception as e:
            break
    
    return all_items


def generate_items_catalog_html(categories, title, breadcrumbs):
    cards = []
    for cat in categories:
        cards.append(ITEMS_CARD_TEMPLATE.format(
            link=cat['filename'],
            img=cat['img'],
            title=cat['title']
        ))
    
    return ITEMS_CATALOG_TEMPLATE.format(
        title=title,
        title_upper=title.upper(),
        breadcrumbs=breadcrumbs,
        cards='\n'.join(cards)
    )


def generate_items_list_html(items, title, breadcrumbs):
    rows = []
    for item in items:
        rows.append(ITEM_ROW_TEMPLATE.format(
            icon=item['icon'],
            name=item['name'],
            status_class=item.get('status_class', 'status-1'),
            desc=item['desc'],
            weight=item['weight'],
            class_icon=item.get('class', 'cl-all')
        ))
    
    return ITEMS_LIST_TEMPLATE.format(
        title=title,
        title_upper=title.upper(),
        breadcrumbs=breadcrumbs,
        items='\n'.join(rows),
        total=len(items)
    )


def scrape_items_section(url, title, output_filename, breadcrumb_path, output_dir='items'):
    print(f"\n{'='*60}")
    print(f"РАЗДЕЛ: {title}")
    print(f"URL: {url}")
    print('='*60)
    
    html = fetch_page(url)
    if not html:
        print("❌ Не удалось загрузить!")
        return False
    
    soup = BeautifulSoup(html, 'lxml')
    
    categories = parse_items_catalog(soup)
    
    if categories:
        print(f"\n📋 Найдено {len(categories)} категорий:")
        for cat in categories:
            print(f"   • {cat['title']}")
        
        catalog_html = generate_items_catalog_html(categories, title, breadcrumb_path)
        save_file(output_filename, catalog_html, output_dir)
        
        for i, cat in enumerate(categories, 1):
            print(f"\n[{i}/{len(categories)}] {cat['title']}")
            cat_url = make_absolute_url(cat['original_link'])
            new_breadcrumb = f'{breadcrumb_path} &gt; <a href="{output_filename}">{title}</a>'
            scrape_items_section(cat_url, cat['title'], cat['filename'], new_breadcrumb, output_dir)
            time.sleep(1)
    else:
        print(f"\n📦 Загружаю список предметов...")
        items = scrape_items_with_pagination(url)
        
        if items:
            print(f"   📊 Всего предметов: {len(items)}")
            list_html = generate_items_list_html(items, title, breadcrumb_path)
            save_file(output_filename, list_html, output_dir)
        else:
            print("   ⚠️ Предметы не найдены")
    
    print(f"\n✅ Раздел '{title}' готов!")
    return True



GUIDE_SECTIONS = {
    '1': {'url': 'https://r2online.ru/wiki/guids/locations', 'title': 'Особенности локаций', 'file': 'locations.html'},
    '2': {'url': 'https://r2online.ru/wiki/guids/boss', 'title': 'Боссы', 'file': 'boss.html'},
    '3': {'url': 'https://r2online.ru/wiki/guids/unique-items', 'title': 'Уникальные предметы', 'file': 'unique-items.html'},
    '4': {'url': 'https://r2online.ru/wiki/guids/craft', 'title': 'Изготовление', 'file': 'craft.html'},
    '5': {'url': 'https://r2online.ru/wiki/guids/guilds', 'title': 'Гильдии', 'file': 'guilds.html'},
    '6': {'url': 'https://r2online.ru/wiki/guids/events', 'title': 'Мероприятия', 'file': 'events.html'},
    '7': {'url': 'https://r2online.ru/wiki/guids/trade', 'title': 'Торговля', 'file': 'trade.html'},
    '8': {'url': 'https://r2online.ru/wiki/guids/client', 'title': 'Функционал клиента', 'file': 'client.html'},
    '9': {'url': 'https://r2online.ru/wiki/guids/account', 'title': 'Аккаунт и безопасность', 'file': 'account.html'},
    '10': {'url': 'https://r2online.ru/wiki/guids/other', 'title': 'Другое', 'file': 'other.html'},
}

ITEMS_SECTIONS = {
    '1': {'url': 'https://r2online.ru/wiki/base/section/15', 'title': 'Экипировка', 'file': 'ekipirovka.html'},
    '2': {'url': 'https://r2online.ru/wiki/base/section/1', 'title': 'Материалы', 'file': 'materialy.html'},
    '3': {'url': 'https://r2online.ru/wiki/base/section/12', 'title': 'Книги', 'file': 'knigi.html'},
    '4': {'url': 'https://r2online.ru/wiki/base/section/17', 'title': 'Руны', 'file': 'runy.html'},
    '5': {'url': 'https://r2online.ru/wiki/base/section/7', 'title': 'Другое', 'file': 'drugoe.html'},
    '6': {'url': 'https://r2online.ru/wiki/base/section/8', 'title': 'Ивенты', 'file': 'iventy.html'},
}


def show_guides_menu():
    print(f"\n{'='*60}")
    print("     📖 ГАЙДЫ")
    print('='*60)
    
    print("\nДоступные разделы:")
    for key, sec in GUIDE_SECTIONS.items():
        print(f"  {key}. {sec['title']}")
    print("  ─────────────────────")
    print("  11. Свой URL")
    print("  12. 🚀 Скрапить ВСЁ")
    print("  0. Назад")
    
    choice = input("\nВыбор: ").strip()
    
    if choice == '0':
        return
    
    if choice == '12':
        confirm = input("Это займёт время. Продолжить? (y/n): ").strip().lower()
        if confirm == 'y':
            for key, sec in GUIDE_SECTIONS.items():
                scrape_guides_section(sec['url'], sec['title'], sec['file'], 'Гайды')
        return
    
    if choice == '11':
        url = input("URL раздела: ").strip()
        title = input("Название: ").strip()
        filename = input(f"Файл [{transliterate(title)}.html]: ").strip()
        if not filename:
            filename = transliterate(title) + '.html'
        scrape_guides_section(url, title, filename, 'Гайды')
        return
    
    if choice in GUIDE_SECTIONS:
        sec = GUIDE_SECTIONS[choice]
        scrape_guides_section(sec['url'], sec['title'], sec['file'], 'Гайды')


def show_items_menu():
    print(f"\n{'='*60}")
    print("     📦 ПРЕДМЕТЫ")
    print('='*60)
    
    print("\nДоступные разделы:")
    for key, sec in ITEMS_SECTIONS.items():
        print(f"  {key}. {sec['title']}")
    print("  ─────────────────────")
    print("  7. Свой URL")
    print("  8. 🚀 Скрапить ВСЁ")
    print("  0. Назад")
    
    choice = input("\nВыбор: ").strip()
    
    if choice == '0':
        return
    
    if choice == '8':
        confirm = input("Это займёт время. Продолжить? (y/n): ").strip().lower()
        if confirm == 'y':
            for key, sec in ITEMS_SECTIONS.items():
                scrape_items_section(sec['url'], sec['title'], sec['file'], 'Предметы')
        return
    
    if choice == '7':
        url = input("URL раздела: ").strip()
        title = input("Название: ").strip()
        filename = input(f"Файл [{transliterate(title)}.html]: ").strip()
        if not filename:
            filename = transliterate(title) + '.html'
        scrape_items_section(url, title, filename, 'Предметы')
        return
    
    if choice in ITEMS_SECTIONS:
        sec = ITEMS_SECTIONS[choice]
        scrape_items_section(sec['url'], sec['title'], sec['file'], 'Предметы')


def main():
    print("="*60)
    print("     R2 ONLINE WIKI AUTO PARSER")
    print("="*60)
    
    while True:
        print("\n📍 Выберите раздел:")
        print("  1. 📖 Гайды")
        print("  2. 📦 Предметы")
        print("  0. Выход")
        
        choice = input("\nВыбор: ").strip()
        
        try:
            if choice == '0':
                break
            elif choice == '1':
                show_guides_menu()
            elif choice == '2':
                show_items_menu()
            else:
                print("Неверный выбор!")
        except KeyboardInterrupt:
            print("\n\nПрервано")
            break
    
    close_driver()


if __name__ == '__main__':
    main()
