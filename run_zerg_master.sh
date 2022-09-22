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
uwsgi --http-socket /dev/shm/pymio.sock --wsgi mio.pymio-uwsgi --tornado 100 --greenlet \
      --zerg-server /dev/shm/mutalisk --enable-threads \
      --master --thunder-lock --optimize 1 --processes=$UWSGI_NUM_PROCESSES \
      --cache 1000 --logto2 $work_path/logs/master-web.log
