# Semantic Git  

Instead of memorizing all commands you may frequently use try ***`semantic_git`*** which gets your commands as semantic plain english sentences and runs corresponding git command for you.
<br><br>

### Examples:
```bash
# to create a new repository with 'main' as default branch
$ sgit create new repository with main as default branch

# to discard all uncommited changes
$ sgit undo all changes
```
<br><br>  

## How to install
first clone the repository:
```bash
$ git clone https://github.com/mese79/semantic_git.git
```
then enter the cloned directory and install it:
```bash
$ cd ./semantic_git
$ pip install -e .
# or
$ python setup.py develop
```
#### Requirements:
- [colorama](https://github.com/tartley/colorama)

<br><br>  

## Help and Utility Commands
Issue **`sgit help`** command to view brief help and utility commands which are not related to `git` but `sgit` itself.  
<br><br>  

## Generate or Update Datasets
You may edit `original_cmd_table.csv` file to add/update your semantic commands and then run this to rebuild datasets:
```
$ sgit generate dataset
```
Or you can build datasets out of your csv file:
```
$ sgit generate dataset from path/to/your/csv
```
<br><br>  

## Commands
To view list of all available commands issue ```sgit list commands```. But it's going to be a long list! However, each command has few *tags* assign to. *tags* include git subcommand and categories of the intended command (don't confuse these tags with git tags). To view list of command tags:
```
$ sgit list command tags
```  
So you can get list of commands include a *tag*. for example:
```bash
# commands with 'undo' tag assign to
$ sgit list commands by tag undo
```  
Also there is a `git_helper.py` to develop python functions that extend git command capabilities.  
<br/><br/>  

### Future ToDo List:
- Add more git commands
- Autocomplete feature on console &lt;tab&gt; key
- Command suggestion feature if user command was not found
- Simple spell checker
- Provide more and better help
- Using a language model like *word2vec* to find closest valid command (maybe)
- Preparing breakfast :grin:
  
<br/><br/>  
