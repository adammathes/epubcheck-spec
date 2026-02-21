# Level 4 Plan: Full Conformance

Level 4 brings epubcheck-spec from 123 checks (Levels 1-3) toward full conformance
with the EPUB 3.3 specification. This document defines the checks, batches, and
implementation order.

## Overview

| Property | Value |
|----------|-------|
| Target checks | ~50 new (173+ total) |
| New categories | ACC (Accessibility) |
| Expanded categories | OPF, HTM, MED, PKG, NCX |
| New valid fixtures | 1 (epub3-with-media-overlay) |
| Implementation | 5 batches, committed sequentially |

## Batch Order

Batches are ordered by concreteness and testability — start with checks that
produce clear epubcheck errors, then move to more nuanced areas.

1. **Advanced OPF & Metadata** — Well-understood error patterns
2. **Advanced Content Documents** — Deep HTML5/SVG/content validation
3. **Accessibility** — ACC category (mostly USAGE-level in epubcheck)
4. **Media Overlays** — SMIL media overlay documents
5. **Container & EPUB 2 Edge Cases** — Remaining coverage gaps

---

## Batch 1: Advanced OPF & Metadata (10 checks)

| Check ID | Name | Fixture | epubcheck ID | Severity | Description |
|----------|------|---------|-------------|----------|-------------|
| OPF-035 | page-progression-direction-valid | opf-ppd-invalid | RSC-005 | ERROR | page-progression-direction must be ltr, rtl, or default |
| OPF-036 | dc-date-valid-format | opf-dc-date-invalid | OPF-054 | WARNING | dc:date should be a valid date format |
| OPF-037 | meta-refines-target-exists | opf-meta-refines-bad-target | OPF-025 | ERROR | meta refines must reference existing ID |
| OPF-038 | spine-linear-valid | opf-spine-linear-invalid | RSC-005 | ERROR | spine itemref linear attribute must be yes or no |
| OPF-039 | epub3-guide-deprecated | opf-epub3-guide | OPF-031 | WARNING | guide element is deprecated in EPUB 3 |
| OPF-040 | uuid-format-valid | opf-uuid-invalid | OPF-085 | WARNING | dc:identifier UUID must be valid format |
| OPF-041 | spine-all-nonlinear | opf-spine-all-nonlinear | OPF-058 | ERROR | spine must contain at least one linear itemref |
| OPF-042 | rendition-flow-valid | opf-rendition-flow-invalid | RSC-005 | ERROR | rendition:flow must be scrolled-doc, scrolled-continuous, paginated, or auto |
| OPF-043 | prefix-declaration-valid | opf-prefix-invalid | OPF-025 | ERROR | prefix attribute must use valid syntax |
| OPF-044 | media-overlay-ref-exists | opf-media-overlay-bad-ref | OPF-050 | ERROR | media-overlay attribute must reference existing manifest item |

**Spec refs:** `#sec-spine-elem`, `#sec-package-doc`, `#sec-opf-dcidentifier`,
`#sec-metadata-elem`, `#sec-fixed-layouts`

---

## Batch 2: Advanced Content Documents (10 checks)

| Check ID | Name | Fixture | epubcheck ID | Severity | Description |
|----------|------|---------|-------------|----------|-------------|
| HTM-024 | head-element-present | content-no-head | RSC-005 | ERROR | Content documents must have a head element |
| HTM-025 | no-embed-element | content-embed-element | RSC-005 | ERROR | embed element not allowed in EPUB content |
| HTM-026 | lang-xml-lang-match | content-lang-mismatch | HTM-048 | ERROR | lang and xml:lang attributes must match |
| HTM-027 | video-poster-exists | content-video-poster-missing | RSC-007 | ERROR | video poster attribute must reference existing file |
| HTM-028 | audio-src-exists | content-audio-missing | RSC-001 | ERROR | audio src must reference existing file |
| HTM-029 | svg-content-valid | content-svg-malformed | RSC-005 | ERROR | Inline SVG must be well-formed |
| HTM-030 | img-src-not-empty | content-img-empty-src | RSC-007 | ERROR | img src must not be empty |
| HTM-031 | ssml-namespace-valid | content-ssml-invalid-ns | RSC-005 | ERROR | SSML namespace must be correct if used |
| HTM-032 | style-element-valid | content-style-syntax-error | CSS-008 | ERROR | Inline style element must contain valid CSS |
| HTM-033 | no-rdf-in-content | content-rdf-element | HTM-052 | ERROR | RDF elements not allowed in EPUB content |

**Spec refs:** `#sec-xhtml`, `#sec-svg`, `#sec-css`, `#sec-scripted`

---

## Batch 3: Accessibility (10 checks)

