#!/bin/bash
set -euo pipefail

# discover-checks.sh — Discover all epubcheck message IDs from real-world corpus
#
# Runs the reference epubcheck on every EPUB in the corpus directory,
# collects all unique message IDs, and identifies which ones we don't
# have fixtures for yet.
#
# Environment variables:
#   EPUBCHECK_JAR — path to epubcheck jar (default: ~/tools/epubcheck-5.3.0/epubcheck.jar)
#   CORPUS_DIR    — path to corpus epubs (default: fixtures/external)
#   ANALYSIS_DIR  — output directory (default: analysis)

EPUBCHECK_JAR="${EPUBCHECK_JAR:-$HOME/tools/epubcheck-5.3.0/epubcheck.jar}"
CORPUS_DIR="${CORPUS_DIR:-fixtures/external}"
ANALYSIS_DIR="${ANALYSIS_DIR:-analysis}"
CHECKS_FILE="checks.json"

if [ ! -f "$EPUBCHECK_JAR" ]; then
    echo "Error: epubcheck not found at $EPUBCHECK_JAR"
    echo "Run ./bootstrap.sh first or set EPUBCHECK_JAR."
    exit 1
fi

if [ ! -d "$CORPUS_DIR" ]; then
    echo "Error: corpus directory not found at $CORPUS_DIR"
    echo "Run 'make corpus' first to download real-world EPUBs."
    exit 1
fi

mkdir -p "$ANALYSIS_DIR"

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

echo "=== Discovering checks from corpus ==="

# Collect all message IDs from every EPUB in the corpus
ALL_IDS_FILE="$TMPDIR/all-ids.txt"
> "$ALL_IDS_FILE"

epub_count=0
for epub in $(find "$CORPUS_DIR" -name "*.epub" -type f | sort); do
    epub_count=$((epub_count + 1))
    name=$(basename "$epub")
    ref_out="$TMPDIR/$name.json"

    echo -n "  Checking: $name ... "
    if java -jar "$EPUBCHECK_JAR" "$epub" --json "$ref_out" 2>/dev/null; then
        echo "valid"
    else
        echo "has issues"
    fi

    # Extract all message IDs
    if [ -f "$ref_out" ]; then
        jq -r '.messages[].ID' "$ref_out" 2>/dev/null >> "$ALL_IDS_FILE" || true
    fi
done

echo ""
echo "Scanned $epub_count EPUBs."

# Generate known message IDs file (sorted, unique, with counts)
echo "=== All message IDs found ==="
sort "$ALL_IDS_FILE" | uniq -c | sort -rn > "$ANALYSIS_DIR/known-message-ids.txt"
cat "$ANALYSIS_DIR/known-message-ids.txt"

# Identify uncovered IDs — those not in our checks.json
KNOWN_IDS="$ANALYSIS_DIR/known-message-ids.txt"
COVERED_IDS="$TMPDIR/covered-ids.txt"

if [ -f "$CHECKS_FILE" ]; then
    jq -r '.checks[].epubcheck_message_id // empty' "$CHECKS_FILE" | sort -u > "$COVERED_IDS"

    echo ""
    echo "=== Uncovered message IDs (no fixture yet) ==="
    uncovered=0
    while read -r count id; do
        if ! grep -qx "$id" "$COVERED_IDS"; then
            echo "  $id (seen $count times)"
            uncovered=$((uncovered + 1))
        fi
    done < "$KNOWN_IDS"

    total_ids=$(wc -l < "$KNOWN_IDS" | tr -d ' ')
    covered_ids=$(wc -l < "$COVERED_IDS" | tr -d ' ')
    echo ""
    echo "Summary: $total_ids unique IDs found in corpus, $covered_ids covered by fixtures, $uncovered uncovered"
else
    echo "Warning: $CHECKS_FILE not found, cannot identify uncovered checks."
fi

echo ""
echo "Results written to $ANALYSIS_DIR/known-message-ids.txt"
