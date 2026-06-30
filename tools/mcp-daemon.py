#!/usr/bin/env python3
"""
MiroFish — MCP Background Daemon
Jalan terus di background. Update data real-time otomatis.
Agent bisa akses data kapan aja tanpa nunggu MCP dipanggil.
"""

import os
import sys
import json
import time
import threading
import subprocess
from pathlib import Path
from datetime import datetime

CACHE_DIR = Path.home() / "MiroFish" / ".mcp-cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

TOOLS_DIR = Path.home() / "MiroFish" / "tools"
MCP_CLIENT = TOOLS_DIR / "mcp-client.py"


def log(msg):
    """Log dengan timestamp."""
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[MCP] [{ts}] {msg}")
    # Juga tulis ke file log
    log_file = CACHE_DIR / "daemon.log"
    with open(log_file, 'a') as f:
        f.write(f"[{ts}] {msg}\n")


def save_cache(name, data):
    """Simpan data ke cache."""
    cache_file = CACHE_DIR / f"{name}.json"
    cache_data = {
        "updated_at": datetime.now().isoformat(),
        "data": data
    }
    cache_file.write_text(json.dumps(cache_data, indent=2, ensure_ascii=False))
    return cache_file


def run_mcp(cmd, args):
    """Jalankan MCP client dengan absolute path + env dari .env."""
    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = str(TOOLS_DIR)
        
        # Load API keys dari .env MiroFish
        env_file = Path.home() / "MiroFish" / ".env"
        if env_file.exists():
            for line in env_file.read_text().split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    env[key.strip()] = val.strip().strip('"').strip("'")
        
        result = subprocess.run(
            [sys.executable, str(MCP_CLIENT), cmd] + args,
            capture_output=True, text=True, timeout=30,
            cwd=str(TOOLS_DIR.parent),
            env=env
        )
        if result.stdout:
            try:
                return json.loads(result.stdout)
            except:
                log(f"  ⚠️ Parse error: {result.stdout[:100]}")
                return {"error": "parse failed"}
        if result.stderr:
            log(f"  ⚠️ Stderr: {result.stderr[:100]}")
            return {"error": result.stderr[:200]}
        return {"error": "empty"}
    except subprocess.TimeoutExpired:
        return {"error": "timeout"}
    except Exception as e:
        return {"error": str(e)}


# =========================================================================
# Data Updaters
# =========================================================================

def update_kurs():
    """Update kurs mata uang setiap 15 menit."""
    log("📊 Update kurs...")
    data = run_mcp('kurs', ['USD/IDR'])
    if data.get('success'):
        f = save_cache('kurs', data)
        log(f"  ✅ USD/IDR: {data.get('rate', '?')} → {f}")
    else:
        log(f"  ⚠️ Gagal: {data.get('error', '?')}")


def update_crypto():
    """Update harga crypto setiap 15 menit."""
    log("₿ Update crypto...")
    for coin in ['bitcoin', 'ethereum', 'solana']:
        data = run_mcp('crypto', [coin])
        if data.get('success'):
            save_cache(f'crypto_{coin}', data)
            log(f"  ✅ {coin}: ${data.get('price_usd', '?')}")
        else:
            log(f"  ⚠️ {coin}: {data.get('error', '?')}")


def update_berita(topics):
    """Update berita untuk topik tertentu setiap 30 menit."""
    log("📰 Update berita...")
    for topic in topics:
        data = run_mcp('news', [topic])
        if data.get('success'):
            count = data.get('count', 0)
            if count > 0:
                save_cache(f'berita_{topic.replace(" ", "_")}', data)
                log(f"  ✅ {topic}: {count} berita")
        else:
            log(f"  ⚠️ {topic}: {data.get('error', '?')}")


def update_ekonomi():
    """Update indikator ekonomi setiap jam."""
    log("📈 Update ekonomi...")
    data = run_mcp('ekonomi', ['Indonesia'])
    if data.get('success'):
        save_cache('ekonomi', data)
        indicators = data.get('indicators', {})
        for k, v in indicators.items():
            log(f"  ✅ {k}: {str(v)[:60]}")
    else:
        log(f"  ⚠️ Ekonomi: {data.get('error', '?')}")


def update_saham():
    """Update indeks saham setiap jam."""
    log("📈 Update saham...")
    for idx in ['IHSG', 'KOSPI', 'Nikkei', 'STI', 'KLSE']:
        data = run_mcp('saham', [idx])
        if data.get('success'):
            save_cache(f'saham_{idx}', data)
            headlines = data.get('headlines', [])
            if headlines:
                log(f"  ✅ {idx}: {headlines[0].get('title', '')[:60]}")
        else:
            log(f"  ⚠️ {idx}")


