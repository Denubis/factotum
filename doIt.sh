#!/bin/bash
set -euo pipefail

./headlessFactorio/updateFactorio.sh
./headlessFactorio/newMap.sh
./headlessFactorio/newFactorioPassword.sh
read -rsp $'Press any key to continue...\n' -n1 key
./headlessFactorio/runFactorio.sh