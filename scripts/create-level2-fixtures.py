#!/usr/bin/env python3
"""Create all Level 2 fixture source directories.

Each fixture is based on minimal-epub3 with exactly ONE defect introduced.
"""
import os
import shutil

FIXTURES_SRC = "fixtures/src"
BASE = os.path.join(FIXTURES_SRC, "valid", "minimal-epub3")
INVALID_DIR = os.path.join(FIXTURES_SRC, "invalid")

# --- Base file contents (from minimal-epub3) ---

MIMETYPE = "application/epub+zip"

CONTAINER_XML = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""

CONTENT_OPF = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>"""

NAV_XHTML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Navigation</title></head>
<body>
  <nav epub:type="toc">
    <h1>Table of Contents</h1>
    <ol>
      <li><a href="chapter1.xhtml">Chapter 1</a></li>
    </ol>
  </nav>
</body>
</html>"""

CHAPTER1_XHTML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 1</title></head>
<body>
  <h1>Chapter 1</h1>
  <p>Hello, world.</p>
</body>
</html>"""


def create_fixture(name, files):
    """Create a fixture directory with the given files.

    files is a dict of {relative_path: content}.
    Always includes mimetype and META-INF/container.xml unless overridden.
    """
    fixture_dir = os.path.join(INVALID_DIR, name)
    if os.path.exists(fixture_dir):
        shutil.rmtree(fixture_dir)

    # Default files
    defaults = {
        "mimetype": MIMETYPE,
        "META-INF/container.xml": CONTAINER_XML,
        "OEBPS/content.opf": CONTENT_OPF,
        "OEBPS/nav.xhtml": NAV_XHTML,
        "OEBPS/chapter1.xhtml": CHAPTER1_XHTML,
    }
    defaults.update(files)

    for relpath, content in defaults.items():
        filepath = os.path.join(fixture_dir, relpath)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        if isinstance(content, bytes):
            with open(filepath, 'wb') as f:
                f.write(content)
        else:
            with open(filepath, 'w', newline='') as f:
                f.write(content)

    print(f"  Created: {name}")


def create_valid_fixture(name, files):
    """Create a valid fixture directory."""
    fixture_dir = os.path.join(FIXTURES_SRC, "valid", name)
    if os.path.exists(fixture_dir):
        shutil.rmtree(fixture_dir)

    for relpath, content in files.items():
        filepath = os.path.join(fixture_dir, relpath)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        if isinstance(content, bytes):
            with open(filepath, 'wb') as f:
                f.write(content)
        else:
            with open(filepath, 'w', newline='') as f:
                f.write(content)

    print(f"  Created valid: {name}")


# ============================================================
# OPF STRUCTURAL CHECKS
# ============================================================

def create_opf_malformed_xml():
    """OPF-011: OPF file must be well-formed XML."""
    create_fixture("opf-malformed-xml", {
        "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
  <!-- missing closing tags -->"""
    })


def create_opf_missing_metadata():
    """OPF-012: Package must have metadata element."""
    create_fixture("opf-missing-metadata", {
        "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>"""
    })


def create_opf_missing_manifest():
    """OPF-013: Package must have manifest element."""
    create_fixture("opf-missing-manifest", {
        "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
  </metadata>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>"""
    })


def create_opf_missing_spine():
    """OPF-014: Package must have spine element."""
    create_fixture("opf-missing-spine", {
        "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
</package>"""
    })


def create_opf_wrong_version():
    """OPF-015: Package version must be valid ("2.0" or "3.0")."""
    create_fixture("opf-wrong-version", {
        "OEBPS/content.opf": CONTENT_OPF.replace('version="3.0"', 'version="4.0"')
    })


def create_opf_duplicate_manifest_href():
    """OPF-016: Manifest must not have duplicate hrefs."""
    create_fixture("opf-duplicate-manifest-href", {
        "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
    <item id="chapter1dup" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>"""
    })


def create_opf_duplicate_spine_idref():
    """OPF-017: Spine should not have duplicate idrefs."""
    create_fixture("opf-duplicate-spine-idref", {
        "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
    <itemref idref="chapter1"/>
  </spine>
</package>"""
    })


def create_opf_manifest_item_no_id():
    """OPF-018: Each manifest item must have an id attribute."""
    create_fixture("opf-manifest-item-no-id", {
        "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>"""
    })


