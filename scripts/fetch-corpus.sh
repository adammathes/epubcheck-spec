#!/bin/bash
set -euo pipefail

# fetch-corpus.sh — Download real-world EPUB corpus for analysis
#
# Downloads sample EPUBs from public sources for frequency analysis.
# These are real-world files that help identify which validation checks
# fire most often in practice.
#
# Sources:
#   1. IDPF epub3-samples (W3C reference samples)
#   2. Standard Ebooks (high-quality, well-structured EPUB 3)
#   3. Project Gutenberg (mass-produced EPUB 3, common errors)
#   4. Feedbooks (public domain, EPUB 3 with various features)
#   5. Internet Archive Open Library (diverse quality and age)
#   6. EPUB test suite (W3C/IDPF conformance test documents)
#
# Environment variables:
#   CORPUS_DIR — where to store downloaded epubs (default: fixtures/external)
#   CORPUS_SKIP — comma-separated list of sources to skip
#                  (e.g., CORPUS_SKIP=gutenberg,feedbooks)

CORPUS_DIR="${CORPUS_DIR:-fixtures/external}"
CORPUS_SKIP="${CORPUS_SKIP:-}"

should_skip() {
    echo ",$CORPUS_SKIP," | grep -qi ",$1,"
}

download_with_retry() {
    local url="$1"
    local dest="$2"
    local retries=3
    local wait=2
    for i in $(seq 1 $retries); do
        if curl -fsSL --connect-timeout 10 --max-time 60 -o "$dest" "$url" 2>/dev/null; then
            return 0
        fi
        if [ "$i" -lt "$retries" ]; then
            sleep "$wait"
            wait=$((wait * 2))
        fi
    done
    return 1
}

echo "=== Fetching EPUB corpus ==="
echo "Target directory: $CORPUS_DIR"
echo ""

# --- 1. epub3-samples from W3C/IDPF ---
SAMPLES_DIR="$CORPUS_DIR/epub3-samples"
if should_skip "epub3-samples"; then
    echo "[skip] epub3-samples (CORPUS_SKIP)"
elif [ -d "$SAMPLES_DIR" ] && [ "$(ls -A "$SAMPLES_DIR" 2>/dev/null)" ]; then
    echo "[ok] epub3-samples already present, skipping."
else
    echo "[fetch] epub3-samples (W3C/IDPF reference samples)..."
    mkdir -p "$SAMPLES_DIR"
    SAMPLES_URL="https://github.com/IDPF/epub3-samples/archive/refs/heads/main.zip"
    SAMPLES_ZIP="$CORPUS_DIR/epub3-samples-main.zip"

    if download_with_retry "$SAMPLES_URL" "$SAMPLES_ZIP"; then
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

# --- 2. Standard Ebooks ---
SE_DIR="$CORPUS_DIR/standard-ebooks"
if should_skip "standard-ebooks"; then
    echo "[skip] standard-ebooks (CORPUS_SKIP)"
elif [ -d "$SE_DIR" ] && [ "$(ls -A "$SE_DIR" 2>/dev/null)" ]; then
    echo "[ok] standard-ebooks already present, skipping."
