#!/usr/bin/env python


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


@click.command(cls=DaemonCLI, daemon_params={'pidfile': '/tmp/factorio.pid'})
@click.option('--serverpassword/--noserverpassword', help='To set the server password / To remove the server password. Overrides genpassword')
@click.option('--genServerPasswordWords','-g', default=4, help='Default 4. Generate a random password with this many words.')
@click.option('--factorioPath', default="/opt/factorio", help='Default /opt/factorio. Path to install/update factorio and the path of the factorio installation to use.', type=click.Path())
@click.option('--save', help="file and path of the save file to use. Otherwise it will use the most recent save in the saves folder of factorio.", type=click.File())
@click.option('--servername',  help="Name of the server for public listings.")
@click.option('--description', help="Description of the server for public listings.")
@click.option('--tag','-t', help="Tags for the server list.", multiple=True)
@click.option('--username', help="Factorio username.")
@click.option('--password', help="Factorio password (will be used to get token).")
@click.option('--newMap', help='Default: mapsettings.json. Generate a new map when first launched. Creates a mapsettings.json in local directory if not already there to pull options from. Provide path to alternate mapsettings.json if desired.', type=click.File())


def main():
    """Factotum for Factorio server stuff. Runs the server."""
    print "hi"
    while True:
        time.sleep(10)

if __name__ == '__main__':
    main()    
  