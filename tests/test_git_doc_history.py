import subprocess
import shlex
from pathlib import Path
from datetime import datetime

from git_doc_history import DocHistory
import git_doc_history.config as conf

this_dir = Path(__file__).parent.absolute()
git_dir = this_dir / "arctee_git"

script = this_dir / "from_filebackups_test"
assert script.exists()


def test_git_doc_history() -> None:

    subprocess.run(shlex.split("bash -x {}".format(script))).check_returncode()
    assert git_dir.exists(), "call from_filebackups_test first"

    cc = conf.expand_dotenv_file(conf.resolve_config(str(this_dir / "config")))
    doc = DocHistory.from_dict(cc)
    doc_histories = list(doc.iter_bytes_from_commits("data.txt"))

    assert len(doc_histories) == 5

    LAST_COMMIT_DT = 1647735650
    assert doc_histories[0].commit.committed_datetime.timestamp() == 1647677974
    assert doc_histories[-1].commit.committed_datetime.timestamp() == LAST_COMMIT_DT

    # extract from a bit before the last commit -- should extract second to last commit
    before_last_commit_data = doc.extract_buffer_at(
        "data.txt", datetime.fromtimestamp(LAST_COMMIT_DT - 10)
    )
    assert doc_histories[-2].data == before_last_commit_data
