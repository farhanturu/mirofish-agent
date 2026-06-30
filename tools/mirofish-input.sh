#!/usr/bin/env bash
# =============================================================================
# MiroFish — Universal Input Handler
# Menangani semua jenis input: dokumen, gambar, URL, localhost review
# Mengkonversi semua input menjadi teks yang bisa diproses MiroFish
# =============================================================================

set -euo pipefail

TOOLS_DIR="$(cd "$(dirname "$0")" && pwd)"
MIROFISH_DIR="$(dirname "$TOOLS_DIR")"
INPUT_DIR="$MIROFISH_DIR/uploads/universal"
mkdir -p "$INPUT_DIR"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
BOLD='\033[1m'; NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
err()   { echo -e "${RED}[✗]${NC} $*"; }

# Load .env
if [ -f "$MIROFISH_DIR/.env" ]; then
    set -a; source "$MIROFISH_DIR/.env"; set +a
fi

# =========================================================================
# Detect input type
# =========================================================================
detect_type() {
    local input="$1"

    # URL
    if [[ "$input" =~ ^https?:// ]]; then
        echo "url"
        return
    fi

    # localhost:port
    if [[ "$input" =~ ^localhost:[0-9]+$ ]] || [[ "$input" =~ ^[0-9]+$ ]]; then
        echo "localhost"
        return
    fi

    # File exists
    if [ -f "$input" ]; then
        local ext="${input##*.}"
        ext=$(echo "$ext" | tr '[:upper:]' '[:lower:]')

        case "$ext" in
            pdf|md|txt|markdown)
                echo "document"
                return
                ;;
            png|jpg|jpeg|gif|webp|bmp|svg)
                echo "image"
                return
                ;;
            *)
                echo "document"
                return
                ;;
        esac
    fi

    echo "unknown"
}

# =========================================================================
# Process URL
# =========================================================================
process_url() {
    local url="$1"
    local analysis_prompt="${2:-}"
    local output_file="$INPUT_DIR/url_$(date +%s).txt"

    info "Mengambil konten dari: $url"

    # Fetch content
    local fetch_result
    fetch_result=$(python3 "$TOOLS_DIR/fetch-url.py" "$url" --screenshot 2>/dev/null || echo '{"error":"fetch failed"}')

    local title=$(echo "$fetch_result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('title',''))" 2>/dev/null || echo "")
    local text=$(echo "$fetch_result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('text',''))" 2>/dev/null || echo "")
    local screenshot=$(echo "$fetch_result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('screenshot_path',''))" 2>/dev/null || echo "")

    # Tulis ke file teks
    cat > "$output_file" << EOF
=== KONTEN URL ===
URL: $url
Judul: $title
Waktu: $(date '+%Y-%m-%d %H:%M:%S')

$text
EOF

    ok "Konten URL disimpan: $output_file ($([ -f "$output_file" ] && wc -c < "$output_file" || echo 0) bytes)"

    # Analisis gambar jika ada screenshot
    if [ -n "$screenshot" ] && [ -f "$screenshot" ]; then
        info "Screenshot diambil: $screenshot"
        if [ -n "$analysis_prompt" ]; then
            info "Menganalisis screenshot..."
            python3 "$TOOLS_DIR/analyze-image.py" "$screenshot" "$analysis_prompt" > "$INPUT_DIR/analysis_$(date +%s).json" 2>/dev/null || true
        fi
    fi

    echo "$output_file"
}

# =========================================================================
# Process Image
# =========================================================================
process_image() {
    local image_path="$1"
    local analysis_prompt="${2:-}"
    local output_file="$INPUT_DIR/image_$(date +%s).txt"

    info "Menganalisis gambar: $image_path"

    # Analisis gambar via LLM vision
    local analysis
    analysis=$(python3 "$TOOLS_DIR/analyze-image.py" "$image_path" "$analysis_prompt" 2>/dev/null || echo '{"error":"analysis failed"}')

    local analysis_text=$(echo "$analysis" | python3 -c "import sys,json; print(json.load(sys.stdin).get('analysis',''))" 2>/dev/null || echo "")
    local image_name=$(basename "$image_path")

    # Tulis ke file teks
    cat > "$output_file" << EOF
=== ANALISIS GAMBAR ===
File: $image_name
Path: $image_path
Waktu: $(date '+%Y-%m-%d %H:%M:%S')

$analysis_text
EOF

    ok "Analisis gambar disimpan: $output_file"

    # Simpan juga JSON lengkap
    echo "$analysis" > "$INPUT_DIR/analysis_$(date +%s).json"

    echo "$output_file"
}

