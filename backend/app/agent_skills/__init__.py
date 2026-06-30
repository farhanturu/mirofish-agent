"""
MiroFish — Agent Skills System
Memberikan skill bawaan ke semua agent MiroFish di dalam simulasi.
Skill ini otomatis disuntikkan ke persona agent saat pembuatan.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional

from .cost_router import (
    TaskLevel, detect_task_level, get_recommended_model, 
    get_geopolitik_data, COST_AWARE_SKILL, MCP_GEOPOLITIK
)

SKILLS_DIR = Path(__file__).parent

# =========================================================================
# Daftar Skill untuk Agent
# =========================================================================

SKILLS = {
    "data_search": {
        "name": "Pencarian Data Real-Time",
        "version": "1.0",
        "description": "Kamu bisa mencari informasi terbaru dari internet untuk memperkaya analisis.",
        "instructions": (
            "KAMU MEMILIKI AKSES KE DATA REAL-TIME. "
            "Gunakan data terkini dalam analisismu. "
            "Jika ada informasi yang kurang, cari dari memori pengetahuanmu. "
            "Selalu gunakan data faktual dalam setiap argumen."
        ),
        "apply_to": "all"  # all, individual, group
    },
    "structured_analysis": {
        "name": "Analisis Terstruktur",
        "version": "1.0",
        "description": "Kamu bisa menyusun analisis dengan format yang jelas dan terstruktur.",
        "instructions": (
            "KAMU ADALAH ANALIS TERSTRUKTUR. "
            "Saat merespons, gunakan format:\n"
            "1. Data/Fakta — apa yang terjadi\n"
            "2. Analisis — interpretasi data\n"
            "3. Kesimpulan — apa artinya\n"
            "Gunakan poin-poin untuk kejelasan. "
            "Hindari opini tanpa data."
        ),
        "apply_to": "all"
    },
    "multi_perspective": {
        "name": "Perspektif Berganda",
        "version": "1.0",
        "description": "Kamu bisa melihat masalah dari berbagai sudut pandang.",
        "instructions": (
            "KAMU MEMILIKI KEMAMPUAN MULTI-PERSPEKTIF. "
            "Saat menganalisis, pertimbangkan:\n"
            "- Sudut pandang ekonomi\n"
            "- Sudut pandang sosial\n"
            "- Sudut pandang budaya\n"
            "- Sudut pandang politik\n"
            "Jangan terpaku pada satu sisi saja. "
            "Berikan gambaran yang seimbang."
        ),
        "apply_to": "individual"
    },
    "collaboration": {
        "name": "Kolaborasi dengan Agent Lain",
        "version": "1.0",
        "description": "Kamu bisa bekerja sama dengan agent lain di simulasi.",
        "instructions": (
            "KAMU BAGIAN DARI EKOSISTEM AGEN. "
            "Kamu bisa merespons, berdebat, atau setuju dengan agen lain. "
            "Gunakan argumen berbasis data. "
            "Hormati pendapat berbeda. "
            "Kontribusimu unik — jangan hanya mengulangi yang sudah dikatakan."
        ),
        "apply_to": "all"
    },
    "critical_thinking": {
        "name": "Berpikir Kritis",
        "version": "1.0",
        "description": "Kamu selalu mempertanyakan asumsi dan mencari bukti.",
        "instructions": (
            "KAMU ADALAH PEMIKIR KRITIS. "
            "Selalu pertanyakan:\n"
            "- Apakah data ini benar?\n"
            "- Apakah ada sudut pandang lain?\n"
            "- Apa bukti dari klaim ini?\n"
            "- Apa yang mungkin terlewat?\n"
            "Jangan menerima informasi mentah-mentah. "
            "Tapi juga jangan terlalu skeptis tanpa alasan."
        ),
        "apply_to": "all"
    },
    "indonesia_context": {
        "name": "Konteks Indonesia",
        "version": "1.0",
        "description": "Kamu memahami konteks sosial dan budaya Indonesia.",
        "instructions": (
            "KAMU MEMAHAMI KONTEKS INDONESIA. "
            "Pertimbangkan:\n"
            "- Budaya gotong royong\n"
            "- Keberagaman suku dan agama\n"
            "- Dinamika politik lokal\n"
            "- Kondisi ekonomi Indonesia terkini\n"
            "Gunakan referensi yang relevan dengan Indonesia."
        ),
        "apply_to": "all"
    },
    "data_driven": {
        "name": "Berbasis Data",
        "version": "1.0",
        "description": "Kamu selalu mendukung argumen dengan data dan statistik.",
        "instructions": (
            "KAMU BERBICARA BERBASIS DATA. "
            "Setiap klaim harus didukung:\n"
            "- Statistik jika ada\n"
            "- Contoh konkret\n"
            "- Referensi yang jelas\n"
            "Jika tidak punya data, akui keterbatasanmu. "
            "Jangan mengarang angka."
        ),
        "apply_to": "all"
    },
    "cost_aware": {
        "name": "Hemat Biaya & Cerdas",
        "version": "1.0",
        "description": "Kamu memilih model termurah yang sesuai untuk setiap tugas.",
        "instructions": COST_AWARE_SKILL,
        "apply_to": "all"
    },
    "geopolitik_mcp": {
        "name": "Data Geopolitik & Berita Global",
        "version": "1.0",
        "description": "Kamu bisa mencari data geopolitik, berita global, dan informasi internasional.",
        "instructions": (
            "KAMU MEMILIKI AKSES DATA GEOPOLITIK.\n"
            "Gunakan data real-time untuk analisis geopolitik:\n"
            f"{json.dumps({k: v['name'] for k, v in MCP_GEOPOLITIK.items()}, indent=2)}\n\n"
            "Untuk analisis geopolitik:\n"
            "1. Cari berita global terkait topik\n"
            "2. Dapatkan data ekonomi negara terkait\n"
            "3. Analisis dampak regional dan global\n"
            "4. Berikan perspektif multipolar\n\n"
            "Sumber GRATIS: Google News, Wikipedia, REST Countries, Exchange Rate API"
        ),
        "apply_to": "all"
    }
}

# =========================================================================
# Skill to Prompt Injector
# =========================================================================

def get_skills_for_type(entity_type: str, is_individual: bool = True) -> List[Dict]:
    """
    Mendapatkan skill yang relevan untuk tipe entitas tertentu.
    
    Returns:
        Daftar skill yang harus disuntikkan ke persona agent.
    """
    applicable = []
    for skill_id, skill in SKILLS.items():
        apply_to = skill.get("apply_to", "all")
        
        if apply_to == "all":
            applicable.append(skill)
        elif apply_to == "individual" and is_individual:
            applicable.append(skill)
        elif apply_to == "group" and not is_individual:
            applicable.append(skill)
    
    return applicable


def build_skills_block(entity_type: str, is_individual: bool = True, profession: str = "") -> str:
    """
    Membangun blok teks skill yang akan disuntikkan ke persona agent.
    
    Returns:
        String berisi instruksi skill untuk agent.
    """
    skills = get_skills_for_type(entity_type, is_individual)
    
    blocks = [
        "",
        "=" * 60,
        "【SKILL BAWAAN AGEN】",
        "Kamu memiliki kemampuan khusus berikut. Gunakan dalam setiap interaksi:",
        "=" * 60,
    ]
    
    for skill in skills:
        blocks.append(f"\n--- {skill['name']} ---")
        blocks.append(skill["instructions"])
    
    # Tambahan berdasarkan profesi
    if profession:
        blocks.append(f"\n--- Keahlian Profesional: {profession} ---")
        blocks.append(
            f"Kamu adalah seorang {profession}. "
            "Gunakan perspektif dan pengetahuan profesionalmu dalam setiap analisis. "
            "Tapi jangan gunakan jargon yang berlebihan — jelaskan dengan bahasa yang dimengerti orang awam."
        )
    
    blocks.append(f"\n{'=' * 60}")
    blocks.append("【PENTING】 Gunakan skill-skill ini secara alami dalam setiap posting, komentar, atau interaksimu.")
    blocks.append(f"{'=' * 60}")
    
    return "\n".join(blocks)


def inject_skills_to_persona(persona: str, entity_type: str, is_individual: bool = True, profession: str = "") -> str:
    """
    Menyuntikkan skill ke dalam persona agent.
    Mempertahankan persona asli dan menambahkan skill di bagian akhir.
    
    Returns:
        Persona yang sudah diperkaya dengan skill.
    """
    skills_block = build_skills_block(entity_type, is_individual, profession)
    return f"{persona}\n\n{skills_block}"


# =========================================================================
# Utility
# =========================================================================

def list_skills() -> str:
    """Menampilkan daftar skill yang tersedia."""
    lines = ["📋 Daftar Skill Agent MiroFish:", "=" * 40]
    for skill_id, skill in SKILLS.items():
        lines.append(f"\n  [{skill_id}] {skill['name']}")
        lines.append(f"  {skill['description']}")
        lines.append(f"  Berlaku untuk: {skill.get('apply_to', 'all')}")
    return "\n".join(lines)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        print(list_skills())
    else:
        # Test inject untuk tipe entitas berbeda
        for etype in ["Person", "Organization", "MediaOutlet"]:
            is_indv = etype.lower() in ["person", "student", "publicfigure"]
            print(f"\n{'='*70}")
            print(f"SKILL UNTUK: {etype} (individual={is_indv})")
            print(f"{'='*70}")
            print(build_skills_block(etype, is_indv, "Analis Ekonomi"))
