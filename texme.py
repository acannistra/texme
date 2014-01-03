#!/usr/bin/env python

# texme: a script for managing LaTeX templates, by Tony Cannistra

import argparse
from sys import argv
import os
import json
import pystache
from pystache import render
from pystache import defaults
from shutil import copy as filecopy

DEFAULT_DIRNAME = ".texme"
DEFAULT_CONFIG  = "config.json"
defaults.DELIMITERS = ('[[', ']]')

# parse arguments and dispatch to methods that do the hard work

def main():
	# toplevel parser for getting mode
	parser = argparse.ArgumentParser(description="a tool for managing LaTeX templates")

	subparsers = parser.add_subparsers(help="subcommand help", dest="mode")

	# parser for 'init' command
	parser_init = subparsers.add_parser('init', help='begin template management in current directory')


	# parser for 'new' command
	parser_new = subparsers.add_parser('new', help="create a new LaTeX document from template")
	parser_new.add_argument('file', nargs='?', 
		default="rendered.tex", help="file to place rendered template into")

	# parser for 'template'
	parser_template = subparsers.add_parser('template', 
										    help="install mustache template from file.")
	parser_template.add_argument('file', help="template filename")

	# parser for 'edit'
	parser_edit = subparsers.add_parser('edit', help="open an editor to change the configuation file")

	args = parser.parse_args()

	mode = args.mode

	if(mode == 'init'): 
		if init():
			status('n', "initialization successful")
			return 0
		else:
			status('e', "initialization failed")
			return 1
	if(mode == 'new') : 
		if new(DEFAULT_CONFIG, args.file):
			status('n', "creation successful")
			return 0
		else:
			status('e', "creation failed")
			return 0
	if(mode == "edit"):
		edit()
	if(mode == "template"):
		if template(args.file):
			status('n', "template install successful")
			return 0
		else:
			status('e', "template install failed")
			return 0


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

	config_file = open(DEFAULT_CONFIG, 'a')
	status('s', "config file created")	
	return True


# returns true if "dir" represents a valid texme install, false otherwisels

def check_install(dir):
	if not os.path.exists(dir): 
		status('e', "not a texme directory. be sure to initialize first.")
		return False
	if not os.path.exists(dir+"/"+DEFAULT_CONFIG):
		status('e', "no configuration file found. something broke.")
		return False

	return True


# edit config.json file in an editor
def edit():
	pass

# create a new document based on template.

def new(config, outfile):
	if not check_install(DEFAULT_DIRNAME): return False

	os.chdir(DEFAULT_DIRNAME)
	config = load_config(config)
	os.chdir("..")
	to_template = {}

	if "template" not in config:
		status('e', "no template installed. see help for details.")
		return False

	if "variables" in config:
		vars = config['variables']
		for i, var in enumerate(vars):
			to_template[var['name']] = raw_input(var['name']+": ")
	else:
		status("s", "no variables")

	if "defaults"  in config:
		defaults = config['defaults']
	else:
		status('s', "no defaults")

	outfile_fp = open(outfile, 'w')
	outfile_fp.write(render_template(config['template'], to_template));
	
	
	return 1

# take a template file and a mapping, 
#returns a string containing the rendered template
def render_template(template_file, map):
	template = open(template_file).read()
	return pystache.render(template, map)

#gets config JSON file.
def load_config(file):
	try:
		return json.loads(open(file).read())
	except ValueError as e:
		return {}

#writes JSON to config file
def write_config(config_json):
	config = open(DEFAULT_CONFIG, 'w');
	config.write(json.dumps(config_json))


# print status message, 
# 	type = 'e' is an error, = 'w' is a warning, = 's' is status
def status(type, message):
	final = ""
	abort = False
	if type == 'e': final = final + "[ERROR] "; 
	if type == 'w': final = final + "[WARNING] ";
	if type == 's': final = final + '[note] '
	print final + message

# installs template into config file and copies it into 
# install directory

def template(file):
	if not check_install(DEFAULT_DIRNAME): return False
	file_abs = os.path.abspath(file);
	os.chdir(DEFAULT_DIRNAME)
	config = load_config(DEFAULT_CONFIG)

	if "template" in config: 
		answer = raw_input("[WARNING] template file \""+config['template']+"\" already installed, "+
						   "this action will overwrite it with "+file+". Continue? [y/n]: ")
		if answer != 'y': return False


	config['template'] = file
	filecopy(file_abs, file)

	write_config(config)
	return True

if __name__ == "__main__":
	main()