#!/bin/sh
PYENV_ROOT="/usr/local/.pyenv"
PYTHON_ROOT="$PYENV_ROOT/shims"
UWSGI_NUM_PROCESSES=`grep -c ^processor /proc/cpuinfo`
export MIO_CONFIG=production
export PYTHONUNBUFFERED=1
cd $(dirname $0)
work_path=$(pwd)
mkdir -p "${work_path}/logs"
ulimit -n 512000
uwsgi --wsgi mio.pymio-uwsgi --tornado 100 --greenlet \
      --zerg /dev/shm/mutalisk --enable-threads \
      --master --thunder-lock --optimize 1 --processes=$UWSGI_NUM_PROCESSES \
      --logto2 $work_path/logs/master-zerg.log
