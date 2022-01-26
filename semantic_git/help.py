from colorama import Fore, Back


RESET = Fore.RESET
BLUE = Fore.BLUE


class Text:
    BOLD = '\033[1m'
    OFF = '\033[0m'


base = f"""
{Fore.GREEN}Semantic Git{RESET}
Plain english commands for git!

usage:    sgit [--help] [--demo] [command ...]
example:  sgit undo all changes

positional arguments:
command     your command in plain english

optional arguments:
-h, --help  show this help message and exit
--demo, -d  just print the final command without running it

utility commands:
{BLUE}sgit help{RESET}                                   show this help
{BLUE}sgit generate dataset{RESET}                       generate datasets from original csv file
{BLUE}sgit generate dataset from <csv file>{RESET}       generate datasets from given csv file
{BLUE}sgit list commands{RESET}                          list all available commands
{BLUE}sgit list command tags{RESET}                      list all tags assigned to commands
{BLUE}sgit list commands by tag <tag name>{RESET}        list all commands contain given tag
"""

tags = f"""
command tags include git subcommand or category of the command 
which hint us about what command does!\n
you can get list of commands that contain a tag with:
{BLUE}sgit list commands by tag <TAG NAME>{RESET}\n
semantic command tags list:
"""


param = '{x} will be replaced by your input.\n'
