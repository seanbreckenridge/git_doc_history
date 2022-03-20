import io
from pathlib import Path
from typing import NamedTuple, List, Dict, Any, Tuple, Iterator, Optional
from datetime import datetime

from git.repo import Repo
from git.objects import Commit


def naive_dt(dt: datetime) -> datetime:
    return datetime.fromtimestamp(dt.timestamp())


def naive_local_time(commit: Commit) -> datetime:
    return naive_dt(commit.committed_datetime)


class DocHistorySnapshot(NamedTuple):
    commit: Commit
    data: bytes


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

    def sorted_timestamped_commits(self) -> List[Tuple[datetime, Commit]]:
        repo = self.repo()
        commits = list(repo.iter_commits())
        data: List[Tuple[datetime, Commit]] = [
            (naive_local_time(c), c) for c in commits
        ]
        data.sort(key=lambda c: c[0])
        return data

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

    def iter_bytes_from_commits(self, file: str) -> Iterator[DocHistorySnapshot]:
        for _, comm in self.sorted_timestamped_commits():
            try:
                blob = self.extract_bytes_from_commit(comm, file)
                yield DocHistorySnapshot(commit=comm, data=blob)
            except KeyError:
                pass
                # TODO: warn?

    def extract_buffer_at(self, file: str, at: datetime) -> bytes:
        commits = self.sorted_timestamped_commits()
        assert len(commits) > 0, "No commits!"
        assert (
            at.tzinfo is None
        ), "Datetime must be naive -- to compare with sorted commits"
        # default to first commit
        commit: Commit = commits[0][1]
        for comm_date, comm in commits:
            if comm_date > at:
                break
            commit = comm
        return self.extract_bytes_from_commit(commit, file)
