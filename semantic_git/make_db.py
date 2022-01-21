import csv
import enum
import pickle
from collections import defaultdict
from pathlib import Path
from pkg_resources import resource_filename
from typing import List


ORIGINAL_CSV = 'original_cmd_table.csv'
USER_CSV = 'user_cmd_table.csv'

SINGLE_PARAM = '{<P>}'
MULTI_PARAM = '{<*>}'


def make_db(csv_file: Path):
    # read csv file
    with open(csv_file, mode='r') as f:
        csv_rows = list(csv.DictReader(f, skipinitialspace=True))
    # make dataset
    keywords, commands = generate_cmd_trees(csv_rows)
    # save db
    with open(resource_filename(__name__, 'keywords_db.pk'), mode='wb') as f:
        pickle.dump(keywords, f)
    with open(resource_filename(__name__, 'commands_db.pk'), mode='wb') as f:
        pickle.dump(commands, f)

    # if csv file was different from original one, save it.
    user_csv = Path(resource_filename(__name__, USER_CSV))
    if (
        csv_file.name != ORIGINAL_CSV and
        csv_file.absolute() != user_csv.absolute()
    ):
        with open(user_csv, mode='w') as f:
            writer = csv.DictWriter(f, fieldnames=csv_rows[0].keys())
            writer.writeheader()
            writer.writerows(csv_rows)
    print('Datasets was generated successfully!\n')


def generate_cmd_trees(rows: List[dict]):
    # keywords is a dict of command words as the key and
    # list of next accepted words as value.
    # e.g. "new": ["repository", "branch", ...]
    keywords = defaultdict(list)
    # a dict for commands with keywords path as the key and
    # git command as value.
    # e.g. "create/new/branch/{<P>}": "git branch {0}"
    commands = {}

    # processing each row of csv table:
    for row in rows:
        words = row['semantic'].split(' ')  # all words in a semantic command
        prev_word = ''                      # holds previous word
        cmd_path = ''                       # holds each command word separated by /
        for idx in range(len(words)):
            w = words[idx]
            # if current word is a parameter like {0}
            # replace it by a constant special keyword.
            if is_param(w):
                # in case of {*}: it is a multi-parameters.
                if '*' in w:
                    w = MULTI_PARAM
                else:
                    w = SINGLE_PARAM

            # there shoudn't be two consecutive appearance of the same word
            if prev_word == w:
                raise ValueError(
                    f'ERROR:\nIn semantic command: {row["semantic"]},'
                    '\nTwo consecutive words are the same.'
                )
            # specially two consecutive parameters.
            if prev_word.startswith('{<') and w.startswith('{<'):
                raise ValueError(
                    f'\nIn semantic command: {row["semantic"]},'
                    '\nSingle param like {0} can not appear right before or after multi-params {*}.'
                )

            # append current word into list of next words of previous word.
            if cmd_path in keywords and w not in keywords[cmd_path]:
                keywords[cmd_path].append(w)

            # combine command words as a path separated by /
            cmd_path = '/'.join([s for s in [cmd_path, w] if s])
            # add combination of so far command words as a keyword into the keywords dict
            if cmd_path not in keywords:
                keywords[cmd_path] = []

            prev_word = w
        # end of each row loop

        # multi-params should be used only once at the end of a semantic command.
        if cmd_path.count(MULTI_PARAM) > 1 or (
            cmd_path.count(MULTI_PARAM) == 1 and
            not cmd_path.endswith(MULTI_PARAM)
        ):
            raise ValueError(
                f'\nIn semantic command: {row["semantic"]},'
                '\n{*} should be used only once at the end of a semantic command.'
            )

        # check for duplicate command keys
        if cmd_path not in commands:
            # put command into dict
            commands[cmd_path] = row['command']
        else:
            raise ValueError(f'Duplicate command keys!\n{cmd_path}')

    return keywords, commands


def is_param(word):
    return word.startswith('{') and word.endswith('}')




if __name__ == '__main__':
    make_db(Path(resource_filename(__name__, ORIGINAL_CSV)))
