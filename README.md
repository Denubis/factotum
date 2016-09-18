# headlessFactorio
Scripts for a headless factorio
By: Brian Ballsun-Stanton

Usage:

* `headlessFactorio/updateFactorio.sh`
	* Downloads and unpacks latest headless experimental factorio build into /opt
* `headlessFactorio/newMap.sh`
	* Creates factorioSave in current directory and makes a map with today's date there.
* `headlessFactorio/runFactorio.sh` `[$1]`
	* Looks in factorioSave for the latest .zip and runs that, or takes an argument of a save
* `headlessFactorio/pullSaves.sh` `<$1>`
	* Takes an argument of an authorised ssh server. Extracts saves and files established by this script from that server and pulls onto present server
* `headlessFactorio/newFactorioPassword.sh` `[$1]`
	* Takes an optional argument of a password. Otherwise creates a random 4 word password from the diceware list. This is not a crpytographically secure usage. Sets the factorio join password to be that password.


