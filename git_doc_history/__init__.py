import io
from pathlib import Path
from typing import (
    NamedTuple,
    Literal,
    List,
    Dict,
    Set,
    Any,
    Optional,
    Iterator,
    Callable,
)
from datetime import datetime

from git.repo import Repo
from git.objects import Commit


def naive_dt(dt: datetime) -> datetime:
    return datetime.fromtimestamp(dt.timestamp())


def commit_local_time(commit: Commit) -> datetime:
    return naive_dt(commit.committed_datetime)


class DocHistorySnapshot(NamedTuple):
    commit_sha: str
    epoch_time: int
    data: bytes

    @property
    def dt(self) -> datetime:
        return datetime.fromtimestamp(self.epoch_time)


class DocHistory(NamedTuple):
    """
    Traverses and/or extracts files from git history
    """

    backup_dir: Path
    copy_files: List[str]
    source_dir: Optional[Path] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocHistory":
        return cls(
            source_dir=Path(data["SOURCE_DIR"]).expanduser().absolute(),
            backup_dir=Path(data["BACKUP_DIR"]).expanduser().absolute(),
            copy_files=data["COPY_FILES"].strip().splitlines(),
        )

    def repo(self) -> Repo:
        return Repo(str(self.backup_dir))

    def extract_bytes_from_commit(self, commit: Commit, file: str) -> bytes:
        try:
            blob = commit.tree / file
        except KeyError as k:
            #  assert file in self.copy_files, f"{file} not in {self.copy_files}"
            raise k
        with io.BytesIO(blob.data_stream.read()) as f:
            data = f.read()
        return data

    def extract_str_from_commit(self, commit: Commit, file: str) -> str:
        return self.extract_bytes_from_commit(commit, file).decode("utf-8")

    def iter_commit_snapshots(self, file: str) -> Iterator[DocHistorySnapshot]:
        for commit in self.repo().iter_commits():
            try:
                blob = self.extract_bytes_from_commit(commit, file)
            except (KeyError, ValueError):
                pass  # file doesn't exist at this hash
            else:
                yield DocHistorySnapshot(
                    commit_sha=commit.hexsha,
                    epoch_time=commit.committed_date,
                    data=blob,
                )

    def list_commit_snapshots(
        self, file: str, reverse: bool = False
    ) -> List[DocHistorySnapshot]:
        items = list(self.iter_commit_snapshots(file))
        if reverse:
            items = list(reversed(items))
        return items

    def extract_buffer_at(self, file: str, at: datetime) -> bytes:
        """
        Given a file in backup_dir, fetch the contents at datetime
        """
        assert (
            at.tzinfo is None
        ), "Datetime must be naive -- to compare with sorted commits"
        # default to first commit -- latest
        commit: Optional[Commit] = None
        for comm in self.repo().iter_commits():
            if commit is None:
                commit = comm
            if commit_local_time(comm) < at:
                break
            commit = comm
        if commit is None:
            raise RuntimeError("No commit set -- likely no commits in repo?")
        return self.extract_bytes_from_commit(commit, file)


Action = Literal["added", "removed"]


class Diff(NamedTuple):
    """
    A diff -- what has changed from one git snapshot to the next
    """

    epoch_time: int
    data: Any
    action: Action

    @property
    def description(self) -> str:
        return f"{self.action} {datetime.fromtimestamp(self.epoch_time)} {self.data}"


def parse_lines(snapshot: DocHistorySnapshot) -> List[str]:
    """
    The most basic parse_func -- decodes to text and returns a list of lines
    """
    return snapshot.data.decode("utf-8").strip().splitlines()


def parse_snapshot_diffs(
    doc: "DocHistory",
    file: str,
    parse_func: Optional[Callable[[DocHistorySnapshot], List[Any]]] = None,
) -> Iterator[Diff]:
    """
    Iterates through the git history in chronological order, keeping track
    of when data was added or removed. By default, this parses the 'file'
    given by splitting it into lines. If lines are added/removed, this returns an
    event which specifies when in the history, and what was added/removed

    Alternatively, can pass a 'parse_func', which is a function which
    accepts the DocHistorySnapshot, and returns a list of hashable items
    to store as state
    """
    if parse_func is None:
        parse_func = parse_lines
    data = doc.list_commit_snapshots(file=file, reverse=True)
    state: Set[Any] = set()

    for snapshot in data:
        # parse the data using the func
        snapshot_data: List[Any] = parse_func(snapshot)
        snapshot_set = set()
        # e.g. iterate over lines -- or whatever data was parsed
        for sn in snapshot_data:
            snapshot_set.add(sn)
            # we're already tracking this in state -- it was added in a previous commit
            if sn in state:
                continue
            state.add(sn)
            yield Diff(epoch_time=snapshot.epoch_time, data=sn, action="added")

        # something is removed, if its in state, but its not in
        # the currently passed data
        for sn in list(state):
            if sn not in snapshot_set:
                yield Diff(epoch_time=snapshot.epoch_time, data=sn, action="removed")
                state.remove(sn)
