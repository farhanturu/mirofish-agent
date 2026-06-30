#!/usr/bin/env python3
"""
MiroFish Agent — Patch Backend untuk System Prompt Indonesia
Menyuntikkan system prompt Bahasa Indonesia ke LLMClient
"""

import os
import sys
import shutil

MIROFISH_DIR = os.path.expanduser("~/MiroFish")
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT_FILE = os.path.join(SKILL_DIR, "patches", "system-prompts.md")
LLM_CLIENT = os.path.join(MIROFISH_DIR, "backend", "app", "utils", "llm_client.py")
CONFIG_FILE = os.path.join(MIROFISH_DIR, "backend", "app", "config.py")


def patch_llm_client():
    """Suntikkan system prompt Indonesia ke LLMClient.chat()"""
    if not os.path.exists(LLM_CLIENT):
        print("[!] llm_client.py tidak ditemukan, skip")
        return False

    if not os.path.exists(PROMPT_FILE):
        print("[!] system-prompts.md tidak ditemukan, skip")
        return False

    # Baca system prompt
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt_text = f.read().strip()

    # Baca llm_client.py
    with open(LLM_CLIENT, "r", encoding="utf-8") as f:
        code = f.read()

    # Cek apakah sudah di-patch
    if "MiroFish Agent: System Prompt Indonesia" in code:
        print("[✓] llm_client.py sudah di-patch sebelumnya")
        return True

    # Backup
    shutil.copy2(LLM_CLIENT, LLM_CLIENT + ".bak")

    # Escape prompt untuk string Python
    prompt_escaped = repr(prompt_text)

    # Inject di dalam __init__ untuk mendeteksi provider type
    init_inject = '''
        # --- MiroFish Agent: Deteksi provider type ---
        self.provider_type = os.environ.get('LLM_PROVIDER_TYPE', 'openai')
        # --- End MiroFish Agent ---'''

    # Inject sebelum "kwargs = {" di dalam method chat()
    # Strategi: Jika Atomesus (system messages diabaikan), gabungkan
    # system prompt ke user message pertama. Jika Openai-compatible,
    # gunakan system message biasa.
    chat_inject = f'''
        # --- MiroFish Agent: System Prompt Indonesia ---
        _mirofish_system_prompt = {prompt_escaped}
        if getattr(self, 'provider_type', 'openai') == 'atomesus':
            # Atomesus mengabaikan system messages,
            # gabungkan ke user message pertama
            _first_user = next(
                (i for i, m in enumerate(messages) if m.get('role') == 'user'), None
            )
            if _first_user is not None:
                messages[_first_user]['content'] = (
                    _mirofish_system_prompt + '\\n\\n---\\n\\n'
                    + messages[_first_user]['content']
                )
            else:
                # Tidak ada user message, tambahkan sebagai user
                messages.append({{'role': 'user', 'content': _mirofish_system_prompt}})
        else:
            # Provider lain: gunakan system message biasa
            _has_system = any(m.get('role') == 'system' for m in messages)
            if not _has_system:
                messages = [{{'role': 'system', 'content': _mirofish_system_prompt}}] + messages
            else:
                _idx = next(
                    i for i, m in enumerate(messages) if m.get('role') == 'system'
                )
                messages[_idx]['content'] = (
                    _mirofish_system_prompt + '\\n\\n' + messages[_idx]['content']
                )
        # --- End MiroFish Agent ---

        kwargs = {{'''

    # 0) Pastikan 'import os' ada (dibutuhkan untuk os.environ.get)
    if "import os" not in code:
        code = "import os\n" + code
        print("[✓] 'import os' ditambahkan")

    # 1) Inject di __init__
    init_target = "        self.client = OpenAI("
    if init_target in code and "MiroFish Agent: Deteksi provider" not in code:
        code = code.replace(init_target, init_inject + "\n\n" + init_target, 1)

    # 2) Inject di chat() sebelum kwargs
    target = "        kwargs = {"
    if target in code:
        code = code.replace(target, chat_inject, 1)
        with open(LLM_CLIENT, "w", encoding="utf-8") as f:
            f.write(code)
        print("[✓] System prompt Indonesia berhasil disuntikkan ke llm_client.py")
        print("[✓] Deteksi provider Atomesus ditambahkan")
        return True
    else:
        print("[!] Injection point 'kwargs = {' tidak ditemukan")
        return False


def patch_config_locale():
    """Tambahkan konfigurasi locale Indonesia ke config.py"""
    if not os.path.exists(CONFIG_FILE):
        print("[!] config.py tidak ditemukan, skip")
        return False

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        code = f.read()

    if "DEFAULT_LOCALE" in code:
        print("[✓] config.py sudah memiliki DEFAULT_LOCALE")
        return True

    # Backup
    shutil.copy2(CONFIG_FILE, CONFIG_FILE + ".bak")

    # Tambahkan DEFAULT_LOCALE setelah SECRET_KEY
    code = code.replace(
        "    SECRET_KEY = os.environ.get('SECRET_KEY', 'mirofish-secret-key')",
        "    SECRET_KEY = os.environ.get('SECRET_KEY', 'mirofish-secret-key')\n    \n    # Locale default (Bahasa Indonesia)\n    DEFAULT_LOCALE = os.environ.get('MIROFISH_LOCALE', 'id')"
    )

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(code)
    print("[✓] DEFAULT_LOCALE='id' ditambahkan ke config.py")
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("MiroFish Agent — Patch Backend")
    print("=" * 50)
    print()

    ok1 = patch_llm_client()
    ok2 = patch_config_locale()

    print()
    if ok1 and ok2:
        print("[✓] Semua patch backend berhasil!")
    elif ok1 or ok2:
        print("[!] Sebagian patch berhasil")
    else:
        print("[✗] Tidak ada patch yang berhasil")

    sys.exit(0 if (ok1 or ok2) else 1)
