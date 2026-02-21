# epubcheck 5.3.0 Divergences from EPUB Spec

This document catalogs every case where the W3C Java epubcheck 5.3.0 reference
tool diverges from what the EPUB spec requires. These are cases where a native
implementation **should** flag an issue but epubcheck does not (or flags it
differently). Each entry needs manual review to confirm the spec interpretation.

## Summary

| Category | Not flagged | Severity mismatch | Different error code | Cascading errors |
|----------|-------------|-------------------|---------------------|-----------------|
| ACC (Accessibility) | 10 | — | — | — |
| HTM (Content) | 6 | 1 | 2 | — |
| CSS | 3 | — | — | — |
| NAV (Navigation) | 2 | — | — | — |
| OPF (Package) | 1 | — | 1 | 39 fixtures |
| PKG (Container) | 2 | — | — | — |
| MED (Media) | 2 | — | — | — |
| NCX (EPUB 2) | 2 | — | — | — |
| RSC (Resources) | 1 | — | 1 | — |
| **Total** | **29** | **1** | **4** | **39 fixtures** |

---

## Category 1: epubcheck Does Not Flag (29 checks)

These are spec violations where epubcheck 5.3.0 produces **no error or warning**
at all. The expected output shows `valid: true` with empty messages. A correct
implementation should flag these.

### Accessibility (10 checks) — requires `--profile` in epubcheck

| Check ID | Fixture | Spec Violation | epubcheck Note |
|----------|---------|---------------|----------------|
| ACC-001 | `acc-no-a11y-metadata` | Missing accessibility metadata (schema.org) | Does not flag without `--profile` option |
| ACC-002 | `acc-img-no-alt` | `<img>` missing `alt` attribute | Does not flag |
| ACC-003 | `acc-no-lang` | Missing `lang`/`xml:lang` on `<html>` | Does not flag |
| ACC-004 | `acc-dc-source-no-page-list` | `dc:source` present but no page-list nav | Does not flag |
| ACC-005 | `acc-no-accessmode` | Missing `schema:accessMode` | Does not flag |
| ACC-006 | `acc-no-access-sufficient` | Missing `schema:accessModeSufficient` | Does not flag |
| ACC-007 | `acc-no-summary` | Missing `schema:accessibilitySummary` | Does not flag |
| ACC-008 | `acc-no-feature` | Missing `schema:accessibilityFeature` | Does not flag |
| ACC-009 | `acc-no-hazard` | Missing `schema:accessibilityHazard` | Does not flag |
| ACC-010 | `acc-no-landmarks` | Missing landmarks navigation | Does not flag |

### Content Documents (6 checks)

| Check ID | Fixture | Spec Violation | epubcheck Note |
|----------|---------|---------------|----------------|
| HTM-003 | `content-empty-href` | Empty `href` attribute | Does not flag empty href attributes |
| HTM-009 | `content-base-element` | `<base>` element in content doc | Does not flag base elements |
| HTM-015 | `content-epub-type-invalid` | Unknown `epub:type` value | Does not flag unknown epub:type values |
| HTM-020 | `content-processing-instruction` | `xml-stylesheet` PI in content doc | Does not flag processing instructions |
| HTM-021 | `content-style-position-absolute` | `position:absolute` in inline style | Does not flag |
| HTM-033 | `content-rdf-element` | RDF metadata in content doc | Does not flag RDF elements |

### CSS (3 checks)

| Check ID | Fixture | Spec Violation | epubcheck Note |
|----------|---------|---------------|----------------|
| CSS-002 | `css-invalid-property` | Unknown CSS property name | Does not flag unknown CSS properties |
| CSS-003 | `css-font-face-no-src` | `@font-face` missing `src` descriptor | Does not flag |
| CSS-005 | `css-import` | `@import` rule in stylesheet | Does not flag @import rules |

### Navigation (2 checks)

| Check ID | Fixture | Spec Violation | epubcheck Note |
|----------|---------|---------------|----------------|
| NAV-009 | `nav-hidden-attribute` | `hidden` attribute on `<nav>` | Does not flag hidden attribute |
| NAV-010 | `nav-landmarks-invalid-type` | Invalid `epub:type` on landmark | Does not flag unknown landmark types |

### Package/OPF (1 check)

| Check ID | Fixture | Spec Violation | epubcheck Note |
|----------|---------|---------------|----------------|
| OPF-039 | `opf-epub3-guide` | `<guide>` element in EPUB 3 | Does not flag deprecated guide element |

### Container/PKG (2 checks)

| Check ID | Fixture | Spec Violation | epubcheck Note |
|----------|---------|---------------|----------------|
| OCF-005 | `ocf-mimetype-compressed` | Mimetype entry is compressed | Does not flag compressed mimetype entries |
| OCF-016 | `ocf-filename-too-long` | Filename exceeds 65535 bytes | Does not flag long filenames |

### Media (2 checks)

| Check ID | Fixture | Spec Violation | epubcheck Note |
|----------|---------|---------------|----------------|
| MED-002 | `image-non-core-media-type` | `image/webp` is not a core media type | Does not flag webp as non-core |
| MED-012 | `video-non-core-type` | `video/x-msvideo` is not a core type | Does not flag non-core video types |

### EPUB 2 / NCX (2 checks)

| Check ID | Fixture | Spec Violation | epubcheck Note |
|----------|---------|---------------|----------------|
| E2-012 | `epub2-guide-invalid-type` | Invalid guide reference type | Does not flag invalid guide types |
| E2-015 | `epub2-ncx-depth-mismatch` | NCX `dtb:depth` doesn't match actual depth | Does not flag depth mismatch |

### Resources (1 check)

