#!/usr/bin/env bash
# =============================================================================
# MiroFish Agent — Konfigurasi Interaktif
# Memandu user memilih model LLM gratis dan memasukkan API key
# =============================================================================

set -euo pipefail

MIROFISH_DIR="$HOME/MiroFish"
ENV_FILE="$MIROFISH_DIR/.env"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
BOLD='\033[1m'; NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
err()   { echo -e "${RED}[✗]${NC} $*"; }

# =========================================================================
# Pilih Model LLM
# =========================================================================
echo -e "\n${BOLD}${CYAN}🐟 MiroFish Agent — Konfigurasi LLM${NC}\n"
echo "Pilih model LLM yang ingin digunakan:"
echo ""
echo -e "  ${BOLD}1)${NC} Atomesus — Cipher ${GREEN}(Prime Account, Direkomendasikan)${NC}"
echo "     Kualitas tinggi, OpenAI-compatible, tanpa rate limit."
echo "     API Key: https://www.atomesus.com/dashboard"
echo ""
echo -e "  ${BOLD}2)${NC} Google Gemini 2.0 Flash Lite ${BOLD}(Paling Hemat, GRATIS)${NC}"
echo "     Paling ringan & cepat. OpenAI-compatible."
echo "     Free: 1500 request/hari, 1M token/menit."
echo "     Dapat key gratis: https://aistudio.google.com/apikey"
echo ""
echo -e "  ${BOLD}3)${NC} Google Gemini 2.0 Flash ${GREEN}(GRATIS)${NC}"
echo "     Balance antara kecepatan & kualitas."
echo "     Free: 1500 request/hari."
echo "     Dapat key gratis: https://aistudio.google.com/apikey"
echo ""
echo -e "  ${BOLD}4)${NC} Groq — Llama 3.3 70B ${GREEN}(Gratis)${NC}"
echo "     Free: 30 RPM. Super cepat."
echo "     API Key: https://console.groq.com/keys"
echo ""
echo -e "  ${BOLD}5)${NC} Groq — Mixtral 8x7B ${GREEN}(Gratis)${NC}"
echo "     Free: 30 RPM. Multilingual bagus."
echo "     API Key: https://console.groq.com/keys"
echo ""
echo -e "  ${BOLD}6)${NC} Groq — Llama 3.1 8B Instant ${GREEN}(Gratis)${NC}"
echo "     Free: 30 RPM. Paling cepat."
echo "     API Key: https://console.groq.com/keys"
echo ""
echo -e "  ${BOLD}7)${NC} Together AI — Llama 3.1 8B ${GREEN}(Gratis)${NC}"
echo "     Free: 60 RPM. Open-source."
echo "     API Key: https://api.together.xyz/settings/api-keys"
echo ""
echo -e "  ${BOLD}8)${NC} Together AI — Mixtral 8x7B ${GREEN}(Gratis)${NC}"
echo "     Free: 60 RPM. Multilingual kuat."
echo "     API Key: https://api.together.xyz/settings/api-keys"
echo ""

# =========================================================================
# Input Pilihan
# =========================================================================
read -rp "$(echo -e "${BOLD}Pilih model [1-8] (default: 1): ${NC}")" MODEL_CHOICE
MODEL_CHOICE="${MODEL_CHOICE:-1}"

