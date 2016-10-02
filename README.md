# Headless Factorio Server Scripts
Scripts for a headless factorio
By: Brian Ballsun-Stanton and James Zhao

Usage:

* `headlessFactorio/setupFactotum.sh`
   * This deploys necessary packages onto the server, installs factorio to /opt/factorio (put alternate path in factorioPath.conf if necessary), gets the authentication token, provides basic data to the server config file and sets a random password, and generates a fresh map.
* `headlessFactorio/doIt.sh`
   * This updates the server and then runs FactoryFactotum factorio start
* `headlessFactorio/FactoryFactotum --help`
   * This provides all Factory Factotum commands.
* `headlessFactorio/FactoryFactotum factorio start`
   * This starts the factorio headless server in daemon mode with latest save.
* `headlessFactorio/FactoryFactotum factorio stop`
   * This asks the headless server to stop. Politely. It will take some time and will likely report failed.
* `headlessFactorio/FactoryFactotum factorio status`
   * This reports on the status of the server.            