def create_opf_dcterms_modified_invalid():
    """OPF-019: dcterms:modified must have valid date format."""
    create_fixture("opf-dcterms-modified-invalid", {
        "OEBPS/content.opf": CONTENT_OPF.replace(
            "2025-01-01T00:00:00Z", "not-a-valid-date"
        )
    })


def create_opf_dc_language_invalid():
    """OPF-020: dc:language must be a valid BCP 47 language tag."""
    create_fixture("opf-dc-language-invalid", {
        "OEBPS/content.opf": CONTENT_OPF.replace(
            "<dc:language>en</dc:language>",
            "<dc:language>invalidlanguagetag123</dc:language>"
        )
    })


# ============================================================
# OPF FALLBACK / MEDIA TYPE CHECKS
# ============================================================

def create_opf_fallback_ref_missing():
    """OPF-021: Fallback attribute must reference an existing manifest item."""
    create_fixture("opf-fallback-ref-missing", {
        "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml" fallback="nonexistent"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>"""
    })


def create_opf_fallback_cycle():
    """OPF-022: Fallback chains must not be circular."""
    create_fixture("opf-fallback-cycle", {
        "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml" fallback="chapter2"/>
    <item id="chapter2" href="chapter2.xhtml" media-type="application/xhtml+xml" fallback="chapter1"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>""",
        "OEBPS/chapter2.xhtml": CHAPTER1_XHTML.replace("Chapter 1", "Chapter 2"),
    })


def create_opf_spine_non_content_doc():
    """OPF-023: Spine items must be content documents (XHTML or SVG)."""
    # Put a CSS file in the spine
    create_fixture("opf-spine-non-content-doc", {
        "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
    <item id="style" href="style.css" media-type="text/css"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
    <itemref idref="style"/>
  </spine>
</package>""",
        "OEBPS/style.css": "body { margin: 0; }",
    })


def create_opf_media_type_mismatch():
    """OPF-024: Declared media-type should match actual file content."""
    # Declare chapter1.xhtml as image/png
    create_fixture("opf-media-type-mismatch", {
        "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="image/png"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>"""
    })


def create_opf_cover_image_not_image():
    """OPF-025: cover-image property must be on an image item."""
    create_fixture("opf-cover-image-not-image", {
        "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml" properties="cover-image"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>"""
    })


def create_opf_multiple_nav():
    """OPF-026: Only one manifest item should have properties="nav"."""
    create_fixture("opf-multiple-nav", {
        "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="nav2" href="nav2.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>""",
        "OEBPS/nav2.xhtml": NAV_XHTML,
    })


# ============================================================
# RSC RESOURCE REFERENCE CHECKS
# ============================================================

def create_content_fragment_id_missing():
    """RSC-003: Fragment identifiers must resolve to valid targets."""
    create_fixture("content-fragment-id-missing", {
        "OEBPS/chapter1.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 1</title></head>
<body>
  <h1>Chapter 1</h1>
  <p><a href="chapter1.xhtml#nonexistent">Link to nowhere</a></p>
</body>
</html>""",
    })


def create_content_remote_resource():
    """RSC-004: Remote resources are not allowed (with few exceptions)."""
    create_fixture("content-remote-resource", {
        "OEBPS/chapter1.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 1</title></head>
<body>
  <h1>Chapter 1</h1>
  <p><img src="http://example.com/image.png" alt="remote"/></p>
</body>
</html>""",
    })


def create_content_css_file_missing():
    """RSC-005: CSS file declared in manifest but missing from zip."""
    create_fixture("content-css-file-missing", {
        "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
    <item id="style" href="style.css" media-type="text/css"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>""",
        # Note: style.css is NOT included in the fixture files
    })


def create_content_resource_not_in_manifest():
    """RSC-006: Resources used in content must be declared in manifest."""
    create_fixture("content-resource-not-in-manifest", {
        "OEBPS/chapter1.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Chapter 1</title>
  <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
  <h1>Chapter 1</h1>
  <p>Hello, world.</p>
</body>
</html>""",
        # CSS file exists but is NOT in the manifest
        "OEBPS/style.css": "body { margin: 0; }",
    })


def create_content_font_file_missing():
    """RSC-007: Font file declared in manifest but missing from zip."""
    create_fixture("content-font-file-missing", {
        "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
    <item id="font1" href="fonts/missing.woff2" media-type="font/woff2"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>""",
        # Note: fonts/missing.woff2 is NOT included
    })


def create_content_remote_stylesheet():
    """RSC-008: Remote CSS stylesheet not allowed."""
    create_fixture("content-remote-stylesheet", {
        "OEBPS/chapter1.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Chapter 1</title>
  <link rel="stylesheet" type="text/css" href="http://example.com/style.css"/>
</head>
<body>
  <h1>Chapter 1</h1>
  <p>Hello, world.</p>
</body>
</html>""",
    })