| Check ID | Fixture | Spec Violation | epubcheck Note |
|----------|---------|---------------|----------------|
| RSC-002 | `zip-entry-not-in-manifest` | File in ZIP not declared in manifest | Does not report at ERROR/WARNING level |

---

## Category 2: Severity Mismatches (1 check)

Cases where both the spec and epubcheck flag the issue, but at different severity levels.

| Check ID | Fixture | Spec Severity | epubcheck Severity | epubcheck ID | Note |
|----------|---------|--------------|-------------------|--------------|------|
| HTM-002 | `content-no-title` | WARNING | WARNING | RSC-017 | Both agree on WARNING. Originally considered ERROR in early drafts. Marked here for review since the check description says "should" not "must". |

---

## Category 3: Different Error Codes (4 checks)

Cases where epubcheck flags the issue but uses a different error code than expected,
suggesting the tool validates the constraint through a different mechanism.

| Check ID | Fixture | Expected Code | Actual epubcheck Code | Note |
|----------|---------|--------------|----------------------|------|
| OPF-009 | `opf-duplicate-manifest-id` | OPF-074 | RSC-005 | Reported as XML schema error, not dedicated OPF check |
| HTM-008 | `content-broken-internal-link` | HTM-008 | RSC-007 | Uses generic resource reference code for hyperlinks |
| RSC-001 | `content-broken-image-ref` | RSC-001 | RSC-001 | Same code, but note says epubcheck uses RSC-001 for manifest-referenced files specifically |
| RSC-002 | `zip-entry-not-in-manifest` | OPF-003 | — (not flagged) | Originally predicted OPF-003; epubcheck doesn't flag at ERROR/WARNING |

---

## Category 4: Cascading Errors (39 fixtures)

These fixtures contain a single intentional defect, but epubcheck reports multiple
errors due to cascading validation failures. The `error_count_min` field in expected
output indicates the minimum number of errors an implementation should report (always
1 = the primary defect), while `error_count` shows what epubcheck actually reports.

| Fixture | Primary Defect | error_count | error_count_min |
|---------|---------------|-------------|-----------------|
| `content-fxl-invalid-viewport` | Invalid viewport meta | 2 | 1 |
| `content-link-parent-dir` | Link escapes container | 2 | 1 |
| `content-remote-resource` | Undeclared remote resource | 2 | 1 |
| `content-style-syntax-error` | CSS syntax error in style | 3 | 1 |
| `content-video-poster-missing` | Missing video poster | 2 | 1 |
| `css-font-face-remote` | Remote font-face src | 2 | 1 |
| `css-syntax-error` | CSS syntax error | 3 | 1 |
| `epub2-guide-broken-href` | Broken guide href | 2 | 1 |
| `epub2-ncx-duplicate-ids` | Duplicate NCX IDs | 2 | 1 |
| `epub2-opf-wrong-order` | OPF elements in wrong order | 4 | 1 |
| `epub2-with-dcterms-modified` | dcterms:modified in EPUB 2 | 3 | 1 |
| `epub2-with-nav-property` | nav property in EPUB 2 | 2 | 1 |
| `image-corrupted` | Corrupt image file | 2 | 1 |
| `manifest-href-bad-encoding` | Bad percent-encoding in href | 4 | 1 |
| `manifest-path-traversal` | Path traversal in manifest | 2 | 1 |
| `media-overlay-audio-missing` | Missing audio resource | 2 | 1 |
| `media-overlay-bad-structure` | Invalid SMIL structure | 3 | 1 |
| `media-overlay-clip-invalid` | Invalid clip timing | 3 | 1 |
| `media-overlay-malformed` | Malformed SMIL XML | 2 | 1 |
| `media-overlay-no-duration` | Missing duration metadata | 3 | 1 |
| `media-overlay-no-property` | Missing media-overlay property | 2 | 1 |
| `media-overlay-text-missing` | Missing text reference | 2 | 1 |
| `nav-toc-no-ol` | Nav TOC missing `<ol>` | 2 | 1 |
| `opf-manifest-href-fragment` | Fragment in manifest href | 3 | 1 |
| `opf-manifest-href-missing` | Missing href attribute | 3 | 1 |
| `opf-manifest-item-no-id` | Missing id on manifest item | 4 | 1 |
| `opf-manifest-media-type-missing` | Missing media-type attribute | 3 | 1 |
| `opf-media-overlay-bad-ref` | Bad media-overlay reference | 4 | 1 |
| `opf-media-type-mismatch` | Media type doesn't match file | 4 | 1 |
| `opf-meta-refines-bad-target` | Bad refines target | 2 | 1 |
| `opf-missing-dc-identifier` | Missing dc:identifier | 3 | 1 |
| `opf-missing-manifest` | Missing manifest element | 3 | 1 |
| `opf-missing-metadata` | Missing metadata element | 3 | 1 |
| `opf-missing-spine` | Missing spine element | 2 | 1 |
| `opf-missing-unique-identifier` | Missing unique-identifier attr | 2 | 1 |
| `opf-no-unique-id-attr` | unique-identifier points nowhere | 3 | 1 |
| `opf-prefix-invalid` | Invalid prefix declaration | 3 | 1 |
| `spine-bad-idref` | Spine idref not in manifest | 3 | 1 |
| `spine-empty` | Empty spine element | 2 | 1 |

---

## How to Use This Document

**For implementers:** If your validator catches issues in Category 1 that epubcheck
misses, that's correct behavior — you're more spec-compliant than the reference tool.

**For test comparison:** When comparing against epubcheck reference output, these
divergences are expected. Use the `epubcheck_note` fields in `checks.json` and
`note` fields in `expected/*.json` for programmatic access to this information.

**For review:** Each Category 1 entry should be verified against the relevant W3C
spec section to confirm the spec actually requires the check. The `spec_ref` field
in `checks.json` links to the relevant spec section for each check.
