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
	args = parse_arguments()
	return texme(args)
	

#parses command line arguments, returns an argparse namespace
def parse_arguments():
	# toplevel parser for getting mode
	parser = argparse.ArgumentParser(description="a tool for managing LaTeX templates")

	subparsers = parser.add_subparsers(help="subcommand help", dest="mode")

	# parser for 'init' command
	parser_init = subparsers.add_parser('init', help='begin template management in current directory')


	# parser for 'new' command
	parser_new = subparsers.add_parser('new', help="create a new LaTeX document from template")
	parser_new.add_argument('file', nargs='?', 
		default="rendered.tex", help="rendered template outfile_fp")

	# parser for 'template'
	parser_template = subparsers.add_parser('template', 
										    help="install mustache template from file.")
	parser_template.add_argument('file', help="template filename")

	# parser for 'add'
	parser_add = subparsers.add_parser('add', help="tell texme about a field, static or variable, in the template")
	parser_add.add_argument('type', choices=['static', 'variable'], help="type of field to add (static or variable)")
	parser_add.add_argument('name', help="name of field to add [required]")
	parser_add.add_argument('value', nargs='?', default=None, help="value of static field [static fields only]")

	#parser for 'remove'
	parser_remove = subparsers.add_parser('remove', help="tell texme to forget about a previously-added template field")
	parser_remove.add_argument('type', choices=['static', 'variable'], help="type of field to remove (static or variable)")
	parser_remove.add_argument('name', help="name of field to be removed")

	return parser.parse_args()

# dispatches to correct method based on arguments in namespace
# returns 1 if operation succeeds, 0 othwerwise
def texme(args):
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
			return 1
		else:
			status('e', "creation failed")
			return 0
	if(mode == "template"):
		if template(args.file):
			status('n', "template install successful")
			return 1
		else:
			status('e', "template install failed")
			return 0
	if (mode == "add"):
		if add(args.type, args.name, args.value):
			status('n', "added "+ args.type +" field \"" + args.name +"\" successfully")
			return 1
		else:
			status('e', "adding field failed")
			return 0
	if (mode == "remove"):
		if remove(args.type, args.name):
			status('n', "removed "+ args.type +" field \"" + args.name +"\" successfully")
			return 1
		else:
			status('e', "removing field failed")
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

	if "statics"  in config:
		statics = config['statics']
		for i, static in enumerate(statics):
			to_template[static['name']] = static['value']
	else:
		status('s', "no static fields")


	outfile_fp = open(outfile, 'w')
	outfile_fp.write(render_template(config['template'], to_template));
	
	return 1

# add field in template to config file. 
# supports variable and constant fields

def add(type, name, value=None):
	if not check_install(DEFAULT_DIRNAME): return False
	os.chdir(DEFAULT_DIRNAME)
	config = load_config(DEFAULT_CONFIG)

	if type == "variable":
		if 'variables' in config:
			config['variables'].append({"name":name})
		else:
			config['variables'] = [{"name":name}]
	if type == "static":
		if not value: return False
		if 'statics' in config:
			config['statics'].append({"name":name, "value":value})
		else:
			config['statics'] = [{"name":name, "value":value}]

	write_config(config)
	return True

# remove a previously-stored template field 
# from config file
def remove(type, name):
	if not check_install(DEFAULT_DIRNAME): return False
	os.chdir(DEFAULT_DIRNAME)
	config = load_config(DEFAULT_CONFIG)

	if type == "variable":
		if 'variables' in config:
			config['variables'] = [var for var in config['variables'] if var['name'] != name]
		else:
			status('e', "field of " + type +" type named "+ name +" is unknown. aborting")
			return False
	if type == "static":
		if not value: return False
		if 'statics' in config:
			config['statics'] = [var for var in config['statics'] if var['name'] != name]
		else:
			status('e', "field of " + type +" type named "+ name +" is unknown. aborting")
			return False

	write_config(config)
	return True


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
	filecopy(file_abs, os.path.basename(file))

	write_config(config)
	return True

if __name__ == "__main__":
	main()