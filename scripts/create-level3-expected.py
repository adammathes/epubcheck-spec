#!/usr/bin/env python3
"""Create expected output JSON files for Level 3 fixtures.

Based on analysis of epubcheck 5.3.0 reference output.
"""
import json
import os
import re

EXPECTED_DIR = "expected"
REFERENCE_DIR = "reference"

# Level 3 check definitions
# Format: fixture_name -> {check_id, epubcheck_id, severity, message_pattern, ...}
# Special keys:
#   valid_override: True means epubcheck doesn't flag this, mark valid=true with note
#   message_count_min: use error_count_min for cascading errors
#   skip_messages: indices of reference messages to skip (not our primary check)
#   extra_messages: additional messages to include beyond the primary one

LEVEL3_CHECKS = {
    # === CSS Validation ===
    "css-syntax-error": {
        "check_id": "CSS-001",
        "epubcheck_id": "CSS-008",
        "severity": "ERROR",
        "message_pattern": "error occurred while parsing the CSS",
        "error_count_min": 1,
    },
    "css-invalid-property": {
        "check_id": "CSS-002",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag unknown CSS property names",
    },
    "css-font-face-no-src": {
        "check_id": "CSS-003",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag @font-face rules missing a src descriptor",
    },
    "css-font-face-remote": {
        "check_id": "CSS-004",
        "epubcheck_id": "OPF-014",
        "severity": "ERROR",
        "message_pattern": "remote-resources.*should be declared",
        "error_count_min": 1,
    },
    "css-import": {
        "check_id": "CSS-005",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag @import rules in CSS",
    },
    "css-font-face-missing-file": {
        "check_id": "CSS-006",
        "epubcheck_id": "RSC-007",
        "severity": "ERROR",
        "message_pattern": "could not be found",
    },
    "css-background-image-missing": {
        "check_id": "CSS-007",
        "epubcheck_id": "RSC-007",
        "severity": "ERROR",
        "message_pattern": "could not be found",
    },
    "css-resource-not-in-manifest": {
        "check_id": "CSS-008",
        "epubcheck_id": "RSC-008",
        "severity": "ERROR",
        "message_pattern": "not declared in the OPF manifest",
    },

    # === Fixed-Layout ===
    "fxl-rendition-layout-invalid": {
        "check_id": "FXL-001",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "rendition:layout.*must be either",
    },
    "fxl-rendition-orientation-invalid": {
        "check_id": "FXL-002",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "rendition:orientation.*must be either",
    },
    "fxl-rendition-spread-invalid": {
        "check_id": "FXL-003",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "rendition:spread.*must be either",
    },
    "fxl-spine-layout-invalid": {
        "check_id": "FXL-004",
        "epubcheck_id": "OPF-027",
        "severity": "ERROR",
        "message_pattern": "Undefined property",
    },
    "fxl-spine-spread-invalid": {
        "check_id": "FXL-005",
        "epubcheck_id": "OPF-027",
        "severity": "ERROR",
        "message_pattern": "Undefined property",
    },

    # === Media/Image ===
    "image-media-type-wrong": {
        "check_id": "MED-001",
        "epubcheck_id": "OPF-029",
        "severity": "ERROR",
        "message_pattern": "does not appear to match the media type",
    },
    "image-non-core-media-type": {
        "check_id": "MED-002",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag image/webp as non-core media type",
    },
    "image-corrupted": {
        "check_id": "MED-003",
        "epubcheck_id": "PKG-021",
        "severity": "ERROR",
        "message_pattern": "Corrupted image",
        "error_count_min": 1,
    },
    "svg-wrong-media-type": {
        "check_id": "MED-004",
        "epubcheck_id": "RSC-032",
        "severity": "ERROR",
        "message_pattern": "Fallback must be provided for foreign resources",
    },
    "audio-non-core-media-type": {
        "check_id": "MED-005",
        "epubcheck_id": "RSC-032",
        "severity": "ERROR",
        "message_pattern": "Fallback must be provided for foreign resources",
    },

    # === Encoding ===
    "content-non-utf8-encoding": {
        "check_id": "ENC-001",
        "epubcheck_id": "RSC-028",
        "severity": "ERROR",
        "message_pattern": "must be encoded in UTF-8",
    },
    "content-utf16-encoding": {
        "check_id": "ENC-002",
        "epubcheck_id": "HTM_058",
        "severity": "ERROR",
        "message_pattern": "must be encoded in UTF-8",
    },

    # === Additional OPF ===
    "opf-no-unique-id-attr": {
        "check_id": "OPF-027",
        "epubcheck_id": "OPF-048",
        "severity": "ERROR",
        "message_pattern": "missing.*unique-identifier",
        "error_count_min": 1,
    },
    "opf-duplicate-dcterms-modified": {
        "check_id": "OPF-028",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "dcterms:modified.*must occur exactly once",
    },
    "opf-manifest-invalid-property": {
        "check_id": "OPF-029",
        "epubcheck_id": "OPF-027",
        "severity": "ERROR",
        "message_pattern": "Undefined property",
    },
    "opf-manifest-href-empty": {
        "check_id": "OPF-030",
        "epubcheck_id": "OPF-099",
        "severity": "ERROR",
        "message_pattern": "must not list the package document",
    },
    "opf-dc-identifier-empty": {
        "check_id": "OPF-031",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "dc:identifier.*invalid",
    },
    "opf-dc-title-empty": {
        "check_id": "OPF-032",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "dc:title.*invalid",
    },
    "opf-manifest-href-fragment": {
        "check_id": "OPF-033",
        "epubcheck_id": "OPF-091",
        "severity": "ERROR",
        "message_pattern": "must not have a fragment",
        "error_count_min": 1,
    },
    "opf-package-dir-invalid": {
        "check_id": "OPF-034",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "dir.*invalid.*must be equal to",
    },

    # === Additional Content Document ===
    "content-epub-type-invalid": {
        "check_id": "HTM-015",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag unknown epub:type values",
    },
    "content-duplicate-ids": {
        "check_id": "HTM-016",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "Duplicate ID",
    },
    "content-html-entity": {
        "check_id": "HTM-017",
        "epubcheck_id": "RSC-016",
        "severity": "FATAL",
        "message_pattern": "entity.*was referenced.*not declared",
    },
    "content-multiple-body": {
        "check_id": "HTM-018",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "body.*not allowed here",
    },
    "content-no-html-element": {
        "check_id": "HTM-019",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "body.*not allowed.*expected.*html",
    },
    "content-processing-instruction": {
        "check_id": "HTM-020",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag xml-stylesheet processing instructions in content documents",
    },
    "content-style-position-absolute": {
        "check_id": "HTM-021",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag position:absolute in inline styles",
    },
    "content-object-no-fallback": {
        "check_id": "HTM-022",
        "epubcheck_id": "RSC-007",
        "severity": "ERROR",
        "message_pattern": "could not be found",
    },
    "content-link-parent-dir": {
        "check_id": "HTM-023",
        "epubcheck_id": "RSC-026",
        "severity": "ERROR",
        "message_pattern": "leaks outside the container",
        "error_count_min": 1,
    },

    # === Navigation Edge Cases ===
    "nav-toc-no-ol": {
        "check_id": "NAV-008",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "missing required element.*ol",
        "error_count_min": 1,
    },
    "nav-hidden-attribute": {
        "check_id": "NAV-009",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag hidden attribute on nav element",
    },
    "nav-landmarks-invalid-type": {
        "check_id": "NAV-010",
        "valid_override": True,
        "note": "epubcheck 5.3.0 does not flag unknown epub:type values on landmark nav entries",
    },
    "nav-malformed-xhtml": {
        "check_id": "NAV-011",
        "epubcheck_id": "RSC-016",
        "severity": "FATAL",
        "message_pattern": "must be terminated by the matching end-tag",
    },

    # === Full EPUB 2 ===
    "epub2-with-nav-property": {
        "check_id": "E2-005",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "properties.*not allowed",
        "error_count_min": 1,
    },
    "epub2-with-dcterms-modified": {
        "check_id": "E2-006",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "property.*not allowed",
        "error_count_min": 1,
    },
    "epub2-ncx-navpoint-no-content": {
        "check_id": "E2-007",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "navPoint.*incomplete.*missing.*content",
    },
    "epub2-ncx-broken-content-src": {
        "check_id": "E2-008",
        "epubcheck_id": "RSC-007",
        "severity": "ERROR",
        "message_pattern": "could not be found",
    },
    "epub2-guide-broken-href": {
        "check_id": "E2-009",
        "epubcheck_id": "OPF-031",
        "severity": "ERROR",
        "message_pattern": "guide.*not declared in OPF manifest",
        "error_count_min": 1,
    },
    "epub2-ncx-uid-mismatch": {
        "check_id": "E2-010",
        "epubcheck_id": "NCX-001",
        "severity": "ERROR",
        "message_pattern": "NCX identifier.*does not match OPF identifier",
    },
    "epub2-ncx-duplicate-ids": {
        "check_id": "E2-011",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "id.*attribute.*does not have a unique value",
        "error_count_min": 1,
    },

    # === Additional Resource Checks ===
    "manifest-href-bad-encoding": {
        "check_id": "RSC-010",
        "epubcheck_id": "RSC-020",
        "severity": "ERROR",
        "message_pattern": "not a valid URL",
        "error_count_min": 1,
    },
    "manifest-path-traversal": {
        "check_id": "RSC-011",
        "epubcheck_id": "RSC-001",
        "severity": "ERROR",
        "message_pattern": "could not be found",
        "error_count_min": 1,
    },
    "manifest-duplicate-item-same-resource": {
        "check_id": "RSC-012",
        "epubcheck_id": "OPF-060",
        "severity": "ERROR",
        "message_pattern": "Duplicate entry in the ZIP",
    },

    # === Container Edge Cases ===
    "ocf-metainf-extra-files": {
        "check_id": "OCF-010",
        "epubcheck_id": "RSC-005",
        "severity": "ERROR",
        "message_pattern": "encryption.*incomplete",
    },
    "ocf-container-multiple-rootfiles": {
        "check_id": "OCF-011",
        "epubcheck_id": "OPF-002",
        "severity": "FATAL",
        "message_pattern": "was not found",
    },
    "manifest-absolute-path": {
        "check_id": "RSC-013",
        "epubcheck_id": "RSC-026",
        "severity": "ERROR",
        "message_pattern": "leaks outside the container",
    },
    "ocf-container-wrong-rootfile-mediatype": {
        "check_id": "OCF-012",
        "epubcheck_id": "RSC-003",
        "severity": "ERROR",
        "message_pattern": "No rootfile tag with media type",
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
        error_count = 0 if severity == "FATAL" else 1
        warning_count = 0

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
            else:
                error_count = ref_errors

            warning_count = ref_warnings

            # Use error_count_min if there are more errors than expected from single defect
            if check_info.get("error_count_min"):
                error_count_min = check_info["error_count_min"]

        msg = {
            "severity": severity,
            "check_id": check_info["check_id"],
            "epubcheck_id": check_info["epubcheck_id"],
            "message_pattern": check_info["message_pattern"],
            "note": ""
        }

        expected = {
            "fixture": fixture_path,
            "valid": False,
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
    print("Creating Level 3 expected output files...\n")

    for fixture_name, check_info in sorted(LEVEL3_CHECKS.items()):
        create_expected(fixture_name, check_info)

    print("\nCreating valid fixture expected files...")
    create_valid_expected("fxl-epub3")
    create_valid_expected("epub3-with-css")

    print(f"\nDone! Created {len(LEVEL3_CHECKS)} invalid + 2 valid expected files.")
