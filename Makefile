EPUBCHECK_JAR ?= $(HOME)/tools/epubcheck-5.3.0/epubcheck.jar

.PHONY: all build reference verify compare parity discover frequency corpus clean help

all: build reference verify

build:                              ## Build epub fixtures from source
	./scripts/build-fixtures.sh

reference:                          ## Generate reference epubcheck output
	./scripts/generate-reference.sh

verify:                             ## Verify expected matches reference
	./scripts/verify-expected.sh

compare:                            ## Compare an implementation (IMPL=./path/to/tool)
	./scripts/compare-implementation.sh $(IMPL)

parity:                             ## Generate parity report (IMPL=./path/to/tool)
	./scripts/parity-report.sh $(IMPL)

discover:                           ## Discover all checks via corpus analysis
	./scripts/discover-checks.sh

frequency:                          ## Rank checks by real-world frequency
	./scripts/frequency-analysis.sh

corpus:                             ## Download real-world epub corpus
	./scripts/fetch-corpus.sh

clean:                              ## Remove generated files
	rm -rf fixtures/epub/ reference/ analysis/

help:                               ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'
