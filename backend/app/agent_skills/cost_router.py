"""
MiroFish — Cost-Saving Smart Router
Memilih provider/model termurah sesuai kompleksitas tugas.
Simple task → DeepSeek (murah $0.14/M)
Kompleks → Groq (gratis) / Atomesus (Prime)
Geopolitik → MCP + model gratis
"""

import os
import json
from pathlib import Path
from enum import Enum

ENV_FILE = Path.home() / "MiroFish" / ".env"

# =========================================================================
# Level Kompleksitas Tugas
# =========================================================================
class TaskLevel(Enum):
    RINGAN = "ringan"       # 1-2 kalimat, fakta sederhana
    SEDANG = "sedang"       # Analisis singkat, butuh data
    BERAT = "berat"         # Analisis mendalam, multi-perspektif
    GEOPOLITIK = "geopolitik"  # Analisis geopolitik, butuh data real-time


# =========================================================================
# Biaya per 1K token (estimasi)
# =========================================================================
COST_TABLE = {
    "deepseek-v4-flash": {"input": 0.00014, "output": 0.00028, "tier": "hemat"},
    "llama-3.3-70b-versatile": {"input": 0.0, "output": 0.0, "tier": "gratis"},  # Groq free
    "gemini-2.0-flash-lite": {"input": 0.0, "output": 0.0, "tier": "gratis"},    # Gemini free
    "gemini-2.0-flash": {"input": 0.0, "output": 0.0, "tier": "gratis"},
    "cipher": {"input": 0.002, "output": 0.004, "tier": "prime"},  # Atomesus Prime
}

# =========================================================================
# Router: Pilih model termurah untuk tugas
# =========================================================================
MODEL_ROUTES = {
    TaskLevel.RINGAN: {
        "provider": "openmodel",  # DeepSeek via OpenModel
        "model": "deepseek-v4-flash",
        "reason": "Termurah ($0.14/M), cukup untuk tugas sederhana",
        "agents": ["deepseek"]  # 1 agent cukup
    },
    TaskLevel.SEDANG: {
        "provider": "openmodel",
        "model": "deepseek-v4-flash",
        "reason": "Murah, kualitas cukup untuk analisis sedang",
        "agents": ["deepseek"]
    },
    TaskLevel.BERAT: {
        "provider": "all",  # SEMUA agent!
        "model": "ensemble",
        "reason": "Tugas berat: semua agent bekerja sama (DeepSeek + Groq + Atomesus)",
        "agents": ["deepseek", "groq", "atomesus"]
    },
    TaskLevel.GEOPOLITIK: {
        "provider": "all",  # SEMUA agent + MCP!
        "model": "ensemble",
        "reason": "Geopolitik: semua agent + MCP data real-time (GRATIS)",
        "agents": ["deepseek", "groq", "atomesus", "mcp"]
    }
}


def detect_task_level(task_desc: str) -> TaskLevel:
    """
    Mendeteksi level kompleksitas tugas dari deskripsi.
    
    Args:
        task_desc: Deskripsi tugas dari user/system
        
    Returns:
        TaskLevel yang sesuai
    """
    desc_lower = task_desc.lower()
    
    # Deteksi GEOPOLITIK
    geopolitik_keywords = [
        'geopolitik', 'global', 'dunia', 'internasional', 'politik luar negeri',
        'konflik', 'perang', 'sanksi', 'diplomasi', 'pbb', 'united nations',
        'amerika', 'china', 'rusia', 'ukraina', 'timur tengah', 'eropa',
        'ekonomi global', 'pasar global', 'perdagangan internasional',
        'opec', 'nato', 'asean', 'g20', 'g7',
        'krisis', 'resesi global', 'inflasi global',
        'negara', 'kawasan', 'aliansi', 'hubungan bilateral'
    ]
    if any(kw in desc_lower for kw in geopolitik_keywords):
        return TaskLevel.GEOPOLITIK
    
    # Deteksi BERAT
    berat_keywords = [
        'analisis mendalam', 'prediksi', 'proyeksi', 'skenario',
        'dampak', 'implikasi', 'rekomendasi', 'strategi',
        'kompleks', 'komprehensif', 'lengkap', 'detail',
        'multidisiplin', 'multi-aspek', 'holistik',
        'riset', 'penelitian', 'studi', 'evaluasi',
        'market', 'industri', 'sektor', 'ekonomi makro'
    ]
    if any(kw in desc_lower for kw in berat_keywords):
        return TaskLevel.BERAT
    
    # Deteksi SEDANG
    sedang_keywords = [
        'analisis', 'bandingkan', 'jelaskan', 'ulas',
        'review', 'evaluasi', 'perbedaan', 'persamaan',
        'dampak', 'pengaruh', 'hubungan', 'korelasi',
        'tren', 'pola', 'data', 'statistik',
        'laporan', 'ringkasan', 'rangkuman'
    ]
    if any(kw in desc_lower for kw in sedang_keywords):
        return TaskLevel.SEDANG
    
    # Default: RINGAN
    return TaskLevel.RINGAN


