#!/usr/bin/env python3
"""
MiroFish — Free ChatGPT-like Agent
Menggunakan Gemini API (gratis) sebagai ChatGPT alternative.
Handle rate limit otomatis dengan retry + exponential backoff.
"""

import os
import sys
import json
import time
from pathlib import Path

ENV_FILE = Path.home() / "MiroFish" / ".env"

# Daftar model gratis yang didukung (tanpa biaya tambahan)
FREE_MODELS = {
    "groq-llama": {
        "provider": "Groq (Free)",
        "endpoint": "https://api.groq.com/openai/v1/chat/completions",
        "type": "openai",
        "free_tier": "30 RPM, gratis",
        "model": "llama-3.3-70b-versatile",
        "quality": "⭐⭐⭐⭐⭐ (Llama 3.3 70B, super cepat)"
    },
    "groq-mixtral": {
        "provider": "Groq (Free)",
        "endpoint": "https://api.groq.com/openai/v1/chat/completions",
        "type": "openai",
        "free_tier": "30 RPM, gratis",
        "model": "mixtral-8x7b-32768",
        "quality": "⭐⭐⭐⭐ (Mixtral 8x7B, multilingual)"
    },
    "gemini-2.0-flash": {
        "provider": "Google Gemini",
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        "type": "google",
        "free_tier": "1500 req/hari",
        "quality": "⭐⭐⭐⭐ (setara GPT-4 mini)"
    },
    "gemini-2.0-flash-lite": {
        "provider": "Google Gemini",
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent",
        "type": "google",
        "free_tier": "1500 req/hari",
        "quality": "⭐⭐⭐ (cepat, ringan)"
    },
    "gemini-2.5-flash": {
        "provider": "Google Gemini",
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        "type": "google",
        "free_tier": "1500 req/hari",
        "quality": "⭐⭐⭐⭐⭐ (terbaru, terbaik)"
    }
}

# Provider gratis alternatif yang butuh signup (tidak ada di sistem)
EXTRA_FREE_PROVIDERS = {
    "groq": {
        "name": "Groq",
        "url": "https://console.groq.com/keys",
        "models": "Llama 3.3 70B, Mixtral 8x7B",
        "free_tier": "30 RPM, gratis"
    },
    "together": {
        "name": "Together AI",
        "url": "https://api.together.xyz/settings/api-keys",
        "models": "Llama 3.1 8B, Mixtral 8x7B",
        "free_tier": "60 RPM, gratis"
    }
}


def load_api_key():
    """Load Gemini API key dari .env atau env var."""
    # Priority: env var > .env file
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if api_key:
        return api_key

    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().split('\n'):
            line = line.strip()
            if line.startswith('GEMINI_API_KEY='):
                api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                if api_key:
                    return api_key
    
    # Fallback: return empty string (user must configure)
    return ""


def query_gemini(prompt, system_prompt=None, model="gemini-2.0-flash", max_retries=3):
    """
    Kirim prompt ke Gemini API (gratis).
    Handle rate limit dengan exponential backoff.
    
    Args:
        prompt: User prompt
        system_prompt: System instruction (optional)
        model: Model name from FREE_MODELS
        max_retries: Max retry on rate limit
    
    Returns:
        dict with 'response' key or 'error'
    """
    api_key = load_api_key()
    model_config = FREE_MODELS.get(model, FREE_MODELS["gemini-2.0-flash"])
    endpoint = model_config["endpoint"]

    # Build contents
    contents = []
    if system_prompt:
        contents.append({"role": "user", "parts": [{"text": system_prompt}]})
    contents.append({"parts": [{"text": prompt}]})

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
            "topP": 0.95
        }
    }

    url = f"{endpoint}?key={api_key}"
    data = json.dumps(payload).encode()

    import urllib.request

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method='POST')
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())

            if 'candidates' in result and result['candidates']:
                text = result['candidates'][0]['content']['parts'][0]['text']
                usage = result.get('usageMetadata', {})
                return {
                    "response": text,
                    "model": model,
                    "provider": "Gemini (Free)",
                    "tokens": {
                        "prompt": usage.get('promptTokenCount', 0),
                        "output": usage.get('candidatesTokenCount', 0)
                    }
                }
            return {"error": "No candidates in response", "raw": str(result)[:300]}

        except urllib.request.HTTPError as e:
            body = e.read().decode()
            if e.code == 429 or 'quota' in body.lower():
                if attempt < max_retries:
                    wait = 2 ** attempt * 5  # exponential backoff: 10s, 20s, 40s
                    print(f"⏳ Rate limit, tunggu {wait}s (percobaan {attempt}/{max_retries})...")
                    time.sleep(wait)
                    continue
                return {"error": f"Quota habis. Tunggu beberapa jam atau gunakan key lain. Detail: {body[:200]}"}
            return {"error": f"HTTP {e.code}: {body[:200]}"}
        except Exception as e:
            if attempt < max_retries:
                time.sleep(2)
                continue
            return {"error": str(e)}

    return {"error": "Max retries exceeded"}


