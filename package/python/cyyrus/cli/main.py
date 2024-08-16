# package/python/cli/main.py

import click


@click.group()
def cli():
    """Cyyrus CLI"""
    pass


@cli.command()
@click.option("--name", default="World", help="Who to greet")
def hello(name):
    """Simple command that greets the user."""
    click.echo(f"Hello, {name}!")


if __name__ == "__main__":
    cli()
