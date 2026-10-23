#!/usr/bin/env bash
set -euo pipefail
# Freeze native packages as well as the base image. Never resolve against "today".
printf 'APT::Snapshot "20261023T000000Z";\n' > /etc/apt/apt.conf.d/50soly-snapshot
apt-get -o Acquire::Check-Valid-Until=false update
if [ "${1:-runtime}" = build ]; then
    packages=(build-essential curl libssl-dev zlib1g-dev libbz2-dev libreadline-dev
              libsqlite3-dev libffi-dev liblzma-dev libgdbm-dev uuid-dev)
else
    packages=(ca-certificates libssl3t64 zlib1g libbz2-1.0 libreadline8t64
              libsqlite3-0 libffi8 liblzma5 libgdbm6t64 libuuid1)
fi
apt-get -o Acquire::Check-Valid-Until=false install -y --no-install-recommends "${packages[@]}"
rm -rf /var/lib/apt/lists/*
