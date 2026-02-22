# Future Work & Known Issues

Tracking items identified during the Level 1-4 build-out of epubverify-spec.

---

## Issues to Address

### 1. Accessibility checks are effectively no-ops (ACC-001 to ACC-010)

All 10 accessibility checks report `valid: true` with empty messages because
epubcheck 5.3.0 doesn't enforce them without the `--profile` option. The fixtures
exist and are correct, but the expected output reflects epubcheck's behavior rather
than the spec requirement.

**Impact:** Implementations testing against `expected/` will see these pass even
with no accessibility validation.

**Action:** Consider adding a second set of expected outputs for
`--profile default` mode, or document that implementations must override these
10 checks. Alternatively, re-run reference generation with `--profile default`.

### 2. 28 checks have no epubcheck_message_id mapping

These represent spec violations that epubcheck 5.3.0 either doesn't check at all
or validates through a different mechanism. See
[epubcheck-divergences.md](epubcheck-divergences.md) for the full list.

**Impact:** Implementations have freedom to design their own error codes for these,
but there's no reference output to compare against.

**Action:** These are documented with `epubcheck_note` in checks.json. No immediate
action needed, but should be revisited when epubcheck 6.x is released.

### 3. Sparse coverage areas

Some categories have minimal check coverage:

| Category | Checks | Notes |
|----------|--------|-------|
| ENC (Encoding) | 2 | Only UTF-8/UTF-16 detection |
| FXL (Fixed Layout) | 5 | Basic viewport + rendition |
| E2 (EPUB 2 specific) | 4 | Most EPUB 2 checks are in other categories |

**Action:** Expand these in a potential Level 5, or accept as intentional given the
maturity level model.

### 4. Cascading error documentation

39 fixtures produce more errors from epubcheck than the single defect they test.
The `error_count_min` mechanism handles this, but it's not prominently documented
in the README.

**Action:** Add a section to README.md explaining `error_count_min` semantics and
how implementations should handle cascading errors.

### 5. Severity mismatches need review

A few checks where our spec severity assignment may differ from epubcheck's:
- `content-no-title` (HTM-002): Spec says WARNING, consistent with epubcheck
- `zip-entry-not-in-manifest` (RSC-002): Spec says ERROR, epubcheck doesn't flag

**Action:** Review the spec references for each to confirm correct severity
assignment.

---

## Future Enhancements

### Level 5: Extended validation
- Expand ENC category (encoding edge cases, BOM handling)
- Expand FXL category (complex layouts, page transitions)
- Add more EPUB 2 edge cases
- Test `--profile default` accessibility enforcement
- Add checks for EPUB Reading System behavior hints

### Tooling improvements
- Add `scripts/compare-implementation.sh` support for `--profile` flag
- Create a machine-readable summary of all divergences (JSON format)
- Add CI integration examples (GitHub Actions, etc.)
- Corpus analysis against real-world EPUBs to prioritize new checks

### epubcheck version tracking
- When epubcheck 6.x releases, re-run all reference generation
- Track which divergences are fixed in newer versions
- Consider maintaining parallel reference outputs for multiple versions
