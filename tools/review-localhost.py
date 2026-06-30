#!/usr/bin/env python3
"""
MiroFish — Localhost Reviewer
Review aplikasi yang berjalan di localhost: analisis UI, konten, dan struktur.
Mengambil screenshot, menganalisis HTML, dan memberikan review desain.
"""

import sys
import os
import json
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse


def find_running_services() -> list:
    """Temukan semua layanan yang berjalan di localhost."""
    services = []
    try:
        result = subprocess.run(
            ['ss', '-tlnp'], capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.split('\n'):
            if 'LISTEN' in line and '127.0.0.1' in line:
                parts = line.split()
                for part in parts:
                    if '127.0.0.1:' in part:
                        port = part.split(':')[-1]
                        if port.isdigit():
                            services.append({
                                'port': int(port),
                                'url': f'http://localhost:{port}'
                            })
    except Exception:
        pass

    # Deduplicate
    seen = set()
    unique = []
    for s in services:
        if s['port'] not in seen:
            seen.add(s['port'])
            unique.append(s)

    return sorted(unique, key=lambda x: x['port'])


def check_service(url: str) -> dict:
    """Cek apakah service berjalan dan ambil info dasar."""
    import requests

    try:
        resp = requests.get(url, timeout=5, verify=False)
        return {
            'url': url,
            'status': 'running',
            'status_code': resp.status_code,
            'content_type': resp.headers.get('Content-Type', ''),
            'content_length': len(resp.content),
            'headers': dict(resp.headers)
        }
    except requests.exceptions.ConnectionRefused:
        return {'url': url, 'status': 'not_running', 'error': 'Connection refused'}
    except Exception as e:
        return {'url': url, 'status': 'error', 'error': str(e)}


def analyze_html_structure(url: str) -> dict:
    """Analisis struktur HTML dari halaman."""
    import requests
    from bs4 import BeautifulSoup

    try:
        resp = requests.get(url, timeout=10, verify=False)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Meta info
        title = soup.title.string.strip() if soup.title and soup.title.string else ''
        meta_desc = ''
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag:
            meta_desc = meta_tag.get('content', '')

        # Framework detection
        frameworks = []
        scripts = [s.get('src', '') for s in soup.find_all('script', src=True)]
        html_str = str(soup)

        if any('react' in s.lower() for s in scripts) or '__NEXT_DATA__' in html_str:
            frameworks.append('React/Next.js')
        if any('vue' in s.lower() for s in scripts) or 'data-v-' in html_str:
            frameworks.append('Vue.js')
        if any('angular' in s.lower() for s in scripts) or 'ng-' in html_str:
            frameworks.append('Angular')
        if any('svelte' in s.lower() for s in scripts):
            frameworks.append('Svelte')
        if 'vite' in html_str.lower():
            frameworks.append('Vite')
        if 'tailwind' in html_str.lower():
            frameworks.append('Tailwind CSS')
        if 'bootstrap' in html_str.lower():
            frameworks.append('Bootstrap')

        # Structure analysis
        headings = {}
        for level in range(1, 7):
            tags = soup.find_all(f'h{level}')
            if tags:
                headings[f'h{level}'] = [t.get_text(strip=True) for t in tags[:5]]

        forms = len(soup.find_all('form'))
        inputs = len(soup.find_all('input'))
        buttons = len(soup.find_all('button'))
        images = len(soup.find_all('img'))
        links = len(soup.find_all('a', href=True))

        # Accessibility
        img_with_alt = len(soup.find_all('img', alt=True))
        img_without_alt = images - img_with_alt
        aria_labels = len(soup.find_all(attrs={'aria-label': True}))
        roles = len(soup.find_all(attrs={'role': True}))

        return {
            'title': title,
            'meta_description': meta_desc,
            'frameworks': frameworks,
            'headings': headings,
            'elements': {
                'forms': forms,
                'inputs': inputs,
                'buttons': buttons,
                'images': images,
                'links': links
            },
            'accessibility': {
                'images_with_alt': img_with_alt,
                'images_without_alt': img_without_alt,
                'aria_labels': aria_labels,
                'roles': roles
            }
        }
    except Exception as e:
        return {'error': str(e)}


def take_screenshot(url: str, output_path: str = None) -> str:
    """Ambil screenshot halaman menggunakan Playwright."""
    if output_path is None:
        output_path = tempfile.mktemp(suffix='.png')

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1280, 'height': 900})
            page.goto(url, wait_until='networkidle', timeout=15000)
            page.screenshot(path=output_path, full_page=True)
            browser.close()
        return output_path
    except Exception:
        pass

    return None


def review_localhost(port: int = None, url: str = None) -> dict:
    """Main function: review aplikasi di localhost."""
    if url is None and port is not None:
        url = f'http://localhost:{port}'

    if url is None:
        # Auto-detect services
        services = find_running_services()
        if not services:
            return {'error': 'Tidak ada layanan yang berjalan di localhost'}
        return {
            'services': services,
            'message': 'Ditemukan {count} layanan. Pilih port untuk review.'.format(
                count=len(services)
            )
        }

    # Check service
    service_info = check_service(url)
    if service_info.get('status') != 'running':
        return {'error': f'Service tidak berjalan di {url}', 'details': service_info}

    # Analyze HTML
    html_analysis = analyze_html_structure(url)

    # Take screenshot
    screenshot_path = take_screenshot(url)

    result = {
        'url': url,
        'service': service_info,
        'html_analysis': html_analysis,
        'screenshot_path': screenshot_path,
        'screenshot_taken': screenshot_path is not None
    }

    return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Penggunaan:")
        print("  python3 review-localhost.py                    # Scan semua layanan")
        print("  python3 review-localhost.py 3000               # Review port 3000")
        print("  python3 review-localhost.py http://localhost:3000  # Review URL")
        sys.exit(1)

    arg = sys.argv[1]

    if arg.isdigit():
        result = review_localhost(port=int(arg))
    elif arg.startswith('http'):
        result = review_localhost(url=arg)
    else:
        result = review_localhost(port=int(arg) if arg.isdigit() else None)

    print(json.dumps(result, indent=2, ensure_ascii=False))
