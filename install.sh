#!/usr/bin/env bash
#
# spotiTermy — Linux install script
#
# Creates a virtual environment in .venv and installs spotiTermy into it in
# editable mode. Run from anywhere; it operates on the repo the script lives in.
#
#   ./install.sh            # base install
#   ./install.sh --ai       # also install the optional AI extras (anthropic, openai)
#   ./install.sh --help     # usage
#
set -euo pipefail

# --- locate the repo (directory this script lives in) -----------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR=".venv"
MIN_PY_MAJOR=3
MIN_PY_MINOR=10
WITH_AI=0

# --- args -------------------------------------------------------------------
usage() {
    cat <<'EOF'
spotiTermy — Linux install script

Creates a virtual environment in .venv and installs spotiTermy into it in
editable mode. Run from anywhere; it operates on the repo the script lives in.

  ./install.sh            base install
  ./install.sh --ai       also install the optional AI extras (anthropic, openai)
  ./install.sh --help     this help
EOF
}

for arg in "$@"; do
    case "$arg" in
        --ai)   WITH_AI=1 ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $arg (try --help)" >&2
            exit 2
            ;;
    esac
done

# --- pretty output ----------------------------------------------------------
info()  { printf '\033[1;35m==>\033[0m %s\n' "$*"; }        # mauve, Catppuccin-ish
warn()  { printf '\033[1;33m==>\033[0m %s\n' "$*" >&2; }    # yellow
err()   { printf '\033[1;31mERROR:\033[0m %s\n' "$*" >&2; }

# --- find a suitable python -------------------------------------------------
# Prefer the newest python3.X on PATH, fall back to python3 / python.
pick_python() {
    local candidate
    for candidate in python3.14 python3.13 python3.12 python3.11 python3.10 python3 python; do
        if command -v "$candidate" >/dev/null 2>&1; then
            if "$candidate" -c "import sys; raise SystemExit(0 if sys.version_info[:2] >= ($MIN_PY_MAJOR, $MIN_PY_MINOR) else 1)" 2>/dev/null; then
                echo "$candidate"
                return 0
            fi
        fi
    done
    return 1
}

# --- distro hint for the venv package (Debian/Ubuntu split it out) ----------
venv_install_hint() {
    local id="" like=""
    if [ -r /etc/os-release ]; then
        # shellcheck disable=SC1091
        . /etc/os-release
        id="${ID:-}"
        like="${ID_LIKE:-}"
    fi
    case "$id $like" in
        *debian*|*ubuntu*) echo "sudo apt install python3 python3-venv python3-pip" ;;
        *fedora*|*rhel*)   echo "sudo dnf install python3 python3-pip" ;;
        *arch*)            echo "sudo pacman -S python python-pip" ;;
        *)                 echo "install your distro's python3 + venv + pip packages" ;;
    esac
}

info "Locating Python ${MIN_PY_MAJOR}.${MIN_PY_MINOR}+ ..."
if ! PYTHON="$(pick_python)"; then
    err "No Python ${MIN_PY_MAJOR}.${MIN_PY_MINOR}+ found on PATH."
    warn "Install it, e.g.:  $(venv_install_hint)"
    exit 1
fi
PY_VERSION="$("$PYTHON" -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])')"
info "Using $PYTHON (Python $PY_VERSION)"

# --- create the venv --------------------------------------------------------
if [ -d "$VENV_DIR" ]; then
    info "Reusing existing $VENV_DIR"
else
    info "Creating virtual environment in $VENV_DIR ..."
    if ! "$PYTHON" -m venv "$VENV_DIR" 2>/tmp/spotitermy-venv-err; then
        err "Failed to create the virtual environment."
        if grep -qi 'ensurepip\|No module named venv' /tmp/spotitermy-venv-err; then
            warn "The stdlib venv module is missing (common on Debian/Ubuntu)."
            warn "Install it:  $(venv_install_hint)"
        else
            cat /tmp/spotitermy-venv-err >&2
        fi
        rm -f /tmp/spotitermy-venv-err
        exit 1
    fi
    rm -f /tmp/spotitermy-venv-err
fi

VENV_PY="$VENV_DIR/bin/python"

# --- install ----------------------------------------------------------------
info "Upgrading pip ..."
"$VENV_PY" -m pip install --quiet --upgrade pip

if [ "$WITH_AI" -eq 1 ]; then
    info "Installing spotiTermy (editable) with AI extras ..."
    "$VENV_PY" -m pip install -e ".[ai]"
else
    info "Installing spotiTermy (editable) ..."
    "$VENV_PY" -m pip install -e .
fi

# --- done -------------------------------------------------------------------
info "Done."
echo
echo "Run it with:"
echo "    $VENV_DIR/bin/spotitermy"
echo
echo "or activate the venv first:"
echo "    source $VENV_DIR/bin/activate"
echo "    spotitermy"
if [ "$WITH_AI" -eq 0 ]; then
    echo
    echo "(AI playlist features need extras: re-run with  ./install.sh --ai)"
fi
