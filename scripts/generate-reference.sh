#!/bin/bash
set -euo pipefail

EPUBCHECK_JAR="${EPUBCHECK_JAR:-$HOME/tools/epubcheck-5.3.0/epubcheck.jar}"
FIXTURES_OUT="fixtures/epub"
REFERENCE_DIR="reference"

for category in valid invalid; do
    if [ -d "$FIXTURES_OUT/$category" ]; then
        mkdir -p "$REFERENCE_DIR/$category"
        for epub in "$FIXTURES_OUT/$category"/*.epub; do
            [ -f "$epub" ] || continue
            name=$(basename "$epub" .epub)
            echo "Reference: $category/$name"
            java -jar "$EPUBCHECK_JAR" "$epub" --json "$REFERENCE_DIR/$category/$name.json" 2>/dev/null || true
        done
    fi
done

echo "Done. Reference output in $REFERENCE_DIR/"
