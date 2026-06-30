<div align="center">

<img src="https://img.shields.io/badge/Version-2.0.0-blue?style=for-the-badge" alt="Version">
<img src="https://img.shields.io/badge/License-AGPL--3.0-green?style=for-the-badge" alt="License">
<img src="https://img.shields.io/badge/Node.js-18+-339933?style=for-the-badge&logo=node.js&logoColor=white" alt="Node.js">
<img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">

<br><br>

# 🐟 MiroFish Agent

### Enhanced Fork — Multi-Agent AI Prediction Engine

**Fork dari [MiroFish](https://github.com/666ghj/MiroFish) oleh [666ghj](https://github.com/666ghj)**  
Ditambahkan: MCP Data Tools · Multi-Provider LLM · Agent Skills · Bahasa Indonesia

<br>

[![Original MiroFish](https://img.shields.io/badge/Original-MiroFish-ff6b6b?style=for-the-badge&logo=github)](https://github.com/666ghj/MiroFish)
[![Groq Free](https://img.shields.io/badge/Groq-GRATIS-4CAF50?style=for-the-badge)](https://console.groq.com/keys)
[![Gemini Free](https://img.shields.io/badge/Gemini-GRATIS-4285F4?style=for-the-badge&logo=google)](https://aistudio.google.com/apikey)

</div>

---

## 📖 Tentang

**MiroFish** adalah mesin prediksi berbasis **kecerdasan sekumul (swarm intelligence)** yang menggunakan teknologi multi-agent. Dengan mengekstraksi informasi seed dari dunia nyata, MiroFish secara otomatis membangun dunia digital paralel di mana ribuan agen cerdas berinteraksi dan berevolusi sosial.

> ⭐ **Repository asli:** [github.com/666ghj/MiroFish](https://github.com/666ghj/MiroFish)  
> 🍴 **Fork ini** menambahkan fitur MCP, multi-provider, agent skills, dan Bahasa Indonesia.

---

## ✨ Apa yang Ditambahkan di Fork Ini?

| Fitur | Original | Fork Ini |
|-------|----------|----------|
| 📄 Upload Dokumen | ✅ | ✅ |
| 🖼️ Analisis Gambar | ❌ | ✅ AI Vision |
| 🔗 Fetch URL | ❌ | ✅ + Screenshot |
| 🖥️ Review Localhost | ❌ | ✅ UI Analysis |
| 🌐 MCP Data Tools | ❌ | ✅ **11 tools GRATIS** |
| 🤖 Multi-Provider LLM | ❌ (1 provider) | ✅ **6 provider** |
| 🏦 Agent Skills | ❌ | ✅ **9 skill bawaan** |
| 💰 Cost-Saving Router | ❌ | ✅ Pilih termurah |
| 🇮🇩 Bahasa Indonesia | ❌ | ✅ 665+ key |
| 📊 History & Replay | ❌ | ✅ Lihat + Hapus |
| 🔄 MCP Daemon | ❌ | ✅ Auto-update data |

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/farhanturu/mirofish-agent.git
cd mirofish-agent

# 2. Daftar ZEP (GRATIS, WAJIB!)
#    Buka https://app.getzep.com → Sign up → Copy API key

# 3. Setup API key
cp .env.example .env
nano .env
#    Isi ZEP_API_KEY (wajib) + minimal 1 provider LLM

# 4. Install semua dependensi
npm run setup:all

# 5. Jalankan!
npm run dev
```

**Buka browser:** http://localhost:3000

---

## 🔑 API Key yang Dibutuhkan

### 🔴 WAJIB: ZEP Memory Graph (GRATIS!)

ZEP digunakan untuk **knowledge graph & memori agent**. Tanpa ZEP, MiroFish **tidak bisa jalan**.

| Info | Detail |
|------|--------|
| **Daftar** | https://app.getzep.com |
| **Biaya** | **GRATIS** untuk penggunaan ringan |
| **Fungsi** | Knowledge graph, memori agent, GraphRAG |
| **Wajib?** | ✅ **YA** |

```bash
# Cara dapat ZEP API key:
# 1. Buka https://app.getzep.com
# 2. Sign up (gratis, no credit card)
# 3. Buka dashboard → copy API key
# 4. Paste ke .env:
ZEP_API_KEY=z_your_key_here
```

### Provider LLM (Pilih Minimal 1)

| Provider | Biaya | Daftar | Model | Kecepatan |
|----------|-------|--------|-------|-----------|
| 🦙 **Groq** | **GRATIS** 30 RPM | [Daftar](https://console.groq.com/keys) | Llama 3.3 70B | ⚡⚡⚡ |
| 🆓 **Gemini** | **GRATIS** 1500/hari | [Daftar](https://aistudio.google.com/apikey) | Gemini 2.0 Flash | ⚡⚡ |
| 🏆 **Atomesus** | Plan-based | [Daftar](https://www.atomesus.com/dashboard) | Cipher | ⚡⚡⚡ |
| 🤖 **Together AI** | **GRATIS** 60 RPM | [Daftar](https://api.together.xyz/settings/api-keys) | Llama 3.1 8B | ⚡⚡ |
| 💻 **Ollama** | **GRATIS** lokal | [Install](https://ollama.com) | Llama 3.2 | ⚡ |

> 💡 **Groq + Gemini = 100% GRATIS**, tanpa kartu kredit!

---

## 🌐 MCP Data Agent — 11 Tools Real-Time

| # | Tool | Perintah | Sumber | Gratis? |
|---|------|----------|--------|---------|
| 1 | 🔍 **Search** | `search <query>` | Google News | ✅ |
| 2 | 📰 **Berita** | `news <topic>` | Google News | ✅ |
| 3 | 🌤️ **Cuaca** | `weather <kota>` | wttr.in | ✅ |
| 4 | 🌏 **Negara** | `country <nama>` | REST Countries | ✅ |
| 5 | 💱 **Kurs** | `kurs USD/IDR` | Exchange Rate | ✅ |
| 6 | ₿ **Crypto** | `crypto bitcoin` | CoinGecko | ✅ |
| 7 | 🏅 **Emas** | `emas` | Gold API | ✅ |
| 8 | 📈 **Saham** | `saham IHSG` | Google News | ✅ |
| 9 | 📊 **Ekonomi** | `ekonomi Indonesia` | Google News | ✅ |
| 10 | 📚 **Wikipedia** | `wiki <query>` | Wikipedia | ✅ |
| 11 | 🤖 **Auto** | `auto <query>` | Auto-detect | ✅ |

```bash
python3 tools/mcp-client.py kurs USD/IDR
python3 tools/mcp-client.py crypto bitcoin
python3 tools/mcp-client.py saham IHSG
```

---

## 🧠 9 Agent Skills Bawaan

Setiap agen dalam simulasi otomatis punya 9 skill:

| # | Skill | Fungsi |
|---|-------|--------|
| 1 | 🔍 Pencarian Data | Cari info real-time |
| 2 | 📊 Analisis Terstruktur | Data → Analisis → Kesimpulan |
| 3 | 👁️ Perspektif Berganda | Multi-sudut pandang |
| 4 | 🤝 Kolaborasi | Kerja sama antar agen |
| 5 | 🧠 Berpikir Kritis | Tantang asumsi |
| 6 | 🌏 Konteks Indonesia | Pahami budaya lokal |
| 7 | 📈 Berbasis Data | Argumen dengan fakta |
| 8 | 🏦 Hemat Biaya | Pilih model termurah |
| 9 | 🌐 Geopolitik | Data global real-time |

---

## 🛠️ CLI Tools

```bash
# Data real-time
python3 tools/mcp-client.py search "ekonomi Indonesia"
python3 tools/mcp-client.py kurs USD/IDR
python3 tools/mcp-client.py weather jakarta

# Chat AI gratis
python3 tools/free-chat.py --model groq-llama "Analisis IHSG"

# History
python3 tools/history-viewer.py env
python3 tools/history-viewer.py hapus sim_xxx

# Monitor
python3 tools/process-monitor.py

# MCP Daemon (auto-update)
python3 tools/mcp-daemon.py start
```

---

## 🌐 API Endpoints

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| `GET` | `/health` | Health check |
| `POST` | `/api/graph/ontology/generate` | Upload & buat ontologi |
| `POST` | `/api/graph/build` | Bangun grafik pengetahuan |
| `POST` | `/api/simulation/create` | Buat simulasi |
| `POST` | `/api/simulation/prepare` | Siapkan lingkungan |
| `POST` | `/api/simulation/start` | Jalankan simulasi |
| `GET` | `/api/simulation/:id/run-status` | Status simulasi |
| `POST` | `/api/report/generate` | Buat laporan prediksi |
| `POST` | `/api/report/chat` | Chat dengan Report Agent |
| `POST` | `/api/simulation/interview` | Wawancara agen |
| `GET` | `/api/mcp/status` | Status MCP daemon |

---

## 📁 Struktur Project

```
mirofish-agent/
├── README.md                 ← Dokumentasi
├── .env.example              ← Template API key (AMAN)
├── .gitignore                ← Proteksi data sensitif
├── package.json              ← Dependencies Node.js
├── docker-compose.yml        ← Docker deployment
├── LICENSE                   ← AGPL-3.0
│
├── frontend/                 ← Vue 3 + Vite
│   └── src/
│       ├── views/            ← Halaman web
│       ├── components/       ← Komponen UI (HistoryDatabase, dll)
│       ├── i18n/             ← Terjemahan
│       └── router/           ← Routing
│
├── backend/                  ← Flask + Python
│   ├── app/
│   │   ├── api/              ← REST API (graph, simulation, report, mcp)
│   │   ├── services/         ← Business logic
│   │   ├── agent_skills/     ← 🆕 9 skill bawaan + cost router
│   │   └── utils/            ← Utilities
│   ├── scripts/              ← Simulation scripts
│   └── uploads/              ← Data simulasi (gitignored)
│
├── tools/                    ← 🆕 CLI Tools
│   ├── mcp-client.py         ← 11 MCP data tools
│   ├── mcp-daemon.py         ← Background data updater
│   ├── free-chat.py          ← Chat AI gratis
│   ├── history-viewer.py     ← Lihat & hapus history
│   ├── simulation-replay.py  ← Replay simulasi
│   ├── process-monitor.py    ← Monitor proses
│   ├── analyze-image.py      ← Analisis gambar
│   ├── fetch-url.py          ← Fetch URL
│   └── review-localhost.py   ← Review aplikasi
│
├── locales/                  ← Terjemahan UI
│   ├── id.json               ← 🆕 Bahasa Indonesia (665+ key)
│   ├── en.json               ← English
│   ├── zh.json               ← 中文
│   └── languages.json        ← Daftar bahasa
│
└── skills/                   ← Agent skill definitions
    └── pinchtab/             ← Browser control skills
```

---

## 🤖 AI Agent Skill — `/mirofish-agent`

Repo ini juga berisi **skill untuk AI agent** yang bisa dipanggil langsung:

```
/mirofish-agent          # Setup & jalankan MiroFish
/mirofish-agent start    # Jalankan ulang
/mirofish-agent config   # Ubah provider/konfigurasi
```

### Instalasi Skill

```bash
# Copy skill ke direktori agent
cp -r skills/mirofish-agent ~/.agents/skills/

# Atau symlink (agar update otomatis)
ln -sf $(pwd)/skills/mirofish-agent ~/.agents/skills/mirofish-agent
```

### Fitur Skill

| Fitur | Keterangan |
|-------|------------|
| 🚀 One-Click Setup | Clone, install, configure, jalankan otomatis |
| 🇮🇩 Bahasa Indonesia | UI diterjemahkan lengkap (665+ key) |
| 🤖 Multi-Provider | Groq, Gemini, Atomesus, Together AI, Ollama |
| 🌐 MCP Data | 11 tools data real-time |
| 🏦 Cost Router | Pilih model termurah otomatis |
| 🧠 9 Agent Skills | Bawaan, aktif otomatis |

### File Skill

```
skills/mirofish-agent/
├── SKILL.md           ← Instruksi utama untuk AI agent
├── README.md          ← Dokumentasi skill
├── .env.example       ← Template API key
├── providers.json     ← Registry provider
├── setup.sh           ← Script instalasi
├── config.sh          ← Konfigurasi interaktif
└── patches/           ← Patch UI & backend
```

---

## 🐳 Docker

```bash
# Build & run
docker compose up -d

# Atau build manual
docker build -t mirofish-agent .
docker run -p 3000:3000 -p 5001:5001 mirofish-agent
```

---

## 📝 Bahasa Indonesia

UI MiroFish sudah diterjemahkan ke **8 bahasa**:

| Bahasa | Code | Status |
|--------|------|--------|
| 🇮🇩 Bahasa Indonesia | `id` | ✅ Default |
| 🇺🇸 English | `en` | ✅ |
| 🇨🇳 中文 | `zh` | ✅ |
| 🇪🇸 Español | `es` | ✅ |
| 🇫🇷 Français | `fr` | ✅ |
| 🇵🇹 Português | `pt` | ✅ |
| 🇷🇺 Русский | `ru` | ✅ |
| 🇩🇪 Deutsch | `de` | ✅ |

---

## 🤝 Kontribusi

1. Fork repository ini
2. Buat branch: `git checkout -b feature/nama-fitur`
3. Commit: `git commit -m "feat: tambah fitur X"`
4. Push: `git push origin feature/nama-fitur`
5. Buat Pull Request

---

## 🙏 Credits

| Kontribusi | Author |
|------------|--------|
| **MiroFish Original** | [666ghj](https://github.com/666ghj) |
| **CAMEL-OASIS Engine** | [camel-ai](https://github.com/camel-ai) |
| **Zep Memory Graph** | [getzep](https://github.com/getzep) |
| **MCP Data Tools** | Fork Enhancement |
| **Multi-Provider** | Fork Enhancement |
| **Agent Skills** | Fork Enhancement |
| **Bahasa Indonesia** | Fork Enhancement |

---

## 📄 License

[AGPL-3.0](LICENSE) — Sesuai dengan license original MiroFish.

---

<div align="center">

**Original:** [github.com/666ghj/MiroFish](https://github.com/666ghj/MiroFish)  
**Fork ini:** [github.com/YOUR_USERNAME/mirofish-agent](https://github.com/YOUR_USERNAME/mirofish-agent)

<br>

🐟 **MiroFish Agent** — Enhanced with MCP, Multi-Provider & Agent Skills

</div>
