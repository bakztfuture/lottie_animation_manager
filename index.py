import click
# utilize emojis in the command line output
import emoji
# use pyfiglet for fancy slanted text
from pyfiglet import Figlet
f = Figlet(font='slant')

# echo hello world simple example
@click.command()
def hello_world():
	click.echo(click.style("--------------------------------------------------------\n", fg='green'))
	click.echo(click.style(f.renderText('Lottie CDN'), fg='green'))
	click.echo(click.style("--------------------------------------------------------", fg='green'))
	click.echo(click.style(emoji.emojize('Hello World! :thumbs_up:'), fg='green'))

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
	hello_world()