else
    echo "[fetch] Standard Ebooks (high-quality EPUB 3)..."
    mkdir -p "$SE_DIR"

    # Standard Ebooks are well-structured EPUB 3 files that should validate
    # cleanly. They exercise: CSS, SVG, multiple spine items, semantic markup.
    SE_BOOKS=(
        "https://standardebooks.org/ebooks/jane-austen/pride-and-prejudice/downloads/jane-austen_pride-and-prejudice.epub"
        "https://standardebooks.org/ebooks/mark-twain/the-adventures-of-tom-sawyer/downloads/mark-twain_the-adventures-of-tom-sawyer.epub"
        "https://standardebooks.org/ebooks/lewis-carroll/alices-adventures-in-wonderland/downloads/lewis-carroll_alices-adventures-in-wonderland.epub"
        "https://standardebooks.org/ebooks/oscar-wilde/the-picture-of-dorian-gray/downloads/oscar-wilde_the-picture-of-dorian-gray.epub"
        "https://standardebooks.org/ebooks/arthur-conan-doyle/the-hound-of-the-baskervilles/downloads/arthur-conan-doyle_the-hound-of-the-baskervilles.epub"
        "https://standardebooks.org/ebooks/herman-melville/moby-dick/downloads/herman-melville_moby-dick.epub"
        "https://standardebooks.org/ebooks/fyodor-dostoevsky/crime-and-punishment/constance-garnett/downloads/fyodor-dostoevsky_crime-and-punishment_constance-garnett.epub"
        "https://standardebooks.org/ebooks/charlotte-bronte/jane-eyre/downloads/charlotte-bronte_jane-eyre.epub"
        "https://standardebooks.org/ebooks/h-g-wells/the-war-of-the-worlds/downloads/h-g-wells_the-war-of-the-worlds.epub"
        "https://standardebooks.org/ebooks/mary-shelley/frankenstein/downloads/mary-shelley_frankenstein.epub"
    )

    dl_count=0
    for url in "${SE_BOOKS[@]}"; do
        filename=$(basename "$url")
        if download_with_retry "$url" "$SE_DIR/$filename"; then
            dl_count=$((dl_count + 1))
        fi
    done
    echo "  Downloaded $dl_count Standard Ebooks."
fi

# --- 3. Project Gutenberg ---
PG_DIR="$CORPUS_DIR/gutenberg"
if should_skip "gutenberg"; then
    echo "[skip] gutenberg (CORPUS_SKIP)"
elif [ -d "$PG_DIR" ] && [ "$(ls -A "$PG_DIR" 2>/dev/null)" ]; then
    echo "[ok] gutenberg already present, skipping."
else
    echo "[fetch] Project Gutenberg (mass-produced EPUB 3)..."
    mkdir -p "$PG_DIR"

    # Gutenberg EPUBs are auto-generated. They frequently trigger:
    # - OPF metadata warnings (date formats, identifier formats)
    # - CSS warnings (non-standard properties)
    # - Content warnings (missing alt text, deprecated elements)
    PG_IDS=(
        1342 11 84 1661 98 74 1232 2701 345 1080   # classics
        16328 4300 1952 5200 1260 844 46 76 2542 174 # more variety
        2591 1400 158 2554 996 43 514 1497 55 28054   # additional coverage
    )

    dl_count=0
    for id in "${PG_IDS[@]}"; do
        url="https://www.gutenberg.org/ebooks/${id}.epub3.images"
        if download_with_retry "$url" "$PG_DIR/pg${id}.epub"; then
            dl_count=$((dl_count + 1))
        fi
    done
    echo "  Downloaded $dl_count Gutenberg EPUBs."
fi

# --- 4. Feedbooks Public Domain ---
FB_DIR="$CORPUS_DIR/feedbooks"
if should_skip "feedbooks"; then
    echo "[skip] feedbooks (CORPUS_SKIP)"
elif [ -d "$FB_DIR" ] && [ "$(ls -A "$FB_DIR" 2>/dev/null)" ]; then
    echo "[ok] feedbooks already present, skipping."
else
    echo "[fetch] Feedbooks (public domain EPUB 3)..."
    mkdir -p "$FB_DIR"

    # Feedbooks produces EPUB 3 with different toolchains than Gutenberg
    # or Standard Ebooks, providing validation diversity.
    FB_BOOKS=(
        "https://www.feedbooks.com/book/6.epub"     # Metamorphosis
        "https://www.feedbooks.com/book/28.epub"    # Siddhartha
        "https://www.feedbooks.com/book/24.epub"    # A Christmas Carol
        "https://www.feedbooks.com/book/7.epub"     # The Trial
        "https://www.feedbooks.com/book/39.epub"    # Heart of Darkness
        "https://www.feedbooks.com/book/53.epub"    # Dubliners
        "https://www.feedbooks.com/book/4.epub"     # The Jungle Book
        "https://www.feedbooks.com/book/36.epub"    # The Prince
        "https://www.feedbooks.com/book/678.epub"   # The Art of War
        "https://www.feedbooks.com/book/14.epub"    # Treasure Island
    )

    dl_count=0
    for url in "${FB_BOOKS[@]}"; do
        filename="feedbooks-$(basename "$url")"
        if download_with_retry "$url" "$FB_DIR/$filename"; then
            dl_count=$((dl_count + 1))
        fi
    done
    echo "  Downloaded $dl_count Feedbooks EPUBs."