def get_recommended_model(task_desc: str) -> dict:
    """
    Mendapatkan rekomendasi provider dan model termurah untuk tugas.
    
    Args:
        task_desc: Deskripsi tugas
        
    Returns:
        dict dengan provider, model, reason, cost_estimate
    """
    level = detect_task_level(task_desc)
    route = MODEL_ROUTES[level]
    
    # Estimasi biaya
    cost_info = COST_TABLE.get(route["model"], {"input": 0, "output": 0})
    
    return {
        "task_level": level.value,
        "provider": route["provider"],
        "model": route["model"],
        "reason": route["reason"],
        "cost_per_1k_input": cost_info["input"],
        "cost_per_1k_output": cost_info["output"],
        "tier": cost_info.get("tier", "unknown"),
        "agents": route.get("agents", ["deepseek"])
    }


def estimate_cost(prompt_chars: int, model: str = "deepseek-v4-flash") -> dict:
    """
    Estimasi biaya untuk prompt tertentu.
    
    Args:
        prompt_chars: Jumlah karakter prompt
        model: Nama model
        
    Returns:
        Estimasi token dan biaya
    """
    import tiktoken
    
    try:
        enc = tiktoken.get_encoding("cl100k_base")
        tokens = len(enc.encode(" " * prompt_chars))  # estimasi kasar
    except:
        tokens = prompt_chars // 4  # fallback: 4 chars ≈ 1 token
    
    cost_info = COST_TABLE.get(model, {"input": 0.00014, "output": 0.00028})
    
    input_cost = tokens * cost_info["input"] / 1000
    output_est = tokens // 3  # asumsi output 1/3 dari input
    output_cost = output_est * cost_info["output"] / 1000
    
    return {
        "estimated_tokens": tokens,
        "estimated_input_cost_usd": round(input_cost, 6),
        "estimated_output_cost_usd": round(output_cost, 6),
        "estimated_total_cost_usd": round(input_cost + output_cost, 6),
        "model": model,
        "tier": cost_info.get("tier", "unknown")
    }


# =========================================================================
# MCP Geopolitik — Data real-time untuk geopolitik
# =========================================================================
MCP_GEOPOLITIK = {
    "global_news": {
        "name": "Berita Global",
        "command": "python3 ~/MiroFish/tools/mcp-client.py news <topic>",
        "source": "Google News RSS",
        "cost": "gratis"
    },
    "country_info": {
        "name": "Info Negara",
        "command": "python3 ~/MiroFish/tools/mcp-client.py country <name>",
        "source": "REST Countries",
        "cost": "gratis"
    },
    "economic_data": {
        "name": "Data Ekonomi",
        "command": "python3 ~/MiroFish/tools/mcp-client.py ekonomi <country>",
        "source": "Google News",
        "cost": "gratis"
    },
    "currency": {
        "name": "Kurs Valuta",
        "command": "python3 ~/MiroFish/tools/mcp-client.py kurs USD/IDR",
        "source": "Exchange Rate API",
        "cost": "gratis"
    },
    "market_data": {
        "name": "Data Pasar",
        "command": "python3 ~/MiroFish/tools/mcp-client.py saham <index>",
        "source": "Google News",
        "cost": "gratis"
    },
    "web_search": {
        "name": "Pencarian Web",
        "command": "python3 ~/MiroFish/tools/mcp-client.py search <query>",
        "source": "Google News + DDG",
        "cost": "gratis"
    },
    "wikipedia": {
        "name": "Referensi Wikipedia",
        "command": "python3 ~/MiroFish/tools/mcp-client.py wiki <query>",
        "source": "Wikipedia API",
        "cost": "gratis"
    }
}


