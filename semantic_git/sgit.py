#!/usr/bin/env python

import sys
import argparse
import pickle
import csv
from pathlib import Path
from itertools import chain
from typing import List
from colorama import init, Fore, Back, Style
from pkg_resources import resource_filename

from dataset import (
    generate_db, SINGLE_PARAM, MULTI_PARAM,
    ORIGINAL_CSV, USER_CSV
)
from git_helper import (
    run_command, print_error,
    call_function
)
import help


init()         # init colorama
TAG_SEP = '|'  # tag and param field separator


def main():
    # create an argument parser
    cmd_parser = argparse.ArgumentParser(
        prog='sgit',
        description='Semantic (plain english) commands for git!',
        add_help=False,
        epilog=f'for example:  {Back.BLUE}{Fore.WHITE}list all branches'
        f'{Back.RESET}{Fore.RESET}'
    )
    cmd_parser.add_argument('--help', '-h', action='store_true', help='show help')
    cmd_parser.add_argument(
        '--demo', '-d', action='store_true',
        help='just print the final command without running it'
    )
    cmd_parser.add_argument(
        'command', action='store', nargs='*', default='',
        help='your command in plain english'
    )

    args = cmd_parser.parse_args()

    # on --help or -h
    if args.help:
        show_help()
        sys.exit(0)

    # no command
    if not args.command:
        show_help()
        print('No command was given!\n')
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

    # get command and its possible parameters
    cmd_key, params = extract_command_and_params(args.command, keywords_db)

    # try to find the command in dataset:
    cmd_key = '/'.join(cmd_key)
    command = commands_db.get(cmd_key)
    if not command:
        # no proper command was found by input words!
        print(
            f'{Fore.YELLOW}Sorry, your specific command was not found!{Fore.RESET}\n'
        )
        sys.exit(1)

    # handle sgit utility commands like generate_db or list_commands
    if command.startswith('sgit'):
        exit_code = handle_utility_command(command, params)
        sys.exit(exit_code)

    # handle git_helper function call
    if command.startswith('git_helper') and not args.demo:
        if call_function(command.split(' ')[1], params):
            sys.exit(0)
        else:
            sys.exit(1)

    # now, it's a git command!
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


def extract_command_and_params(cmd_words, keywords_db):
    # main loop to digest given command and parameters
    cmd_key = [cmd_words[0]]                # to get command from dict
    next_words = keywords_db[cmd_words[0]]  # list of next accepted words
    params = []                             # user input parameters
    for idx in range(1, len(cmd_words)):
        w = cmd_words[idx]
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
                params.extend(cmd_words[idx:])
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

    return cmd_key, params


def handle_utility_command(command, params):
    func_name = command.split(' ')[1]
    func = globals().get(func_name)
    if func is None:
        print_error(f'function {func_name} was not found!')
        return 1

    return int(not func(params))


def run_generate_db(params):
    csv_file = Path(resource_filename(__name__, ORIGINAL_CSV))
    if params:
        csv_file = Path(params[0])
    if not csv_file.exists():
        print(f'{Fore.RED}Missing file at {csv_file.absolute()}\n')
        return False

    generate_db(csv_file)
    return True


def read_csv() -> List[dict]:
    csv_file = Path(resource_filename(__name__, USER_CSV))
    if not csv_file.exists():
        csv_file = Path(resource_filename(__name__, ORIGINAL_CSV))
    # read csv table
    with open(csv_file, mode='r') as f:
        csv_rows = list(csv.DictReader(f, skipinitialspace=True))

    return csv_rows


def list_commands(params=None):
    # return list of all available commands in csv file
    # group by command and comment.
    csv_rows = read_csv()

    cmd_list = []
    semantics = []
    params = []
    prev_cmd = csv_rows[0]['command']
    prev_comment = csv_rows[0]['comment']
    params.append(csv_rows[0]['params'])
    for row in csv_rows:
        if prev_cmd != row['command'] or prev_comment != row['comment']:
            cmd_list.append((semantics, prev_comment))
            semantics = []
            prev_cmd = row['command']
            prev_comment = row['comment']
            params.append(row['params'])

        semantics.append(row['semantic'])
    # add last one to command list
    cmd_list.append((semantics, row['comment']))
    params.append(row['params'])
    # prettify params
    for i, plist in enumerate(params):
        plist = ', '.join(plist.split(TAG_SEP))
        params[i] = f'{Style.DIM}{Fore.CYAN}{plist}{Style.RESET_ALL}'
        if plist:
            params[i] += '\n'

    cmd_list = f'List of available commands(in {Fore.BLUE}blue{Fore.RESET}):\n\n' + \
        '\n\n'.join([
            f'{help.Text.BOLD}{Fore.BLUE}' + '\n'.join(semantics) +
            f'{Fore.RESET}{help.Text.OFF}\n{param}{comment}'
            for (semantics, comment), param in zip(cmd_list, params)
        ])

    print(f'{cmd_list}', f'\n\n\n{help.param}')


def list_tags(params=None):
    csv_rows = read_csv()
    tags = [row['tags'].split(TAG_SEP) for row in csv_rows]
    tags = list(set(chain.from_iterable(tags)))
    tags.sort()
    longest = max([len(t) for t in tags]) + 4
    per_line = 5
    num_bins, rem = divmod(len(tags), per_line)
    if rem > 0:
        num_bins += 1
    print(help.tags)
    for i in range(num_bins):
        end = min((i + 1) * per_line, len(tags))
        row = [t.ljust(longest) for t in tags[i * per_line: end]]
        print(''.join(row))
    print()


def list_by_tag(params):
    csv_rows = read_csv()
    tag = params[0]
    results = [
        (row['semantic'], row['params'].replace(TAG_SEP, ', '), row['comment'])
        for row in csv_rows if tag in row['tags']
    ]
    print(
        '\n\n'.join([
            f'{Fore.BLUE}{item[0]}{Fore.RESET}\n' +
            f'{Style.DIM}{Fore.CYAN}{item[1]}{Style.RESET_ALL}\n{item[2]}'
            if item[1] else f'{Fore.BLUE}{item[0]}{Fore.RESET}\n{item[2]}'
            for item in results
        ]),
        f'\n\n\n{help.param}'
    )


def show_help(params=None):
    print(help.base)


if __name__ == '__main__':
    main()
