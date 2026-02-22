#!/bin/bash
set -euo pipefail

# analyze-corpus.sh — Run epubcheck on corpus EPUBs and produce a summary
#
# Runs the reference epubcheck on every EPUB in the corpus directory and
# produces a JSON report mapping each file to its validation results.
# This feeds into corpus-known-issues.json for tracking regressions.
#
# Usage:
#   ./scripts/analyze-corpus.sh
#   CORPUS_DIR=path/to/corpus ./scripts/analyze-corpus.sh
#
# Output:
#   analysis/corpus-results.json   — full validation results per file
#   analysis/corpus-summary.txt    — human-readable summary
#   analysis/check-frequency.txt   — checks ranked by frequency

CORPUS_DIR="${CORPUS_DIR:-fixtures/external}"
ANALYSIS_DIR="${ANALYSIS_DIR:-analysis}"
EPUBCHECK_JAR="${EPUBCHECK_JAR:-}"

# Find epubcheck
if [ -z "$EPUBCHECK_JAR" ]; then
    for candidate in ~/tools/epubcheck-*/epubcheck.jar; do
        if [ -f "$candidate" ]; then
            EPUBCHECK_JAR="$candidate"
            break
        fi
    done
fi

if [ -z "$EPUBCHECK_JAR" ] || [ ! -f "$EPUBCHECK_JAR" ]; then
    echo "Error: epubcheck JAR not found."
    echo "Run ./bootstrap.sh first or set EPUBCHECK_JAR."
    exit 1
fi

if [ ! -d "$CORPUS_DIR" ] || [ -z "$(find "$CORPUS_DIR" -name '*.epub' 2>/dev/null | head -1)" ]; then
    echo "Error: No EPUBs found in $CORPUS_DIR"
    echo "Run 'make corpus' first."
    exit 1
fi

mkdir -p "$ANALYSIS_DIR"

echo "=== Analyzing EPUB corpus ==="
echo "Corpus: $CORPUS_DIR"
echo "epubcheck: $EPUBCHECK_JAR"
echo ""

# Collect all EPUBs
mapfile -t EPUBS < <(find "$CORPUS_DIR" -name "*.epub" -type f | sort)
total=${#EPUBS[@]}
echo "Found $total EPUBs to analyze."
echo ""

# Initialize results
RESULTS_FILE="$ANALYSIS_DIR/corpus-results.json"
echo '{"results":[' > "$RESULTS_FILE"

valid_count=0
invalid_count=0
error_count=0
first=true

for epub in "${EPUBS[@]}"; do
    relpath="${epub#$CORPUS_DIR/}"
    source_dir=$(echo "$relpath" | cut -d/ -f1)
    filename=$(basename "$epub")

    # Run epubcheck
    tmpjson=$(mktemp)
    if java -jar "$EPUBCHECK_JAR" "$epub" --json "$tmpjson" >/dev/null 2>&1; then
        is_valid=true
    else
        is_valid=false
    fi

    if [ -f "$tmpjson" ] && [ -s "$tmpjson" ]; then
        # Extract message IDs and severities
        messages=$(jq -c '[.messages[] | {id: .ID, severity: .severity, message: .message}]' "$tmpjson" 2>/dev/null || echo '[]')
        msg_count=$(echo "$messages" | jq 'length' 2>/dev/null || echo 0)
    else
        messages='[]'
        msg_count=0
        is_valid=false
    fi

    rm -f "$tmpjson"

    # Track counts
    if [ "$is_valid" = "true" ]; then
        valid_count=$((valid_count + 1))
        status="VALID"
    else
        invalid_count=$((invalid_count + 1))
        status="INVALID"
    fi

    printf "  %-8s %-20s %s (%d messages)\n" "$status" "$source_dir" "$filename" "$msg_count"

    # Append to JSON
    if [ "$first" = "true" ]; then
        first=false
    else
        echo ',' >> "$RESULTS_FILE"
    fi
    cat >> "$RESULTS_FILE" <<ENTRY
{"source":"$source_dir","file":"$filename","valid":$is_valid,"message_count":$msg_count,"messages":$messages}
ENTRY
done

echo ']}' >> "$RESULTS_FILE"

# Generate frequency analysis
echo ""
echo "=== Generating check frequency analysis ==="

jq -r '.results[].messages[].id' "$RESULTS_FILE" 2>/dev/null \
    | sort | uniq -c | sort -rn \
    > "$ANALYSIS_DIR/check-frequency.txt"

freq_checks=$(wc -l < "$ANALYSIS_DIR/check-frequency.txt")

# Generate human-readable summary
cat > "$ANALYSIS_DIR/corpus-summary.txt" <<SUMMARY
EPUB Corpus Analysis Summary
=============================
Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)
epubcheck: $(java -jar "$EPUBCHECK_JAR" --version 2>&1 | head -1 || echo "unknown")

Total EPUBs:   $total
Valid:         $valid_count
Invalid:       $invalid_count
Unique checks: $freq_checks

Top 20 most frequent checks:
$(head -20 "$ANALYSIS_DIR/check-frequency.txt")

Per-source breakdown:
$(jq -r '.results | group_by(.source) | .[] | "\(.[0].source): \(length) EPUBs (\([.[] | select(.valid)] | length) valid, \([.[] | select(.valid | not)] | length) invalid)"' "$RESULTS_FILE" 2>/dev/null)
SUMMARY

echo ""
echo "=== Done ==="
echo "Results:    $ANALYSIS_DIR/corpus-results.json"
echo "Summary:    $ANALYSIS_DIR/corpus-summary.txt"
echo "Frequency:  $ANALYSIS_DIR/check-frequency.txt"
echo ""
echo "Valid: $valid_count / $total  |  Invalid: $invalid_count / $total  |  Unique checks: $freq_checks"
