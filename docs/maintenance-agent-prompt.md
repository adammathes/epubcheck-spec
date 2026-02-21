# Maintenance Agent Prompt: epubverify-spec

You are maintaining **epubverify-spec**, a language-independent, machine-readable test suite for EPUB validation. The suite consists of 125 fixture EPUBs (4 valid, 121 invalid) and a `checks.json` registry of 123 checks across 10 categories, all validated against the reference Java [epubcheck](https://github.com/w3c/epubcheck).

This document is your runbook. Follow the relevant section for the task at hand.

---

## Project Layout (Quick Reference)

```
epubverify-spec/
├── checks.json                  # Central registry (version, checks[], categories, levels)
├── fixtures/src/
│   ├── valid/                   # 4 valid EPUB source directories
│   └── invalid/                 # 121 invalid EPUB source directories (1 defect each)
├── expected/
│   ├── valid/*.json             # Curated expected output for valid fixtures
│   └── invalid/*.json           # Curated expected output for invalid fixtures
├── reference/                   # Generated epubcheck output (gitignored)
├── scripts/                     # Build, reference, verify, compare scripts
├── Makefile                     # Orchestration (build / reference / verify / compare / parity)
├── bootstrap.sh                 # Environment setup (Java, epubcheck, tools)
└── .github/workflows/ci.yml     # GitHub Actions CI
```

**Key invariant:** `expected/` is curated by humans. `reference/` is generated and gitignored. CI confirms that `expected/` still matches what the current reference epubcheck produces.

---

## Task 1: Upgrade to a New epubcheck Version

Run this when a new epubcheck release is available (e.g., upgrading from 5.3.0 to 5.4.0).

### Step 1 — Set up the new version

```bash
# Download the new release
NEW_VERSION=5.4.0   # change this
mkdir -p ~/tools
curl -fsSL "https://github.com/w3c/epubcheck/releases/download/v${NEW_VERSION}/epubcheck-${NEW_VERSION}.zip" \
  -o /tmp/epubcheck.zip
unzip -q /tmp/epubcheck.zip -d ~/tools/

# Verify it runs
java -jar ~/tools/epubcheck-${NEW_VERSION}/epubcheck.jar --version
```

### Step 2 — Build fixtures and generate new reference output

```bash
make build
EPUBCHECK_JAR=~/tools/epubcheck-${NEW_VERSION}/epubcheck.jar make reference
```

### Step 3 — Identify what changed

```bash
make verify
```

Any FAIL lines mean the new epubcheck produces different output than what is in `expected/`. For each failure, examine the diff manually:

```bash
# Example: fixture invalid/opf-missing-dc-title
diff <(jq . expected/invalid/opf-missing-dc-title.json) \
     <(jq . reference/invalid/opf-missing-dc-title.json)
```

Categorize each failure as one of:

| Category | What happened | Action |
|----------|---------------|--------|
| **A — Message text changed** | Same error, different wording | Update `message_pattern` in `expected/` if the old pattern no longer matches |
| **B — Message ID changed** | epubcheck renamed a check ID | Update `epubcheck_message_id` in `checks.json`; update `epubcheck_id` in `expected/` |
| **C — Behavior changed** | epubcheck now reports a different error for the same defect | Evaluate: update `expected/` to match, or keep the old expectation with a `note` explaining the divergence |
| **D — New cascading errors** | New epubcheck version reports more errors from the same defect | Use `error_count_min` instead of exact `error_count`; set `error_count_min` to the minimum acceptable count |
| **E — Check removed** | epubcheck no longer reports this error | Mark the check in `checks.json` with `"deprecated_in_epubcheck": "5.4.0"` and add a `note` to the expected file |
| **F — New check added** | epubcheck now reports an error we didn't expect | See Task 2 (Adding a New Check) |

### Step 4 — Update expected/ files

For each failure, update the corresponding `expected/` file to reflect the new correct behavior. Do NOT auto-generate expected files — examine each one individually and confirm the change makes sense.

```bash
# After updating, re-verify
make verify
# Must exit 0 before proceeding
```

### Step 5 — Update version references

Update every hardcoded version string:

1. **`checks.json`** — `"reference_tool"` field:
   ```json
   "reference_tool": "epubcheck-5.4.0"
   ```

2. **`.github/workflows/ci.yml`** — `EPUBCHECK_VERSION` env var:
   ```yaml
   EPUBCHECK_VERSION: 5.4.0
   ```

3. **`bootstrap.sh`** — wherever the version is hardcoded (search for the old version string):
   ```bash
   grep -r "5.3.0" . --include="*.sh" --include="*.yml" --include="*.json" -l
   ```

4. **`README.md`** — if the epubcheck version is mentioned anywhere.

### Step 6 — Verify CI passes

Commit the changes and confirm the GitHub Actions CI workflow passes. The `build-and-verify` job will independently reproduce the same checks.

---

## Task 2: Adding a New Check

Run this when you want to add a check that epubcheck enforces but we don't yet cover.

### Step 1 — Identify the check

Either from corpus analysis (`make discover && make frequency`) or from reviewing the [epubcheck message catalog](https://github.com/w3c/epubcheck/blob/main/src/main/resources/com/adobe/epubcheck/util/messages.properties).

You need:
- The epubcheck message ID (e.g., `OPF-085`)
- What EPUB defect triggers it
- Which spec section it enforces

### Step 2 — Create the fixture source directory

Pick the most appropriate base (usually `valid/minimal-epub3`). Copy it and introduce **exactly one defect**:

```bash
# Example: adding a check for duplicate spine itemrefs
cp -r fixtures/src/valid/minimal-epub3 fixtures/src/invalid/spine-duplicate-itemref
# Edit the defective file
$EDITOR fixtures/src/invalid/spine-duplicate-itemref/OEBPS/content.opf
```

Naming convention: `{category-abbreviation}-{what-is-wrong}`, all lowercase, hyphens. Examples:
- `opf-missing-dc-language`
- `nav-broken-toc-link`
- `pkg-mimetype-wrong-content`

### Step 3 — Build and run reference

```bash
make build
make reference
```

Inspect what epubcheck actually reports:

```bash
jq . reference/invalid/spine-duplicate-itemref.json
```

**If epubcheck reports zero errors:** your defect didn't trigger validation. Revisit the fixture — the defect may not be severe enough or may be in the wrong location.

**If epubcheck reports cascading errors:** use `error_count_min` in the expected file (set to 1 or the minimum meaningful count).

### Step 4 — Create the expected file

Create `expected/invalid/{fixture-name}.json`. Model it on existing expected files. Fill in:

```json
{
  "fixture": "invalid/spine-duplicate-itemref",
  "valid": false,
  "messages": [
    {
      "severity": "ERROR",
      "check_id": "OPF-XXX",        // your new check ID from checks.json
      "epubcheck_id": "OPF-085",    // the epubcheck message ID
      "message_pattern": "duplicate",  // regex fragment matching the epubcheck message text
      "note": ""
    }
  ],
  "fatal_count": 0,
  "error_count": 1,
  "error_count_min": null,
  "warning_count": 0
}
```

The `message_pattern` must be a case-insensitive regex substring that matches the epubcheck message text in `reference/`. Check it:

```bash
jq '.messages[].message' reference/invalid/spine-duplicate-itemref.json
```

### Step 5 — Verify the expected file is correct

```bash
make verify
# The new fixture should PASS
```

### Step 6 — Register the check in checks.json

Add a new entry to the `"checks"` array in `checks.json`. Assign the next sequential ID within its category (e.g., if the last OPF check is `OPF-034`, add `OPF-035`). Choose the appropriate `level` (1–3) based on the maturity level description. Set `frequency_rank` to `null` unless you have data from corpus analysis.

```json
{
  "id": "OPF-035",
  "name": "spine-no-duplicate-itemref",
  "description": "The spine must not contain duplicate itemref elements referencing the same manifest item",
  "spec_ref": "https://www.w3.org/TR/epub-33/#sec-pkg-spine",
  "category": "OPF",
  "severity": "ERROR",
  "level": 2,
  "applies_to": ["epub2", "epub3"],
  "fixture_invalid": "invalid/spine-duplicate-itemref",
  "fixture_valid": "valid/minimal-epub3",
  "epubcheck_message_id": "OPF-085",
  "frequency_rank": null,
  "implemented": {}
}
```

### Step 7 — Update README stats

Update the category count table and total in `README.md`:

```
OPF  35    Package document     ← was 34
```

And update the total: `Currently 124 checks are defined...`

Also update the level count for whichever level the new check belongs to.

---

## Task 3: Fixing a Broken Expected File (Without an epubcheck Upgrade)

Run this when `make verify` fails on the current epubcheck version — meaning `expected/` has drifted from what epubcheck reports, for reasons other than a version upgrade (e.g., a fixture was edited, a new epubcheck patch was released).

```bash
# See all failures
make verify

# Inspect one failure
diff <(jq . expected/invalid/FIXTURE_NAME.json) \
     <(jq . reference/invalid/FIXTURE_NAME.json)
```

For each failure:
1. Confirm the fixture source was not accidentally changed: `git diff fixtures/src/`
2. If the fixture is unchanged and epubcheck changed, treat as an epubcheck upgrade (Task 1, Step 3+)
3. If the fixture was intentionally changed, regenerate the expected file from reference, then manually review and curate

---

## Task 4: Adding a Bulk Set of Checks (New Level or Category)

Use this when adding a whole category (e.g., implementing Level 4 accessibility checks).

### Step 1 — Research what epubcheck checks

```bash
make corpus      # Download real-world EPUBs (one-time)
make discover    # Run epubcheck on corpus, collect all message IDs
make frequency   # Rank by frequency
cat analysis/check-frequency.txt
```

Cross-reference against `checks.json` to find uncovered message IDs:

```bash
# List all epubcheck IDs already in checks.json
jq -r '.checks[].epubcheck_message_id' checks.json | sort > /tmp/covered.txt

# List all IDs seen in corpus analysis
sort analysis/known-message-ids.txt > /tmp/all.txt

# Find gaps
comm -23 /tmp/all.txt /tmp/covered.txt
```

### Step 2 — Prioritize by frequency

Focus on the highest-frequency uncovered checks first. For each, follow Task 2 (Adding a New Check).

### Step 3 — Create fixtures in bulk

For large batches, you can use a creation script (see `scripts/create-level2-fixtures.py` and `scripts/create-level3-fixtures.py` as models). The script should:
1. Copy the appropriate base fixture
2. Apply the specific defect programmatically
3. Write the fixture to `fixtures/src/invalid/`

Then run `make build && make reference` once for all new fixtures, then create all expected files.

---

## Task 5: Removing or Deprecating a Check

Run this when a check no longer applies (e.g., epubcheck stopped reporting it, or the EPUB spec changed).

1. Add `"deprecated": true` and `"deprecated_reason": "..."` to the check entry in `checks.json`
2. Do NOT delete the fixture source or expected file — they serve as historical reference
3. Add a `"note"` to the expected file explaining the deprecation
4. If the fixture now produces different output in `reference/`, update `expected/` accordingly

---

## Invariants to Maintain

These must always be true after any maintenance task:

- [ ] `make verify` exits 0 — all `expected/` files match reference epubcheck output
- [ ] Every entry in `checks.json` has a corresponding fixture in `fixtures/src/invalid/` (or `valid/` for `fixture_valid`)
- [ ] Every fixture in `fixtures/src/` has a corresponding file in `expected/`
- [ ] `checks.json` JSON is valid: `jq empty checks.json`
- [ ] All `expected/*.json` are valid JSON: `find expected/ -name '*.json' | xargs -I{} jq empty {}`
- [ ] README category counts and total match actual `checks.json` entries
- [ ] `checks.json` `"reference_tool"` matches the epubcheck version used to generate `reference/`
- [ ] CI passes on main branch

## Checking Counts

To quickly verify README stats match reality:

```bash
# Total checks
jq '.checks | length' checks.json

# Per-category counts
jq -r '.checks[].category' checks.json | sort | uniq -c | sort -rn

# Per-level counts
jq -r '.checks[].level' checks.json | sort | uniq -c | sort -n

# Fixture counts
ls fixtures/src/valid/ | wc -l
ls fixtures/src/invalid/ | wc -l
```
