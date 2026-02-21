#!/bin/bash
set -euo pipefail

# fetch-corpus.sh — Download real-world EPUB corpus for analysis
#
# Downloads sample EPUBs from public sources for frequency analysis.
# These are real-world files that help identify which validation checks
# fire most often in practice.
#
# Environment variables:
#   CORPUS_DIR — where to store downloaded epubs (default: fixtures/external)

CORPUS_DIR="${CORPUS_DIR:-fixtures/external}"

echo "=== Fetching EPUB corpus ==="
echo "Target directory: $CORPUS_DIR"

# --- epub3-samples from W3C/IDPF ---
SAMPLES_DIR="$CORPUS_DIR/epub3-samples"
if [ -d "$SAMPLES_DIR" ] && [ "$(ls -A "$SAMPLES_DIR" 2>/dev/null)" ]; then
    echo "epub3-samples already present, skipping."
else
    echo "Downloading epub3-samples..."
    mkdir -p "$SAMPLES_DIR"
    SAMPLES_URL="https://github.com/IDPF/epub3-samples/archive/refs/heads/main.zip"
    SAMPLES_ZIP="$CORPUS_DIR/epub3-samples-main.zip"

    if curl -fsSL -o "$SAMPLES_ZIP" "$SAMPLES_URL" 2>/dev/null; then
        # Extract only the pre-built epub files
        TMP_EXTRACT=$(mktemp -d)
        unzip -q "$SAMPLES_ZIP" -d "$TMP_EXTRACT" 2>/dev/null || true
        find "$TMP_EXTRACT" -name "*.epub" -exec cp {} "$SAMPLES_DIR/" \;
        rm -rf "$TMP_EXTRACT" "$SAMPLES_ZIP"
        count=$(ls -1 "$SAMPLES_DIR"/*.epub 2>/dev/null | wc -l)
        echo "  Downloaded $count epub3-samples."
    else
        echo "  Warning: Could not download epub3-samples (network error)."
    fi
fi

# --- Standard Ebooks ---
SE_DIR="$CORPUS_DIR/standard-ebooks"
if [ -d "$SE_DIR" ] && [ "$(ls -A "$SE_DIR" 2>/dev/null)" ]; then
    echo "standard-ebooks already present, skipping."
else
    echo "Downloading Standard Ebooks samples..."
    mkdir -p "$SE_DIR"

    # A curated list of Standard Ebooks — small, well-structured EPUBs
    SE_BOOKS=(
        "https://standardebooks.org/ebooks/jane-austen/pride-and-prejudice/downloads/jane-austen_pride-and-prejudice.epub"
        "https://standardebooks.org/ebooks/mark-twain/the-adventures-of-tom-sawyer/downloads/mark-twain_the-adventures-of-tom-sawyer.epub"
        "https://standardebooks.org/ebooks/lewis-carroll/alices-adventures-in-wonderland/downloads/lewis-carroll_alices-adventures-in-wonderland.epub"
        "https://standardebooks.org/ebooks/oscar-wilde/the-picture-of-dorian-gray/downloads/oscar-wilde_the-picture-of-dorian-gray.epub"
        "https://standardebooks.org/ebooks/arthur-conan-doyle/the-hound-of-the-baskervilles/downloads/arthur-conan-doyle_the-hound-of-the-baskervilles.epub"
    )

    dl_count=0
    for url in "${SE_BOOKS[@]}"; do
        filename=$(basename "$url")
        if curl -fsSL -o "$SE_DIR/$filename" "$url" 2>/dev/null; then
            dl_count=$((dl_count + 1))
        fi
    done
    echo "  Downloaded $dl_count Standard Ebooks."
fi

# --- Project Gutenberg ---
PG_DIR="$CORPUS_DIR/gutenberg"
if [ -d "$PG_DIR" ] && [ "$(ls -A "$PG_DIR" 2>/dev/null)" ]; then
    echo "gutenberg already present, skipping."
else
    echo "Downloading Project Gutenberg samples..."
    mkdir -p "$PG_DIR"

    # Well-known Gutenberg EPUB3 files by ID
    PG_IDS=(1342 11 84 1661 98 74 1232 2701 345 1080)

    dl_count=0
    for id in "${PG_IDS[@]}"; do
        url="https://www.gutenberg.org/ebooks/${id}.epub3.images"
        if curl -fsSL -o "$PG_DIR/pg${id}.epub" "$url" 2>/dev/null; then
            dl_count=$((dl_count + 1))
        fi
    done
    echo "  Downloaded $dl_count Gutenberg EPUBs."
fi

# Summary
total=0
for dir in "$SAMPLES_DIR" "$SE_DIR" "$PG_DIR"; do
    if [ -d "$dir" ]; then
        n=$(find "$dir" -name "*.epub" 2>/dev/null | wc -l)
        total=$((total + n))
    fi
done

echo ""
echo "Corpus: $total EPUBs total in $CORPUS_DIR/"
echo "Run 'make discover' to analyze the corpus."