fi

# --- 5. Internet Archive ---
IA_DIR="$CORPUS_DIR/internet-archive"
if should_skip "internet-archive"; then
    echo "[skip] internet-archive (CORPUS_SKIP)"
elif [ -d "$IA_DIR" ] && [ "$(ls -A "$IA_DIR" 2>/dev/null)" ]; then
    echo "[ok] internet-archive already present, skipping."
else
    echo "[fetch] Internet Archive (diverse quality EPUBs)..."
    mkdir -p "$IA_DIR"

    # Internet Archive EPUBs come from many different digitization pipelines
    # and tend to have the widest variety of validation issues.
    IA_ITEMS=(
        "alicesadventure00carr"
        "prideandprejudice00aust"
        "warandpeace00tols"
        "greatexpectations00dick"
        "taleoftwocities00dick"
    )

    dl_count=0
    for item in "${IA_ITEMS[@]}"; do
        url="https://archive.org/download/${item}/${item}.epub"
        if download_with_retry "$url" "$IA_DIR/${item}.epub"; then
            dl_count=$((dl_count + 1))
        fi
    done
    echo "  Downloaded $dl_count Internet Archive EPUBs."
fi

# --- 6. EPUB Test Suite (W3C/IDPF conformance tests) ---
EPUBTEST_DIR="$CORPUS_DIR/epub-testsuite"
if should_skip "epub-testsuite"; then
    echo "[skip] epub-testsuite (CORPUS_SKIP)"
elif [ -d "$EPUBTEST_DIR" ] && [ "$(ls -A "$EPUBTEST_DIR" 2>/dev/null)" ]; then
    echo "[ok] epub-testsuite already present, skipping."
else
    echo "[fetch] EPUB Test Suite (W3C conformance tests)..."
    mkdir -p "$EPUBTEST_DIR"
    TESTSUITE_URL="https://github.com/w3c/epub-tests/archive/refs/heads/main.zip"
    TESTSUITE_ZIP="$CORPUS_DIR/epub-tests-main.zip"

    if download_with_retry "$TESTSUITE_URL" "$TESTSUITE_ZIP"; then
        TMP_EXTRACT=$(mktemp -d)
        unzip -q "$TESTSUITE_ZIP" -d "$TMP_EXTRACT" 2>/dev/null || true
        find "$TMP_EXTRACT" -name "*.epub" -exec cp {} "$EPUBTEST_DIR/" \;
        rm -rf "$TMP_EXTRACT" "$TESTSUITE_ZIP"
        count=$(ls -1 "$EPUBTEST_DIR"/*.epub 2>/dev/null | wc -l)
        echo "  Downloaded $count EPUB test suite files."
    else
        echo "  Warning: Could not download epub-tests (network error)."
    fi
fi

# --- Summary ---
echo ""
echo "=== Corpus Summary ==="
grand_total=0
for subdir in "$CORPUS_DIR"/*/; do
    if [ -d "$subdir" ]; then
        name=$(basename "$subdir")
        n=$(find "$subdir" -name "*.epub" 2>/dev/null | wc -l)
        if [ "$n" -gt 0 ]; then
            printf "  %-20s %3d EPUBs\n" "$name" "$n"
            grand_total=$((grand_total + n))
        fi
    fi
done
echo "  --------------------"
printf "  %-20s %3d EPUBs\n" "TOTAL" "$grand_total"
echo ""
echo "Run 'make discover' to analyze the corpus."
