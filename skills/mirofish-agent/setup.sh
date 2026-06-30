#!/usr/bin/env bash
# =============================================================================
# MiroFish Agent — Setup Otomatis
# Skrip ini meng-clone, menginstal dependensi, menerjemahkan UI,
# dan mengonfigurasi MiroFish untuk penggunaan lokal.
# =============================================================================

set -euo pipefail

MIROFISH_DIR="$HOME/MiroFish"
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
PATCHES_DIR="$SKILL_DIR/patches"

# --- Warna & Ikon ---
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
BOLD='\033[1m'; NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
err()   { echo -e "${RED}[✗]${NC} $*"; }
header(){ echo -e "\n${BOLD}${CYAN}━━━ $* ━━━${NC}\n"; }

# =========================================================================
# STEP 0: Verifikasi Dependensi Sistem
# =========================================================================
header "STEP 0: Verifikasi Dependensi Sistem"

check_cmd() {
    local cmd="$1" pkg="${2:-$1}"
    if command -v "$cmd" &>/dev/null; then
        ok "$cmd terinstal: $("$cmd" --version 2>/dev/null | head -1)"
    else
        warn "$cmd belum terinstal, mencoba menginstal $pkg..."
        return 1
    fi
}

# Node.js
if ! check_cmd node "nodejs"; then
    if command -v apt-get &>/dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - && sudo apt-get install -y nodejs
    elif command -v brew &>/dev/null; then
        brew install node@22
    else
        err "Tidak dapat menginstal Node.js. Silakan instal manual: https://nodejs.org/"
        exit 1
    fi
fi

# Python 3.11+
if ! check_cmd python3 "python3"; then
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y python3 python3-venv python3-pip
    elif command -v brew &>/dev/null; then
        brew install python@3.12
    else
        err "Tidak dapat menginstal Python. Silakan instal manual: https://python.org/"
        exit 1
    fi
fi

# uv (Python package manager)
if ! check_cmd uv "uv"; then
    info "Menginstal uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    ok "uv terinstal"
fi

# Git
if ! check_cmd git "git"; then
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y git
    fi
fi

# =========================================================================
# STEP 1: Clone / Update MiroFish
# =========================================================================
header "STEP 1: Clone / Update MiroFish"

if [ -d "$MIROFISH_DIR/.git" ]; then
    info "MiroFish sudah ada di $MIROFISH_DIR, melakukan pull..."
    cd "$MIROFISH_DIR"
    git pull --ff-only 2>/dev/null || warn "Git pull gagal, menggunakan versi lokal"
    ok "MiroFish siap (versi lokal)"
else
    info "Meng-clone MiroFish dari GitHub..."
    git clone https://github.com/666ghj/MiroFish.git "$MIROFISH_DIR"
    ok "MiroFish berhasil di-clone ke $MIROFISH_DIR"
fi

cd "$MIROFISH_DIR"

# =========================================================================
# STEP 2: Instal Dependensi
# =========================================================================
header "STEP 2: Instal Dependensi (Node.js + Python)"

info "Menginstal dependensi Node.js..."
npm install 2>/dev/null || npm install
info "Menginstal dependensi frontend..."
cd frontend && npm install 2>/dev/null && cd ..
info "Menginstal dependensi Python (backend)..."
npm run setup:backend 2>/dev/null || (cd backend && uv sync && cd ..)
ok "Semua dependensi terinstal"

# =========================================================================
# STEP 3: Patch UI ke Bahasa Indonesia
# =========================================================================
header "STEP 3: Patch UI ke Bahasa Indonesia"

LOCALES_DIR="$MIROFISH_DIR/locales"
I18N_FILE="$MIROFISH_DIR/frontend/src/i18n/index.js"

# Copy locale Indonesia
if [ -f "$PATCHES_DIR/id.json" ]; then
    cp "$PATCHES_DIR/id.json" "$LOCALES_DIR/id.json"
    ok "Locale Bahasa Indonesia ditambahkan"
