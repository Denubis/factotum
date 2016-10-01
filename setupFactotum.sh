#!/bin/bash
set -euo pipefail

sudo apt-get update && sudo apt-get install -y libzmq-dev libevent-dev python-dev python-pip python-dev build-essential

pip install --user click ptyprocess clint circus daemonocle requests python-valve

mkdir -p $HOME/bin


ln -sf "$(git rev-parse --show-toplevel)/FactoryFactotum.py" $HOME/bin/FactoryFactotum

if [ -w /opt/factorio ]; then
	echo "/opt/factorio" > $HOME/.factorioPath
else
	echo "$HOME/factorio" > $HOME/.factorioPath
fi


FactoryFactotum install
FactoryFactotum authenticate
FactoryFactotum setup
FactoryFactotum newmap




