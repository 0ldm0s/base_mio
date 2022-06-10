#!/bin/bash
PYENV_ROOT="/usr/local/.pyenv"
PYTHON_ROOT="$PYENV_ROOT/shims"
cd $(dirname $0)
work_path=$(pwd)
mkdir -p "${work_path}/logs"
ulimit -n 512000
${PYTHON_ROOT}/circusd --daemon circus.ini