import sys
import os
from pathlib import Path
from typing import Dict, Union

import click
from dotenv import dotenv_values

config_dir = os.environ.get("XDG_CONFIG_DIR", os.path.expanduser("~/.config"))


def _resolve_env_file(conf: str) -> str:
    if os.path.exists(conf):
        return conf
    dconf = Path(config_dir) / "git_doc_history" / conf
    if dconf.exists():
        return str(dconf)
    raise FileNotFoundError(f"Could not find config file at {conf} or {dconf}")


def resolve_config(path: str) -> Path:
    try:
        conf = Path(_resolve_env_file(path)).absolute()
    except FileNotFoundError as fe:
        click.echo(str(fe), err=True)
        sys.exit(1)
    return conf


def parse_config(input_file: Union[Path, str]) -> Dict[str, str]:
    res: Dict[str, str] = {}
    for k, v in dotenv_values(Path(input_file)).items():
        assert v is not None
        if os.linesep not in v and k != "COPY_FILES":
            res[k] = str(Path(v).expanduser().absolute())  # expand directory names
        else:
            res[k] = v  # dont modify lines with multiple lines
    assert "SOURCE_DIR" in res, "Missing SOURCE_DIR key"
    assert "BACKUP_DIR" in res, "Missing BACKUP_DIR key"
    assert "COPY_FILES" in res, "Missing COPY_FILES key"
    return res
