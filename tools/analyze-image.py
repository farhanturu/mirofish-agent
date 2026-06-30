#!/usr/bin/env python3
"""
MiroFish — Image Analyzer
Menganalisis gambar (logo, desain, screenshot, foto) menggunakan LLM vision.
Menggunakan Atomesus API dengan model cipher yang mendukung vision.
"""

import sys
import os
import json
import base64
import mimetypes
from pathlib import Path


def encode_image(image_path: str) -> tuple:
    """Encode gambar ke base64 dan dapatkan MIME type."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Gambar tidak ditemukan: {image_path}")

    mime_type, _ = mimetypes.guess_type(str(path))
    if not mime_type or not mime_type.startswith('image/'):
        mime_type = 'image/png'

    with open(path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')

    return data, mime_type


def analyze_with_atomesus(image_path: str, prompt: str = None) -> str:
    """Analisis gambar menggunakan Atomesus API (OpenAI-compatible vision)."""
    import requests

    api_key = os.environ.get('LLM_API_KEY', '')
    base_url = os.environ.get('LLM_BASE_URL', 'https://api.atomesus.com/v1')

    if not api_key:
        return "Error: LLM_API_KEY tidak diset. Cek ~/MiroFish/.env"

    img_data, mime_type = encode_image(image_path)

    if prompt is None:
        prompt = """Analisis gambar ini secara mendalam. Jelaskan:
1. Apa yang terlihat di gambar
2. Jenis gambar (logo, desain UI, screenshot, foto, diagram, dll)
3. Elemen visual (warna, bentuk, tipografi, layout)
4. Kesan dan pesan yang disampaikan
5. Kualitas desain (jika relevan)
6. Saran perbaikan (jika relevan)

Gunakan Bahasa Indonesia."""

    payload = {
        'model': os.environ.get('LLM_MODEL_NAME', 'cipher'),
        'messages': [
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': prompt},
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f'data:{mime_type};base64,{img_data}'
                        }
                    }
                ]
            }
        ],
        'max_tokens': 2000
    }

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    resp = requests.post(
        f'{base_url}/chat/completions',
        headers=headers,
        json=payload,
        timeout=120
    )
    resp.raise_for_status()
    data = resp.json()

    return data['choices'][0]['message']['content']


def analyze_with_openai_compatible(image_path: str, prompt: str = None) -> str:
    """Analisis gambar menggunakan OpenAI-compatible API (Gemini, Groq, dll)."""
    try:
        from openai import OpenAI
    except ImportError:
        return analyze_with_atomesus(image_path, prompt)

    api_key = os.environ.get('LLM_API_KEY', '')
    base_url = os.environ.get('LLM_BASE_URL', 'https://api.atomesus.com/v1')
    model = os.environ.get('LLM_MODEL_NAME', 'cipher')

    if not api_key:
        return "Error: LLM_API_KEY tidak diset."

    img_data, mime_type = encode_image(image_path)

    if prompt is None:
        prompt = """Analisis gambar ini secara mendalam dalam Bahasa Indonesia.
Jelaskan: konten, elemen visual, jenis gambar, kualitas desain, dan saran perbaikan."""

    client = OpenAI(api_key=api_key, base_url=base_url)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': prompt},
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f'data:{mime_type};base64,{img_data}'
                        }
                    }
                ]
            }
        ],
        max_tokens=2000
    )

    return response.choices[0].message.content


def analyze_image(image_path: str, prompt: str = None) -> dict:
    """Main function: analisis gambar dan kembalikan hasil."""
    path = Path(image_path)
    file_size = path.stat().st_size

    try:
        result_text = analyze_with_atomesus(image_path, prompt)
    except Exception as e:
        result_text = f"Error menganalisis gambar: {e}"

    return {
        'image_path': str(path.absolute()),
        'image_name': path.name,
        'image_size': file_size,
        'image_size_human': f"{file_size / 1024:.1f} KB",
        'analysis': result_text,
        'prompt_used': prompt or 'Default analysis prompt'
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Penggunaan: python3 analyze-image.py <IMAGE_PATH> [PROMPT]")
        print("")
        print("Contoh:")
        print("  python3 analyze-image.py logo.png")
        print("  python3 analyze-image.py screenshot.jpg 'Analisis UI/UX website ini'")
        print("  python3 analyze-image.py desain.png 'Apakah logo ini cocok untuk startup tech?'")
        sys.exit(1)

    image_path = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else None

    # Load .env
    env_file = Path.home() / 'MiroFish' / '.env'
    if env_file.exists():
        for line in env_file.read_text().split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ.setdefault(key.strip(), val.strip())

    try:
        result = analyze_image(image_path, prompt)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False))
        sys.exit(1)
