#!/usr/bin/env python

import sys
import argparse
from pathlib import Path
import pickle
import csv
from colorama import init, Fore, Back
from pkg_resources import resource_filename

from make_db import (
    make_db, SINGLE_PARAM, MULTI_PARAM,
    ORIGINAL_CSV, USER_CSV
)
from git_helper import (
    run_command, print_error,
    call_function
)


# colorama
init()


def main():
    # create an argument parser
    cmd_parser = argparse.ArgumentParser(
        prog='sgit',
        description='Semantic (plain english) commands for git!',
        epilog=f'for example:  {Back.BLUE}{Fore.WHITE}sgit create new repository'
        f'{Back.RESET}{Fore.RESET}'
    )
    cmd_parser.add_argument(
        '--make-db', action='store_true',
        help='generate command dataset from csv file'
    )
    cmd_parser.add_argument(
        '--list', '-l', action='store_true',
        help='list all possible commands'
    )
    cmd_parser.add_argument(
        '--demo', '-d', action='store_true',
        help='just show the final command without running it'
    )
    cmd_parser.add_argument(
        'command', action='store', nargs='*', default='',
        help='git command in plain english'
    )

    args = cmd_parser.parse_args()

    # on --make-db just generate dataset and exit.
    if args.make_db:
        print('\ngenerating command trees dataset...\n')
        if run_make_db(args.command):
            sys.exit(0)
        else:
            sys.exit(1)
    # -------------------------------------------------------------

    # on --list switch list all available commands.
    if args.list:
        cmd_list = list_commands()
        print(f'{cmd_parser.format_help()}\n{cmd_list}')
        print('\n\n{x} will be replaced by your input.\n')
        sys.exit(0)
    # -------------------------------------------------------------

    # check and run given command
    if not args.command:
        cmd_parser.print_help()
        print('\nNo command was given!\n')
        sys.exit(0)

    # load datasets
    with open(resource_filename(__name__, 'keywords_db.pk'), mode='rb') as f:
        keywords_db = pickle.load(f)
    with open(resource_filename(__name__, 'commands_db.pk'), mode='rb') as f:
        commands_db = pickle.load(f)

    # first input word must be in keywords.
    if args.command[0] not in keywords_db:
        print(
            f'{Fore.YELLOW}\nCould not find any command started with '
            f'"{args.command[0]}". Sorry!{Fore.RESET}\n'
        )
        sys.exit(1)

    cmd_key = [args.command[0]]                # to get command from dict
    next_words = keywords_db[args.command[0]]  # list of next accepted words
    params = []                                # user input parameters
    for idx in range(1, len(args.command)):
        w = args.command[idx]
        if w not in next_words:
            # current word is not in list of next accepted words:
            # maybe it is a parameter:
            # check if parameter is in next words list.
            if SINGLE_PARAM in next_words:
                params.append(w)
                w = SINGLE_PARAM
            else:
                # there is no command with such input words sequence.
                # maybe the rest of input are parameters.
                params.extend(args.command[idx:])
                # replace single param with multi-param keyword or
                # add it if it's not in command key.
                if cmd_key[-1] == SINGLE_PARAM:
                    cmd_key[-1] = MULTI_PARAM
                else:
                    cmd_key.append(MULTI_PARAM)
                break  # loop

        # add current word (w) to command key
        cmd_key.append(w)
        # get list of next accepted words after current word (w)
        next_words = keywords_db['/'.join(cmd_key)]

    # try to find the command in dataset:
    cmd_key = '/'.join(cmd_key)
    command = commands_db.get(cmd_key)
    if not command:
        # no proper command was found by input words!
        print(
            f'{Fore.YELLOW}Sorry, your specific command was not found!{Fore.RESET}\n'
        )
        sys.exit(1)

    # if command is a git_helper function, call it!
    if command.startswith('git_helper') and not args.demo:
        if call_function(command.split()[1], params):
            sys.exit(0)
        else:
            sys.exit(1)

    # match command parameters with user input parameters
    num_params = cmd_key.count(SINGLE_PARAM)
    # if command accepts multi-parameters too:
    # take num_params for single parameter(s) and join the rest with space.
    if MULTI_PARAM in cmd_key:
        params = params[:num_params] + [' '.join(params[num_params:])]
        num_params += 1

    if num_params != len(params):
        print_error(
            f'command: {command}\ntakes {num_params} parameter(s),\n'
            f'but {len(params)} is given!\n'
            f'{Fore.YELLOW}given parameters: {0}'.format(', '.join(params))
        )
        sys.exit(1)

    else:
        # matched!
        # insert input parameters into command and run the final git command.
        command = command.format(*params)
        if not args.demo:
            run_command(command)


def run_make_db(inputs):
    csv_file = Path(resource_filename(__name__, 'original_cmd_table.csv'))
    if inputs:
        csv_file = Path(inputs[0])
    if not csv_file.exists():
        print(f'{Fore.RED}Missing file at {csv_file.absolute()}\n')
        return False

    make_db(csv_file)
    return True


def list_commands():
    # return list of all available commands in csv table.
    csv_file = Path(resource_filename(__name__, USER_CSV))
    if not csv_file.exists():
        csv_file = Path(resource_filename(__name__, ORIGINAL_CSV))
    # read csv table
    with open(csv_file, mode='r') as f:
        csv_rows = list(csv.DictReader(f, skipinitialspace=True))

    cmd_list = []
    semantics = []
    prev_cmd = csv_rows[0]['command']
    prev_comment = csv_rows[0]['comment']
    for row in csv_rows:
        if prev_cmd != row['command'] or prev_comment != row['comment']:
            cmd_list.append((semantics, prev_comment))
            semantics = []
            prev_cmd = row['command']
            prev_comment = row['comment']

        semantics.append(row['semantic'])
    # add last one to command list
    cmd_list.append((semantics, row['comment']))

    return f'List of available commands(in {Fore.BLUE}blue{Fore.RESET}):\n\n' + \
        '\n\n'.join([
            f'{Fore.BLUE}' + '\n'.join(semantics) +
            f'{Fore.RESET}\n{comment}' for semantics, comment in cmd_list
        ])






if __name__ == '__main__':
    main()
