#!/bin/bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
	echo "please state server to pull settings from"
	exit 1
fi

ssh $1 "test -e /opt/factorio/config/settings.json"

if [ $? -eq 1 ]; then
    echo "cannot find settings.json on remote server. Nothing to copy"
    exit 1
fi

scp -r $1:/opt/factorio/saves /opt/factorio/saves
scp -r $1:/opt/factorio/config /opt/factorio/config
scp -r $1:/opt/factorio/mods /opt/factorio/mods
scp $1:/opt/factorio/banlist.json /opt/factorio/banlist.json
scp -r $1:factorioSave factorioSave
