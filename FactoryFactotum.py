#!/usr/bin/env python
from __future__ import print_function

'''
FactoryFactoum -- a CLI for managing the headless linux factorio server
By: Brian Ballsun-Stanton
GPL v3

Usage
'''
'''
import click

@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name',
              help='The person to greet.')
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo('Hello %s!' % name)

if __name__ == '__main__':
    hello()

'''


import time

import click
from daemonocle.cli import DaemonCLI

import os
import tempfile
import subprocess
import time
import json
import codecs
import ptyprocess
import io


@click.group()
@click.option('--factoriopath', default="/opt/factorio", help='Default /opt/factorio. Path to install/update factorio and the path of the factorio installation to use.', type=click.Path())
@click.pass_context
def cli0(ctx, factoriopath):
	print(factoriopath)

@click.group()
def cli1():
	pass

@cli1.command(cls=DaemonCLI, daemon_params={'pidfile': '/tmp/factorio.pid'})
@click.option('--serverpassword', help='To set the server password')
@click.option('--genServerPasswordWords','-g', default=4, help='Default 4. Generate a random password with this many words.')

@click.option('--newMap', help='Create a mapseettings.json file in this directory and generate a new map before launching server.')
@click.option('--newMapPath', help='Generate a new map when first launched from alternate mapsettings.json.', type=click.File())

#@click.option('--save', help="file and path of the save file to use. Otherwise it will use the most recent save in the saves folder of factorio.", type=click.File())
def factorio():
    """Factotum for Factorio server stuff. Runs the server. Start with `factorio start`. Help with `factorio --help`."""
    print("hi")
    while True:
        time.sleep(10)

@click.group()
@click.pass_context
def cli2(ctx):

	print(ctx)
    

@cli2.command()
@click.pass_context
@click.option('--servername', prompt=True,  help="Name of the server for public listings.")
@click.option('--description', prompt=True, help="Description of the server for public listings.")
@click.option('--visibility', default="public", help="Default: public. public/lan/hidden")
@click.option('--tag','-t', help="Tags for the server list.", multiple=True)

def setup(ctx, servername, description, tag, visibility):
	"""Setup tasks for deploying a server."""

	print(servername, description, [x for x in tag], visibility, ctx.obj)
	
	if os.path.isfile("%s/config/settings.json" % (factoriopath)):
		with codecs.open("%s/config/settings.json" % (factoriopath), 'r+', encoding='utf-8') as settings_file:

			settingsJson = json.load(settings_file)
			settingsJson['name'] = servername
			settingsJson['description'] = description
			settingsJson['tags'] = [x for xs in tag]
			settingsJson['visibility'] = visibility
			
			settings_file.seek(0)
			json.dump(settingsJson, settings_file, indent=4)
	else:
		updated_settings="""{
  "name": "%s",
  "description": "%s",
  "tags": %s,
  "max_players": "0",

  "_comment_visibility": ["public: Game will be published on the official Factorio matching server",
                          "lan: Game will be broadcast on LAN",
                          "hidden: Game will not be published anywhere"],
  "visibility": "%s",

  "_comment_credentials": "Your factorio.com login credentials. Required for games with visibility public",
  "username": "",
  "password": "",

  "_comment_token": "Authentication token. May be used instead of 'password' above.",
  "token": "",

  "game_password": "",

  "_comment_verify_user_identity": "When set to true, the server will only allow clients that have a valid Factorio.com account",
  "verify_user_identity": true,
  "_commend_max_upload_in_kilobytes_per_second" : "optional, default value is 0. 0 means unlimited.",
  "max_upload_in_kilobytes_per_second": 0
}
""" % (servername, description, [x for x in tag], visibility)
		with open("%s/config/settings.json" % (factoriopath), 'w') as settings_file:
			settings_file.write(updated_settings)
			settings_file.close()

@click.group()
def cli3():
	pass

@cli3.command()
@click.option('--username', prompt=True,  help="Name of the server for public listings.")
@click.option('--password', prompt=True, hide_input=True, help="Description of the server for public listings.")

def authenticate(username, password, factoriopath):
	"""Save an authentication token from factorio"""
	print("Fetching token for %s" %  (username))
	if not os.path.isfile("%s/bin/x64/factorio" % (factoriopath) ):
		print("Could not find factorio at %s" % (factoriopath))
		sys.exit(1)
	else:
		settings="""{
  "name": "Name of the game as it will appear in the game listing",
  "description": "Description of the game that will appear in the listing",
  "tags": ["game", "tags"],
  "max_players": "0",

  "_comment_visibility": ["public: Game will be published on the official Factorio matching server",
                          "lan: Game will be broadcast on LAN",
                          "hidden: Game will not be published anywhere"],
  "visibility": "hidden",

  "_comment_credentials": "Your factorio.com login credentials. Required for games with visibility public",
  "username": "%s",
  "password": "%s",

  "_comment_token": "Authentication token. May be used instead of 'password' above.",
  "token": "",

  "game_password": "",

  "_comment_verify_user_identity": "When set to true, the server will only allow clients that have a valid Factorio.com account",
  "verify_user_identity": true,
  "_commend_max_upload_in_kilobytes_per_second" : "optional, default value is 0. 0 means unlimited.",
  "max_upload_in_kilobytes_per_second": 0
}
""" % (username, password)
		try:
			f = tempfile.NamedTemporaryFile()
			f.write(settings)
			f.seek(0)
			#print f.read()
			print("Settings file: %s" % (f.name))
			factorio = ptyprocess.PtyProcessUnicode.spawn(["%s/bin/x64/factorio" % (factoriopath), "--start-server-load-latest", "--server-settings", f.name ])
			
			time.sleep(5)					
			factorio.write("/quit\n")
			
			
			
			with open("%s/player-data.json" % (factoriopath)) as data_file:
				data = json.load(data_file)

			print(data['service-username'], data['service-token'])


			if os.path.isfile("%s/config/settings.json" % (factoriopath)):
				with codecs.open("%s/config/settings.json" % (factoriopath), 'r+', encoding='utf-8') as settings_file:
					settingsJson = json.load(settings_file)
					settingsJson['service-token'] = data['service-token']
					settingsJson['service-username'] = data['service-username']
					settings_file.seek(0)
					json.dump(settingsJson, settings_file, indent=4)
			else:
				updated_settings="""{
  "name": "Name of the game as it will appear in the game listing",
  "description": "Description of the game that will appear in the listing",
  "tags": ["game", "tags"],
  "max_players": "0",

  "_comment_visibility": ["public: Game will be published on the official Factorio matching server",
                          "lan: Game will be broadcast on LAN",
                          "hidden: Game will not be published anywhere"],
  "visibility": "hidden",

  "_comment_credentials": "Your factorio.com login credentials. Required for games with visibility public",
  "username": "%s",
  "password": "",

  "_comment_token": "Authentication token. May be used instead of 'password' above.",
  "token": "%s",

  "game_password": "",

  "_comment_verify_user_identity": "When set to true, the server will only allow clients that have a valid Factorio.com account",
  "verify_user_identity": true,
  "_commend_max_upload_in_kilobytes_per_second" : "optional, default value is 0. 0 means unlimited.",
  "max_upload_in_kilobytes_per_second": 0
}
""" % (data['service-username'], data['service-token'])
				with open("%s/config/settings.json" % (factoriopath), 'w') as settings_file:
					settings_file.write(updated_settings)
					settings_file.close()

		finally:
			f.close()



cli = click.CommandCollection(sources=[cli1, cli2, cli3])

if __name__ == '__main__':
    cli()    

