#!/bin/bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
	if [ -z "$#" ]; then
	echo -e "command is empty. please enter arguments"
	exit 1  
	fi
fi
if [ -a "$2" ]; then
        echo "deleting existing modpack install"
        rm "$2"
fi

if [ -w /opt/factorio/mods ]; then
        echo "deleting existing mods in factorio"
        rm -r /opt/factorio/mods
fi

gdrive download $1

7z x -o/opt/factorio/mods "$2"
