#!/usr/bin/env python3
"""Create expected output JSON files for Level 4 fixtures.

Based on analysis of epubcheck 5.3.0 reference output.
"""
import json
import os

EXPECTED_DIR = "expected"
REFERENCE_DIR = "reference"

# Level 4 check definitions
# Format: fixture_name -> {check_id, epubcheck_id, severity, message_pattern, ...}
# Special keys:
#   valid_override: True means epubcheck doesn't flag this, mark valid=true with note
#   error_count_min: use error_count_min for cascading errors

LEVEL4_CHECKS = {
    # === Batch 1: Advanced OPF & Metadata ===
    "opf-ppd-invalid": {
        "check_id": "OPF-035",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "page-progression-direction.*must be equal to",
    },
    "opf-dc-date-invalid": {
        "check_id": "OPF-036",
        "epubcheck_id": "OPF-053",
        "severity": "WARNING",
        "message_pattern": "Date value.*does not follow recommended syntax",
    },
    "opf-meta-refines-bad-target": {
        "check_id": "OPF-037",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "refines missing target id",
        "error_count_min": 1,
    },
    "opf-spine-linear-invalid": {
        "check_id": "OPF-038",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "linear.*must be equal to",
    },
    "opf-epub3-guide": {
        "check_id": "OPF-039",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag guide element in EPUB 3 packages",
    },
    "opf-uuid-invalid": {
        "check_id": "OPF-040",
        "epubcheck_id": "OPF-085",
        "severity": "WARNING",
        "message_pattern": "UUID.*invalid",
    },
    "opf-spine-all-nonlinear": {
        "check_id": "OPF-041",
        "epubcheck_id": "OPF-033",
        "severity": "ERROR",
        "message_pattern": "spine contains no linear resources",
    },
    "opf-rendition-flow-invalid": {
        "check_id": "OPF-042",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "rendition:flow.*must be either",
    },
    "opf-prefix-invalid": {
        "check_id": "OPF-043",
        "epubcheck_id": "OPF-004c",
        "severity": "ERROR",
        "message_pattern": "Invalid prefix declaration",
        "error_count_min": 1,
    },
    "opf-media-overlay-bad-ref": {
        "check_id": "OPF-044",
        "epubcheck_id": "MED_013",
        "severity": "ERROR",
        "message_pattern": "Media Overlay Document referenced",
        "error_count_min": 1,
    },

    # === Batch 2: Advanced Content Documents ===
    "content-no-head": {
        "check_id": "HTM-024",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "missing required element.*head",
    },
    "content-embed-element": {
        "check_id": "HTM-025",
        "epubcheck_id": "RSC-007",
        "severity": "ERROR",
        "message_pattern": "could not be found",
    },
    "content-lang-mismatch": {
        "check_id": "HTM-026",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "lang and xml:lang.*must have the same value",
    },
    "content-video-poster-missing": {
        "check_id": "HTM-027",
        "epubcheck_id": "RSC-007",
        "severity": "ERROR",
        "message_pattern": "could not be found",
        "error_count_min": 1,
    },
    "content-audio-missing": {
        "check_id": "HTM-028",
        "epubcheck_id": "RSC-007",
        "severity": "ERROR",
        "message_pattern": "could not be found",
    },
    "content-svg-malformed": {
        "check_id": "HTM-029",
        "epubcheck_id": "RSC-016",
        "severity": "FATAL",
        "message_pattern": "Attribute name.*associated with an element",
    },
    "content-img-empty-src": {
        "check_id": "HTM-030",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "src.*is invalid.*must be a string with length",
    },
    "content-ssml-invalid-ns": {
        "check_id": "HTM-031",
        "epubcheck_id": "HTM_054",
        "severity": "ERROR",
        "message_pattern": "Custom attribute namespace.*must not include",
    },
    "content-style-syntax-error": {
        "check_id": "HTM-032",
        "epubcheck_id": "CSS-008",
        "severity": "ERROR",
        "message_pattern": "error occurred while parsing the CSS",
        "error_count_min": 1,
    },
    "content-rdf-element": {
        "check_id": "HTM-033",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag RDF metadata in content documents",
    },

    # === Batch 3: Accessibility ===
    "acc-no-a11y-metadata": {
        "check_id": "ACC-001",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag missing accessibility metadata without --profile option",
    },
    "acc-img-no-alt": {
        "check_id": "ACC-002",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag img elements missing alt attribute",
    },
    "acc-no-lang": {
        "check_id": "ACC-003",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag missing lang attribute on html element",
    },
    "acc-dc-source-no-page-list": {
        "check_id": "ACC-004",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag missing page-list when dc:source is present",
    },
    "acc-no-accessmode": {
        "check_id": "ACC-005",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag missing schema:accessMode metadata",
    },
    "acc-no-access-sufficient": {
        "check_id": "ACC-006",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag missing schema:accessModeSufficient metadata",
    },
    "acc-no-summary": {
        "check_id": "ACC-007",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag missing schema:accessibilitySummary metadata",
    },
    "acc-no-feature": {
        "check_id": "ACC-008",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag missing schema:accessibilityFeature metadata",
    },
    "acc-no-hazard": {
        "check_id": "ACC-009",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag missing schema:accessibilityHazard metadata",
    },
    "acc-no-landmarks": {
        "check_id": "ACC-010",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag missing landmarks navigation",
    },
}


