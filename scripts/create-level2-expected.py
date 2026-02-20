#!/usr/bin/env python3
"""Create expected JSON files for Level 2 fixtures based on reference output.

Reads reference/*.json files, extracts the key information, and creates
expected/*.json files with our curated check IDs and notes.
"""
import json
import os

REFERENCE_DIR = "reference"
EXPECTED_DIR = "expected"

# Level 1 fixtures (already have expected files, skip these)
LEVEL1_FIXTURES = {
    "content-broken-image-ref", "content-broken-internal-link",
    "content-malformed-xhtml", "manifest-file-not-in-zip",
    "nav-missing", "nav-no-toc", "ocf-container-malformed-xml",
    "ocf-container-missing", "ocf-container-no-rootfile",
    "ocf-container-rootfile-not-found", "ocf-mimetype-compressed",
    "ocf-mimetype-extra-field", "ocf-mimetype-extra-whitespace",
    "ocf-mimetype-missing", "ocf-mimetype-not-first",
    "ocf-mimetype-wrong-content", "opf-duplicate-manifest-id",
    "opf-manifest-href-missing", "opf-manifest-media-type-missing",
    "opf-missing-dc-identifier", "opf-missing-dc-language",
    "opf-missing-dc-title", "opf-missing-dcterms-modified",
    "opf-missing-unique-identifier", "spine-bad-idref",
    "spine-empty", "zip-entry-not-in-manifest",
}

