#!/bin/bash


./headlessFactorio/updateFactorio.sh
./headlessFactorio/newMap.sh
./headlessFactorio/newFactorioPassword.sh

hold=' '
printf "Press 'SPACE' to continue or 'CTRL+C' to exit : "
tty_state=$(stty -g)
stty -icanon
until [ -z "${hold#$in}" ] ; do
    in=$(dd bs=1 count=1 </dev/tty 2>/dev/null)
done
stty "$tty_state"


./headlessFactorio/runFactorio.sh