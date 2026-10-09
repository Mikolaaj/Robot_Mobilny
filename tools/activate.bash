# Source this script: source tools/activate.bash
_amr_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -f "${_amr_root}/.venv/bin/activate" ]]; then
    echo "Missing .venv. Create it with /usr/bin/python3 -m venv --system-site-packages .venv" >&2
    unset _amr_root
    return 1
fi
source /opt/ros/jazzy/setup.bash
source "${_amr_root}/.venv/bin/activate"
unset _amr_root
