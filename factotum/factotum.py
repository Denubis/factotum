"""
FactoryFactoum -- a CLI for managing the headless linux factorio server
By: Brian Ballsun-Stanton
GPL v3
"""

import os
import click
import time
import subprocess
import json
import codecs
import sys
import circus
import inspect
import signal
import glob

from daemonocle.cli import DaemonCLI

from .update import safeInstall, safeUpdate
from .factoriopath import getFactorioPath
from .diceware import generatePhrase
from .newmap import newFactorioMap
from .settings import configSetup, configAuthenticate, getPassword
from .rcon import rconCmd



def runFactorio(stdin=True):
	if stdin:
		print("Interactive mode enabled. Server can only be quit with ctrl-C. /quit will only restart the server.")
	FACTORIOPATH = getFactorioPath()

	phrase = generatePhrase(6)
	with open("/tmp/factorioRcon", "w") as phraseFile:
		phraseFile.write(phrase)

	with codecs.open("%s/config/settings.json" % (FACTORIOPATH), 'r+', encoding='utf-8') as settings_file:
		try:
			settingsJson = json.load(settings_file)
		except Exception as e:
			print("Problem with settings file.")
			print(e)
			sys.exit(1)


	if not filter(os.path.isfile, glob.glob('%s/saves/*.zip' % (FACTORIOPATH))):
		print("Cannot find a save file. Exiting.")
		sys.exit(1)

	myprogram = {"cmd": "%s/bin/x64/factorio --rcon-port 27015 --rcon-password \"%s\" --start-server-load-latest --server-settings %s/config/settings.json" % (FACTORIOPATH, phrase, FACTORIOPATH) , "numprocesses": 1, "stop_timeout": 20, "close_child_stdin":stdin}

	arbiter = circus.get_arbiter([myprogram])
	try:
		arbiter.start()
	finally:
		os.remove("/tmp/factorioRcon")
		arbiter.stop()
		print(subprocess.check_output(['tail', '-13', '%s/factorio-current.log'%FACTORIOPATH]).decode("unicode_escape"))

@click.group()
def cli():
	pass

@click.command(cls=DaemonCLI, daemon_params={'pidfile': '/tmp/factorio.pid'})
def factorio():
	"""Factotum for Factorio server stuff. Runs the server. Start with `factorio start`. Help with `factorio --help`."""
	runFactorio()
		



@click.command()
def password():
	"""Get the server game password"""
	print("The server password is: \"%s\" " % (getPassword()))


@click.argument("cmd", nargs=-1)	

@click.command()
def rcon(cmd):
	"""Pass an rcon command to the server. Find out possible by saying rcon /help"""
	rconCmd(cmd)


@click.command()
def update():
	"""Download and unpack latest factorio."""
	safeUpdate()
		

@click.command()
def newMap():
	"""Generate a new map."""
	newFactorioMap()
		


@click.command()
def install():
	"""Create the FACTORIOPATH directory, then download and unpack factorio.""" 
	safeInstall()


@click.command()
@click.option('--servername', help="Name of the server for public listings.")
@click.option('--description',  help="Description of the server for public listings.")
@click.option('--visibility', default="public", help="Default: public. public/lan/hidden")
@click.option('--serverpassword', help='To set the server password')
@click.option('--genServerPasswordWords','-g', default=4, help='Default 4. Generate a random password with this many words.')
@click.option('--tag','-t', help="Tags for the server list.", multiple=True)
@click.option('--admins','-a', help="Set default admin names.", multiple=True)
@click.option('--ignorePlayerLimit/--noIgnorePlayerLimit', help="Enable/Disable ignore Player Limit for returing players.")
@click.option('--afk', help='Set the afk timeout in minutes')
@click.option('--uploadrate', help='Upload limit in kbps', type=click.INT)
@click.option('--UpdatePassword/--noUpdatePassword', '-u/-n', help="Don't change the json password", default=True)


def setup(servername, description, tag, visibility, serverpassword, genserverpasswordwords, admins, ignoreplayerlimit, afk, uploadrate, updatepassword):
	"""Setup tasks for deploying a server."""
	configSetup(servername, description, tag, visibility, serverpassword, genserverpasswordwords, admins, ignoreplayerlimit, afk, uploadrate, updatepassword)

@click.command()
@click.option('--username', prompt=True,  help="Name of the server for public listings.")
@click.option('--password', prompt=True, hide_input=True, help="Description of the server for public listings.")

def authenticate(username, password):
	"""Save an authentication token from factorio"""
	configAuthenticate(username, password)



@click.command()
@click.option('--genServerPasswordWords','-g', default=4, help='Default 4. Generate a random password with this many words.')
def diceware(genserverpasswordwords):
	"""Generates a diceware password for the user."""
	print(generatePhrase(genserverpasswordwords))

@click.command()
@click.option('--username', prompt=True,  help="Name of the server for public listings.")
@click.option('--password', prompt=True, hide_input=True, help="Description of the server for public listings.")
@click.option('--servername', prompt=True, help="Name of the server for public listings.")
@click.option('--description', prompt=True, help="Description of the server for public listings.")
@click.option('--tag','-t', prompt=True, help="Tag for the server list. (You can deploy multiple with factotum setup")
@click.option('--admin','-a',prompt=True, help="Set default admin (You can deploy multiple with factotum setup).")

def fulldeploy( username, password, servername, description, tag, admin):
	"""Completely deploy a factorio server. Prompt for install, authenticate, setup, and newmap"""
	safeInstall()
	configAuthenticate(username, password)
	newFactorioMap()
	configSetup(servername=servername, 
				description=description, 
				tag=tag, 
				visibility="public", 
				serverpassword=None, 
				genserverpasswordwords=4, 
				admins=admin, 
				ignoreplayerlimit=True, 
				afk=5, 
				uploadrate=None, 
				updatepassword=True)
	runFactorio(False)
	
	
	

@click.command()
def start():
	"""Shortcut for factorio start."""
	factorio()

@click.command()
def interactive():
	"""Run factorio in the shell, interactively."""
	runFactorio(False)	

@click.command()
def stop():
	"""Shortcut for factorio stop."""
	try:
		FACTORIOPATH = getFactorioPath()
		with open('/tmp/factorio.pid', 'r') as pidfile:
			pid = int(pidfile.read().strip())
			os.kill(pid, signal.SIGINT)
		print("SIGINT sent")
		time.sleep(10)
	except FileNotFoundError:
		print("Cannot find pid. Factorio has not been started.")		
	print(subprocess.check_output(['tail', '-13', '%s/factorio-current.log'%FACTORIOPATH]).decode("unicode_escape"))



cli.add_command(password)
cli.add_command(factorio)
cli.add_command(rcon)
cli.add_command(update)
cli.add_command(newMap)
cli.add_command(install)
cli.add_command(setup)
cli.add_command(authenticate)
cli.add_command(fulldeploy)
cli.add_command(diceware)
cli.add_command(start)
cli.add_command(stop)
cli.add_command(interactive)




if __name__ == '__main__':
	cli()    
