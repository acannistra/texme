#!/usr/bin/env python

# texme: a script for managing LaTeX templates, by Tony Cannistra

import argparse
from sys import argv
import os

DEFAULT_DIRNAME = ".texme"

# parse arguments and dispatch to methods that do the hard work

def main():
	# toplevel parser for getting mode
	parser = argparse.ArgumentParser(description="a tool for managing LaTeX templates")

	subparsers = parser.add_subparsers(help="subcommand help", dest="mode")

	# parser for 'init' command
	parser_init = subparsers.add_parser('init', help='begin template management in current directory')


	# parser for 'new' command
	parser_new = subparsers.add_parser('new', help="create a new LaTeX document from template")
	# what to do here..

	# parser for 'template'
	parser_template = subparsers.add_parser('template', 
										    help="install new mustache template from file.")

	args = parser.parse_args()

	mode = args.mode

	if(mode == 'init'): 
		if init():
			status('n', "initialization successful")
			return 0
		else:
			status('e', "initialization failed")
			return 1
	if(mode == 'new') : new()

# initialize a new directory only if a texme 
# install does not already exist.

def init():
	status('s', "initializing new texme directory")
	try:
		os.mkdir(DEFAULT_DIRNAME)
	except OSError as e:
		if e[0] == 17: # file exists
			status ('e', "whoops, a texme directory already exists at this location.")
			return False
	else:
		status('s', "texme directory created")
		os.chdir(DEFAULT_DIRNAME)

	config_file = open('config.json', 'a')
	status('s', "config file created")	
	return True


# returns true if "dir" represents a valid texme install, false otherwisels

def check_install(dir):
	if not os.path.exists(dir): 
		status('e', "not a texme directory. be sure to initialize first.")
		return False
	if not os.path.exists(dir+"/config.json"):
		status('e', "no configuration file found. something broke.")
		return False

	return True




# create a new document based on template.

def new():
	print os.getcwd()
	if not check_install(DEFAULT_DIRNAME): exit(1)




# print status message, 
# 	type = 'e' is an error, = 'w' is a warning, = 's' is status
def status(type, message):
	final = ""
	abort = False
	if type == 'e': final = final + "[ERROR] "; 
	if type == 'w': final = final + "[WARNING] ";
	if type == 's': final = final + '[note] '
	print final + message




if __name__ == "__main__":
	main()