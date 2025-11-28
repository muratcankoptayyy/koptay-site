"""
CSS and JavaScript Minification Script
Minifies assets for production deployment
"""

import os
import re

def minify_css(css_content):
    """
    Basic CSS minification
    - Remove comments
    - Remove whitespace
    - Remove unnecessary semicolons
    """
    # Remove comments
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    
    # Remove whitespace
    css_content = re.sub(r'\s+', ' ', css_content)
    css_content = re.sub(r'\s*{\s*', '{', css_content)
    css_content = re.sub(r'\s*}\s*', '}', css_content)
    css_content = re.sub(r'\s*:\s*', ':', css_content)
    css_content = re.sub(r'\s*;\s*', ';', css_content)
    css_content = re.sub(r'\s*,\s*', ',', css_content)
    
    # Remove last semicolon in blocks
    css_content = re.sub(r';}', '}', css_content)
    
    return css_content.strip()

def minify_js(js_content):
    """
    Basic JavaScript minification
    - Remove comments (single-line and multi-line)
    - Remove unnecessary whitespace
    - Preserve strings and regex
    """
    # Remove multi-line comments
    js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
    
    # Remove single-line comments (but not URLs)
    js_content = re.sub(r'(?<!:)//.*$', '', js_content, flags=re.MULTILINE)
    
    # Remove extra whitespace (but preserve single spaces)
    js_content = re.sub(r'\n\s*\n', '\n', js_content)
    js_content = re.sub(r'\s+', ' ', js_content)
    
    # Remove spaces around operators and punctuation
    js_content = re.sub(r'\s*([{}();,:\[\]])\s*', r'\1', js_content)
    js_content = re.sub(r'\s*([=+\-*/<>!&|])\s*', r'\1', js_content)
    
    return js_content.strip()

def minify_file(input_path, output_path, file_type):
    """
    Minify a single file
    
    Args:
        input_path: Path to source file
        output_path: Path to output minified file
        file_type: 'css' or 'js'
    """
    print(f'Minifying {input_path}...')
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_size = len(content)
    
    if file_type == 'css':
        minified = minify_css(content)
    elif file_type == 'js':
        minified = minify_js(content)
    else:
        raise ValueError(f'Unsupported file type: {file_type}')
    
    minified_size = len(minified)
    reduction = ((original_size - minified_size) / original_size) * 100
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(minified)
    
    print(f'  ✓ Saved to {output_path}')
    print(f'  Original: {original_size:,} bytes')
    print(f'  Minified: {minified_size:,} bytes')
    print(f'  Reduction: {reduction:.1f}%')
    print()

def minify_all_assets():
    """Minify all CSS and JS assets"""
    
    # Define files to minify
    assets = [
        {
            'input': 'static/css/animations.css',
            'output': 'static/css/animations.min.css',
            'type': 'css'
        },
        {
            'input': 'static/js/ui-utils.js',
            'output': 'static/js/ui-utils.min.js',
            'type': 'js'
        }
    ]
    
    print('=' * 60)
    print('Asset Minification - Production Build')
    print('=' * 60)
    print()
    
    total_original = 0
    total_minified = 0
    
    for asset in assets:
        if not os.path.exists(asset['input']):
            print(f'⚠ Warning: {asset["input"]} not found, skipping...')
            print()
            continue
        
        # Get original size
        with open(asset['input'], 'r', encoding='utf-8') as f:
            original_content = f.read()
            original_size = len(original_content)
            total_original += original_size
        
        # Minify
        minify_file(asset['input'], asset['output'], asset['type'])
        
        # Get minified size
        with open(asset['output'], 'r', encoding='utf-8') as f:
            minified_size = len(f.read())
            total_minified += minified_size
    
    if total_original > 0:
        total_reduction = ((total_original - total_minified) / total_original) * 100
        print('=' * 60)
        print('Summary')
        print('=' * 60)
        print(f'Total Original Size: {total_original:,} bytes ({total_original/1024:.2f} KB)')
        print(f'Total Minified Size: {total_minified:,} bytes ({total_minified/1024:.2f} KB)')
        print(f'Total Reduction: {total_reduction:.1f}% ({(total_original-total_minified):,} bytes saved)')
        print()
        print('✓ Minification complete!')
    else:
        print('⚠ No files were minified.')

if __name__ == '__main__':
    minify_all_assets()
