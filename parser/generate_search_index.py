import os
import re
import json
from bs4 import BeautifulSoup

WIKI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

CATEGORY_MAP = {
    'colfort': 'Колфорт',
    'elter': 'Эльтер',
    'rp': 'Руины Полнолуния',
    'illumina': 'Иллюмина',
    'hram-meteos': 'Храм Метеоса',
    'acra': 'Акра',
    'locality': 'Деревни',
    'items': 'Предметы',
    'guids': 'Гайды',
}


def extract_title(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        title_el = soup.select_one('.inner-page__title-text, h1.inner-page__title-text, h1')
        if title_el:
            title = title_el.get_text(strip=True)
            title = re.sub(r'\s*[—-]\s*База знаний.*$', '', title)
            return title
        
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            title = re.sub(r'\s*[—-]\s*База знаний.*$', '', title)
            title = re.sub(r'\s*[—-]\s*R2 Online.*$', '', title)
            return title
        
        return None
    except Exception as e:
        print(f"[ERROR] {filepath}: {e}")
        return None


def get_category(filepath):
    rel_path = os.path.relpath(filepath, WIKI_DIR)
    parts = rel_path.replace('\\', '/').split('/')
    
    if len(parts) > 1:
        folder = parts[0]
        return CATEGORY_MAP.get(folder, folder.capitalize())
    
    return 'Общее'


def scan_html_files():
    index = []
    
    for root, dirs, files in os.walk(WIKI_DIR):
        dirs[:] = [d for d in dirs if d not in ['parser', '__pycache__', 'node_modules', 'css', 'images', 'fonts', 'libs', 'plugins']]
        
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, WIKI_DIR).replace('\\', '/')
                
                title = extract_title(filepath)
                if not title:
                    title = file.replace('.html', '').replace('_', ' ').replace('-', ' ').title()
                
                category = get_category(filepath)
                
                url = './' + rel_path
                
                index.append({
                    'title': title,
                    'url': url,
                    'category': category
                })
                print(f"[OK] {title} ({category})")
    
    return index


def generate_js_index(index):
    js_items = []
    for item in sorted(index, key=lambda x: (x['category'], x['title'])):
        js_items.append(f'        {{ title: "{item["title"]}", url: "{item["url"]}", category: "{item["category"]}" }}')
    
    return ',\n'.join(js_items)


def main():
    print("="*60)
    print("     SEARCH INDEX GENERATOR")
    print("="*60)
    
    print("\n[SCAN] Scanning HTML files...")
    index = scan_html_files()
    
    print(f"\n[DONE] Found {len(index)} pages")
    
    json_path = os.path.join(WIKI_DIR, 'search-index.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"[SAVE] JSON: search-index.json")
    
    js_code = generate_js_index(index)
    
    print("\n" + "="*60)
    print("JavaScript index (copy to wiki.html):")
    print("="*60)
    print(f"\nconst wikiSearchIndex = [\n{js_code}\n    ];")
    
    js_path = os.path.join(WIKI_DIR, 'search-index.js')
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(f"const wikiSearchIndex = [\n{js_code}\n];")
    print(f"\n[SAVE] JS: search-index.js")


if __name__ == '__main__':
    main()
