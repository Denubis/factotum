#!/bin/bash
set -euo pipefail

if [ ! -w /opt/factorio/config/settings.json ]; then
	echo "cannot find /opt/factorio/config/settings.json"
	exit 1
fi


if [ ! -w diceware.wordlist.asc ]; then
	wget http://world.std.com/~reinhold/diceware.wordlist.asc -O diceware.wordlist.asc
fi	


if [ "$#" -ne 1 ]; then
	FACTORIOPASSWORD=$(shuf --random-source /dev/urandom diceware.wordlist.asc | head -n 4 | cut -f 2 | tr '\n' ' ' | sed -e 's/[[:space:]]*$//' || true)
else
	FACTORIOPASSWORD=$1	
fi

echo "/\"game_password\": \".*\"/\"game_password\": \"$FACTORIOPASSWORD\"/"
sed -i "/\"game_password\": \".*\"/\"game_password\": \"$FACTORIOPASSWORD\"/" /opt/factorio/config/settings.json

echo -e "\n\n***********\n\nYour factorio password is: $FACTORIOPASSWORD"

