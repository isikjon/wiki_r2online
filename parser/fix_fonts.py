
import os
import re

WIKI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def fix_html_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        rel_path = os.path.relpath(filepath, WIKI_DIR)
        depth = rel_path.count(os.sep)
        
        if depth == 0:
            css_prefix = './css/'
        else:
            css_prefix = '../' * depth + 'css/'
        
        style_css_link = f'<link href="{css_prefix}style.css" rel="stylesheet">'
        
        if 'style.css' not in content:
            patterns = [
                (r'(<link[^>]*bootstrap\.min\.css[^>]*>)', r'\1\n    ' + style_css_link),
                (r'(<link[^>]*core\.css[^>]*>)', r'\1\n    ' + style_css_link),
                (r'(<link[^>]*wiki\.css[^>]*>)', r'\1\n    ' + style_css_link),
            ]
            
            for pattern, replacement in patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content, count=1)
                    break
            else:
                content = content.replace('</head>', f'    {style_css_link}\n</head>')
        
        if 'fonts.googleapis.com' not in content:
            google_fonts = '''    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap" rel="stylesheet">
'''
            content = content.replace('<head>', '<head>\n' + google_fonts)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"[ERROR] {filepath}: {e}")
        return False


def fix_all_html():
    fixed = 0
    skipped = 0
    
    for root, dirs, files in os.walk(WIKI_DIR):
        if 'parser' in root or '__pycache__' in root:
            continue
        
        dirs[:] = [d for d in dirs if d not in ['parser', '__pycache__', 'node_modules']]
            
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, WIKI_DIR)
                
                if fix_html_file(filepath):
                    print(f"[OK] Updated: {rel_path}")
                    fixed += 1
                else:
                    skipped += 1
    
    return fixed, skipped


def main():
    print("="*60)
    print("     FONT FIX SCRIPT - Adding style.css")
    print("="*60)
    print(f"Wiki dir: {WIKI_DIR}")
    
    print("\n[HTML] Checking all HTML files...")
    fixed, skipped = fix_all_html()
    
    print("\n" + "="*60)
    print(f"[OK] Updated: {fixed} files")
    print(f"[SKIP] Already correct: {skipped} files")
    print("="*60)


if __name__ == '__main__':
    main()
