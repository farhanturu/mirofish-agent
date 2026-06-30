# Skill: mirofish-agent

> **Gunakan skill ini ketika**: User ingin menjalankan simulasi prediksi AI, analisis dokumen/gambar/URL, review website atau aplikasi localhost, prediksi multi-agent, atau cari data real-time dari web.

## Apa Itu MiroFish?

MiroFish adalah **mesin prediksi & analisis multi-agent** dengan dukungan **multi-provider LLM** dan **MCP data real-time**.

| Input | Contoh | Yang Dilakukan |
|-------|--------|----------------|
| 📄 **Dokumen** | PDF, TXT, MD | Ekstraksi → grafik pengetahuan → simulasi → prediksi |
| 🖼️ **Gambar** | Logo, desain, screenshot | Analisis visual via LLM vision |
| 🔗 **URL/Link** | Website, artikel | Fetch konten + screenshot → analisis |
| 🖥️ **Localhost** | App di port tertentu | Review UI/HTML → screenshot → skor |

## Cara Menjalankan MiroFish

```bash
# Cek apakah sudah jalan
curl -s http://localhost:5001/health

# Start
cd ~/MiroFish && npm run dev &
sleep 10

# Stop
pkill -f "npm run dev"
```

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5001

## Provider LLM

| Provider | Model | Biaya | Peran |
|----------|-------|-------|-------|
| 🦙 **Groq** 🆓 | `llama-3.3-70b-versatile` | **GRATIS 30 RPM** | Primary — ChatGPT-quality |
| 🆓 **Gemini** 🆓 | `gemini-2.0-flash` | **GRATIS 1500/hari** | Backup — Google AI |
| 🏆 **Atomesus** | `cipher` | Plan-based | Cadangan premium |
| 🤖 **Together AI** 🆓 | `Llama-3.3-70B` | **GRATIS 60 RPM** | Alternatif open-source |
| 💻 **Ollama** 🆓 | `llama3.2` | **GRATIS lokal** | 100% Privat |

## MCP Data Agent — 11 Tools (GRATIS)

| # | Tool | Perintah | Sumber |
|---|------|----------|--------|
| 1 | 🔍 **Search** | `search <q>` | Google News |
| 2 | 📰 **Berita** | `news <q>` | Google News |
| 3 | 🌤️ **Cuaca** | `weather <lokasi>` | wttr.in |
| 4 | 🌏 **Negara** | `country <name>` | REST Countries |
| 5 | 💱 **Kurs** | `kurs USD/IDR` | Exchange Rate API |
| 6 | ₿ **Crypto** | `crypto bitcoin` | CoinGecko |
| 7 | 🏅 **Emas** | `emas` | Gold API |
| 8 | 📈 **Saham** | `saham IHSG` | Google News |
| 9 | 📊 **Ekonomi** | `ekonomi Indonesia` | Google News |
| 10 | 📚 **Wikipedia** | `wiki <q>` | Wikipedia API |
| 11 | 🤖 **Auto** | `auto <q>` | Auto-detect |

```bash
python3 ~/MiroFish/tools/mcp-client.py search "ekonomi Indonesia 2026"
python3 ~/MiroFish/tools/mcp-client.py kurs USD/IDR
python3 ~/MiroFish/tools/mcp-client.py crypto bitcoin
```

## Team Agent — Multi-Provider + Shared Memory

| Tim | Agent | Provider | Peran |
|-----|-------|----------|-------|
| **Standar** | Analis Data | Groq | Kumpulkan data |
| | Sintesis | Groq | Analisis & kesimpulan |
| **Prediksi** | Analis Data | Groq | Data & statistik |
| | Strategist | Groq | Pola & strategi |
| | Kreator | Gemini | Ide kreatif |
| | Kritikus | Groq | Validasi |
| **Dev** | Implementer | Groq | Coding |
| | Reviewer | Gemini | Review kode |
| | Tester | Groq | Test coverage |

```bash
python3 ~/.agents/skills/team-agent/team-manager.py default "Analisis ekonomi"
python3 ~/.agents/skills/team-agent/team-manager.py prediksi "Prediksi IHSG"
python3 ~/.agents/skills/team-agent/team-manager.py dev "Buat fungsi fibonacci"
```

## History & Replay

```bash
# Lihat history
python3 ~/MiroFish/tools/history-viewer.py env
python3 ~/MiroFish/tools/history-viewer.py sims

# Hapus
python3 ~/MiroFish/tools/history-viewer.py hapus sim_xxx
python3 ~/MiroFish/tools/history-viewer.py clean --force

# Replay simulasi
python3 ~/MiroFish/tools/simulation-replay.py world sim_xxx
python3 ~/MiroFish/tools/simulation-replay.py replay sim_xxx
```

## Tools Lengkap

```
~/MiroFish/tools/
├── mirofish-input.sh     ← Master input (dokumen/gambar/URL/localhost)
├── mcp-client.py         ← 11 MCP tools (data real-time GRATIS)
├── mcp-daemon.py         ← Background daemon (auto-update data)
├── free-chat.py          ← Chat dengan AI gratis (Groq/Gemini)
├── history-viewer.py     ← Lihat & hapus history
├── simulation-replay.py  ← Replay simulasi
├── process-monitor.py    ← Monitor proses
├── analyze-image.py      ← Analisis gambar
├── fetch-url.py          ← Fetch URL
└── review-localhost.py   ← Review aplikasi localhost
```

## Konfigurasi

```bash
cp ~/MiroFish/.env.example ~/MiroFish/.env
nano ~/MiroFish/.env  # Isi API key
```

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Backend down | `cd ~/MiroFish && npm run dev &` |
| Frontend down | Tunggu 10 detik |
| Port dipakai | `lsof -i :5001` lalu `kill <PID>` |
| Groq quota | Tunggu 1 menit, 30 RPM free tier |
| Gemini quota | Tunggu, reset midnight |
| History duplikat | `history-viewer.py hapus sim_xxx` |
