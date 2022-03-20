from git_doc_history import DocHistory
from git_doc_history.config import parse_config, resolve_config

# parse the config from the env file
doc = DocHistory.from_dict(parse_config(resolve_config("todo")))

# iterate through the history for the todo.txt file
for snapshot in doc.iter_commit_snapshots("todo.txt"):
    print(str(snapshot.commit_sha))
    print(str(snapshot.dt))
    print(snapshot.data.decode("utf-8"))
