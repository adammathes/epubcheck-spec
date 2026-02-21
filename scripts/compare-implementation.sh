#!/bin/bash
set -euo pipefail

# compare-implementation.sh — Compare an EPUB validator implementation against expected results
#
# Usage:
#   ./scripts/compare-implementation.sh <impl-command>
#
# The implementation command receives an epub file path as its sole argument
# and must output JSON to stdout with this structure:
#
#   {
#     "messages": [
#       { "severity": "ERROR", "message": "description text", "ID": "OPT-001" }
#     ],
#     "checker": { "nFatal": 0, "nError": 1, "nWarning": 0 }
#   }
#
# Messages must include "severity" (FATAL/ERROR/WARNING/USAGE) and "message".
# The "ID" field is optional. If checker counts are missing, they are derived
# from the messages array.
#
# Environment variables:
#   FIXTURES_DIR  — path to fixture epubs (default: fixtures/epub)
#   EXPECTED_DIR  — path to expected JSON files (default: expected)
#   LEVEL         — only test checks at this level or below (default: all)
#   VERBOSE       — set to 1 for detailed diff output on failures

IMPL="${1:?Usage: $0 <implementation-command>}"
FIXTURES_DIR="${FIXTURES_DIR:-fixtures/epub}"
EXPECTED_DIR="${EXPECTED_DIR:-expected}"
CHECKS_FILE="checks.json"
LEVEL="${LEVEL:-}"
VERBOSE="${VERBOSE:-0}"

