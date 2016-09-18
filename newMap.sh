#!/bin/bash

set -euo pipefail

mkdir -p factorioSave
/opt/factorio/bin/x64/factorio --create /home/factorio/factorioSave/$(date +%Y%m%d)

