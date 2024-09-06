#!/usr/bin/env bash
set -e

# Set magic variables for current file & dir
# shellcheck disable=SC2034
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC2034
__file="${__dir}/$(basename "${BASH_SOURCE[0]}")"
# shellcheck disable=SC2034
__base="$(basename "${__file}" .sh)"

# shellcheck source=scripts/_ensure.sh
source "${__dir}/../_ensure.sh"

load_pyenv

# shellcheck disable=SC2034
project_root=$(readlink -f "${__dir}/../../")
pyenv_venv_name="lexicon-backend-venv"
project_venv_root="$(pyenv prefix ${pyenv_venv_name})"
gunicorn_exec="${project_venv_root}/bin/gunicorn"
gunicorn_worker=${GUNICORN_WORKER:-0}
gunicorn_timeout=${GUNICORN_TIMEOUT:-30}

# if number of gunicorn worker is not set, then find depending upon available cores
if [[ ${gunicorn_worker} -le 0 ]]; then
  NUM_CORES=$(grep -c ^processor /proc/cpuinfo 2>/dev/null || sysctl -n hw.ncpu)
  gunicorn_worker=$((2 * NUM_CORES + 1))
fi

export PYTHONPATH=${PYTHONPATH:-}:${project_root}/src

# shellcheck disable=SC2093
exec "${gunicorn_exec}" --bind 0.0.0.0:5000 -k gevent --workers "${gunicorn_worker}" \
  --timeout "${gunicorn_timeout}" lexicon.conf.wsgi:application