# Check ID mapping: fixture name -> (check_id, check details)
# Each entry: (check_id, primary_severity, primary_epubcheck_id, message_pattern, note)
LEVEL2_CHECKS = {
    # OPF Structural
    "opf-malformed-xml": {
        "check_id": "OPF-011",
        "severity": "FATAL",
        "epubcheck_id": "RSC-016",
        "message_pattern": "XML document structures must start and end",
        "note": "",
    },
    "opf-missing-metadata": {
        "check_id": "OPF-012",
        "severity": "ERROR",
        "epubcheck_id": "RSC-005",
        "message_pattern": "missing required element.*metadata",
        "note": "Cascading errors from missing metadata element",
    },
    "opf-missing-manifest": {
        "check_id": "OPF-013",
        "severity": "ERROR",
        "epubcheck_id": "RSC-005",
        "message_pattern": "missing required element.*manifest",
        "note": "Cascading errors from missing manifest element",
    },
    "opf-missing-spine": {
        "check_id": "OPF-014",
        "severity": "ERROR",
        "epubcheck_id": "RSC-005",
        "message_pattern": "missing required element.*spine",
        "note": "Cascading errors from missing spine element",
    },
    "opf-wrong-version": {
        "check_id": "OPF-015",
        "severity": "ERROR",
        "epubcheck_id": "OPF-001",
        "message_pattern": "version",
        "note": "",
    },
    "opf-duplicate-manifest-href": {
        "check_id": "OPF-016",
        "severity": "ERROR",
        "epubcheck_id": "OPF-074",
        "message_pattern": "declared in several manifest items",
        "note": "",
    },
    "opf-duplicate-spine-idref": {
        "check_id": "OPF-017",
        "severity": "ERROR",
        "epubcheck_id": "RSC-005",
        "message_pattern": "same manifest entry as a previous",
        "note": "",
    },
    "opf-manifest-item-no-id": {
        "check_id": "OPF-018",
        "severity": "ERROR",
        "epubcheck_id": "RSC-005",
        "message_pattern": "missing required attribute.*id",
        "note": "Cascading errors from missing id attribute",
    },
    "opf-dcterms-modified-invalid": {
        "check_id": "OPF-019",
        "severity": "ERROR",
        "epubcheck_id": "RSC-005",
        "message_pattern": "dcterms:modified",
        "note": "",
    },
    "opf-dc-language-invalid": {
        "check_id": "OPF-020",
        "severity": "ERROR",
        "epubcheck_id": "OPF-092",
        "message_pattern": "not well-formed",
        "note": "",
    },
    # OPF Fallback/Media
    "opf-fallback-ref-missing": {
        "check_id": "OPF-021",
        "severity": "ERROR",
        "epubcheck_id": "OPF-040",
        "message_pattern": "could not be found",
        "note": "",
    },
    "opf-fallback-cycle": {
        "check_id": "OPF-022",
        "severity": "ERROR",
        "epubcheck_id": "OPF-045",
        "message_pattern": "circular reference",
        "note": "",
    },
    "opf-spine-non-content-doc": {
        "check_id": "OPF-023",
        "severity": "ERROR",
        "epubcheck_id": "OPF-043",
        "message_pattern": "non-standard media-type.*no fallback",
        "note": "",
    },
    "opf-media-type-mismatch": {
        "check_id": "OPF-024",
        "severity": "ERROR",
        "epubcheck_id": "OPF-029",
        "message_pattern": "does not appear to match the media type",
        "note": "Cascading errors from media type mismatch",
    },
    "opf-cover-image-not-image": {
        "check_id": "OPF-025",
        "severity": "ERROR",
        "epubcheck_id": "OPF-012",
        "message_pattern": "cover-image.*not defined for media type",
        "note": "",
    },
    "opf-multiple-nav": {
        "check_id": "OPF-026",
        "severity": "ERROR",
        "epubcheck_id": "RSC-005",
        "message_pattern": "Exactly one.*nav",
        "note": "",
    },
    # RSC Resources
    "content-fragment-id-missing": {
        "check_id": "RSC-003",
        "severity": "ERROR",
        "epubcheck_id": "RSC-012",
        "message_pattern": "Fragment identifier is not defined",
        "note": "",
    },
    "content-remote-resource": {
        "check_id": "RSC-004",
        "severity": "ERROR",
        "epubcheck_id": "RSC-006",
        "message_pattern": "Remote resource reference is not allowed",
        "note": "Also triggers OPF-014 for undeclared remote-resources property",
    },
    "content-css-file-missing": {
        "check_id": "RSC-005",
        "severity": "ERROR",
        "epubcheck_id": "RSC-001",
        "message_pattern": "style\\.css.*could not be found",
        "note": "",
    },
    "content-resource-not-in-manifest": {
        "check_id": "RSC-006",
        "severity": "ERROR",
        "epubcheck_id": "RSC-008",
        "message_pattern": "not declared in the OPF manifest",
        "note": "",
    },
    "content-font-file-missing": {
        "check_id": "RSC-007",
        "severity": "ERROR",
        "epubcheck_id": "RSC-001",
        "message_pattern": "missing\\.woff2.*could not be found",
        "note": "",
    },
    "content-remote-stylesheet": {
        "check_id": "RSC-008",
        "severity": "ERROR",
        "epubcheck_id": "RSC-006",
        "message_pattern": "Remote resource reference",
        "note": "",
    },
    # HTM Content
    "content-no-title": {
        "check_id": "HTM-002",
        "severity": "WARNING",
        "epubcheck_id": "RSC-017",
        "message_pattern": "title",
        "note": "epubcheck reports this as a WARNING, not an ERROR",
    },
    "content-empty-href": {
        "check_id": "HTM-003",
        "severity": "ERROR",
        "epubcheck_id": None,
        "message_pattern": None,
        "note": "epubcheck 5.3.0 does not flag empty href attributes. Spec requires non-empty href.",
        "valid_override": True,
    },
    "content-obsolete-element": {
        "check_id": "HTM-004",
        "severity": "ERROR",
        "epubcheck_id": "RSC-005",
        "message_pattern": "center.*not allowed",
        "note": "",
    },
    "content-scripted-undeclared": {
        "check_id": "HTM-005",
        "severity": "ERROR",
        "epubcheck_id": "OPF-014",
        "message_pattern": "scripted.*should be declared",
        "note": "",
    },
    "content-svg-undeclared": {
        "check_id": "HTM-006",
        "severity": "ERROR",
        "epubcheck_id": "OPF-014",
        "message_pattern": "svg.*should be declared",
        "note": "",
    },
    "content-mathml-undeclared": {
        "check_id": "HTM-007",
        "severity": "ERROR",
        "epubcheck_id": "OPF-014",
        "message_pattern": "mathml.*should be declared",
        "note": "",
    },
    "content-fxl-no-viewport": {
        "check_id": "HTM-008",
        "severity": "ERROR",
        "epubcheck_id": "HTM-046",
        "message_pattern": "no.*viewport",
        "note": "",
    },
    "content-fxl-invalid-viewport": {
        "check_id": "HTM-009",
        "severity": "ERROR",
        "epubcheck_id": "HTM_056",
        "message_pattern": "Viewport metadata",
        "note": "Reports separate errors for missing width and height dimensions",
    },
    "content-base-element": {
        "check_id": "HTM-010",
        "severity": "ERROR",
        "epubcheck_id": None,
        "message_pattern": None,
        "note": "epubcheck 5.3.0 does not flag base elements in content documents. Spec restricts their use.",
        "valid_override": True,
    },
    "content-wrong-doctype": {
        "check_id": "HTM-011",
        "severity": "ERROR",
        "epubcheck_id": "HTM-004",
        "message_pattern": "Irregular DOCTYPE",
        "note": "",
    },
    "content-wrong-namespace": {
        "check_id": "HTM-012",
        "severity": "ERROR",
        "epubcheck_id": "RSC-005",
        "message_pattern": "namespace.*wrong",
        "note": "",
    },
    # NAV Navigation
    "nav-toc-broken-link": {
        "check_id": "NAV-003",
        "severity": "ERROR",
        "epubcheck_id": "RSC-007",
        "message_pattern": "nonexistent\\.xhtml.*could not be found",
        "note": "",
    },
    "nav-toc-empty-link": {
        "check_id": "NAV-004",
        "severity": "ERROR",
        "epubcheck_id": "RSC-005",
        "message_pattern": "Anchors within nav.*must contain text",
        "note": "",
    },
    "nav-multiple-toc": {
        "check_id": "NAV-005",
        "severity": "ERROR",
        "epubcheck_id": "RSC-005",
        "message_pattern": "Exactly one.*toc",
        "note": "",
    },
    "nav-landmarks-broken": {
        "check_id": "NAV-006",
        "severity": "ERROR",
        "epubcheck_id": "RSC-007",
        "message_pattern": "nonexistent\\.xhtml.*could not be found",
        "note": "",
    },
    "nav-page-list-broken": {
        "check_id": "NAV-007",
        "severity": "ERROR",
        "epubcheck_id": "RSC-007",
        "message_pattern": "nonexistent\\.xhtml.*could not be found",
        "note": "",
    },
    # EPUB 2
    "epub2-ncx-missing": {
        "check_id": "E2-001",
        "severity": "ERROR",
        "epubcheck_id": "RSC-001",
        "message_pattern": "toc\\.ncx.*could not be found",
        "note": "",
    },
    "epub2-ncx-malformed": {
        "check_id": "E2-002",
        "severity": "FATAL",
        "epubcheck_id": "RSC-016",
        "message_pattern": "XML document structures must start and end",
        "note": "",
    },
    "epub2-ncx-no-navmap": {
        "check_id": "E2-003",
        "severity": "ERROR",
        "epubcheck_id": "RSC-005",
        "message_pattern": "missing required element",
        "note": "",
    },
    "epub2-spine-no-toc": {
        "check_id": "E2-004",
        "severity": "ERROR",
        "epubcheck_id": "RSC-005",
        "message_pattern": "missing required attribute.*toc",
        "note": "",
    },
}


