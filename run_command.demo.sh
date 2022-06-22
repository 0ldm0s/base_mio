#!/bin/bash
PYENV_ROOT="/opt/.pyenv"
PYTHON_ROOT="$PYENV_ROOT/shims"
EXECUTION="cli.WorkMan.Daemon.hello"
export FLASK_APP=mio.shell
export PYTHONIOENCODING=utf-8
export MIO_CONFIG="production"
export MIO_LIMIT_CPU=1
cd $(dirname $0)
mkdir -p logs
# You can use the nohup to run in backgroup
#nohup ${PYTHON_ROOT}/flask cli exe -cls=${EXECUTION} &> "${work_path}/logs/cron.log" 2>&1 &
${PYTHON_ROOT}/flask cli exe -cls=${EXECUTION}