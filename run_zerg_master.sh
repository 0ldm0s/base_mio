#!/bin/sh
PYENV_ROOT="/usr/local/.pyenv"
PYTHON_ROOT="$PYENV_ROOT/shims"
export MIO_CONFIG=production
export PYTHONUNBUFFERED=1
cd $(dirname $0)
work_path=$(pwd)
mkdir -p "${work_path}/logs"
ulimit -n 512000
uwsgi --http-socket /dev/shm/pymio.sock --wsgi-file mio/pymio-uwsgi.py --tornado 100 --greenlet \
      --zerg-server /dev/shm/mutalisk --enable-threads -lazy-apps \
      --master --thunder-lock --processes=8
