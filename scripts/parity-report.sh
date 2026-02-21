#!/bin/bash
set -euo pipefail

# parity-report.sh — Generate a markdown parity report for an implementation
#
# Usage:
#   ./scripts/parity-report.sh <impl-command>
#
# Runs the implementation against every fixture and generates a markdown table
# showing which checks pass, fail, or are skipped. Output goes to stdout.
#
# Environment variables:
#   FIXTURES_DIR  — path to fixture epubs (default: fixtures/epub)
#   EXPECTED_DIR  — path to expected JSON files (default: expected)

IMPL="${1:?Usage: $0 <implementation-command>}"
FIXTURES_DIR="${FIXTURES_DIR:-fixtures/epub}"
EXPECTED_DIR="${EXPECTED_DIR:-expected}"
CHECKS_FILE="checks.json"

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# Build results for each fixture
declare -A RESULTS

for category in valid invalid; do
    [ -d "$EXPECTED_DIR/$category" ] || continue

    for expected_file in "$EXPECTED_DIR/$category"/*.json; do
        [ -f "$expected_file" ] || continue
        name=$(basename "$expected_file" .json)
        epub_file="$FIXTURES_DIR/$category/$name.epub"
        fixture_key="$category/$name"

        if [ ! -f "$epub_file" ]; then
            RESULTS["$fixture_key"]="SKIP"
            continue
        fi

        impl_output="$TMPDIR/$category-$name.json"
        if ! $IMPL "$epub_file" > "$impl_output" 2>/dev/null; then
            if [ ! -s "$impl_output" ]; then
                RESULTS["$fixture_key"]="FAIL"
                continue
            fi
        fi

        if ! jq empty "$impl_output" 2>/dev/null; then
            RESULTS["$fixture_key"]="FAIL"
            continue
        fi

        # Parse expected
        exp_valid=$(jq -r '.valid' "$expected_file")
        exp_fatal=$(jq -r '.fatal_count // 0' "$expected_file")
        exp_error=$(jq -r '.error_count' "$expected_file")
        exp_error_min=$(jq -r '.error_count_min // "null"' "$expected_file")
        exp_warning=$(jq -r '.warning_count' "$expected_file")

        # Parse implementation
        impl_fatal=$(jq '(.checker.nFatal // null) // ([.messages[] | select(.severity == "FATAL")] | length)' "$impl_output" 2>/dev/null || echo "0")
        impl_error=$(jq '(.checker.nError // null) // ([.messages[] | select(.severity == "ERROR")] | length)' "$impl_output" 2>/dev/null || echo "0")
        impl_warning=$(jq '(.checker.nWarning // null) // ([.messages[] | select(.severity == "WARNING")] | length)' "$impl_output" 2>/dev/null || echo "0")

        if [ "$impl_fatal" -eq 0 ] 2>/dev/null && [ "$impl_error" -eq 0 ] 2>/dev/null; then
            impl_valid="true"
        else
            impl_valid="false"
        fi

        ok=true

        [ "$exp_valid" != "$impl_valid" ] && ok=false

        if [ "$exp_error_min" != "null" ]; then
            [ "$impl_error" -lt "$exp_error_min" ] 2>/dev/null && ok=false
        else
            [ "$exp_error" -ne "$impl_error" ] 2>/dev/null && ok=false
        fi

        [ "$exp_fatal" -ne "$impl_fatal" ] 2>/dev/null && ok=false
        [ "$exp_warning" -ne "$impl_warning" ] 2>/dev/null && ok=false

        # Check message patterns
        msg_count=$(jq '.messages | length' "$expected_file")
        for ((i=0; i<msg_count; i++)); do
            pattern=$(jq -r ".messages[$i].message_pattern" "$expected_file")
            severity=$(jq -r ".messages[$i].severity" "$expected_file")
            if [ -n "$pattern" ] && [ "$pattern" != "null" ]; then
                match=$(jq --arg pat "$pattern" --arg sev "$severity" \
                    '[.messages[] | select(.severity == $sev and (.message | test($pat; "i")))] | length' \
                    "$impl_output" 2>/dev/null || echo "0")
                [ "$match" -eq 0 ] && ok=false
            fi
        done

        if $ok; then
            RESULTS["$fixture_key"]="PASS"
        else
            RESULTS["$fixture_key"]="FAIL"
        fi
    done
done

# Generate markdown report
echo "# Parity Report"
echo ""
echo "Generated: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""

# Summary counts
pass=0; fail=0; skip=0
for key in "${!RESULTS[@]}"; do
    case "${RESULTS[$key]}" in
        PASS) pass=$((pass + 1)) ;;
        FAIL) fail=$((fail + 1)) ;;
        SKIP) skip=$((skip + 1)) ;;
    esac
done
total=$((pass + fail))
if [ "$total" -gt 0 ]; then
    pct=$((pass * 100 / total))
else
    pct=0
fi

echo "**Overall: ${pass}/${total} checks passing (${pct}%)** — ${skip} skipped"
echo ""

# Report by level from checks.json
if [ -f "$CHECKS_FILE" ]; then
    for level in 1 2 3 4; do
        level_checks=$(jq --argjson lvl "$level" '[.checks[] | select(.level == $lvl)]' "$CHECKS_FILE")
        count=$(echo "$level_checks" | jq 'length')
        [ "$count" -eq 0 ] && continue

        level_pass=0; level_fail=0; level_skip=0
        echo "## Level $level"
        echo ""
        echo "| Check | Name | Fixture | Status |"
        echo "|-------|------|---------|--------|"

        for ((i=0; i<count; i++)); do
            check_id=$(echo "$level_checks" | jq -r ".[$i].id")
            check_name=$(echo "$level_checks" | jq -r ".[$i].name")
            fixture_invalid=$(echo "$level_checks" | jq -r ".[$i].fixture_invalid | if type == \"array\" then .[0] else . end")

            status="${RESULTS[$fixture_invalid]:-SKIP}"
            case "$status" in
                PASS) status_icon="PASS"; level_pass=$((level_pass + 1)) ;;
                FAIL) status_icon="FAIL"; level_fail=$((level_fail + 1)) ;;
                *)    status_icon="SKIP"; level_skip=$((level_skip + 1)) ;;
            esac

            echo "| $check_id | $check_name | \`$fixture_invalid\` | $status_icon |"
        done

        level_total=$((level_pass + level_fail))
        if [ "$level_total" -gt 0 ]; then
            level_pct=$((level_pass * 100 / level_total))
        else
            level_pct=0
        fi
        echo ""
        echo "Level $level: ${level_pass}/${level_total} passing (${level_pct}%)"
        echo ""
    done
fi