def create_expected(fixture_name, check_info, category="invalid"):
    """Create expected JSON file for a fixture."""
    fixture_path = f"{category}/{fixture_name}"
    out_dir = os.path.join(EXPECTED_DIR, category)
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{fixture_name}.json")

    if check_info.get("valid_override"):
        # Fixture where epubcheck doesn't flag the issue
        expected = {
            "fixture": fixture_path,
            "valid": True,
            "messages": [],
            "fatal_count": 0,
            "error_count": 0,
            "error_count_min": None,
            "warning_count": 0,
            "note": check_info.get("note", "")
        }
    else:
        severity = check_info["severity"]
        fatal_count = 1 if severity == "FATAL" else 0
        error_count = 0 if severity in ("FATAL", "WARNING", "USAGE") else 1
        warning_count = 1 if severity == "WARNING" else 0

        # Read reference to get actual counts
        ref_path = os.path.join(REFERENCE_DIR, category, f"{fixture_name}.json")
        error_count_min = None
        if os.path.exists(ref_path):
            with open(ref_path) as f:
                ref = json.load(f)
            ref_fatals = ref["checker"]["nFatal"]
            ref_errors = ref["checker"]["nError"]
            ref_warnings = ref["checker"]["nWarning"]

            if severity == "FATAL":
                fatal_count = ref_fatals
                error_count = ref_errors
            elif severity == "WARNING":
                error_count = ref_errors
                warning_count = ref_warnings
            else:
                error_count = ref_errors

            if not warning_count and severity != "WARNING":
                warning_count = ref_warnings

            # Use error_count_min if there are more errors than expected from single defect
            if check_info.get("error_count_min"):
                error_count_min = check_info["error_count_min"]

        # EPUB is valid if there are no FATAL or ERROR messages
        is_valid = (fatal_count == 0 and error_count == 0)

        msg = {
            "severity": severity,
            "check_id": check_info["check_id"],
            "epubcheck_id": check_info["epubcheck_id"],
            "message_pattern": check_info["message_pattern"],
            "note": ""
        }

        expected = {
            "fixture": fixture_path,
            "valid": is_valid,
            "messages": [msg],
            "fatal_count": fatal_count,
            "error_count": error_count,
            "error_count_min": error_count_min,
            "warning_count": warning_count,
        }

    with open(out_file, 'w') as f:
        json.dump(expected, f, indent=2)
        f.write('\n')

    print(f"  Created: {out_file}")


def create_valid_expected(fixture_name):
    """Create expected JSON file for a valid fixture."""
    out_dir = os.path.join(EXPECTED_DIR, "valid")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{fixture_name}.json")

    expected = {
        "fixture": f"valid/{fixture_name}",
        "valid": True,
        "messages": [],
        "fatal_count": 0,
        "error_count": 0,
        "error_count_min": None,
        "warning_count": 0,
    }

    with open(out_file, 'w') as f:
        json.dump(expected, f, indent=2)
        f.write('\n')

    print(f"  Created: {out_file}")


if __name__ == "__main__":
    print("Creating Level 4 expected output files...\n")

    for fixture_name, check_info in sorted(LEVEL4_CHECKS.items()):
        create_expected(fixture_name, check_info)

    print(f"\nDone! Created {len(LEVEL4_CHECKS)} expected files.")
