"""Immosearch's main configuration"""

from configparser import ConfigParser

__all__ = ['core', 'db']

CONFIG_FILE = '/etc/immosearch.conf'

config = ConfigParser()
config.read(CONFIG_FILE)

core = config['core']
db = config['db']
www = config['www']