# ============================================================
# HTM CONTENT DOCUMENT CHECKS
# ============================================================

def create_content_no_title():
    """HTM-002: XHTML content documents must have a title element."""
    create_fixture("content-no-title", {
        "OEBPS/chapter1.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head></head>
<body>
  <h1>Chapter 1</h1>
  <p>Hello, world.</p>
</body>
</html>""",
    })


def create_content_empty_href():
    """HTM-003: href attributes must not be empty."""
    create_fixture("content-empty-href", {
        "OEBPS/chapter1.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 1</title></head>
<body>
  <h1>Chapter 1</h1>
  <p><a href="">Empty link</a></p>
</body>
</html>""",
    })


def create_content_obsolete_element():
    """HTM-004: Content documents must not use obsolete HTML elements."""
    create_fixture("content-obsolete-element", {
        "OEBPS/chapter1.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 1</title></head>
<body>
  <h1>Chapter 1</h1>
  <center><p>This uses an obsolete element.</p></center>
</body>
</html>""",
    })


def create_content_scripted_undeclared():
    """HTM-005: Scripted content must declare scripted property in manifest."""
    create_fixture("content-scripted-undeclared", {
        "OEBPS/chapter1.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 1</title></head>
<body>
  <h1>Chapter 1</h1>
  <p>Hello, world.</p>
  <script type="text/javascript">alert('hello');</script>
</body>
</html>""",
    })


def create_content_svg_undeclared():
    """HTM-006: Inline SVG must declare svg property in manifest."""
    create_fixture("content-svg-undeclared", {
        "OEBPS/chapter1.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 1</title></head>
<body>
  <h1>Chapter 1</h1>
  <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
    <circle cx="50" cy="50" r="40" fill="red"/>
  </svg>
</body>
</html>""",
    })


def create_content_mathml_undeclared():
    """HTM-007: MathML content must declare mathml property in manifest."""
    create_fixture("content-mathml-undeclared", {
        "OEBPS/chapter1.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 1</title></head>
<body>
  <h1>Chapter 1</h1>
  <math xmlns="http://www.w3.org/1998/Math/MathML">
    <mrow><mi>x</mi><mo>=</mo><mn>2</mn></mrow>
  </math>
</body>
</html>""",
    })


def create_content_fxl_no_viewport():
    """HTM-008: Fixed-layout documents must have a viewport meta tag."""
    create_fixture("content-fxl-no-viewport", {
        "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
    <meta property="rendition:layout">pre-paginated</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>""",
        # chapter1.xhtml has NO viewport meta
    })


def create_content_fxl_invalid_viewport():
    """HTM-009: Fixed-layout viewport meta must have valid syntax."""
    create_fixture("content-fxl-invalid-viewport", {
        "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
    <meta property="rendition:layout">pre-paginated</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>""",
        "OEBPS/chapter1.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Chapter 1</title>
  <meta name="viewport" content="invalid-viewport-value"/>
</head>
<body>
  <h1>Chapter 1</h1>
  <p>Hello, world.</p>
</body>
</html>""",
    })


def create_content_base_element():
    """HTM-010: base element is not allowed in EPUB content documents."""
    create_fixture("content-base-element", {
        "OEBPS/chapter1.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Chapter 1</title>
  <base href="http://example.com/"/>
</head>
<body>
  <h1>Chapter 1</h1>
  <p>Hello, world.</p>
</body>
</html>""",
    })


def create_content_wrong_doctype():
    """HTM-011: DOCTYPE must be correct for XHTML content docs."""
    create_fixture("content-wrong-doctype", {
        "OEBPS/chapter1.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 1</title></head>
<body>
  <h1>Chapter 1</h1>
  <p>Hello, world.</p>
</body>
</html>""",
    })


def create_content_wrong_namespace():
    """HTM-012: html element must use the XHTML namespace."""
    # Use a wrong namespace — this should cause XML parsing issues
    create_fixture("content-wrong-namespace", {
        "OEBPS/chapter1.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.example.com/wrong-namespace">
<head><title>Chapter 1</title></head>
<body>
  <h1>Chapter 1</h1>
  <p>Hello, world.</p>
</body>
</html>""",
    })


