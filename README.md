# A Factotum for Headless Factorio!
A python manager to deploy and run headless factorio servers.
By: Brian Ballsun-Stanton, Andrew Ardill, and James Zhao

Released under the GPL v3 License, 2016.
No warranty of any kind, folks.

## Installation:

### On ubuntu 14.04/16.04:

```sudo apt update && sudo apt install python3-pip -y && echo /opt/factorio > $HOME/.factorioPath && sudo pip3 install factotum && factotum fulldeploy && source $HOME/.bashrc```	

### On other systems:

```sudo pip3 install factotum```

## Usage:

* `factotum --help`
   * This provides all Factory Factotum commands.
* `factotum COMMAND --help`
   * This provides help for each Factory Factotum command.

* `factotum fulldeploy`
   * Runs install, authenticate, newmap, setup.
* `factotum install`
	* Installs factorio (default /opt/factorio, override with a new path in ~/.factorioPath)
* `factotum authenticate --username <Username>`
	* Gets your authentication token from factorio servers so your password isn't stored in plaintext.
* `factotum newmap`
	* Generates a new map from a config file in FACTORIOHOME/config/mapsettings.json
* `factotum setup --servername "Server Name Here" --description "Server Description Here" --tag "Tag 1" --tag "Tag n"`
	* Configures the settings.json file including setting a password of 4 diceware words.
* `factotum factorio start`
   * This starts the factorio headless server in daemon mode with latest save.
* `factotum factorio stop`
   * This asks the headless server to stop. Politely. It will take some time and will likely report failed.
* `factotum factorio status`
   * This reports on the status of the server.      
* `factotum rcon /help`
   * This sends commands into an already running server started by factotum.         


