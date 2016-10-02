# Headless Factorio Server Scripts
Scripts for a headless factorio
By: Brian Ballsun-Stanton and James Zhao


Installation:

* ```sudo apt update && sudo apt install python3-pip -y && sudo pip3 install FactoryFactotum && sudo mkdir -p /opt/factorio && sudo chown $USER /opt/factorio && FactoryFactotum install && source $HOME/.bashrc && echo /opt/factorio > $HOME/.factorioPath```	

Usage:

* `FactoryFactotum --help`
   * This provides all Factory Factotum commands.
* `FactoryFactotum COMMAND --help`
   * This provides help for each Factory Factotum command.


* `FactoryFactotum install`
	* Installs factorio (default /opt/factorio, override with a new path in ~/.factorioPath)
* `FactoryFactotum authenticate --username <Username>`
	* Gets your authentication token from factorio servers so your password isn't stored in plaintext.
* `FactoryFactotum newmap`
	* Generates a new map from a config file in FACTORIOHOME/config/mapsettings.json
* `FactoryFactotum setup --servername "Server Name Here" --description "Server Description Here" --tag "Tag 1" --tag "Tag n"`
	* Configures the settings.json file including setting a password of 4 diceware words.
* `FactoryFactotum factorio start`
   * This starts the factorio headless server in daemon mode with latest save.
* `FactoryFactotum factorio stop`
   * This asks the headless server to stop. Politely. It will take some time and will likely report failed.
* `FactoryFactotum factorio status`
   * This reports on the status of the server.      
* `FactoryFactotum rcon /help`
   * This sends commands into an already running server.         


