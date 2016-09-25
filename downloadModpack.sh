#!/bin/bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
	if [ -z "$#" ]; then
	echo -e "command is empty. please enter arguments"
        exit 1
	fi
fi
rm "$2"

rm -r /opt/factorio/mods

./gdrive download $1

7z x -o/opt/factorio/mods "$2"