def read_reference(category, name):
    """Read a reference JSON file and extract key info."""
    ref_path = os.path.join(REFERENCE_DIR, category, f"{name}.json")
    if not os.path.exists(ref_path):
        return None

    with open(ref_path) as f:
        data = json.load(f)

    messages = data.get("messages", [])
    fatal_count = sum(1 for m in messages if m["severity"] == "FATAL")
    error_count = sum(1 for m in messages if m["severity"] == "ERROR")
    warning_count = sum(1 for m in messages if m["severity"] == "WARNING")

    return {
        "messages": messages,
        "fatal_count": fatal_count,
        "error_count": error_count,
        "warning_count": warning_count,
    }


def create_expected(fixture_name, check_info, ref_data):
    """Create an expected JSON file for a fixture."""
    is_valid_override = check_info.get("valid_override", False)

    if is_valid_override:
        # epubcheck doesn't flag this — mark as valid with note
        expected = {
            "fixture": f"invalid/{fixture_name}",
            "valid": True,
            "messages": [],
            "fatal_count": 0,
            "error_count": 0,
            "error_count_min": None,
            "warning_count": 0,
            "note": check_info["note"],
        }
    else:
        severity = check_info["severity"]
        epubcheck_id = check_info["epubcheck_id"]
        pattern = check_info["message_pattern"]
        note = check_info.get("note", "")

        messages = [{
            "severity": severity,
            "check_id": check_info["check_id"],
            "epubcheck_id": epubcheck_id,
            "message_pattern": pattern,
            "note": note,
        }]

        fatal_count = ref_data["fatal_count"]
        error_count = ref_data["error_count"]
        warning_count = ref_data["warning_count"]

        is_valid = fatal_count == 0 and error_count == 0

        # Use error_count_min for fixtures with cascading errors
        error_count_min = None
        if error_count > 1 and severity == "ERROR":
            error_count_min = 1

        expected = {
            "fixture": f"invalid/{fixture_name}",
            "valid": is_valid,
            "messages": messages,
            "fatal_count": fatal_count,
            "error_count": error_count,
            "error_count_min": error_count_min,
            "warning_count": warning_count,
        }

    return expected


