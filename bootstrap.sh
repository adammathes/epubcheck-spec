#!/usr/bin/env bash
#
# bootstrap.sh — Set up dev environment for epubverify-spec and implementations
#
# Works in: Claude Code VMs (Ubuntu 24), local Ubuntu 22/24, Debian 12+
# Usage: ./bootstrap.sh [--with-go] [--with-rust] [--all]
#
# By default installs only what's needed for the test suite (Java + tools).
# Pass flags to also install implementation languages.
#
set -euo pipefail

EPUBCHECK_VERSION="5.3.0"
GO_VERSION="1.23.6"
TOOLS_DIR="$HOME/tools"
TESTDATA_DIR="$HOME/testdata"

# Colors (if terminal supports them)
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    RED='\033[0;31m'
    NC='\033[0m'
else
    GREEN='' YELLOW='' RED='' NC=''
fi

info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; }

# Parse flags
INSTALL_GO=false
INSTALL_RUST=false

for arg in "$@"; do
    case "$arg" in
        --with-go)   INSTALL_GO=true ;;
        --with-rust) INSTALL_RUST=true ;;
        --all)       INSTALL_GO=true; INSTALL_RUST=true ;;
        --help|-h)
            echo "Usage: $0 [--with-go] [--with-rust] [--all]"
            echo ""
            echo "  --with-go    Install Go ${GO_VERSION}"
            echo "  --with-rust  Install Rust via rustup"
            echo "  --all        Install everything"
            echo ""
            echo "Without flags, installs only test suite dependencies (Java, epubcheck, test data)."
            exit 0
            ;;
        *) error "Unknown flag: $arg"; exit 1 ;;
    esac
done

echo "================================================"
echo "  epubcheck dev environment bootstrap"
echo "================================================"
echo ""

# ── 1. Check/install Java ──────────────────────────────────────────────

if command -v java &>/dev/null; then
    JAVA_VER=$(java -version 2>&1 | head -1)
    info "Java already installed: $JAVA_VER"
else
    warn "Java not found, installing OpenJDK 21..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get update -qq
        sudo apt-get install -y -qq openjdk-21-jre-headless
    else
        error "No apt-get found. Install Java 17+ manually and re-run."
        exit 1
    fi
    info "Java installed: $(java -version 2>&1 | head -1)"
fi

# ── 2. Check basic tools ───────────────────────────────────────────────

for tool in curl unzip zip git; do
    if ! command -v "$tool" &>/dev/null; then
        warn "$tool not found, installing..."
        sudo apt-get install -y -qq "$tool"
    fi
done
info "Basic tools present (curl, unzip, zip, git)"

# jq is needed for JSON comparison in test scripts
if ! command -v jq &>/dev/null; then
    warn "jq not found, installing..."
    sudo apt-get install -y -qq jq
fi
info "jq present"

# ── 3. Download reference epubcheck ────────────────────────────────────

mkdir -p "$TOOLS_DIR"
EPUBCHECK_DIR="$TOOLS_DIR/epubcheck-${EPUBCHECK_VERSION}"
EPUBCHECK_JAR="$EPUBCHECK_DIR/epubcheck.jar"

if [ -f "$EPUBCHECK_JAR" ]; then
    info "Reference epubcheck ${EPUBCHECK_VERSION} already installed"
else
    echo "Downloading epubcheck ${EPUBCHECK_VERSION}..."
    curl -fsSL "https://github.com/w3c/epubcheck/releases/download/v${EPUBCHECK_VERSION}/epubcheck-${EPUBCHECK_VERSION}.zip" \
        -o /tmp/epubcheck.zip
    unzip -qo /tmp/epubcheck.zip -d "$TOOLS_DIR/"
    rm /tmp/epubcheck.zip
    info "Reference epubcheck installed at $EPUBCHECK_JAR"
fi

# Quick smoke test
echo "  Smoke test: $(java -jar "$EPUBCHECK_JAR" --version 2>&1 | head -1)"

# ── 4. Download test data ──────────────────────────────────────────────

mkdir -p "$TESTDATA_DIR"

if [ -d "$TESTDATA_DIR/epub3-samples" ]; then
    info "epub3-samples already present"
