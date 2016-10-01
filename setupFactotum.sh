#!/bin/bash

sudo apt-get update && sudo apt-get install -y libzmq-dev libevent-dev python-dev python-pip python-dev build-essential


pip install --user click ptyprocess clint circus daemonocle requests
 
./headlessFactorio/FactoryFactotum install
./headlessFactorio/FactoryFactotum authenticate
./headlessFactorio/FactoryFactotum setup
./headlessFactorio/FactoryFactotum newmap




