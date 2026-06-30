# Skill: mirofish-agent

> **Gunakan ketika**: User ingin menjalankan simulasi prediksi multi-agent AI, analisis dokumen/gambar/URL, cari data real-time, atau review aplikasi.

## Ringkasan

MiroFish adalah mesin prediksi berbasis kecerdasan sekumul (swarm intelligence). Upload dokumen, gambar, atau URL → MiroFish bangun grafik pengetahuan → simulasi 31+ agen AI berinteraksi → hasilkan laporan prediksi.

---

## Setup (Sekali Saja)

```bash
# 1. Clone
git clone https://github.com/farhanturu/mirofish-agent.git ~/MiroFish
cd ~/MiroFish

# 2. Daftar ZEP (WAJIB, GRATIS): https://app.getzep.com
# 3. Daftar LLM (pilih salah satu, GRATIS):
#    - Groq: https://console.groq.com/keys
#    - Gemini: https://aistudio.google.com/apikey

# 4. Buat .env
cat > .env << 'EOF'
ZEP_API_KEY=your_zep_key
GROQ_API_KEY=your_groq_key
EOF

# 5. Install
npm run setup:all

# 6. Jalankan
npm run dev
```

- Frontend: http://localhost:3000
- Backend: http://localhost:5001

---

## Menjalankan MiroFish

```bash
# Cek status
curl -s http://localhost:5001/health

# Start (jika belum jalan)
cd ~/MiroFish && npm run dev &

# Stop
pkill -f "npm run dev"
```

---

## Provider LLM

| Provider | Biaya | Daftar |
|----------|-------|--------|
| 🦙 Groq | GRATIS 30 RPM | https://console.groq.com/keys |
| 🆓 Gemini | GRATIS 1500/hari | https://aistudio.google.com/apikey |
| 🏆 Atomesus | Plan-based | https://www.atomesus.com/dashboard |
| 🤖 Together AI | GRATIS 60 RPM | https://api.together.xyz/settings/api-keys |
| 💻 Ollama | GRATIS lokal | `ollama pull llama3.2` |

Isi di `.env`:
```
GROQ_API_KEY=gsk_xxx
GEMINI_API_KEY=xxx
ZEP_API_KEY=z_xxx
```

---

## Alur Prediksi Lengkap

### 1. Upload Dokumen → Buat Ontologi
```bash
curl -X POST http://localhost:5001/api/graph/ontology/generate \
  -F "files=@dokumen.pdf" \
  -F "simulation_requirement=Prediksi dampak kebijakan X"
```

### 2. Bangun Grafik Pengetahuan
```bash
curl -X POST http://localhost:5001/api/graph/build \
  -H "Content-Type: application/json" \
  -d '{"project_id": "proj_xxx"}'
```

### 3. Buat Simulasi
```bash
curl -X POST http://localhost:5001/api/simulation/create \
  -H "Content-Type: application/json" \
  -d '{"project_id": "proj_xxx"}'
```

### 4. Siapkan Lingkungan
```bash
curl -X POST http://localhost:5001/api/simulation/prepare \
  -H "Content-Type: application/json" \
  -d '{"simulation_id": "sim_xxx"}'
```

### 5. Jalankan Simulasi
```bash
curl -X POST http://localhost:5001/api/simulation/start \
  -H "Content-Type: application/json" \
  -d '{"simulation_id": "sim_xxx", "max_rounds": 30}'
```

### 6. Monitor Progress
```bash
curl http://localhost:5001/api/simulation/sim_xxx/run-status
```

### 7. Buat Laporan
```bash
curl -X POST http://localhost:5001/api/report/generate \
  -H "Content-Type: application/json" \
  -d '{"simulation_id": "sim_xxx"}'
```

### 8. Ambil Laporan
```bash
curl http://localhost:5001/api/report/report_xxx
```

---

## MCP Data Tools (Real-Time, GRATIS)

```bash
cd ~/MiroFish

# Berita
python3 tools/mcp-client.py news "ekonomi Indonesia"

# Kurs
python3 tools/mcp-client.py kurs USD/IDR

# Crypto
python3 tools/mcp-client.py crypto bitcoin

# Cuaca
python3 tools/mcp-client.py weather jakarta

# Info negara
python3 tools/mcp-client.py country indonesia

# Indeks saham
python3 tools/mcp-client.py saham IHSG

# Ekonomi
python3 tools/mcp-client.py ekonomi Indonesia

# Wikipedia
python3 tools/mcp-client.py wiki "Piala Dunia 2026"

# Auto-detect
python3 tools/mcp-client.py auto "berapa harga bitcoin?"
```

---

## Chat dengan AI (GRATIS)

```bash
cd ~/MiroFish

# Groq (gratis, cepat)
GROQ_API_KEY=gsk_xxx python3 tools/free-chat.py --model groq-llama "Analisis IHSG"

# Gemini (gratis)
GEMINI_API_KEY=xxx python3 tools/free-chat.py "Prediksi ekonomi 2027"
```

---

## History & Hapus

```bash
cd ~/MiroFish

# Lihat semua
python3 tools/history-viewer.py env

# Detail simulasi
python3 tools/history-viewer.py sim sim_xxx

# Hapus
python3 tools/history-viewer.py hapus sim_xxx

# Hapus semua
python3 tools/history-viewer.py clean --force
```

---

## Monitor Proses

```bash
python3 tools/process-monitor.py
```

---

## Chat dengan Report Agent

```bash
curl -X POST http://localhost:5001/api/report/chat \
  -H "Content-Type: application/json" \
  -d '{
    "simulation_id": "sim_xxx",
    "message": "Apa prediksi utama?"
  }'
```

---

## Wawancara Agen

```bash
curl -X POST http://localhost:5001/api/simulation/interview \
  -H "Content-Type: application/json" \
  -d '{
    "simulation_id": "sim_xxx",
    "agent_id": 0,
    "prompt": "Apa pendapat Anda?"
  }'
```

---

## Endpoint API Lengkap

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | `/health` | Health check |
| POST | `/api/graph/ontology/generate` | Upload & ontologi |
| POST | `/api/graph/build` | Bangun grafik |
| POST | `/api/simulation/create` | Buat simulasi |
| POST | `/api/simulation/prepare` | Siapkan lingkungan |
| POST | `/api/simulation/start` | Jalankan simulasi |
| GET | `/api/simulation/:id/run-status` | Status simulasi |
| POST | `/api/report/generate` | Buat laporan |
| POST | `/api/report/chat` | Chat Report Agent |
| POST | `/api/simulation/interview` | Wawancara agen |
| GET | `/api/simulation/history` | Riwayat simulasi |
| GET | `/api/mcp/status` | Status MCP |

---

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Backend mati | `cd ~/MiroFish && npm run dev &` |
| Frontend mati | Tunggu 10 detik |
| Port dipakai | `lsof -i :5001` lalu `kill <PID>` |
| ZEP error | Cek `ZEP_API_KEY` di `.env` |
| Groq quota | Tunggu 1 menit (30 RPM free) |
| Gemini quota | Tunggu reset midnight |

---

## Lokasi

```
~/MiroFish/
├── frontend/     ← Vue 3 (localhost:3000)
├── backend/      ← Flask (localhost:5001)
├── tools/        ← CLI tools
└── skills/       ← Skill ini
```