else
    echo "Cloning IDPF epub3-samples..."
    git clone --depth 1 https://github.com/IDPF/epub3-samples.git \
        "$TESTDATA_DIR/epub3-samples" 2>/dev/null
    info "epub3-samples cloned to $TESTDATA_DIR/epub3-samples"
fi

if [ -d "$TESTDATA_DIR/epubcheck-src/src/test/resources" ]; then
    info "epubcheck test fixtures already present"
else
    echo "Cloning epubcheck test fixtures (sparse)..."
    git clone --depth 1 --filter=blob:none --sparse \
        https://github.com/w3c/epubcheck.git \
        "$TESTDATA_DIR/epubcheck-src" 2>/dev/null
    cd "$TESTDATA_DIR/epubcheck-src"
    git sparse-checkout set src/test/resources
    cd - >/dev/null
    info "epubcheck test fixtures cloned"
fi

# ── 5. Install Go (optional) ──────────────────────────────────────────

if $INSTALL_GO; then
    if command -v go &>/dev/null; then
        info "Go already installed: $(go version)"
    else
        echo "Installing Go ${GO_VERSION}..."
        curl -fsSL "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" -o /tmp/go.tar.gz
        sudo rm -rf /usr/local/go
        sudo tar -C /usr/local -xzf /tmp/go.tar.gz
        rm /tmp/go.tar.gz

        # Add to PATH for current session
        export PATH="$PATH:/usr/local/go/bin:$HOME/go/bin"

        # Persist PATH
        SHELL_NAME=$(basename "$SHELL")
        case "$SHELL_NAME" in
            fish)
                mkdir -p ~/.config/fish
                grep -q '/usr/local/go/bin' ~/.config/fish/config.fish 2>/dev/null || \
                    echo 'set -gx PATH $PATH /usr/local/go/bin ~/go/bin' >> ~/.config/fish/config.fish
                ;;
            *)
                RC_FILE="$HOME/.${SHELL_NAME}rc"
                grep -q '/usr/local/go/bin' "$RC_FILE" 2>/dev/null || \
                    echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> "$RC_FILE"
                ;;
        esac
        info "Go ${GO_VERSION} installed: $(go version)"
    fi
fi

# ── 6. Install Rust (optional) ────────────────────────────────────────

if $INSTALL_RUST; then
    if command -v rustc &>/dev/null; then
        info "Rust already installed: $(rustc --version)"
    else
        echo "Installing Rust via rustup..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
        source "$HOME/.cargo/env"
        info "Rust installed: $(rustc --version)"
    fi
fi

# ── 7. Write environment file ─────────────────────────────────────────

ENV_FILE="$HOME/.epubcheck-dev.env"
cat > "$ENV_FILE" <<EOF
# epubcheck dev environment — source this or use direnv
export EPUBCHECK_JAR="$EPUBCHECK_JAR"
export EPUBCHECK_VERSION="$EPUBCHECK_VERSION"
export TESTDATA_DIR="$TESTDATA_DIR"
export EPUB3_SAMPLES="$TESTDATA_DIR/epub3-samples"
export EPUBCHECK_FIXTURES="$TESTDATA_DIR/epubcheck-src/src/test/resources"
EOF

info "Environment file written to $ENV_FILE"

# ── Summary ────────────────────────────────────────────────────────────

echo ""
echo "================================================"
echo "  Setup complete!"
echo "================================================"
echo ""
echo "  Reference epubcheck: $EPUBCHECK_JAR"
echo "  Test data:           $TESTDATA_DIR/"
echo "  Environment:         source $ENV_FILE"
echo ""
echo "  Quick test:"
echo "    source $ENV_FILE"
echo "    java -jar \$EPUBCHECK_JAR --help"
echo ""
if $INSTALL_GO; then
    echo "  Go:    $(go version 2>/dev/null || echo 'restart shell to use')"
fi
if $INSTALL_RUST; then
    echo "  Rust:  $(rustc --version 2>/dev/null || echo 'restart shell to use')"
fi
echo ""
echo "  Next: cd into your project and run 'make build && make reference'"
echo ""