| Check ID | Name | Fixture | epubcheck ID | Severity | Description |
|----------|------|---------|-------------|----------|-------------|
| ACC-001 | accessibility-metadata-present | acc-no-a11y-metadata | ACC-002 | USAGE | Accessibility metadata should be present |
| ACC-002 | img-alt-text-present | acc-img-no-alt | ACC-005 | USAGE | img elements should have alt attribute |
| ACC-003 | html-lang-present | acc-no-lang | ACC-004 | USAGE | html element should have lang attribute |
| ACC-004 | page-source-has-page-list | acc-dc-source-no-page-list | ACC-007 | USAGE | page-list nav required when dc:source present |
| ACC-005 | accessmode-metadata | acc-no-accessmode | ACC-002 | USAGE | schema:accessMode metadata should be present |
| ACC-006 | access-sufficient-metadata | acc-no-access-sufficient | ACC-002 | USAGE | schema:accessModeSufficient should be present |
| ACC-007 | accessibility-summary | acc-no-summary | ACC-002 | USAGE | schema:accessibilitySummary should be present |
| ACC-008 | accessibility-feature | acc-no-feature | ACC-002 | USAGE | schema:accessibilityFeature should be present |
| ACC-009 | accessibility-hazard | acc-no-hazard | ACC-002 | USAGE | schema:accessibilityHazard should be present |
| ACC-010 | landmarks-nav-present | acc-no-landmarks | ACC-003 | USAGE | landmarks nav element should be present |

**Note:** Most ACC checks in epubcheck report at USAGE severity, meaning the EPUB
is technically valid but lacks accessibility best practices. The expected output
format will use `"severity": "USAGE"` for these.

**Spec refs:** EPUB Accessibility 1.1, WCAG 2.1

---

## Batch 4: Media Overlays (8 checks)

| Check ID | Name | Fixture | epubcheck ID | Severity | Description |
|----------|------|---------|-------------|----------|-------------|
| MED-006 | media-overlay-well-formed | media-overlay-malformed | RSC-016 | FATAL | Media overlay SMIL must be well-formed XML |
| MED-007 | media-overlay-audio-exists | media-overlay-audio-missing | RSC-001 | ERROR | Audio files referenced in overlays must exist |
| MED-008 | media-overlay-text-exists | media-overlay-text-missing | RSC-001 | ERROR | Text references in overlays must resolve |
| MED-009 | duration-metadata-required | media-overlay-no-duration | OPF-027 | ERROR | Duration metadata required with media overlays |
| MED-010 | clip-timing-valid | media-overlay-clip-invalid | MED-009 | ERROR | clipBegin/clipEnd must use valid SMIL clock values |
| MED-011 | smil-structure-valid | media-overlay-bad-structure | RSC-005 | ERROR | SMIL must have valid seq/par structure |
| MED-012 | video-core-media-type | video-non-core-type | RSC-032 | ERROR | Video resources must use core media type or have fallback |
| MED-013 | media-overlay-property-declared | media-overlay-no-property | OPF-014 | ERROR | Manifest items with overlays need media-overlay property |

**New valid fixture:** `epub3-with-media-overlay` — minimal EPUB 3 with a working
SMIL media overlay and audio file.

**Spec refs:** `#sec-media-overlays`, Media Overlays 3.3

---

## Batch 5: Container & EPUB 2 Edge Cases (8 checks)

| Check ID | Name | Fixture | epubcheck ID | Severity | Description |
|----------|------|---------|-------------|----------|-------------|
| OCF-013 | encryption-xml-well-formed | ocf-encryption-malformed | RSC-016 | ERROR | encryption.xml must be well-formed XML |
| OCF-014 | container-version-valid | ocf-container-bad-version | RSC-005 | ERROR | container version attribute must be 1.0 |
| OCF-015 | filename-valid-characters | ocf-filename-invalid-chars | PKG-009 | ERROR | Filenames must not contain restricted characters |
| OCF-016 | filename-length-valid | ocf-filename-too-long | PKG-008 | WARNING | File paths should not exceed 65535 bytes |
| E2-012 | epub2-guide-type-valid | epub2-guide-invalid-type | OPF-070 | WARNING | Guide reference type must be valid |
| E2-013 | epub2-metadata-role-valid | epub2-dc-creator-bad-role | OPF-052 | WARNING | dc:creator opf:role must be valid MARC relator |
| E2-014 | epub2-opf-elements-ordered | epub2-opf-wrong-order | RSC-005 | ERROR | EPUB 2 OPF elements must appear in correct order |
| E2-015 | epub2-ncx-depth-valid | epub2-ncx-depth-mismatch | NCX-001 | ERROR | NCX dtb:depth must match actual depth |

**Spec refs:** `#sec-zip-container`, `#sec-container-metainf`, OPF 2.0.1

---

## Implementation Notes

### For each batch:

1. Create `scripts/create-level4-fixtures.py` (appending each batch)
2. Create `scripts/create-level4-expected.py` (appending each batch)
3. Run fixture creation: `python3 scripts/create-level4-fixtures.py`
4. Build EPUBs: `make build`
5. Run reference: `make reference`
6. Verify expected matches reference: `make verify`
7. Update `checks.json` with new check entries
8. Commit and push

### Key conventions:

- **One defect per fixture** — each invalid fixture introduces exactly one problem
- **Expected from reference** — run epubcheck first, then curate expected output
- **error_count_min** — use when single defect causes cascading errors
- **valid_override** — use when epubcheck doesn't flag a spec violation we want to track
- **USAGE severity** — new for Level 4 ACC checks; EPUB is valid but lacks best practices

### Check ID allocation:

| Category | Range | Count |
|----------|-------|-------|
| OPF | 035-044 | 10 |
| HTM | 024-033 | 10 |
| ACC | 001-010 | 10 |
| MED | 006-013 | 8 |
| OCF | 013-016 | 4 |
| E2 | 012-015 | 4 |
| **Total** | | **46** |

This brings the total from 123 checks (L1-L3) to **169 checks** (L1-L4).
