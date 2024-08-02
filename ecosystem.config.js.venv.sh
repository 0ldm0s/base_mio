#!/usr/bin/env bash
export PYTHON_VERSION=3.12.4
export PYENV_ROOT="$HOME/work-env"
export PYTHONHOME="$PYENV_ROOT"
cat <<EOF >| ~/ecosystem.config.js
module.exports = {
  apps: [
    {
      name: "base_mio",
      cwd: "$HOME/base_mio",
      args: ["--ini", "app.venv.ini"],
      script: "$HOME/bin/uwsgi",
      merge_logs: true,
      env: {
        PYTHONIOENCODING: "utf-8",
        PYTHONUNBUFFERED: 1,
        MIO_CONFIG: "production",
        MIO_LIMIT_CPU: "0",
        PYTHONMALLOC: "malloc",
        LD_PRELOAD: "/usr/lib/x86_64-linux-gnu/libtcmalloc.so",
      }
    },
  ]
}
EOF
