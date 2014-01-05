# texme > A script for managing LaTeX templates.

This originally came out of my hatred of having to manually fill in the
pertinent fields in LaTeX documents for homework (i.e. homework number, due
date, collaborators, etc.). This is a barebones first attempt written in a day,
but I hope to add more  features as time allows.

## Usage: If you've ever used Git, `texme` uses a similar hierarchy of commands.
Basically, you'll need the following steps:

1.	`texme init` in the directory that you'd like to track. For me, this action
will happen in course homework directories (i.e. at the beginning of each 
semester, once in each course that has LaTeX homework)
2.	Create a template file. We currently only support simple key:value mappings 
in the templates, using `[[ key ]]` style delimiters. 
3.	`texme template <templatefile>` this installs the template file into the texme 
configuration. 
4.	We support both static keys and variable keys in the template. For example, 
if the assignment name (`[[assignment]]`) changes weekly but the name of the 
course (`[[coursename]]`) does not, we can use the commands `texme add variable assignment`
and `texme add static coursename Algorithms`. The `add` command must be run
for each key that you'd like texme to track. 
5.	Finally, running `texme new` uses the template installed and the aformetioned
static and variable keys, prompts the user for the values for the variable keys, 
and creates a rendered file. The default outfile name is `rendered.tex`; you can 
pass a desired alternative outfile name as an argument (`texme new outfile.tex`).