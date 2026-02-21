#!/usr/bin/env python3
"""Create Level 4 fixture source directories.

Level 4 — "Full conformance" (~170+ checks total, ~46 new)
Covers: Advanced OPF/metadata, deep content validation, accessibility,
media overlays, container edge cases, advanced EPUB 2.
"""
import os
import shutil

FIXTURES_SRC = "fixtures/src"
BASE_EPUB3 = os.path.join(FIXTURES_SRC, "valid", "minimal-epub3")
BASE_EPUB2 = os.path.join(FIXTURES_SRC, "valid", "minimal-epub2")

# Default file contents for minimal-epub3
DEFAULTS = {
    "mimetype": "application/epub+zip",
    "META-INF/container.xml": """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>""",
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
  </spine>
</package>""",
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
</body>
</html>""",
    "OEBPS/chapter1.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 1</title></head>
<body>
  <h1>Chapter 1</h1>
  <p>Hello, world.</p>
</body>
</html>""",
}

EPUB2_DEFAULTS = {
    "mimetype": "application/epub+zip",
    "META-INF/container.xml": DEFAULTS["META-INF/container.xml"],
    "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
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
</package>""",
    "OEBPS/toc.ncx": """<?xml version="1.0" encoding="UTF-8"?>
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
</ncx>""",
    "OEBPS/chapter1.xhtml": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 1</title></head>
<body>
  <h1>Chapter 1</h1>
  <p>Hello, world.</p>
</body>
</html>""",
}


def create_fixture(name, files, base="epub3"):
    """Create fixture directory with given files merged over defaults."""
    defaults = DEFAULTS if base == "epub3" else EPUB2_DEFAULTS
    fixture_dir = os.path.join(FIXTURES_SRC, "invalid", name)
    if os.path.exists(fixture_dir):
        shutil.rmtree(fixture_dir)

    merged = dict(defaults)
    merged.update(files)

    for filepath, content in merged.items():
        full_path = os.path.join(fixture_dir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        if isinstance(content, bytes):
            with open(full_path, 'wb') as f:
                f.write(content)
        else:
            with open(full_path, 'w', newline='') as f:
                f.write(content)

    print(f"  Created: {fixture_dir}")
    return fixture_dir


def create_valid_fixture(name, files, base="epub3"):
    """Create valid fixture directory."""
    defaults = DEFAULTS if base == "epub3" else EPUB2_DEFAULTS
    fixture_dir = os.path.join(FIXTURES_SRC, "valid", name)
    if os.path.exists(fixture_dir):
        shutil.rmtree(fixture_dir)

    merged = dict(defaults)
    merged.update(files)

    for filepath, content in merged.items():
        full_path = os.path.join(fixture_dir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        if isinstance(content, bytes):
            with open(full_path, 'wb') as f:
                f.write(content)
        else:
            with open(full_path, 'w', newline='') as f:
                f.write(content)

    print(f"  Created: {fixture_dir}")
    return fixture_dir


# ============================================================================
# BATCH 1: Advanced OPF & Metadata Checks
# ============================================================================
print("\n=== Batch 1: Advanced OPF & Metadata ===")

# OPF-035: page-progression-direction with invalid value
create_fixture("opf-ppd-invalid", {
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
  <spine page-progression-direction="up">
    <itemref idref="chapter1"/>
  </spine>
</package>""",
})

# OPF-036: dc:date with invalid format
create_fixture("opf-dc-date-invalid", {
    "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <dc:date>not-a-date</dc:date>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>""",
})

# OPF-037: meta refines attribute references nonexistent id
create_fixture("opf-meta-refines-bad-target", {
    "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
    <meta refines="#nonexistent-id" property="title-type">main</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>""",
})

# OPF-038: spine linear attribute with invalid value
create_fixture("opf-spine-linear-invalid", {
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
    <itemref idref="chapter1" linear="maybe"/>
  </spine>
</package>""",
})

# OPF-039: guide element in EPUB 3 (deprecated)
create_fixture("opf-epub3-guide", {
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
  </spine>
  <guide>
    <reference type="toc" title="Table of Contents" href="nav.xhtml"/>
  </guide>
</package>""",
})

# OPF-040: dc:identifier UUID with invalid format
create_fixture("opf-uuid-invalid", {
    "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:not-a-valid-uuid</dc:identifier>
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
</package>""",
})

# OPF-041: spine where all items are non-linear
create_fixture("opf-spine-all-nonlinear", {
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
    <itemref idref="chapter1" linear="no"/>
  </spine>
</package>""",
})

# OPF-042: rendition:flow with invalid value
create_fixture("opf-rendition-flow-invalid", {
    "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345678-1234-1234-1234-123456789012</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
    <meta property="rendition:flow">invalid-flow</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>""",
})

# OPF-043: prefix attribute with invalid syntax
create_fixture("opf-prefix-invalid", {
    "OEBPS/content.opf": """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid"
         prefix="bad prefix syntax :::">
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
</package>""",
})

# OPF-044: media-overlay attribute referencing nonexistent manifest item
create_fixture("opf-media-overlay-bad-ref", {
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
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml" media-overlay="nonexistent-overlay"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>""",
})


print(f"\nDone! Created Batch 1 (Advanced OPF & Metadata) fixtures.")