def create_valid_expected(name):
    """Create expected JSON for a valid fixture."""
    return {
        "fixture": f"valid/{name}",
        "valid": True,
        "messages": [],
        "fatal_count": 0,
        "error_count": 0,
        "error_count_min": None,
        "warning_count": 0,
    }


def main():
    # Create expected for valid EPUB 2
    os.makedirs(os.path.join(EXPECTED_DIR, "valid"), exist_ok=True)
    valid_epub2_path = os.path.join(EXPECTED_DIR, "valid", "minimal-epub2.json")
    with open(valid_epub2_path, "w") as f:
        json.dump(create_valid_expected("minimal-epub2"), f, indent=2)
        f.write("\n")
    print(f"Created: valid/minimal-epub2.json")

    # Create expected for each Level 2 invalid fixture
    os.makedirs(os.path.join(EXPECTED_DIR, "invalid"), exist_ok=True)
    created = 0
    skipped = 0

    for fixture_name, check_info in sorted(LEVEL2_CHECKS.items()):
        ref_data = read_reference("invalid", fixture_name)
        if ref_data is None:
            print(f"SKIP: {fixture_name} (no reference)")
            skipped += 1
            continue

        expected = create_expected(fixture_name, check_info, ref_data)

        out_path = os.path.join(EXPECTED_DIR, "invalid", f"{fixture_name}.json")
        with open(out_path, "w") as f:
            json.dump(expected, f, indent=2)
            f.write("\n")

        status = "valid=true (note)" if expected["valid"] else f"F={expected['fatal_count']} E={expected['error_count']} W={expected['warning_count']}"
        print(f"Created: invalid/{fixture_name}.json  [{status}]")
        created += 1

    print(f"\nDone: {created} created, {skipped} skipped")


if __name__ == "__main__":
    main()
