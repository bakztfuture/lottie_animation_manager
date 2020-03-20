import click

# echo hello world simple example
@click.command()
def hello_world():
	click.echo('Hello World!')

# group/chaining example
@click.group()
def cli():
    pass

@cli.command()
def initdb():
    click.echo('Initialized the database')

@cli.command()
def dropdb():
    click.echo('Dropped the database')

# feed in an input value, count parameter which is added to the help value
@click.command()
@click.option('--count', default=1, help='number of greetings')
@click.argument('name')
def hello(count, name):
    for x in range(count):
        click.echo('Hello %s!' % name)


if __name__ == '__main__':
	cli()
	hello()