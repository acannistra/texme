#!/usr/bin/env python

# texme: a script for managing LaTeX templates, by Tony Cannistra

import argparse
from sys import argv

def main():
	# toplevel parser for getting mode
	parser = argparse.ArgumentParser(description="a tool for managing LaTeX templates")
	parser.add_argument('mode')
	subparsers = parser.add_subparsers(help="subcommand help")

	# parser for 'init' command
	parser_init = subparsers.add_parser('init', help='initalize a new templating directory')
	parser_init.add_argument('dir', help="base directory for new template manager, uses current as default")

	# parser for 'new' command
	

