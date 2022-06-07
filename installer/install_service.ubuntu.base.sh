#!/bin/bash
cat > /usr/local/www/${1}/${2}/init_system.sh <<-EOF
#!/bin/bash
mkdir -p /run/${2}/
chown -R ${1}:${1} /run/${2}/
EOF
cat > /lib/systemd/system/${2}.service <<-EOF
[Unit]
Description=${2}
After=network.target

[Service]
User=${1}
LimitNPROC=infinity
LimitNOFILE=infinity
LimitFSIZE=infinity
LimitCPU=infinity
LimitAS=infinity
ExecStart=/usr/local/www/${1}/${2}/run_webserver.sh
ExecStop=/usr/local/www/${1}/${2}/stop_webserver.linux ${2}

[Install]
WantedBy=multi-user.target
EOF
