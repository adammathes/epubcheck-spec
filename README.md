# epubcheck-spec

A language-independent, machine-readable test suite for EPUB validation. Any implementation (Go, Rust, Zig, C, etc.) can test against this suite to verify correctness. All fixtures are validated against the reference Java [epubcheck](https://github.com/w3c/epubcheck) to ensure accuracy.

## Why

Building a native EPUB validator to replace the Java-only W3C epubcheck requires a rock-solid test suite that:

- Defines exactly what "correct" validation means
- Is validated against the reference Java implementation
- Can be consumed by any language's test harness
- Tracks which spec requirements are covered
- Prioritizes checks by real-world frequency

The test suite is the hard part. The implementation is just making tests pass.

## Maturity Levels

Every check in the registry is assigned a level representing implementation priority:

| Level | Name | Checks | Description |
|-------|------|--------|-------------|
| 1 | Catches pandoc problems | ~26 | Container structure, basic OPF, manifest/spine cross-refs, required metadata |
| 2 | Daily driver | ~42 | Full resource validation, fallback chains, content well-formedness, EPUB 2 basics |
| 3 | Production validator | ~55 | CSS validation, navigation edge cases, fixed-layout, encoding, image validation |
| 4 | Full conformance | TBD | Accessibility, encryption, media overlays, dictionaries, deep HTML5 validation |

Currently 123 checks are defined across Levels 1-3, covering 10 categories:

```
OPF  34    Package document
HTM  22    HTML content documents
RSC  13    Resource references
PKG  12    Container/zip structure
NAV  11    Navigation documents
NCX  11    EPUB 2 NCX
CSS   8    CSS validation
FXL   5    Fixed-layout
MED   5    Media types & overlays
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
epubcheck-spec/
├── checks.json                 # Machine-readable registry of all checks
├── fixtures/
│   ├── src/                    # Human-readable source for each test EPUB
│   │   ├── valid/              # 4 valid EPUBs (epub3, epub2, fxl, css)
│   │   └── invalid/            # 121 invalid EPUBs, one defect each
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

## License

This test suite references the [EPUB 3.3 specification](https://www.w3.org/TR/epub-33/) published by the W3C.