# ============================================================
# NAV NAVIGATION CHECKS
# ============================================================

def create_nav_toc_broken_link():
    """NAV-003: TOC nav links must reference existing resources."""
    create_fixture("nav-toc-broken-link", {
        "OEBPS/nav.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Navigation</title></head>
<body>
  <nav epub:type="toc">
    <h1>Table of Contents</h1>
    <ol>
      <li><a href="chapter1.xhtml">Chapter 1</a></li>
      <li><a href="nonexistent.xhtml">Missing Chapter</a></li>
    </ol>
  </nav>
</body>
</html>""",
    })


def create_nav_toc_empty_link():
    """NAV-004: Navigation links must have text content."""
    create_fixture("nav-toc-empty-link", {
        "OEBPS/nav.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Navigation</title></head>
<body>
  <nav epub:type="toc">
    <h1>Table of Contents</h1>
    <ol>
      <li><a href="chapter1.xhtml"></a></li>
    </ol>
  </nav>
</body>
</html>""",
    })


def create_nav_multiple_toc():
    """NAV-005: Navigation document must have exactly one toc nav."""
    create_fixture("nav-multiple-toc", {
        "OEBPS/nav.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Navigation</title></head>
<body>
  <nav epub:type="toc">
    <h1>Table of Contents</h1>
    <ol>
      <li><a href="chapter1.xhtml">Chapter 1</a></li>
    </ol>
  </nav>
  <nav epub:type="toc">
    <h1>Another TOC</h1>
    <ol>
      <li><a href="chapter1.xhtml">Chapter 1 again</a></li>
    </ol>
  </nav>
</body>
</html>""",
    })


def create_nav_landmarks_broken():
    """NAV-006: Landmarks nav links must resolve to valid targets."""
    create_fixture("nav-landmarks-broken", {
        "OEBPS/nav.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Navigation</title></head>
<body>
  <nav epub:type="toc">
    <h1>Table of Contents</h1>
    <ol>
      <li><a href="chapter1.xhtml">Chapter 1</a></li>
    </ol>
  </nav>
  <nav epub:type="landmarks">
    <h2>Landmarks</h2>
    <ol>
      <li><a epub:type="bodymatter" href="nonexistent.xhtml">Start</a></li>
    </ol>
  </nav>
</body>
</html>""",
    })