else
    err "File patches/id.json tidak ditemukan di $PATCHES_DIR"
    exit 1
fi

# Update languages.json — tambah Bahasa Indonesia
if [ -f "$PATCHES_DIR/languages.json" ]; then
    cp "$PATCHES_DIR/languages.json" "$LOCALES_DIR/languages.json"
    ok "languages.json diperbarui (menambah Bahasa Indonesia)"
fi

# Update default locale ke 'id'
if [ -f "$PATCHES_DIR/i18n-index.js" ]; then
    cp "$PATCHES_DIR/i18n-index.js" "$I18N_FILE"
    ok "Default locale diubah ke Bahasa Indonesia (id)"
fi

# Update meta title bahasa Indonesia
HOME_VUE="$MIROFISH_DIR/frontend/src/views/Home.vue"
if [ -f "$HOME_VUE" ]; then
    # Ganti fallback title ke Indonesia
    sed -i "s/MiroFish - Predict Everything/MiroFish - Prediksi Segalanya/g" "$HOME_VUE" 2>/dev/null || true
    sed -i "s/MiroFish - Social Media Opinion Simulation System/MiroFish - Sistem Simulasi Opini Media Sosial/g" "$HOME_VUE" 2>/dev/null || true
    ok "Meta title diterjemahkan ke Bahasa Indonesia"
fi

# =========================================================================
# STEP 4: Patch Backend — Prompt Agent Pintar Indonesia
# =========================================================================
header "STEP 4: Patch Backend — System Prompt Indonesia"

PATCH_SCRIPT="$PATCHES_DIR/patch-backend.py"
if [ -f "$PATCH_SCRIPT" ]; then
    python3 "$PATCH_SCRIPT" || warn "Patch backend sebagian gagal (bisa diabaikan)"
else
    warn "patch-backend.py tidak ditemukan, skip patch backend"
fi

# =========================================================================
# STEP 5: Konfigurasi .env
# =========================================================================
header "STEP 5: Konfigurasi LLM Gratis"

ENV_FILE="$MIROFISH_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    warn "File .env sudah ada, melewati konfigurasi otomatis"
    info "Untuk mengubah konfigurasi, jalankan: /mirofish-agent config"
else
    info "Menjalankan konfigurasi interaktif..."
    if [ -f "$SKILL_DIR/config.sh" ]; then
        bash "$SKILL_DIR/config.sh"
    else
        warn "config.sh tidak ditemukan, membuat .env template..."
        cat > "$ENV_FILE" << 'ENVEOF'
# === MiroFish Agent — Konfigurasi LLM ===
# Edit file ini dengan API key yang benar

# LLM API Configuration
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.atomesus.com/v1
LLM_MODEL_NAME=cipher

# Provider type: 'atomesus' atau 'openai'
# Atomesus mengabaikan system messages, prompt otomatis digabung ke user msg
LLM_PROVIDER_TYPE=atomesus

# ZEP Memory Graph Configuration
# Daftar gratis: https://app.getzep.com/
ZEP_API_KEY=your_zep_api_key_here
ENVEOF
        warn "File .env template dibuat di $ENV_FILE"
        warn "Silakan edit manual dengan API key yang benar"
    fi
fi

# =========================================================================
# STEP 6: Informasi Akhir
# =========================================================================
header "INSTALASI SELESAI!"

echo -e "${GREEN}${BOLD}🐟 MiroFish Agent siap digunakan!${NC}"
echo ""
echo -e "  ${CYAN}Lokasi:${NC}   $MIROFISH_DIR"
echo -e "  ${CYAN}Frontend:${NC} http://localhost:3000"
echo -e "  ${CYAN}Backend:${NC}  http://localhost:5001"
echo ""
echo -e "  ${YELLOW}Untuk menjalankan:${NC}"
echo -e "    cd $MIROFISH_DIR && npm run dev"
echo ""
echo -e "  ${YELLOW}Untuk mengubah konfigurasi:${NC}"
echo -e "    Edit $ENV_FILE"
echo ""
