#!/usr/bin/env bash
export PYTHON_VERSION=3.12.4
export PYENV_ROOT="$HOME/.pyenv"
export PYTHONHOME="$PYENV_ROOT/versions/$PYTHON_VERSION"
cat <<EOF >~/ecosystem.config.js
module.exports = {
  apps: [
    {
      name: "maker-api",
      cwd: "$HOME/maker-api",
      args: ["--ini", "app.ini"],
      script: "$HOME/bin/uwsgi",
      merge_logs: true,
      env: {
        PYTHONIOENCODING: "utf-8",
        PYTHONUNBUFFERED: 1,
        PYTHON_VERSION: "$PYTHON_VERSION",
        PYENV_ROOT: "$HOME/.pyenv",
        PYTHONHOME: "$PYENV_ROOT/versions/$PYTHON_VERSION",
        MIO_CONFIG: "production",
        MIO_LIMIT_CPU: "0",
        PYTHONMALLOC: "malloc",
        LD_PRELOAD: "/usr/lib/libtcmalloc.so",
      }
    },
    {
      name: "maker-watchdog",
      cwd: "$HOME/maker-api",
      args: ["cli", "exe", "-cls=cli.WatchDog.Daemon.do_run"],
      script: "$PYTHONHOME/bin/flask",
      interpreter: "$PYTHONHOME/bin/python",
      merge_logs: true,
      env: {
        PYTHONIOENCODING: "utf-8",
        PYTHONUNBUFFERED: 1,
        PYTHON_VERSION: "$PYTHON_VERSION",
        PYENV_ROOT: "$HOME/.pyenv",
        PYTHONHOME: "$PYENV_ROOT/versions/$PYTHON_VERSION",
        FLASK_APP: "mio.shell",
        MIO_CONFIG: "production",
        MIO_LIMIT_CPU: "0",
        PYTHONMALLOC: "malloc",
        LD_PRELOAD: "/usr/lib/libtcmalloc.so",
      }
    },
    {
      name: "maker-celery",
      cwd: "$HOME/maker-api",
      args: ["celery", "run", "--app=cli.celery.Worker.celery_app", "--worker=hostname=pymio@%h without-heartbeat loglevel=INFO B E"],
      script: "$PYTHONHOME/bin/flask",
      interpreter: "$PYTHONHOME/bin/python",
      merge_logs: true,
      env: {
        PYTHONIOENCODING: "utf-8",
        PYTHONUNBUFFERED: 1,
        PYTHON_VERSION: "$PYTHON_VERSION",
        PYENV_ROOT: "$HOME/.pyenv",
        PYTHONHOME: "$PYENV_ROOT/versions/$PYTHON_VERSION",
        FLASK_APP: "mio.shell",
        MIO_CONFIG: "production",
        MIO_LIMIT_CPU: "0",
        PYTHONMALLOC: "malloc",
        LD_PRELOAD: "/usr/lib/libtcmalloc.so",
      }
    },
  ]
}
EOF