def create_nav_page_list_broken():
    """NAV-007: Page list references must resolve to valid targets."""
    create_fixture("nav-page-list-broken", {
        "OEBPS/nav.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Navigation</title></head>
<body>
  <nav epub:type="toc">
    <h1>Table of Contents</h1>
    <ol>
      <li><a href="chapter1.xhtml">Chapter 1</a></li>
    </ol>
  </nav>
  <nav epub:type="page-list">
    <h2>Pages</h2>
    <ol>
      <li><a href="nonexistent.xhtml#p1">1</a></li>
    </ol>
  </nav>
</body>
</html>""",
    })


# ============================================================
# EPUB 2 CHECKS
# ============================================================

EPUB2_OPF = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine toc="ncx">
    <itemref idref="chapter1"/>
  </spine>
</package>"""

EPUB2_NCX = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:12345678-1234-1234-1234-123456789012"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>Test Book</text></docTitle>
  <navMap>
    <navPoint id="np-1" playOrder="1">
      <navLabel><text>Chapter 1</text></navLabel>
      <content src="chapter1.xhtml"/>
    </navPoint>
  </navMap>
</ncx>"""

EPUB2_CHAPTER = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 1</title></head>
<body>
  <h1>Chapter 1</h1>
  <p>Hello, world.</p>
</body>
</html>"""

EPUB2_CONTAINER = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""


def create_valid_epub2():
    """Minimal valid EPUB 2 fixture."""
    create_valid_fixture("minimal-epub2", {
        "mimetype": MIMETYPE,
        "META-INF/container.xml": EPUB2_CONTAINER,
        "OEBPS/content.opf": EPUB2_OPF,
        "OEBPS/toc.ncx": EPUB2_NCX,
        "OEBPS/chapter1.xhtml": EPUB2_CHAPTER,
    })


def create_epub2_ncx_missing():
    """E2-001: EPUB 2 must have NCX file."""
    create_fixture("epub2-ncx-missing", {
        "OEBPS/content.opf": EPUB2_OPF,
        "OEBPS/chapter1.xhtml": EPUB2_CHAPTER,
        # NCX file is NOT included
    })
    # Remove nav.xhtml since this is EPUB 2
    nav_path = os.path.join(INVALID_DIR, "epub2-ncx-missing", "OEBPS", "nav.xhtml")
    if os.path.exists(nav_path):
        os.remove(nav_path)


def create_epub2_ncx_malformed():
    """E2-002: NCX must be well-formed XML."""
    create_fixture("epub2-ncx-malformed", {
        "OEBPS/content.opf": EPUB2_OPF,
        "OEBPS/toc.ncx": """<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:12345678-1234-1234-1234-123456789012"/>
  </head>
  <!-- broken: missing closing tags""",
        "OEBPS/chapter1.xhtml": EPUB2_CHAPTER,
    })
    # Remove nav.xhtml since this is EPUB 2
    nav_path = os.path.join(INVALID_DIR, "epub2-ncx-malformed", "OEBPS", "nav.xhtml")
    if os.path.exists(nav_path):
        os.remove(nav_path)


def create_epub2_ncx_no_navmap():
    """E2-003: NCX must have navMap element."""
    create_fixture("epub2-ncx-no-navmap", {
        "OEBPS/content.opf": EPUB2_OPF,
        "OEBPS/toc.ncx": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:12345678-1234-1234-1234-123456789012"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>Test Book</text></docTitle>
</ncx>""",
        "OEBPS/chapter1.xhtml": EPUB2_CHAPTER,
    })
    # Remove nav.xhtml since this is EPUB 2
    nav_path = os.path.join(INVALID_DIR, "epub2-ncx-no-navmap", "OEBPS", "nav.xhtml")
    if os.path.exists(nav_path):
        os.remove(nav_path)


def create_epub2_spine_no_toc():
    """E2-004: EPUB 2 spine must have toc attribute referencing NCX."""
    opf_no_toc = EPUB2_OPF.replace(' toc="ncx"', '')
    create_fixture("epub2-spine-no-toc", {
        "OEBPS/content.opf": opf_no_toc,
        "OEBPS/toc.ncx": EPUB2_NCX,
        "OEBPS/chapter1.xhtml": EPUB2_CHAPTER,
    })
    # Remove nav.xhtml since this is EPUB 2
    nav_path = os.path.join(INVALID_DIR, "epub2-spine-no-toc", "OEBPS", "nav.xhtml")
    if os.path.exists(nav_path):
        os.remove(nav_path)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("Creating Level 2 fixture source directories...")
    print()

    # OPF Structural
    print("=== OPF Structural ===")
    create_opf_malformed_xml()
    create_opf_missing_metadata()
    create_opf_missing_manifest()
    create_opf_missing_spine()
    create_opf_wrong_version()
    create_opf_duplicate_manifest_href()
    create_opf_duplicate_spine_idref()
    create_opf_manifest_item_no_id()
    create_opf_dcterms_modified_invalid()
    create_opf_dc_language_invalid()

    # OPF Fallback/Media
    print("\n=== OPF Fallback/Media ===")
    create_opf_fallback_ref_missing()
    create_opf_fallback_cycle()
    create_opf_spine_non_content_doc()
    create_opf_media_type_mismatch()
    create_opf_cover_image_not_image()
    create_opf_multiple_nav()

    # RSC Resources
    print("\n=== RSC Resources ===")
    create_content_fragment_id_missing()
    create_content_remote_resource()
    create_content_css_file_missing()
    create_content_resource_not_in_manifest()
    create_content_font_file_missing()
    create_content_remote_stylesheet()

    # HTM Content
    print("\n=== HTM Content ===")
    create_content_no_title()
    create_content_empty_href()
    create_content_obsolete_element()
    create_content_scripted_undeclared()
    create_content_svg_undeclared()
    create_content_mathml_undeclared()
    create_content_fxl_no_viewport()
    create_content_fxl_invalid_viewport()
    create_content_base_element()
    create_content_wrong_doctype()
    create_content_wrong_namespace()

    # NAV Navigation
    print("\n=== NAV Navigation ===")
    create_nav_toc_broken_link()
    create_nav_toc_empty_link()
    create_nav_multiple_toc()
    create_nav_landmarks_broken()
    create_nav_page_list_broken()

    # EPUB 2
    print("\n=== EPUB 2 ===")
    create_valid_epub2()
    create_epub2_ncx_missing()
    create_epub2_ncx_malformed()
    create_epub2_ncx_no_navmap()
    create_epub2_spine_no_toc()

    print()
    print("Done! Created all Level 2 fixture source directories.")
