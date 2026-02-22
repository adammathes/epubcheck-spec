# Testing Strategy for EPUB Validator Implementations

This document explains how to use epubverify-spec to build and test an EPUB
validator in any programming language.

---

## Overview

epubverify-spec provides 169 checks across 4 maturity levels. Each check has:
- A fixture EPUB that triggers exactly one validation failure
- An expected JSON output describing what a correct validator should report
- A registry entry in `checks.json` with spec references and metadata

Your implementation reads `checks.json`, runs against the fixtures, and
compares output to `expected/`. Start at Level 1 and work up.

---

## Implementation Approach

### Phase 1: Output Format

Your validator must accept an `.epub` file path and produce JSON output matching
this schema:

```json
{
  "valid": false,
  "messages": [
    {
      "severity": "ERROR",
      "message": "Human-readable description of the problem"
    }
  ],
  "fatal_count": 0,
  "error_count": 1,
  "warning_count": 0
}
```

**Required fields:**
- `valid` — `true` if no FATAL or ERROR messages, `false` otherwise
- `messages` — array of message objects with at least `severity` and `message`
- `fatal_count`, `error_count`, `warning_count` — counts by severity

**Matching rules:**
- `valid` must match exactly
- Each expected message's `severity` must match one of your reported messages
- Each expected message's `message_pattern` (regex, case-insensitive) must match
  the `message` text of one of your reported messages
- You may report additional messages (e.g., from cascading errors) — extra
  messages are not penalized

### Phase 2: Level 1 (26 checks)

Start here. Level 1 covers the structural basics:
- OCF container (mimetype, container.xml, zip structure)
- OPF package document (metadata, manifest, spine)
- Basic cross-references (spine→manifest, manifest→files)
- Required metadata (dc:title, dc:identifier, dc:language, dcterms:modified)

These are the checks that catch broken output from tools like pandoc. A
validator that passes Level 1 is useful for catching common authoring mistakes.

```bash
# Run only Level 1 checks
LEVEL=1 make compare IMPL=./your-validator
```

### Phase 3: Level 2 (42 checks)

Level 2 adds full resource validation, content well-formedness, and EPUB 2:
- Manifest href validation (empty, fragment, traversal, encoding)
- Resource existence checks (images, stylesheets, scripts)
- Content document well-formedness (XHTML parsing)
- EPUB 2 basics (NCX, OPF 2.0 structure)
- Fallback chains

### Phase 4: Level 3 (55 checks)

Level 3 covers production-quality validation:
- CSS validation (syntax, @import, @font-face)
- Navigation document edge cases
- Fixed-layout support
- Encoding detection
- Image validation (corrupt files, media type mismatches)
- Advanced content checks (SVG, MathML, scripting)

### Phase 5: Level 4 (46 checks)

Full conformance includes:
- Accessibility checks (metadata, alt text, landmarks)
- Media overlays (SMIL structure, timing, audio references)
- Advanced OPF validation (prefix declarations, rendition properties)
- EPUB 2 edge cases (guide types, NCX depth, element ordering)

---

## Running Comparisons

### Basic comparison

```bash
make compare IMPL=./your-validator
```

### Level-filtered comparison

```bash
LEVEL=1 make compare IMPL=./your-validator
LEVEL=2 make compare IMPL=./your-validator
```

### Parity report

```bash
make parity IMPL=./your-validator
```

This generates a detailed report showing PASS/FAIL/SKIP per check with the
specific expected vs. actual output for failures.

---

## Common Implementation Pitfalls

### 1. Zip handling

EPUB files are ZIP archives with specific constraints:
- `mimetype` must be the first entry
- `mimetype` must be stored uncompressed (no deflation)
- `mimetype` content must be exactly `application/epub+zip` (no whitespace)

Many ZIP libraries add extra fields or don't guarantee entry order. Test against
`ocf-mimetype-*` fixtures early.

### 2. XML parsing

EPUB content documents are XHTML (strict XML). Common issues:
- HTML-only parsers accept malformed XML that EPUB validators must reject
- Namespace handling differences between XML parsers
- Entity resolution behavior varies between parsers

Use a strict XML parser, not an HTML parser.

### 3. Cascading errors

A single defect (e.g., missing manifest) can trigger multiple downstream errors.
The expected output uses `error_count_min` for these cases — your validator may
report more errors than `error_count`, but must report at least `error_count_min`.

### 4. Message matching

The comparison uses `message_pattern` as a case-insensitive regex. Your error
messages don't need to match epubcheck's exact wording — they just need to
contain the key term (e.g., "mimetype", "identifier", "spine").

### 5. EPUB 2 vs EPUB 3

The test suite includes both EPUB 2 and EPUB 3 fixtures. Check the `applies_to`
field in `checks.json` to know which version each check targets. Some checks
apply to both versions.

---

## Validation Against Real-World EPUBs

After passing the fixture suite, test against real-world EPUBs:

```bash
make corpus          # Download ~100 EPUBs from public sources
make analyze         # Run epubcheck and generate frequency analysis
```

The corpus includes EPUBs from:
- **Standard Ebooks** — high quality, should validate cleanly
- **Project Gutenberg** — auto-generated, common metadata warnings
- **Feedbooks** — different toolchain, varied issues
- **Internet Archive** — diverse quality, widest variety of problems
- **IDPF samples** — reference implementations of EPUB features
- **W3C test suite** — conformance test documents

Use the frequency analysis to prioritize which real-world issues to handle
beyond the fixture suite.

---

## Tracking Implementation Progress

Register your implementation in `checks.json` by updating the `implemented`
field on each check you support:

```json
{
  "id": "OCF-001",
  "implemented": {
    "epubverify-go": true,
    "your-tool": true
  }
}
```

This allows the suite to generate parity reports comparing implementations.

---

## Known Divergences from epubcheck

29 checks in the suite represent spec violations that epubcheck 5.3.0 does not
flag. See [epubcheck-divergences.md](epubcheck-divergences.md) for the full
list. For these checks, the `expected/` output shows `valid: true` (matching
epubcheck), but a spec-compliant implementation should flag them.

The most notable category is **accessibility** (ACC-001 to ACC-010): epubcheck
requires the `--profile` flag to enforce these, but the spec requires them
unconditionally.
