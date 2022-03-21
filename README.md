# git_doc_history

Copy and track files in `git`, and a library to traverse the history

I use this to track my [`todo.txt`](https://github.com/todotxt/todo.txt-cli) files, changes to configuration files, any shell histories which don't support timestamps (see all of my config files [here](https://github.com/seanbreckenridge/dotfiles/tree/master/.config/git_doc_history))

This copies the files to a different directory, so it doesn't interfere with the application/configuration

By copying those files to a separate directory, I can always roll back to previous file, or see what the file was like a couple days/months ago.

For shell histories/files which are unique lines of text (e.g., my `todo.txt` file) this also lets me estimate timestamps for when new lines were added to the history/text files, using the `iter_commit_snapshots` and `parse_snapshot_diffs` below, which emits added/removed events for individual lines with estimated times

This was mostly created for [HPI](https://github.com/seanbreckenridge/HPI), so I don't have to rewrite the code to extract lines for git history over and over

## Installation

Requires `python3.8+`

To install with pip, run:

```
pip install git_doc_history
```

## Usage

The main script to backup data is the bash script [`bin/git_doc_history`](bin/git_doc_history), which gets installed into your `~/.local/bin/` directory.

If uses a config file (parsed with [`python-dotenv`](https://github.com/theskumar/python-dotenv) -- so you can use bash-like syntax to grab environment variables) like:

```
SOURCE_DIR=~/.todo  # copy from
BACKUP_DIR=~/data/todo_git_history # copy to
# multiple lines means multiple files
COPY_FILES="todo.txt
done.txt"
```

You can either provide the full path to that config file, or place the file in `~/.config/git_doc_history`

For example, after placing it at `~/.config/git_doc_history/todo` -- to copy/commit any changes, run:

```bash
$ git_doc_history todo
```

```
Generated configuration:
SOURCE_DIR: /home/sean/data/todo
BACKUP_DIR: /home/sean/data/todo_git_history
COPY_FILES: todo.txt
done.txt
'/home/sean/data/todo/todo.txt' -> '/home/sean/data/todo_git_history/todo.txt'
'/home/sean/data/todo/done.txt' -> '/home/sean/data/todo_git_history/done.txt'
'/home/sean/data/todo/.gitignore' -> '/home/sean/data/todo_git_history/.gitignore'
[master f927490] update
 1 file changed, 1 insertion(+)
 create mode 100644 .gitignore
```

That uses `python3 -m git_doc_history shell todo` to parse the configuration file, like:

```bash
eval "$(python3 -m git_doc_history shell todo)"
```

The python library comes with a small CLI interface to extract a file from some time ago:

```
$ python3 -m git_doc_history extract-file-at --at 2020-09-20 -c todo todo.txt -
setup command of completion
```

The `BACKUP_DIR` is of course just a regular git directory -- you can `reset --hard` to some point in the past to get rid of recent commits, `rebase`/`squash` to merge commits or do whatever you please

### Library Usage

Most things will be done with `git_doc_history.DocHistory`

This doesn't assume the filetype is readable text (you may be storing images/binary doc files in the git repository), so the default is to return the data as `bytes` -- you can `.decode("utf-8")` to convert that to readable text

To traverse the entire history:

```python
from git_doc_history import DocHistory
from git_doc_history.config import parse_config, resolve_config

# parse the config from the env file
doc = DocHistory.from_dict(parse_config(resolve_config("todo")))

# iterate through the history for the todo.txt file
for snapshot in doc.iter_commit_snapshots("todo.txt"):
    print(str(snapshot.commit_sha))
    print(str(snapshot.dt))
    print(snapshot.data.decode("utf-8"))
```

#### Parsing Diffs

Iterates through the git history in chronological order, keeping track
of when data was added or removed. By default, this parses the `file`
given by splitting it into lines. If lines are added/removed, this returns an
event which specifies when in the history, and what was added/removed

Alternatively, can pass a `parse_func`, which is a function which
accepts the `DocHistorySnapshot`, and retuns a list of hashable items
to store as state

For an example of parsing diffs, see [`examples/todotxt_diff.py`](examples/todotxt_diff.py):

Example output looks something like:

```
added 2022-03-08 12:14:45 (C) 2022-03-08 create shebang script +programming
removed 2022-03-08 13:14:58 (C) 2022-03-08 create shebang script +programming
added 2022-03-08 22:23:39 save formhistory.sqlite in browserexport
removed 2022-03-08 23:23:45 save formhistory.sqlite in browserexport
added 2022-03-09 02:49:58 (C) create a python fzf wrapper because apparently I cant find a good one
added 2022-03-10 16:24:24 (B) 2022-03-10 create plaintext playlist parser module +music
removed 2022-03-11 01:30:49 (B) 2022-03-10 create plaintext playlist parser module +music
added 2022-03-11 10:37:06 (C) 2022-03-11 sync tmux from home directory +programming
added 2022-03-12 03:44:24 install undotree +vim +programming
removed 2022-03-12 04:44:51 (C) 2022-03-11 sync tmux from home directory +programming
removed 2022-03-12 10:51:20 install undotree +vim +programming
```

In this case, 'removed' would mean I either changed the text on the line, or (more likely) I completed it

### Tests

```bash
git clone 'https://github.com/seanbreckenridge/git_doc_history'
cd ./git_doc_history
pip install '.[testing]'
pytest
flake8 ./git_doc_history
mypy ./git_doc_history
```
