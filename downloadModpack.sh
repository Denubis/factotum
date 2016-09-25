#!/bin/bash
set -euo pipefail

rm "$2"

rm -r /opt/factorio/mods

gdrive download $1

7z x -o/opt/factorio/mods "$2"