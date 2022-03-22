import sys
import shlex
import subprocess as sp
import threading
from pathlib import Path
from colorama import Fore, Back


def print_error(log: str):
    print(
        f'{Back.RED}{Fore.WHITE}Oops, an error has occured:{Back.RESET}{Fore.RESET}\n'
        f'{Fore.RED}{log}{Fore.RESET}\n'
    )


def run_command(command):
    # split shell command into proper parts
    command = shlex.split(command)
    # insert coloring options for git output
    command[1:1] = shlex.split('-c color.ui=always -c color.status=always')
    # run cmd through a new process
    process = sp.Popen(
        command, stdout=sp.PIPE, stderr=sp.STDOUT, shell=False,
        bufsize=1, universal_newlines=True,
        encoding='utf-8', errors='backslashreplace'
    )
    # log command output by a new thread
    ret_code = []  # to get process return code from its thread
    th = threading.Thread(target=process_logger, args=(process, ret_code), name='sgit_logger')
    th.start()
    th.join()

    return ret_code and ret_code[0] == 0


def process_logger(process: sp.Popen, ret_code: list):
    return_code = None
    while True:
        output = process.stdout.readline()
        if output:
            if 'fatal:' in output:
                print_error(output)
            else:
                print(output.strip('\n'))

        # check if process has finished:
        return_code = process.poll()
        if return_code is not None and output == '':
            if return_code == 0:
                print(f'\n{Fore.GREEN}Done!{Fore.RESET}\n')
            else:
                print(f'{Fore.RED}Error Code: {return_code}{Fore.RESET}\n')
            # end while loop
            break

    ret_code.append(return_code)
    return return_code


def call_function(func_name, params):
    print(func_name, params)
    func = globals().get(func_name)
    if func is not None:
        return func(params)

    else:
        print_error(f'function {func_name} was not found!')
        return False


def stage_all_except(params: list):
    # add all files of current directory(cwd) into stage
    # with given params as exceptions(not to stage)
    cwd = Path.cwd()
    accepted_files = [
        f.name for f in cwd.iterdir()
        if f.name not in params and not f.name.startswith('.')
    ]
    command = 'git add --verbose ' + ' '.join(accepted_files)
    return run_command(command)


def ignore(params: list):
    # create .gitignore file if not exists
    # and append given files into it.
    # get ignored file names from params
    ignored = [Path(p).resolve().relative_to(Path.cwd()) for p in params]
    with open(Path.cwd().joinpath('.gitignore'), mode='a') as f:
        f.write('\n')
        f.write('\n'.join(ignored))
    return True


def unignore(params: list):
    # remove given files/folders from .gitignore file
    unignored = [Path(p).name for p in params]
    output = []
    with open(Path.cwd().joinpath('.gitignore'), mode='r+') as f:
        for line in f.readlines():
            line = line.strip()
            if line and line not in unignored:
                output.append(line)
        # write back remaining ignored files
        f.seek(0)
        f.write('\n'.join(output))
        f.truncate()
    return True