case "$MODEL_CHOICE" in
    1)
        PROVIDER_NAME="Atomesus — Cipher"
        BASE_URL="https://api.atomesus.com/v1"
        MODEL_NAME="cipher"
        API_KEY_URL="https://www.atomesus.com/dashboard"
        PROVIDER_TYPE="atomesus"
        ;;
    2)
        PROVIDER_NAME="Google Gemini 2.0 Flash Lite"
        BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
        MODEL_NAME="gemini-2.0-flash-lite"
        API_KEY_URL="https://aistudio.google.com/apikey"
        PROVIDER_TYPE="openai"
        ;;
    3)
        PROVIDER_NAME="Google Gemini 2.0 Flash"
        BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
        MODEL_NAME="gemini-2.0-flash"
        API_KEY_URL="https://aistudio.google.com/apikey"
        PROVIDER_TYPE="openai"
        ;;
    4)
        PROVIDER_NAME="Groq — Llama 3.3 70B"
        BASE_URL="https://api.groq.com/openai/v1"
        MODEL_NAME="llama-3.3-70b-versatile"
        API_KEY_URL="https://console.groq.com/keys"
        PROVIDER_TYPE="openai"
        ;;
    5)
        PROVIDER_NAME="Groq — Mixtral 8x7B"
        BASE_URL="https://api.groq.com/openai/v1"
        MODEL_NAME="mixtral-8x7b-32768"
        API_KEY_URL="https://console.groq.com/keys"
        PROVIDER_TYPE="openai"
        ;;
    6)
        PROVIDER_NAME="Groq — Llama 3.1 8B Instant"
        BASE_URL="https://api.groq.com/openai/v1"
        MODEL_NAME="llama-3.1-8b-instant"
        API_KEY_URL="https://console.groq.com/keys"
        PROVIDER_TYPE="openai"
        ;;
    7)
        PROVIDER_NAME="Together AI — Llama 3.1 8B"
        BASE_URL="https://api.together.xyz/v1"
        MODEL_NAME="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
        API_KEY_URL="https://api.together.xyz/settings/api-keys"
        PROVIDER_TYPE="openai"
        ;;
    8)
        PROVIDER_NAME="Together AI — Mixtral 8x7B"
        BASE_URL="https://api.together.xyz/v1"
        MODEL_NAME="mistralai/Mixtral-8x7B-Instruct-v0.1"
        API_KEY_URL="https://api.together.xyz/settings/api-keys"
        PROVIDER_TYPE="openai"
        ;;
    *)
        warn "Pilihan tidak valid, menggunakan Atomesus — Cipher"
        PROVIDER_NAME="Atomesus — Cipher"
        BASE_URL="https://api.atomesus.com/v1"
        MODEL_NAME="cipher"
        API_KEY_URL="https://www.atomesus.com/dashboard"
        PROVIDER_TYPE="atomesus"
        ;;
esac

echo ""
ok "Dipilih: ${BOLD}$PROVIDER_NAME${NC}"
echo ""

# =========================================================================
# Input API Key LLM
# =========================================================================
echo -e "${YELLOW}Dapatkan API key di:${NC} $API_KEY_URL"
read -rp "$(echo -e "${BOLD}Masukkan API Key LLM: ${NC}")" LLM_API_KEY

if [ -z "$LLM_API_KEY" ]; then
    err "API Key tidak boleh kosong!"
    exit 1
fi

# =========================================================================
# Input API Key ZEP
# =========================================================================
echo ""
echo -e "${YELLOW}ZEP digunakan untuk knowledge graph (memori agent).${NC}"
echo -e "${YELLOW}Daftar gratis di:${NC} https://app.getzep.com/"
read -rp "$(echo -e "${BOLD}Masukkan API Key ZEP: ${NC}")" ZEP_API_KEY

if [ -z "$ZEP_API_KEY" ]; then
    err "API Key ZEP tidak boleh kosong!"
    exit 1
fi

# =========================================================================
# Tulis .env
# =========================================================================
cat > "$ENV_FILE" << EOF
# === MiroFish Agent — Konfigurasi LLM ===
# Provider: $PROVIDER_NAME
# Dibuat otomatis oleh mirofish-agent skill

# LLM API Configuration
LLM_API_KEY=$LLM_API_KEY
LLM_BASE_URL=$BASE_URL
LLM_MODEL_NAME=$MODEL_NAME

# Provider type: 'atomesus' atau 'openai'
# Atomesus mengabaikan system messages, jadi perlu penanganan khusus
LLM_PROVIDER_TYPE=$PROVIDER_TYPE

# ZEP Memory Graph Configuration
ZEP_API_KEY=$ZEP_API_KEY
EOF

echo ""
ok "File .env berhasil dibuat di $ENV_FILE"
echo ""
echo -e "${GREEN}${BOLD}Konfigurasi selesai!${NC}"
echo -e "  Model: ${CYAN}$PROVIDER_NAME${NC}"
echo -e "  URL:   ${CYAN}$BASE_URL${NC}"
echo ""