def get_geopolitik_data(query: str) -> dict:
    """
    Mendapatkan data geopolitik dari MCP tools.
    Menggabungkan berita + info negara + ekonomi.
    """
    import subprocess
    import json
    
    results = {}
    
    # Cari berita
    try:
        berita = subprocess.run(
            ['python3', str(Path.home() / 'MiroFish/tools/mcp-client.py'), 'news', query],
            capture_output=True, text=True, timeout=15
        )
        if berita.stdout:
            results['news'] = json.loads(berita.stdout)
    except:
        results['news'] = {"error": "gagal ambil berita"}
    
    # Cari info negara (jika query berisi nama negara)
    negara_keywords = ['indonesia', 'malaysia', 'singapore', 'thailand', 'china', 'jepang', 
                       'korea', 'india', 'amerika', 'inggris', 'prancis', 'jerman', 'rusia']
    for negara in negara_keywords:
        if negara in query.lower():
            try:
                info = subprocess.run(
                    ['python3', str(Path.home() / 'MiroFish/tools/mcp-client.py'), 'country', negara],
                    capture_output=True, text=True, timeout=15
                )
                if info.stdout:
                    results['country'] = json.loads(info.stdout)
            except:
                pass
            break
    
    return results


# =========================================================================
# Skill: Cost-Aware Agent
# =========================================================================
COST_AWARE_SKILL = """
### SKILL: HEMAT BIAYA 🏦
Kamu adalah agent yang pintar milih model. Aturannya:

| Level Tugas | Agent Yang Dipakai | Biaya |
|-------------|-------------------|-------|
| 🔵 Ringan/Sedang | DeepSeek aja | $0.14/M (murah) |
| 🟡 Berat | **SEMUA AGEN** 🤝 (DeepSeek + Groq + Atomesus) | **GRATIS** |
| 🔴 Geopolitik | **SEMUA AGEN + MCP DATA** 🌐 | **GRATIS** |

PRINSIP:
- Tugas ringan → DeepSeek aja, irit
- Tugas berat → ALL HANDS ON DECK! Semua agent kerja bareng
- Geopolitik → Semua agent + data real-time dari MCP
- Gunakan MCP tools (GRATIS) untuk data terkini
- Jangan buang token untuk basa-basi
"""


# =========================================================================
# MAIN — CLI
# =========================================================================
def list_routes():
    """Tampilkan semua route."""
    lines = ["\n🗺️  Cost-Saving Router MiroFish:", "=" * 50]
    for level, route in MODEL_ROUTES.items():
        agents = ", ".join(route.get("agents", ["?"]))
        lines.append(f"\n  [{level.value.upper()}]")
        lines.append(f"     Agent: {agents}")
        lines.append(f"     Alasan: {route['reason']}")
    return "\n".join(lines)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        task = ' '.join(sys.argv[1:])
        rec = get_recommended_model(task)
        est = estimate_cost(len(task) * 10)
        print(json.dumps({
            "rekomendasi": rec,
            "estimasi_biaya": est
        }, indent=2, ensure_ascii=False))
    else:
        print("Cost-Saving Router — Pilih model termurah")
        print()
        print("Penggunaan: python3 cost_router.py <deskripsi tugas>")
        print()
        print("Contoh:")
        print('  python3 cost_router.py "Apa ibu kota Indonesia?"  → DeepSeek')
        print('  python3 cost_router.py "Analisis geopolitik kawasan Asia"  → Groq gratis')
        print()
        print(list_routes())