# =========================================================================
# Process Localhost
# =========================================================================
process_localhost() {
    local target="$1"
    local analysis_prompt="${2:-}"
    local output_file="$INPUT_DIR/localhost_$(date +%s).txt"

    # Parse port
    local port
    if [[ "$target" =~ ^[0-9]+$ ]]; then
        port="$target"
    elif [[ "$target" =~ localhost:([0-9]+) ]]; then
        port="${BASH_REMATCH[1]}"
    else
        port="$target"
    fi

    info "Review localhost:$port"

    # Review localhost
    local review
    review=$(python3 "$TOOLS_DIR/review-localhost.py" "$port" 2>/dev/null || echo '{"error":"review failed"}')

    local html_title=$(echo "$review" | python3 -c "import sys,json; print(json.load(sys.stdin).get('html_analysis',{}).get('title',''))" 2>/dev/null || echo "")
    local frameworks=$(echo "$review" | python3 -c "import sys,json; print(', '.join(json.load(sys.stdin).get('html_analysis',{}).get('frameworks',[])))" 2>/dev/null || echo "")
    local screenshot=$(echo "$review" | python3 -c "import sys,json; print(json.load(sys.stdin).get('screenshot_path',''))" 2>/dev/null || echo "")

    # Tulis ke file teks
    cat > "$output_file" << EOF
=== REVIEW LOCALHOST ===
URL: http://localhost:$port
Judul: $html_title
Framework: $frameworks
Waktu: $(date '+%Y-%m-%d %H:%M:%S')

$(echo "$review" | python3 -c "
import sys, json
data = json.load(sys.stdin)
html = data.get('html_analysis', {})
elems = html.get('elements', {})
acc = html.get('accessibility', {})
headings = html.get('headings', {})

print('=== Struktur HTML ===')
for level, texts in headings.items():
    for t in texts:
        print(f'  {level}: {t}')

print()
print('=== Elemen UI ===')
for k, v in elems.items():
    print(f'  {k}: {v}')

print()
print('=== Aksesibilitas ===')
for k, v in acc.items():
    print(f'  {k}: {v}')
" 2>/dev/null || echo "")
EOF

    ok "Review localhost disimpan: $output_file"

    # Analisis screenshot jika ada
    if [ -n "$screenshot" ] && [ -f "$screenshot" ]; then
        info "Screenshot diambil: $screenshot"
        local prompt="${analysis_prompt:-Review UI/UX website ini. Analisis layout, desain, warna, tipografi, dan user experience. Berikan skor 1-10 dan saran perbaikan.}"
        python3 "$TOOLS_DIR/analyze-image.py" "$screenshot" "$prompt" > "$INPUT_DIR/review_$(date +%s).json" 2>/dev/null || true
    fi

    echo "$output_file"
}

# =========================================================================
# Process Document
# =========================================================================
process_document() {
    local file_path="$1"
    info "Dokumen terdeteksi: $file_path"
    info "File ini bisa langsung diunggah ke MiroFish via API"
    echo "$file_path"
}

# =========================================================================
# Main
# =========================================================================
usage() {
    echo -e "${BOLD}MiroFish Universal Input Handler${NC}"
    echo ""
    echo "Penggunaan:"
    echo "  $0 <INPUT> [PROMPT]"
    echo ""
    echo "Jenis input yang didukung:"
    echo "  Dokumen:  file.pdf, file.txt, file.md"
    echo "  Gambar:   logo.png, desain.jpg, screenshot.png"
    echo "  URL:      https://example.com"
    echo "  Localhost: 3000 atau localhost:3000"
    echo ""
    echo "Contoh:"
    echo "  $0 dokumen.pdf"
    echo "  $0 logo.png 'Apakah logo ini cocok untuk startup tech?'"
    echo "  $0 https://github.com 'Review desain website ini'"
    echo "  $0 3000 'Review UI/UX aplikasi ini'"
    echo "  $0 https://google.com 'Analisis struktur dan SEO'"
}

if [ $# -lt 1 ]; then
    usage
    exit 1
fi

INPUT="$1"
PROMPT="${2:-}"
INPUT_TYPE=$(detect_type "$INPUT")

echo -e "\n${BOLD}${CYAN}🐟 MiroFish Universal Input${NC}"
echo -e "Input: ${BOLD}$INPUT${NC}"
echo -e "Tipe:  ${BOLD}$INPUT_TYPE${NC}\n"

case "$INPUT_TYPE" in
    url)
        process_url "$INPUT" "$PROMPT"
        ;;
    image)
        process_image "$INPUT" "$PROMPT"
        ;;
    localhost)
        process_localhost "$INPUT" "$PROMPT"
        ;;
    document)
        process_document "$INPUT"
        ;;
    *)
        err "Tipe input tidak dikenali: $INPUT"
        usage
        exit 1
        ;;
esac
