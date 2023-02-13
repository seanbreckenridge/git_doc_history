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

    cc = conf.parse_config(conf.resolve_config(str(this_dir / "config")))
    doc = DocHistory.from_dict(cc)
    doc_histories = doc.list_commit_snapshots("data.txt", reverse=True)

    assert len(doc_histories) == 5

    LAST_COMMIT_DT = 1647735650
    assert doc_histories[0].epoch_time == 1647677974
    assert doc_histories[-1].epoch_time == LAST_COMMIT_DT

    assert (
        doc.extract_buffer_at("data.txt", datetime.fromtimestamp(1647677974 + 3))
        == b"one\ntwo\nthree\n"
    )
    assert (
        doc_histories[-1].data.decode("utf-8").strip()
        == "one\nthree\nfour\nfive\nsix\nseven"
    )
