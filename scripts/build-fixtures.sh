#!/bin/bash
set -euo pipefail

FIXTURES_SRC="fixtures/src"
FIXTURES_OUT="fixtures/epub"

build_epub() {
    local src_dir="$1"
    local out_file="$2"

    mkdir -p "$(dirname "$out_file")"
    rm -f "$out_file"

    out_file="$(cd "$(dirname "$out_file")" && pwd)/$(basename "$out_file")"

    cd "$src_dir"
    if [ -f mimetype ]; then
        zip -X0 "$out_file" mimetype
        zip -Xr9D "$out_file" . -x mimetype
    else
        zip -Xr9D "$out_file" .
    fi
    cd - > /dev/null
}

for category in valid invalid; do
    if [ -d "$FIXTURES_SRC/$category" ]; then
        for fixture_dir in "$FIXTURES_SRC/$category"/*/; do
            [ -d "$fixture_dir" ] || continue
            name=$(basename "$fixture_dir")
            echo "Building: $category/$name"
            build_epub "$fixture_dir" "$FIXTURES_OUT/$category/$name.epub"
        done
    fi
done

# Build special fixtures that need non-standard zip manipulation
if [ -f scripts/build-special-fixtures.py ]; then
    python3 scripts/build-special-fixtures.py
fi

echo "Done. Built epubs in $FIXTURES_OUT/"