def query_groq(prompt, system_prompt=None, model="groq-llama", max_retries=3):
    """Kirim prompt ke Groq API (gratis, 30 RPM)."""
    import urllib.request

    api_key = os.environ.get('GROQ_API_KEY', '')
    if not api_key and ENV_FILE.exists():
        for line in ENV_FILE.read_text().split('\n'):
            if line.startswith('GROQ_API_KEY='):
                api_key = line.split('=', 1)[1].strip().strip('"').strip("'")

    if not api_key:
        api_key = ""  # User must configure in .env

    model_config = FREE_MODELS.get(model, FREE_MODELS["groq-llama"])
    model_name = model_config.get("model", "llama-3.3-70b-versatile")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2048
    }
    data = json.dumps(payload).encode()

    url = "https://api.groq.com/openai/v1/chat/completions"

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
            }, method='POST')
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())

            if 'choices' in result and result['choices']:
                text = result['choices'][0]['message']['content']
                usage = result.get('usage', {})
                return {
                    "response": text,
                    "model": model_name,
                    "provider": "Groq (Free)",
                    "tokens": {
                        "prompt": usage.get('prompt_tokens', 0),
                        "output": usage.get('completion_tokens', 0)
                    }
                }
            return {"error": "No response", "raw": str(result)[:300]}

        except urllib.request.HTTPError as e:
            body = e.read().decode()[:200]
            if e.code == 429:
                if attempt < max_retries:
                    wait = 2 ** attempt * 3
                    print(f"⏳ Rate limit, tunggu {wait}s...")
                    time.sleep(wait)
                    continue
            return {"error": f"HTTP {e.code}: {body}"}
        except Exception as e:
            if attempt < max_retries:
                time.sleep(2)
                continue
            return {"error": str(e)}
    return {"error": "Max retries"}


def list_free_models():
    """Tampilkan daftar model gratis yang didukung."""
    lines = []
    lines.append("\n🤖 Model Gratis Tersedia:")
    lines.append("=" * 50)
    for model_id, config in FREE_MODELS.items():
        lines.append(f"\n  {model_id}")
        lines.append(f"     Provider: {config['provider']}")
        lines.append(f"     Kualitas: {config['quality']}")
        lines.append(f"     Free Tier: {config['free_tier']}")
    
    lines.append("\n\n📋 Provider Gratis Lain (daftar gratis):")
    lines.append("=" * 50)
    for pid, pconfig in EXTRA_FREE_PROVIDERS.items():
        lines.append(f"\n  {pid}: {pconfig['name']}")
        lines.append(f"     Models: {pconfig['models']}")
        lines.append(f"     {pconfig['free_tier']}")
        lines.append(f"     Daftar: {pconfig['url']}")
    
    return "\n".join(lines)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        print(list_free_models())
        sys.exit(0)

    if len(sys.argv) < 2:
        print("🐟 Free ChatGPT Agent — Gemini API (Gratis)")
        print()
        print("Penggunaan:")
        print("  python3 free-chat.py <prompt>")
        print("  python3 free-chat.py --model <model> <prompt>")
        print("  python3 free-chat.py --list")
        print()
        print("Contoh:")
        print('  python3 free-chat.py "Apa kabar?"')
        print('  python3 free-chat.py --model gemini-2.5-flash "Jelaskan AI"')
        sys.exit(1)

    model = "gemini-2.0-flash"
    prompt_start = 1

    if sys.argv[1] == '--model' and len(sys.argv) > 3:
        model = sys.argv[2]
        prompt_start = 3

    prompt = ' '.join(sys.argv[prompt_start:])
    system = None
    if '|' in prompt:
        parts = prompt.split('|', 1)
        system = parts[0].strip()
        prompt = parts[1].strip()

    # Route ke provider yang tepat
    if model.startswith('groq'):
        print(f"🚀 Mengirim ke {model} (Groq Free 30 RPM)...")
        result = query_groq(prompt, system, model)
    else:
        print(f"🚀 Mengirim ke {model} (Gemini Free)...")
        result = query_gemini(prompt, system, model)

    if 'response' in result:
        print(f"✅ {result['provider']} — {result['model']}")
        print()
        print(result['response'])
        if 'tokens' in result:
            print()
            print(f"📊 Input: {result['tokens']['prompt']} | Output: {result['tokens']['output']} token")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown')}")
        print()
        print("Coba model lain atau tunggu quota reset.")
        print("Daftar model: python3 free-chat.py --list")
