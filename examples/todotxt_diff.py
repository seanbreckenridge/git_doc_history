#!/usr/bin/env python3

from typing import List
from functools import cached_property

import pytodotxt  # type: ignore[import]
from git_doc_history import DocHistory, DocHistorySnapshot, parse_snapshot_diffs
from git_doc_history.config import parse_config, resolve_config


# a todotxt task which has a __hash__ based on the raw line
class TaskHashable(pytodotxt.Task):
    @cached_property
    def bare(self) -> str:
        return self.bare_description()

    # defines some dunder functions that allows this to be used in sets
    # required to check the diffs between snapshots

    def __hash__(self) -> int:
        return hash(self.bare)

    def __eq__(self, other) -> bool:
        if not isinstance(other, pytodotxt.Task):
            return False
        return self.bare == other.bare

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


def parse_into_todos(doc: DocHistorySnapshot) -> List[TaskHashable]:
    # pytodotxt.TodoTxtParser accepts bytes as inputs
    tasks = pytodotxt.TodoTxtParser(task_type=TaskHashable).parse(doc.data)
    return tasks


def main() -> None:
    # parse the config from the env file
    doc = DocHistory.from_dict(parse_config(resolve_config("todo")))
    for diff in parse_snapshot_diffs(doc, file="todo.txt", parse_func=parse_into_todos):
        print(diff.description)


if __name__ == "__main__":
    main()
