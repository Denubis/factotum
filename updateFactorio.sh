#!/bin/bash
set -euo pipefail

if [ ! -w /opt ] ; then 
        echo 'Please allow $(whoami) to write to /opt'; 
        exit 1 
fi

wget https://www.factorio.com/get-download/latest/headless/linux64 -O /tmp/latestFactorio.tar.gz

cd /opt
tar -xzf /tmp/latestFactorio.tar.gz


