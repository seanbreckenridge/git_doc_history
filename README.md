# git_doc_history

Copy and Track files in `git`, and a library to traverse the history

Really, the `doc` would isn't super accurate, but 'file/index/history' is such an overloaded term when it comes to `git`

I use this to track my `todo.txt` files, changes to configuration files, any shell histories which don't support timestamps

This copies the files to a different directory, so it doesn't interfere with the application/configuration

By copying those files to a separate directory, I can always roll back to previous file, or see what the file was like a couple days/months ago.

For shell histories/files which are unique lines of text (e.g., my `todo.txt` file) this also lets me estimate timestamps for when new lines were added to the history/text files, using the `linediff` or `history` features described below, which emits added/removed events for individual events with estimated times

## Installation

Requires `python3.7+`

To install with pip, run:

```
pip install git_doc_history
```

## Usage

The main script to backup data is [`bin/git_doc_history`], which gets installed into your `~/.local/bin/` directory.

If uses a config file (parsed with [`python-dotenv`](https://github.com/theskumar/python-dotenv)) like:

```
SOURCE_DIR=~/.todo  # copy from
BACKUP_DIR=~/data/todo_git_history # copy to
# multiple lines means multiple files
COPY_FILES="todo.txt
done.txt"
```

You can either provide the full path to that config file, or place the file in ~/.config/git_doc_history

To copy/commit any changes, run:

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

The python library comes with a small CLI interface to extract a file from some time ago:

```
$ python3 -m git_doc_history extract-file-at --at 2020-09-20 -c todo todo.txt -
setup command of completion
```

### Library Usage

Most things will be done with `git_doc_history.DocHistory`

### Tests

```bash
git clone 'https://github.com/seanbreckenridge/git_doc_history'
cd ./git_doc_history
pip install '.[testing]'
pytest
flake8 ./git_doc_history
mypy ./git_doc_history
```
