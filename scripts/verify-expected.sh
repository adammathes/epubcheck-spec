#!/bin/bash
set -euo pipefail

EXPECTED_DIR="expected"
REFERENCE_DIR="reference"
PASS=0
FAIL=0
SKIP=0
ERRORS=""

for category in valid invalid; do
    if [ -d "$EXPECTED_DIR/$category" ]; then
        for expected_file in "$EXPECTED_DIR/$category"/*.json; do
            [ -f "$expected_file" ] || continue
            name=$(basename "$expected_file" .json)
            ref_file="$REFERENCE_DIR/$category/$name.json"

            if [ ! -f "$ref_file" ]; then
                echo "SKIP: $category/$name (no reference output)"
                SKIP=$((SKIP + 1))
                continue
            fi

            # Parse expected
            exp_valid=$(jq -r '.valid' "$expected_file")
            exp_fatal=$(jq -r '.fatal_count // 0' "$expected_file")
            exp_error=$(jq -r '.error_count' "$expected_file")
            exp_error_min=$(jq -r '.error_count_min // "null"' "$expected_file")
            exp_warning=$(jq -r '.warning_count' "$expected_file")

            # Parse reference
            ref_fatal=$(jq '[.messages[] | select(.severity == "FATAL")] | length' "$ref_file")
            ref_error=$(jq '[.messages[] | select(.severity == "ERROR")] | length' "$ref_file")
            ref_warning=$(jq '[.messages[] | select(.severity == "WARNING")] | length' "$ref_file")

            # Determine validity from reference
            if [ "$ref_fatal" -eq 0 ] && [ "$ref_error" -eq 0 ]; then
                ref_valid="true"
            else
                ref_valid="false"
            fi

            fixture_ok=true
            fixture_errors=""

            # Check valid status
            if [ "$exp_valid" != "$ref_valid" ]; then
                fixture_ok=false
                fixture_errors="${fixture_errors}\n  valid: expected=$exp_valid reference=$ref_valid"
            fi

            # Check error count (with min support)
            if [ "$exp_error_min" != "null" ]; then
                # Use min threshold: reference must have at least this many
                if [ "$ref_error" -lt "$exp_error_min" ]; then
                    fixture_ok=false
                    fixture_errors="${fixture_errors}\n  error_count: expected>=$exp_error_min reference=$ref_error"
                fi
            else
                # Exact match
                if [ "$exp_error" -ne "$ref_error" ]; then
                    fixture_ok=false
                    fixture_errors="${fixture_errors}\n  error_count: expected=$exp_error reference=$ref_error"
                fi
            fi

            # Check fatal count
            if [ "$exp_fatal" -ne "$ref_fatal" ]; then
                fixture_ok=false
                fixture_errors="${fixture_errors}\n  fatal_count: expected=$exp_fatal reference=$ref_fatal"
            fi

            # Check warning count
            if [ "$exp_warning" -ne "$ref_warning" ]; then
                fixture_ok=false
                fixture_errors="${fixture_errors}\n  warning_count: expected=$exp_warning reference=$ref_warning"
            fi

            # Check message patterns
            msg_count=$(jq '.messages | length' "$expected_file")
            for ((i=0; i<msg_count; i++)); do
                pattern=$(jq -r ".messages[$i].message_pattern" "$expected_file")
                severity=$(jq -r ".messages[$i].severity" "$expected_file")
                epubcheck_id=$(jq -r ".messages[$i].epubcheck_id" "$expected_file")

                if [ "$pattern" != "" ] && [ "$pattern" != "null" ]; then
                    # Check that at least one reference message matches the pattern and severity
                    match=$(jq --arg pat "$pattern" --arg sev "$severity" \
                        '[.messages[] | select(.severity == $sev and (.message | test($pat; "i")))] | length' \
                        "$ref_file")
                    if [ "$match" -eq 0 ]; then
                        fixture_ok=false
                        fixture_errors="${fixture_errors}\n  message[$i]: no $severity message matching /$pattern/i"
                    fi
                fi

                if [ "$epubcheck_id" != "" ] && [ "$epubcheck_id" != "null" ]; then
                    # Check that at least one reference message has this ID
                    match=$(jq --arg id "$epubcheck_id" \
                        '[.messages[] | select(.ID == $id)] | length' \
                        "$ref_file")
                    if [ "$match" -eq 0 ]; then
                        fixture_ok=false
                        fixture_errors="${fixture_errors}\n  message[$i]: no message with ID=$epubcheck_id"
                    fi
                fi
            done

            if $fixture_ok; then
                echo "PASS: $category/$name"
                PASS=$((PASS + 1))
            else
                echo "FAIL: $category/$name"
                echo -e "$fixture_errors"
                FAIL=$((FAIL + 1))
            fi
        done
    fi
done

echo ""
echo "Results: $PASS passed, $FAIL failed, $SKIP skipped"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
