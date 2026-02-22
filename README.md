# epubverify-spec

A language-independent, machine-readable test suite for EPUB validation. Any implementation (Go, Rust, Zig, C, etc.) can test against this suite to verify correctness. All fixtures are validated against the reference Java [epubcheck](https://github.com/w3c/epubcheck) to ensure accuracy.

## ⚠️ WARNING: Vibecoded Experiment

**This is an experimental project created as a vibecoded experiment. It is not production-ready and is not used anywhere yet. Use at your own risk.**


## Why

Currently there is a great Java validator from the W3C -- epubcheck. This project is not in any way affiliated with that.

This is an AI assisted coding experiment to see how far AI agents can get in making working versions in other languages with different tradeoffs than Java that might run faster.

Building an EPUB validator requires a test suite that:

- Defines exactly what "correct" validation means
- Is validated against the reference Java implementation
- Can be consumed by any language's test harness
- Tracks which spec requirements are covered
- Prioritizes checks by real-world frequency

The test suite is a hard part. Then AI agents can do the implementation by making tests pass.

## Maturity Levels

Every check in the registry is assigned a level representing implementation priority:

| Level | Name | Checks | Description |
|-------|------|--------|-------------|
| 1 | Catches pandoc problems | 26 | Container structure, basic OPF, manifest/spine cross-refs, required metadata |
| 2 | Daily driver | 42 | Full resource validation, fallback chains, content well-formedness, EPUB 2 basics |
| 3 | Production validator | 55 | CSS validation, navigation edge cases, fixed-layout, encoding, image validation |
| 4 | Full conformance | 46 | Accessibility, media overlays, advanced OPF/content, EPUB 2 edge cases |

Currently 169 checks are defined across Levels 1-4, covering 11 categories:

```
OPF  46    Package document
HTM  32    HTML content documents
PKG  16    Container/zip structure
RSC  13    Resource references
NCX  13    EPUB 2 NCX
MED  13    Media types & overlays
NAV  11    Navigation documents
ACC  10    Accessibility
CSS   8    CSS validation
FXL   5    Fixed-layout
ENC   2    Encoding & characters
```

## Quick Start

```bash
./bootstrap.sh          # Install Java, epubcheck, tools
make build              # Build EPUB fixtures from source directories
make reference          # Run reference epubcheck on all fixtures
make verify             # Verify expected output matches reference
```

## Project Structure

```
epubverify-spec/
├── checks.json                 # Machine-readable registry of all checks
├── fixtures/
│   ├── src/                    # Human-readable source for each test EPUB
│   │   ├── valid/              # 8 valid EPUBs (epub3, epub2, fxl, css, svg, images, multi-chapter, media-overlay)
│   │   └── invalid/            # 167 invalid EPUBs, one defect each
│   └── epub/                   # Built .epub zips (generated, gitignored)
├── expected/                   # Curated expected validation results
│   ├── valid/*.json
│   └── invalid/*.json
├── reference/                  # Raw epubcheck output (generated, gitignored)
├── scripts/                    # Build, reference, and verification scripts
├── Makefile                    # Orchestration
└── bootstrap.sh                # Environment setup
```

## How It Works

### Fixtures

Each fixture is a directory under `fixtures/src/` containing the raw files of an EPUB. Invalid fixtures introduce exactly **one defect** each, making failures easy to diagnose. The `build-fixtures.sh` script zips them into proper `.epub` files, and `build-special-fixtures.py` handles cases requiring non-standard zip construction (e.g., mimetype not stored first, compressed mimetype).

### Expected Output

Each fixture has a corresponding JSON file in `expected/` describing the validation result:

```json
{
  "fixture": "invalid/ocf-mimetype-missing",
  "valid": false,
  "messages": [
    {
      "severity": "ERROR",
      "check_id": "OCF-001",
      "epubcheck_id": "PKG-006",
      "message_pattern": "mimetype",
      "note": ""
    }
  ],
  "fatal_count": 0,
  "error_count": 1,
  "error_count_min": null,
  "warning_count": 0
}
```

Implementations must match: `valid` status, each message's `severity`, and each message's `message_pattern` (regex, case-insensitive). They do **not** need exact message text, exact cascading error counts, or identical message IDs.

Use `error_count_min` instead of exact `error_count` when epubcheck reports cascading errors from a single defect.

### checks.json

The central registry maps every check to its spec reference, category, severity, maturity level, fixtures, and corresponding epubcheck message ID. Implementations read this to know what to build and test against.

### Verification Pipeline

```
fixtures/src/  →  build  →  fixtures/epub/  →  epubcheck  →  reference/
                                                                 ↓
                                                    expected/  ←  verify (compare)
```

1. **build** — Zip source directories into `.epub` files
2. **reference** — Run epubcheck on every fixture, save JSON output
3. **verify** — Compare `expected/` against `reference/`, report PASS/FAIL per fixture

## Make Targets

| Target | Description |
|--------|-------------|
| `make build` | Build EPUB fixtures from source directories |
| `make reference` | Generate reference epubcheck output |
| `make verify` | Verify expected matches reference |
| `make compare IMPL=./tool` | Compare an implementation against expected |
| `make parity IMPL=./tool` | Generate parity report for an implementation |
| `make corpus` | Download real-world EPUB corpus |
| `make analyze` | Run epubcheck on corpus, produce summary and frequency report |
| `make discover` | Discover all check IDs via corpus analysis |
| `make frequency` | Rank checks by real-world frequency |
| `make clean` | Remove generated files |
| `make help` | Show available targets |

## Testing Your Implementation

Write a wrapper that accepts an `.epub` path and outputs JSON in the expected format, then:

```bash
make compare IMPL=./your-validator-wrapper
```

This runs your tool on every fixture and compares results against `expected/`. Output shows PASS/FAIL/SKIP per check with a summary percentage.

## Key Principles

1. **One defect per invalid fixture.** Each tests exactly one validation rule.
2. **Expected output is curated, not auto-generated.** Reference informs; expected decides.
3. **Fixtures are source-controlled as directories.** EPUB zips are build artifacts.
4. **checks.json is the contract.** Implementations read it to know what to build and test.
5. **Comparison is against expected/, not reference/.** This allows intentional divergence when warranted.
6. **Frequency drives priority.** After Level 1, real-world data determines what matters most.
7. **Every fixture validated against reference before commit.** Reference epubcheck is ground truth.

## CI

A GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push and pull request:

| Job | What it checks | Dependencies |
|-----|---------------|--------------|
| `validate-json` | All `.json` files are valid JSON | `jq` |
| `build-and-verify` | Fixtures build cleanly; expected output matches epubcheck reference | Java 17, epubcheck 5.3.0, `jq`, `zip`, `python3` |

The build-and-verify job catches two classes of problems:
- A fixture source directory that can't be zipped into a valid EPUB
- An `expected/` file that no longer matches what epubcheck 5.3.0 actually reports

To run the same checks locally:

```bash
make build              # Build all fixture EPUBs
make reference          # Run epubcheck on every fixture
make verify             # Diff expected/ against reference/
```

## License

This test suite references the [EPUB 3.3 specification](https://www.w3.org/TR/epub-33/) published by the W3C.
