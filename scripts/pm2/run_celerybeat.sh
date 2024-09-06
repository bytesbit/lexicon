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

die() {
  echo "$*" 1>&2
  exit 1
}

# shellcheck disable=SC2034
project_root=$(readlink -f "${__dir}/../../")
pyenv_venv_name="lexicon-backend-venv"
project_venv_root="$(pyenv prefix ${pyenv_venv_name})"
celery_exec="${project_venv_root}/bin/celery"
lib_dir="/var/lib/lexicon-backend"
[ ! -d "${lib_dir}" ] && die "Directory '${lib_dir}' does not exists. Please create it first and try again."
[ ! -w "${lib_dir}" ] && die "Directory '${lib_dir}' is not writable. Make it writable first and try again."

# Explicitly disable AWS Xray for celery as system env variable priority is high over .env file
export AWS_XRAY_SDK_ENABLED="False"
export PYTHONPATH=${PYTHONPATH:-}:${project_root}/src

exec "${celery_exec}" -A lexicon beat -l info --pidfile="${lib_dir}/lexicon-celerybeat.pid"
