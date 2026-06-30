#!/usr/bin/env python3
"""
MiroFish — Gemini Query Tool
Gunakan Gemini gratis sebagai secondary LLM untuk opini lebih beragam.
Berjalan paralel dengan Atomesus Prime.
"""

import os
import sys
import json
from pathlib import Path

ENV_FILE = Path.home() / "MiroFish" / ".env"


def load_env():
    """Load Gemini API key dari .env."""
    if not ENV_FILE.exists():
        return None, None
    api_key = None
    base_url = None
    model = None
    for line in ENV_FILE.read_text().split('\n'):
        line = line.strip()
        if line.startswith('GEMINI_API_KEY='):
            api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
        elif line.startswith('GEMINI_BASE_URL='):
            base_url = line.split('=', 1)[1].strip().strip('"').strip("'")
        elif line.startswith('GEMINI_MODEL_NAME='):
            model = line.split('=', 1)[1].strip().strip('"').strip("'")
    return api_key, base_url, model


def query_gemini(prompt: str, system_prompt: str = None) -> dict:
    """Kirim prompt ke Gemini Flash Lite."""
    import urllib.request

    api_key, base_url, model = load_env()
    if not api_key:
        return {"error": "GEMINI_API_KEY tidak ditemukan di .env"}

    # Fallback
    model = model or "gemini-2.0-flash-lite"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    contents = []
    if system_prompt:
        contents.append({"parts": [{"text": system_prompt}]})
    contents.append({"parts": [{"text": prompt}]})

    payload = json.dumps({
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024,
            "topP": 0.95
        }
    }).encode()

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": api_key
    }

    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            if 'candidates' in data and data['candidates']:
                text = data['candidates'][0]['content']['parts'][0]['text']
                tokens = data.get('usageMetadata', {})
                return {
                    "response": text,
                    "model": model,
                    "tokens": {
                        "prompt": tokens.get('promptTokenCount', 0),
                        "output": tokens.get('candidatesTokenCount', 0)
                    }
                }
            return {"error": "Tidak ada respons", "raw": data}
    except urllib.request.HTTPError as e:
        body = e.read().decode()
        try:
            err_data = json.loads(body)
            msg = err_data.get('error', {}).get('message', body)[:200]
        except:
            msg = body[:200]
        return {"error": f"Quota habis (HTTP {e.code}). Tunggu 1-2 menit atau gunakan key lain. Detail: {msg}"}
    except Exception as e:
        return {"error": str(e)}


def query_gemini_openai(prompt: str, system_prompt: str = None) -> dict:
    """Kirim prompt ke Gemini via OpenAI-compatible endpoint."""
    import urllib.request

    api_key, base_url, model = load_env()
    if not api_key:
        return {"error": "GEMINI_API_KEY tidak ditemukan"}

    url = f"https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = json.dumps({
        "model": "gemini-2.0-flash-lite",
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.7
    }).encode()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            if isinstance(data, list):
                data = data[0]
            if 'choices' in data and data['choices']:
                text = data['choices'][0]['message']['content']
                return {
                    "response": text,
                    "model": "gemini-2.0-flash-lite",
                    "method": "openai-compatible"
                }
            return {"error": "Tidak ada respons", "raw": data}
    except urllib.request.HTTPError as e:
        body = e.read().decode()
        return {"error": f"HTTP {e.code}: {body[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def compare_opinions(topic: str) -> dict:
    """Bandingkan opini Atomesus vs Gemini tentang suatu topik."""
    # Atomesus sudah jadi primary LLM MiroFish
    # Gemini sebagai pembanding
    
    gemini_result = query_gemini(topic)
    
    return {
        "topic": topic,
        "gemini_opinion": gemini_result.get('response', gemini_result.get('error', 'Error')),
        "note": "Atomesus adalah primary LLM MiroFish. Gemini digunakan untuk opini alternatif."
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Penggunaan:")
        print("  python3 query-gemini.py <prompt>")
        print("  python3 query-gemini.py --compare <topik>")
        print("")
        print("Contoh:")
        print('  python3 query-gemini.py "Apa prediksi cuaca besok?"')
        print('  python3 query-gemini.py --compare "Siapa yang akan menang Piala Dunia 2026?"')
        sys.exit(1)

    if sys.argv[1] == '--compare' and len(sys.argv) > 2:
        topic = ' '.join(sys.argv[2:])
        result = compare_opinions(topic)
    else:
        prompt = ' '.join(sys.argv[1:])
        result = query_gemini(prompt)

    print(json.dumps(result, indent=2, ensure_ascii=False))
