# Semantic Git  

Instead of memorizing all commands you may frequently use try ***`semantic_git`*** which gets your commands as semantic plain english sentences and runs corresponding git command for you.
<br><br>

### Examples:
- creating new repository:
```bash
$ create new repository  

# to create a new repository with 'main' as default branch
$ create new repository with main as default branch
```

<br><br>


## How to install
first clone the repository:
```bash
$ git clone 
```
then enter the cloned directory and install it:
```bash
$ cd ./semantic_git
$ pip install -e .
# or
$ python setup.py develop
```
<br><br>

## Making/Updating datasets
You may edit `original_cmd_table.csv` file to add/update your semantic commands and then run this to rebuild datasets:
```bash
$ sgit --make-db
```
Or you can build datasets out of your csv file:
```bash
$ sgit --make-db path/to/your/csv
```
Also there is `git_helper.py` to develop more functionality that simple git command can not provide.
<br><br>