PASS=0
FAIL=0
SKIP=0
ERRORS=""

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# If LEVEL is set, build list of fixtures for that level from checks.json
declare -A LEVEL_FIXTURES
if [ -n "$LEVEL" ] && [ -f "$CHECKS_FILE" ]; then
    while IFS= read -r fixture; do
        LEVEL_FIXTURES["$fixture"]=1
    done < <(jq -r --argjson lvl "$LEVEL" \
        '.checks[] | select(.level <= $lvl) |
         if (.fixture_invalid | type) == "array" then .fixture_invalid[]
         else .fixture_invalid end' "$CHECKS_FILE" 2>/dev/null || true)
    # Add valid fixtures too
    while IFS= read -r fixture; do
        LEVEL_FIXTURES["$fixture"]=1
    done < <(jq -r --argjson lvl "$LEVEL" \
        '.checks[] | select(.level <= $lvl) | .fixture_valid' "$CHECKS_FILE" 2>/dev/null | sort -u || true)
fi

for category in valid invalid; do
    if [ ! -d "$EXPECTED_DIR/$category" ]; then
        continue
    fi

    for expected_file in "$EXPECTED_DIR/$category"/*.json; do
        [ -f "$expected_file" ] || continue
        name=$(basename "$expected_file" .json)
        epub_file="$FIXTURES_DIR/$category/$name.epub"

        # Level filtering
        if [ -n "$LEVEL" ] && [ ${#LEVEL_FIXTURES[@]} -gt 0 ]; then
            if [ -z "${LEVEL_FIXTURES[$category/$name]:-}" ]; then
                SKIP=$((SKIP + 1))
                continue
            fi
        fi

        if [ ! -f "$epub_file" ]; then
            echo "SKIP: $category/$name (no fixture epub)"
            SKIP=$((SKIP + 1))
            continue
        fi

        # Run implementation
        impl_output="$TMPDIR/$category-$name.json"
        if ! $IMPL "$epub_file" > "$impl_output" 2>/dev/null; then
            # Non-zero exit is expected for invalid epubs, check if we got output
            if [ ! -s "$impl_output" ]; then
                echo "FAIL: $category/$name (implementation produced no output)"
                FAIL=$((FAIL + 1))
                continue
            fi
        fi

        # Validate JSON output
        if ! jq empty "$impl_output" 2>/dev/null; then
            echo "FAIL: $category/$name (implementation output is not valid JSON)"
            FAIL=$((FAIL + 1))
            continue
        fi

        # Parse expected
        exp_valid=$(jq -r '.valid' "$expected_file")
        exp_fatal=$(jq -r '.fatal_count // 0' "$expected_file")
        exp_error=$(jq -r '.error_count' "$expected_file")
        exp_error_min=$(jq -r '.error_count_min // "null"' "$expected_file")
        exp_warning=$(jq -r '.warning_count' "$expected_file")

        # Parse implementation output — support both checker.nFatal and derived counts
        impl_fatal=$(jq '(.checker.nFatal // null) // ([.messages[] | select(.severity == "FATAL")] | length)' "$impl_output" 2>/dev/null || echo "0")
        impl_error=$(jq '(.checker.nError // null) // ([.messages[] | select(.severity == "ERROR")] | length)' "$impl_output" 2>/dev/null || echo "0")
        impl_warning=$(jq '(.checker.nWarning // null) // ([.messages[] | select(.severity == "WARNING")] | length)' "$impl_output" 2>/dev/null || echo "0")

        # Determine validity
        if [ "$impl_fatal" -eq 0 ] 2>/dev/null && [ "$impl_error" -eq 0 ] 2>/dev/null; then
            impl_valid="true"
        else
            impl_valid="false"
        fi

        fixture_ok=true
        fixture_errors=""

        # Check valid status
        if [ "$exp_valid" != "$impl_valid" ]; then
            fixture_ok=false
            fixture_errors="${fixture_errors}\n  valid: expected=$exp_valid got=$impl_valid"
        fi

        # Check error count
        if [ "$exp_error_min" != "null" ]; then
            if [ "$impl_error" -lt "$exp_error_min" ] 2>/dev/null; then
                fixture_ok=false
                fixture_errors="${fixture_errors}\n  error_count: expected>=$exp_error_min got=$impl_error"
            fi
        else
            if [ "$exp_error" -ne "$impl_error" ] 2>/dev/null; then
                fixture_ok=false
                fixture_errors="${fixture_errors}\n  error_count: expected=$exp_error got=$impl_error"
            fi
        fi

        # Check fatal count
        if [ "$exp_fatal" -ne "$impl_fatal" ] 2>/dev/null; then
            fixture_ok=false
            fixture_errors="${fixture_errors}\n  fatal_count: expected=$exp_fatal got=$impl_fatal"
        fi

        # Check warning count
        if [ "$exp_warning" -ne "$impl_warning" ] 2>/dev/null; then
            fixture_ok=false
            fixture_errors="${fixture_errors}\n  warning_count: expected=$exp_warning got=$impl_warning"
        fi

        # Check message patterns
        msg_count=$(jq '.messages | length' "$expected_file")
        for ((i=0; i<msg_count; i++)); do
            pattern=$(jq -r ".messages[$i].message_pattern" "$expected_file")
            severity=$(jq -r ".messages[$i].severity" "$expected_file")

            if [ -n "$pattern" ] && [ "$pattern" != "null" ]; then
                match=$(jq --arg pat "$pattern" --arg sev "$severity" \
                    '[.messages[] | select(.severity == $sev and (.message | test($pat; "i")))] | length' \
                    "$impl_output" 2>/dev/null || echo "0")
                if [ "$match" -eq 0 ]; then
                    fixture_ok=false
                    fixture_errors="${fixture_errors}\n  message[$i]: no $severity message matching /$pattern/i"
                fi
            fi
        done

        if $fixture_ok; then
            echo "PASS: $category/$name"
            PASS=$((PASS + 1))
        else
            echo "FAIL: $category/$name"
            if [ "$VERBOSE" = "1" ]; then
                echo -e "$fixture_errors"
            fi
            FAIL=$((FAIL + 1))
        fi
    done
done

TOTAL=$((PASS + FAIL + SKIP))
if [ "$TOTAL" -gt 0 ]; then
    PCT=$((PASS * 100 / (PASS + FAIL + (FAIL == 0 && PASS == 0 ? 1 : 0))))
else
    PCT=0
fi

echo ""
echo "Results: $PASS passed, $FAIL failed, $SKIP skipped out of $TOTAL total"
if [ "$PASS" -gt 0 ] || [ "$FAIL" -gt 0 ]; then
    echo "Pass rate: ${PCT}% ($PASS / $((PASS + FAIL)))"
fi

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
