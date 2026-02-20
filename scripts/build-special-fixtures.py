#!/usr/bin/env python3
"""Build fixtures requiring non-standard zip manipulation."""
import zipfile, os, struct

FIXTURES_SRC = "fixtures/src"
FIXTURES_OUT = "fixtures/epub"
# Use minimal-epub3 as the base for all special fixtures
BASE = os.path.join(FIXTURES_SRC, "valid", "minimal-epub3")


def collect_files(src_dir, exclude=None):
    """Walk src_dir, yield (arcname, filepath) pairs."""
    for root, dirs, files in os.walk(src_dir):
        dirs.sort()
        for f in sorted(files):
            arcname = os.path.relpath(os.path.join(root, f), src_dir)
            if exclude and arcname in exclude:
                continue
            yield arcname, os.path.join(root, f)


def build_mimetype_not_first():
    """mimetype exists but is not the first entry in the zip."""
    out = os.path.join(FIXTURES_OUT, "invalid", "ocf-mimetype-not-first.epub")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with zipfile.ZipFile(out, 'w') as zf:
        # Write other files first
        for arcname, filepath in collect_files(BASE, exclude={"mimetype"}):
            zf.write(filepath, arcname, compress_type=zipfile.ZIP_DEFLATED)
        # Then mimetype last (stored, but not first)
        zf.write(os.path.join(BASE, "mimetype"), "mimetype",
                 compress_type=zipfile.ZIP_STORED)
    print(f"  Built: {out}")


def build_mimetype_compressed():
    """mimetype is first but uses DEFLATED instead of STORED."""
    out = os.path.join(FIXTURES_OUT, "invalid", "ocf-mimetype-compressed.epub")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with zipfile.ZipFile(out, 'w') as zf:
        zf.write(os.path.join(BASE, "mimetype"), "mimetype",
                 compress_type=zipfile.ZIP_DEFLATED)
        for arcname, filepath in collect_files(BASE, exclude={"mimetype"}):
            zf.write(filepath, arcname, compress_type=zipfile.ZIP_DEFLATED)
    print(f"  Built: {out}")


def build_mimetype_extra_field():
    """mimetype entry has a non-empty extra field in its local header."""
    out = os.path.join(FIXTURES_OUT, "invalid", "ocf-mimetype-extra-field.epub")
    os.makedirs(os.path.dirname(out), exist_ok=True)

    # Build a normal epub first
    tmp = out + ".tmp"
    with zipfile.ZipFile(tmp, 'w') as zf:
        zf.write(os.path.join(BASE, "mimetype"), "mimetype",
                 compress_type=zipfile.ZIP_STORED)
        for arcname, filepath in collect_files(BASE, exclude={"mimetype"}):
            zf.write(filepath, arcname, compress_type=zipfile.ZIP_DEFLATED)

    # Now patch the local file header to add an extra field
    with open(tmp, 'rb') as f:
        data = bytearray(f.read())

    # The local file header starts at offset 0 for the first entry
    # Local file header signature = 0x04034b50
    assert data[0:4] == b'PK\x03\x04', "Expected local file header at offset 0"

    # Extra field length is at offset 28-29 (2 bytes, little-endian)
    # Currently should be 0
    extra_len = struct.unpack_from('<H', data, 28)[0]

    # We need to inject an extra field. The extra field for the mimetype entry.
    # Extra field: a simple unknown tag with some data
    extra_data = struct.pack('<HH', 0xCAFE, 4) + b'\x00\x00\x00\x00'  # 8 bytes total

    # File name length at offset 26
    fname_len = struct.unpack_from('<H', data, 26)[0]

    # Insert point: after local header (30 bytes) + filename + existing extra
    insert_at = 30 + fname_len + extra_len

    # Update extra field length
    new_extra_len = extra_len + len(extra_data)
    struct.pack_into('<H', data, 28, new_extra_len)

    # Insert the extra data
    data[insert_at:insert_at] = extra_data

    with open(out, 'wb') as f:
        f.write(data)

    os.remove(tmp)
    print(f"  Built: {out}")


if __name__ == "__main__":
    build_mimetype_not_first()
    build_mimetype_compressed()
    build_mimetype_extra_field()
    print("Special fixtures built.")
