#!/bin/bash
set -euo pipefail

# frequency-analysis.sh — Rank epubcheck message IDs by real-world frequency
#
# Runs epubcheck on the entire corpus and produces a ranked frequency report.
# The top unfixture'd checks become candidates for the next level.
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

echo "=== Frequency Analysis ==="

ALL_IDS_FILE="$TMPDIR/all-ids.txt"
EPUB_IDS_FILE="$TMPDIR/epub-ids.txt"
> "$ALL_IDS_FILE"

epub_count=0
affected_counts="$TMPDIR/affected.txt"
> "$affected_counts"

for epub in $(find "$CORPUS_DIR" -name "*.epub" -type f | sort); do
    epub_count=$((epub_count + 1))
    name=$(basename "$epub")
    ref_out="$TMPDIR/$name.json"

    java -jar "$EPUBCHECK_JAR" "$epub" --json "$ref_out" 2>/dev/null || true

    if [ -f "$ref_out" ]; then
        # All IDs (with duplicates for total count)
        jq -r '.messages[].ID' "$ref_out" 2>/dev/null >> "$ALL_IDS_FILE" || true

        # Unique IDs per epub (for "N epubs affected" count)
        jq -r '.messages[].ID' "$ref_out" 2>/dev/null | sort -u >> "$affected_counts" || true
    fi
done

echo "Analyzed $epub_count EPUBs."
echo ""

# Frequency report: total occurrences
FREQ_FILE="$ANALYSIS_DIR/check-frequency.txt"
{
    echo "# Check Frequency Report"
    echo "# Generated: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo "# Corpus: $epub_count EPUBs from $CORPUS_DIR"
    echo "#"
    echo "# Format: TOTAL_HITS  EPUBS_AFFECTED  MESSAGE_ID  COVERED  LEVEL"
    echo "#"

    # Build lookup of covered IDs and their levels
    if [ -f "$CHECKS_FILE" ]; then
        covered_json=$(jq -r '.checks[] | select(.epubcheck_message_id != null) | "\(.epubcheck_message_id)\t\(.level)"' "$CHECKS_FILE" 2>/dev/null || true)
    else
        covered_json=""
    fi

    # Count total hits per ID
    sort "$ALL_IDS_FILE" | uniq -c | sort -rn > "$TMPDIR/total-counts.txt"

    # Count affected EPUBs per ID
    sort "$affected_counts" | uniq -c | sort -rn > "$TMPDIR/affected-counts.txt"

    while read -r total_count id; do
        epub_affected=$(grep -w "$id" "$TMPDIR/affected-counts.txt" | awk '{print $1}' || echo "0")
        [ -z "$epub_affected" ] && epub_affected=0

        covered="no"
        level="-"
        if [ -n "$covered_json" ]; then
            match=$(echo "$covered_json" | grep "^${id}	" | head -1 || true)
            if [ -n "$match" ]; then
                covered="yes"
                level=$(echo "$match" | cut -f2)
            fi
        fi

        printf "%-8s %-6s %-12s %-8s %s\n" "$total_count" "$epub_affected" "$id" "$covered" "$level"
    done < "$TMPDIR/total-counts.txt"
} > "$FREQ_FILE"

cat "$FREQ_FILE"

# Coverage report
COVERAGE_FILE="$ANALYSIS_DIR/coverage-report.md"
{
    echo "# Coverage Report"
    echo ""
    echo "Generated: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo "Corpus: $epub_count EPUBs"
    echo ""

    total_ids=$(wc -l < "$TMPDIR/total-counts.txt" | tr -d ' ')
    if [ -f "$CHECKS_FILE" ]; then
        covered_count=$(jq '[.checks[] | select(.epubcheck_message_id != null) | .epubcheck_message_id] | unique | length' "$CHECKS_FILE")
    else
        covered_count=0
    fi

    echo "## Summary"
    echo ""
    echo "- **Unique message IDs in corpus:** $total_ids"
    echo "- **Message IDs with fixtures:** $covered_count"
    echo ""

    echo "## Uncovered IDs by Frequency"
    echo ""
    echo "These message IDs appear in real-world EPUBs but have no fixture yet."
    echo "They are candidates for the next level of checks."
    echo ""
    echo "| Rank | ID | Total Hits | EPUBs Affected |"
    echo "|------|------|------------|----------------|"

    rank=0
    while read -r total_count id; do
        epub_affected=$(grep -w "$id" "$TMPDIR/affected-counts.txt" | awk '{print $1}' || echo "0")
        [ -z "$epub_affected" ] && epub_affected=0

        is_covered="no"
        if [ -f "$CHECKS_FILE" ]; then
            is_covered=$(jq --arg id "$id" '[.checks[] | select(.epubcheck_message_id == $id)] | if length > 0 then "yes" else "no" end' "$CHECKS_FILE" 2>/dev/null || echo "no")
            is_covered=$(echo "$is_covered" | tr -d '"')
        fi

        if [ "$is_covered" = "no" ]; then
            rank=$((rank + 1))
            echo "| $rank | $id | $total_count | $epub_affected |"
        fi
    done < "$TMPDIR/total-counts.txt"

    echo ""
    echo "Total uncovered IDs: $rank"
} > "$COVERAGE_FILE"

echo ""
echo "Results written to:"
echo "  $FREQ_FILE"
echo "  $COVERAGE_FILE"
