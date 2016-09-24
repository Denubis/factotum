#!/usr/bin/python2.7
'''
FactoryFactoum -- a CLI for managing the headless linux factorio server
By: Brian Ballsun-Stanton
GPL v3

Usage
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

import time

import click
from daemonocle.cli import DaemonCLI

@click.command(cls=DaemonCLI, daemon_params={'pidfile': '/var/run/example.pid'})
def main():
    """This is my awesome daemon. It pretends to do work in the background."""
    while True:
        time.sleep(10)

if __name__ == '__main__':
    main()    
  '''