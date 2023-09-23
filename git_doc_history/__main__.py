import sys

import click


from .config import resolve_config, parse_config


@click.group()
def main() -> None:
    pass


@main.command()
@click.argument("ENV_FILE", type=str, required=True)
def shell(env_file: str) -> None:
    import shlex

    for k, v in parse_config(resolve_config(env_file)).items():
        click.echo(f"{k}={shlex.quote(v)}")


@main.command()
@click.option(
    "-a",
    "--at",
    type=str,
    prompt="You can provide a date, an ISO-like timestamp, or something like '10 days ago'\nFrom when?",
)
@click.option(
    "-c", "--config", type=str, required=True, help="path or name of config file"
)
@click.argument("EXTRACT_FILE", type=str, required=True)
@click.argument("OUTPUT_FILE", type=click.Path(allow_dash=True))
def extract_file_at(at: str, config: str, extract_file: str, output_file: str) -> None:
    """
    Extract a file from the git history from a particular datetime

    \b
    EXTRACT_FILE is the name of the file, e.g. todo.txt
    OUTPUT_FILE is the file to write to, or '-' to write to STDOUT
    """
    import dateparser

    from . import DocHistory, naive_dt

    conf = DocHistory.from_dict(parse_config(resolve_config(config)))
    dt = dateparser.parse(at)
    if dt is None:
        click.echo(f"Couldn't parse {at} into a datetime", err=True)
        sys.exit(1)

    data_bytes = conf.extract_buffer_at(extract_file, naive_dt(dt))
    if output_file == "-":
        click.echo(data_bytes.decode("utf-8"), nl=False)
    else:
        with open(output_file, "wb") as f:
            f.write(data_bytes)


if __name__ == "__main__":
    main(prog_name="git_doc_history")