def update_weather():
    """Update cuaca kota besar setiap jam."""
    log("🌤️ Update cuaca...")
    for kota in ['jakarta', 'new york', 'tokyo', 'london', 'dubai']:
        data = run_mcp('weather', [kota])
        if data.get('success'):
            save_cache(f'cuaca_{kota}', data)
            log(f"  ✅ {kota}: {data.get('temperature', '?')}°C")
        else:
            log(f"  ⚠️ {kota}")


def update_negara():
    """Update data negara setiap 6 jam."""
    log("🌏 Update data negara...")
    for negara in ['indonesia', 'china', 'amerika serikat', 'jepang', 'india']:
        data = run_mcp('country', [negara])
        if data.get('success'):
            save_cache(f'negara_{negara.replace(" ", "_")}', data)
            log(f"  ✅ {negara}: populasi {data.get('population', '?')}")
        else:
            log(f"  ⚠️ {negara}")


# =========================================================================
# Simple Background Daemon — run in main thread
# =========================================================================

_RUNNING = False
_STATS = {"updates": 0, "errors": 0, "started": None}


def start_daemon():
    """Start MCP daemon — runs forever, call in subprocess."""
    global _RUNNING
    _RUNNING = True
    _STATS["started"] = datetime.now().isoformat()
    log("🚀 MCP Daemon started! Update data otomatis aktif.")
    log(f"  Cache dir: {CACHE_DIR}")
    _run_loop()


def stop_daemon():
    """Stop daemon."""
    global _RUNNING
    _RUNNING = False
    log("🛑 MCP Daemon stopped")


def _run_loop():
    """Loop utama — jalan terus sampai dihentikan."""
    global _STATS
    counters = {k: 0 for k in ['kurs', 'crypto', 'berita', 'ekonomi', 'weather', 'negara']}
    topik_berita = ['indonesia ekonomi', 'global news', 'teknologi', 'IHSG', 'politik indonesia']

    while _RUNNING:
        try:
            counters['kurs'] += 1
            if counters['kurs'] >= 3:
                update_kurs(); counters['kurs'] = 0

            counters['crypto'] += 1
            if counters['crypto'] >= 3:
                update_crypto(); counters['crypto'] = 0

            counters['berita'] += 1
            if counters['berita'] >= 5:
                update_berita(topik_berita); counters['berita'] = 0

            counters['ekonomi'] += 1
            if counters['ekonomi'] >= 10:
                update_ekonomi(); update_saham(); counters['ekonomi'] = 0

            counters['weather'] += 1
            if counters['weather'] >= 15:
                update_weather(); counters['weather'] = 0

            counters['negara'] += 1
            if counters['negara'] >= 30:
                update_negara(); counters['negara'] = 0

            _STATS['updates'] += 1
            time.sleep(60)

        except Exception as e:
            _STATS['errors'] += 1
            log(f"❌ Error: {e}")
            time.sleep(10)

    log("Daemon selesai")


def get_cache(name):
    """Ambil data dari cache."""
    cache_file = CACHE_DIR / f"{name}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text())
    return None


def get_all_caches():
    """Daftar semua cache yang tersedia."""
    caches = {}
    for f in sorted(CACHE_DIR.glob("*.json")):
        if f.name != "daemon.log":
            try:
                data = json.loads(f.read_text())
                caches[f.stem] = {"updated": str(data.get("updated_at", "?"))[:19]}
            except:
                pass
    return caches


def cache_status():
    """Status semua cache."""
    caches = get_all_caches()
    lines = ["\n📦 MCP Cache Status:", "=" * 50]
    for name, info in caches.items():
        lines.append(f"\n  {name}  (updated: {info['updated']})")
    lines.append(f"\n\n  Total: {len(caches)} cache files")
    lines.append(f"  Updates: {_STATS['updates']}")
    lines.append(f"  Errors: {_STATS['errors']}")
    return "\n".join(lines)


# =========================================================================
# MAIN
# =========================================================================
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='MCP Background Daemon')
    parser.add_argument('command', nargs='?', default='start',
                       choices=['start', 'stop', 'status', 'cache'])
    args = parser.parse_args()

    if args.command == 'start':
        # Buat PID file
        pid_file = CACHE_DIR / "daemon.pid"
        pid_file.write_text(str(os.getpid()))
        start_daemon()  # This runs forever

    elif args.command == 'stop':
        pid_file = CACHE_DIR / "daemon.pid"
        if pid_file.exists():
            pid = pid_file.read_text().strip()
            try:
                os.kill(int(pid), 15)
                pid_file.unlink()
                log(f"Daemon {pid} dihentikan")
            except:
                log("Gagal menghentikan daemon")
        else:
            log("Daemon tidak berjalan")

    elif args.command == 'status':
        print(cache_status())

    elif args.command == 'cache':
        caches = get_all_caches()
        print(json.dumps(caches, indent=2, ensure_ascii=False) if caches else "Cache kosong")
