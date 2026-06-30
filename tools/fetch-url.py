#!/usr/bin/env python3
"""
MiroFish — URL Content Fetcher
Mengambil konten dari URL: teks, metadata, dan screenshot.
Mendukung review website, artikel, dan halaman web apapun.
"""

import sys
import os
import json
import hashlib
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

def fetch_with_requests(url: str) -> dict:
    """Fetch URL content using requests + BeautifulSoup."""
    import requests
    from bs4 import BeautifulSoup

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                       '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    resp = requests.get(url, headers=headers, timeout=30, verify=False)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')

    # Hapus script dan style
    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        tag.decompose()

    # Metadata
    title = soup.title.string.strip() if soup.title and soup.title.string else ''
    meta_desc = ''
    meta_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_tag:
        meta_desc = meta_tag.get('content', '')

    # Konten teks
    text = soup.get_text(separator='\n', strip=True)
    # Bersihkan multiple newlines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    clean_text = '\n'.join(lines)

    # Gambar
    images = []
    for img in soup.find_all('img', src=True)[:20]:
        src = img['src']
        if src.startswith('//'):
            src = 'https:' + src
        elif src.startswith('/'):
            parsed = urlparse(url)
            src = f"{parsed.scheme}://{parsed.netloc}{src}"
        elif not src.startswith('http'):
            src = url.rstrip('/') + '/' + src
        alt = img.get('alt', '')
        images.append({'src': src, 'alt': alt})

    # Links
    links = []
    for a in soup.find_all('a', href=True)[:30]:
        href = a['href']
        if href.startswith('http'):
            links.append({'text': a.get_text(strip=True), 'href': href})

    return {
        'url': url,
        'title': title,
        'meta_description': meta_desc,
        'text': clean_text[:10000],  # Limit 10K chars
        'text_length': len(clean_text),
        'images': images,
        'links': links[:20],
        'status_code': resp.status_code
    }


def take_screenshot(url: str, output_path: str = None) -> str:
    """Take screenshot of URL using Playwright or puppeteer."""
    if output_path is None:
        output_path = tempfile.mktemp(suffix='.png')

    # Coba Playwright
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1280, 'height': 900})
            page.goto(url, wait_until='networkidle', timeout=30000)
            page.screenshot(path=output_path, full_page=True)
            browser.close()
        return output_path
    except Exception:
        pass

    # Fallback: puppeteer via node
    try:
        script = f'''
        const puppeteer = require('puppeteer');
        (async () => {{
            const browser = await puppeteer.launch({{headless: true}});
            const page = await browser.newPage();
            await page.setViewport({{width: 1280, height: 900}});
            await page.goto('{url}', {{waitUntil: 'networkidle2', timeout: 30000}});
            await page.screenshot({{path: '{output_path}', fullPage: true}});
            await browser.close();
        }})();
        '''
        subprocess.run(['node', '-e', script], timeout=30, check=True)
        return output_path
    except Exception:
        pass

    return None


def fetch_url(url: str, take_ss: bool = False) -> dict:
    """Main function: fetch URL content and optionally take screenshot."""
    result = fetch_with_requests(url)

    if take_ss:
        ss_path = take_screenshot(url)
        if ss_path:
            result['screenshot_path'] = ss_path
            result['screenshot_size'] = os.path.getsize(ss_path)

    return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Penggunaan: python3 fetch-url.py <URL> [--screenshot]")
        print("Contoh: python3 fetch-url.py https://example.com --screenshot")
        sys.exit(1)

    url = sys.argv[1]
    take_ss = '--screenshot' in sys.argv

    try:
        result = fetch_url(url, take_ss)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False))
        sys.exit(1)
