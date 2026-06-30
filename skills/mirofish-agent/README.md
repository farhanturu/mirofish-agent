# 🐟 Skill: mirofish-agent

AI Agent skill untuk menjalankan **MiroFish** — mesin prediksi multi-agent AI.

## Fitur Skill

| Fitur | Keterangan |
|-------|------------|
| 🚀 **One-Click Setup** | Clone, install, configure, jalankan otomatis |
| 🇮🇩 **Bahasa Indonesia** | UI diterjemahkan lengkap (665+ key) |
| 🤖 **Multi-Provider** | Groq, Gemini, Atomesus, Together AI, Ollama |
| 🌐 **MCP Data** | 11 tools data real-time (berita, ekonomi, crypto, dll) |
| 🏦 **Cost Router** | Pilih model termurah otomatis |
| 🧠 **9 Agent Skills** | Bawaan, aktif otomatis untuk semua agen |

## Cara Pakai

```
/mirofish-agent                    # Setup & jalankan lengkap
/mirofish-agent start              # Jalankan ulang
/mirofish-agent config             # Ubah provider/konfigurasi
```

## Provider

| Provider | Biaya | Daftar |
|----------|-------|--------|
| Groq | GRATIS | https://console.groq.com/keys |
| Gemini | GRATIS | https://aistudio.google.com/apikey |
| Atomesus | Plan | https://www.atomesus.com/dashboard |
| Together AI | GRATIS | https://api.together.xyz/settings/api-keys |
| Ollama | GRATIS | Lokal |

## Setup

```bash
cp .env.example .env
# Edit .env — isi minimal 1 API key
```

## File

```
~/.agents/skills/mirofish-agent/
├── SKILL.md           ← Instruksi utama
├── README.md          ← File ini
├── setup.sh           ← Script instalasi
├── config.sh          ← Konfigurasi interaktif
├── providers.json     ← Registry provider
├── .env.example       ← Template API key (AMAN)
└── patches/           ← Patch UI & backend
```
