import os, sys
import boto
import boto.s3.connection
from boto.s3.key import Key
from boto.exception import NoAuthHandlerFound
import pathlib
from utils import *

# command line application library
import click
# utilize emojis in the command line output
import emoji
# use pyfiglet for fancy slanted text
from pyfiglet import Figlet
f = Figlet(font='slant')

# for the purposes of securely storing tinypng API if necessary
# the service ID is just a namespace for your app
import keyring
LOTTIE_KEYRING_SERVICE_ID = 'lottie_animation_manager'

# compression library through tinypng
configured_tiny_png_key = None
compression_enabled = True

# connect to the default AWS profile
# if it's not found or fails, close the application.
bucket = None
#conn = boto.connect_s3()
try:
	conn = boto.connect_s3()
except NoAuthHandlerFound:
	click.echo(click.style(emoji.emojize('  Lottie Animation Manager - AWS Config Error  '), bg='red', fg="bright_white"))
	click.echo('\n')
	# Tell the user they need to configure AWS in order to continue.
	click.echo(click.style('In order to continue, please reconfigure and test your local AWS profile/configuration. You\'ll need to download the AWS CLI and configure it first before you can proceed.', fg="green"))
	sys.exit()
except Exception:
	click.echo(click.style(emoji.emojize('  Lottie Animation Manager - AWS Config Error  '), bg='red', fg="bright_white"))
	click.echo('\n')
	# Tell the user they need to configure AWS in order to continue.
	click.echo(click.style('In order to continue, please reconfigure and test your local AWS profile/configuration. You\'ll need to download the AWS CLI and configure it first before you can proceed.', fg="green"))
	sys.exit()

# Clear keyring in order to test to make sure the configuration screen is working
def clear_keyring():
	global bucket
	global configured_tiny_png_key
	global compression_enabled

	keyring.delete_password(LOTTIE_KEYRING_SERVICE_ID, 'lottie_animation_manager_config_complete')
	keyring.delete_password(LOTTIE_KEYRING_SERVICE_ID, 's3_bucket_name')
	keyring.delete_password(LOTTIE_KEYRING_SERVICE_ID, 'tiny_png_credentials')
	click.echo("cleared keyring")


# Compress image with tinypng API
def compress_image(file_name):
	global bucket
	global configured_tiny_png_key
	global compression_enabled

	import tinify
	tinify.key = configured_tiny_png_key

	click.echo(click.style('Compressing image files:',
				fg="green"),
				nl=True)
	try:
		original_file_size = sizeof_fmt(os.path.getsize(file_name))
		source = tinify.from_file(file_name)
		source.to_file(file_name)
		compressed_file_size = sizeof_fmt(os.path.getsize(file_name))
		click.echo(click.style('{} - Compression successful'.format(file_name),
						fg="bright_cyan"),
						nl=False)
		click.echo(click.style(' {} ➟ {} '.format(original_file_size, compressed_file_size),
						fg="blue"))
	except Exception as e:
		click.echo(click.style('{} - Error compressing this file'.format(file_name),
						fg="red"))

# Main program to upload the current directory which should be the animation's assets
def uploadDirectory(directory_name):
	global bucket
	global configured_tiny_png_key
	global compression_enabled

	# Screen Title
	click.echo(click.style(emoji.emojize(' Upload Current Working Directory :up_arrow:  '), bg='green', fg="bright_white"))
	# Screen Instructions
	click.echo(click.style("Make sure you are 'inside' of the animation directory with all of your lottie assets.\n", fg="green"))
	click.echo(click.style(emoji.emojize('Lottie Animation Manager has discovered the following files in the current directory: '),
						   fg='green'),
			   			   nl=True)
	# list out current files which will be sent to the user
	file_count = 0
	for root, dirs, files in os.walk("."):
		for f in files:
			current_file = os.path.relpath(os.path.join(root, f), ".")
			if not ".DS_Store" in current_file:
				if os.sep in current_file:
					click.echo(click.style(" {}".format(current_file), fg="blue"))
					file_count += 1
				else:
					click.echo(click.style(current_file, fg="blue"))
					file_count += 1

	click.echo('\n')
	click.echo(click.style('The above',
							fg='white'),
							nl=False)
	click.echo(click.style(' {} files '.format(file_count),
							bold=True,
							fg='white'),
							nl=False)

	# confirm they want to proceed with the upload process
	if click.confirm(click.style('will be uploaded to AWS S3 Storage.  Please confirm'.format(file_count),
							fg='white'),
							abort=True):
		# Clear screen
		if compression_enabled == True:
			click.clear()
			# Title
			click.echo(click.style(emoji.emojize(' Compressing & Uploading Animation Assets '), bg='green', fg="bright_white"))
			click.echo('\n')
			# compress any images first
			for root, dirs, files in os.walk("."):
				for f in files:
					current_file = os.path.relpath(os.path.join(root, f), ".")
					temp_current_file = current_file.lower()
					if temp_current_file.endswith(".png") or temp_current_file.endswith(".jpg") \
						or temp_current_file.endswith(".jpeg"):
						compress_image(current_file)

		click.echo('\n')
		click.echo(click.style('Uploading animation asset files to AWS S3 Storage Bucket:',
					fg="green"),
					nl=True)
		# the user has confirmed, images are compressed, now send it up to s3
		for root, dirs, files in os.walk("."):
			for f in files:
				current_file = os.path.relpath(os.path.join(root, f), ".")
				if not ".DS_Store" in current_file:
					try:
						k = bucket.new_key("{}/{}".format(directory_name, current_file))
						k.set_contents_from_filename(current_file)
						k.set_acl('public-read')
						click.echo(click.style('{} - Upload successful'.format(current_file),
											   fg="bright_cyan"))
					except:
						click.echo('Error uploading file to s3!')

		# Send them to the view animations listing view, now that we're done here
		if(click.confirm('\nAll done!  Do you want to continue to the animations listings section?')):
			list_hosted_animations()
		else:
			click.echo(click.style(emoji.emojize("Thanks for using Lottie Animation Manager, have a nice day :sun: \n"), fg='bright_green'))
	else:
		# terminate the program
		click.echo(click.style(emoji.emojize("Thanks for using Lottie Animation Manager, have a nice day :sun: \n"), fg='bright_green'))

# Gets the 'animation_name' before starting the process of uploading the files to S3
@click.command()
def upload_current_lottie_directory():
	global bucket
	global configured_tiny_png_key
	global compression_enabled

	# Clear screen
	click.clear()
	# Screen Title
	click.echo(click.style(emoji.emojize(' Create a New Animation :rocket: '), bg='green', fg="bright_white"))
	# Screen Instructions
	click.echo(click.style("Create your new animation by giving it a name.\n", fg="green"))
	click.echo(click.style("The animation name is the name you will use in your vue project to reference/call the animation. It's also the name given to the 'folder' inside your S3 bucket where your assets will be stored. Please name it carefully and follow typical file naming conventions.\n", fg="green"))

	# Ask for a name for their new animation
	valid = False
	while (valid == False):
		animation_name = click.prompt('Please enter a CaSE SENSitive name for your new animation (eg. animation-1)')
		if (animation_name is None or len(animation_name) < 3 or len(animation_name) > 59):
			click.echo(click.style("Please enter a valid animation name. Longer than 3 characters, shorter than 60 characters.", fg="red"))
		elif (" " in animation_name):
			click.echo(click.style("Please avoid using spaces in your animation name (best practice)", fg="red"))
		else:
			click.echo(click.style("Now checking if '{}' already exists in your S3 Bucket...".format(animation_name), fg="blue"))

			# creating a working list of folders in the bucket
			existing_folders = []
			folders = bucket.list("","/")
			for folder in folders:
				folder_name = folder.name
				# strip the folder name to just the root level, with no trailing slashes
				folder_name = pathlib.Path(folder_name).parts[0]
				folder_name = folder_name.lower()
				existing_folders.append(folder_name)

			# check if animation name actually exists in the bucket already
			if(animation_name.lower() not in existing_folders):
				valid = True
			else:
				click.echo(click.style("Sorry, please enter another animation name. '{}' already exists in your bucket.".format(animation_name), fg="red"))

	# Clear screen
	click.clear()
	# Go to the upload current directory wizard, pass on the name they have requested
	uploadDirectory(animation_name)

# Main Menu Screen
@click.command()
def list_hosted_animations():
	global bucket
	global configured_tiny_png_key
	global compression_enabled

	# Clear screen
	click.clear()
	# Window Title
	click.echo(click.style(emoji.emojize(' List Recent Animations '), bg='green', fg="bright_white"))
	click.echo('\n')

	click.echo(click.style('Found the following folders in your s3 bucket:', fg="green"))
	# creating a working list of folders in the bucket
	existing_folders = []
	folders = bucket.list("","/")
	for folder in folders:
		folder_name = folder.name
		# strip the folder name to just the root level, with no trailing slashes
		folder_name = pathlib.Path(folder_name).parts[0]
		existing_folders.append(folder_name)

	count = 1
	for folder in existing_folders:
		click.echo(click.style("{}) ".format(count), fg="bright_white"), nl=False)
		click.echo(click.style("{}".format(folder), bg='bright_white', fg="black"), nl=True)
		count += 1

# Initialize the configuration if the user has no existing credentials
@click.command()
def initialize_configuration():
	global bucket
	global configured_tiny_png_key
	global compression_enabled

	# Detect if the configuration was successfully completed in the past
	if(keyring.get_password(LOTTIE_KEYRING_SERVICE_ID, 'lottie_animation_manager_config_complete') == 'true'):
		# grab the stored configuration values
		# s3 bucket
		bucket_name = keyring.get_password(LOTTIE_KEYRING_SERVICE_ID, 's3_bucket_name')
		bucket = conn.get_bucket(bucket_name)

		# configured tinypng API info (if any)
		configured_tiny_png_key = keyring.get_password(LOTTIE_KEYRING_SERVICE_ID, 'tiny_png_credentials')

		if configured_tiny_png_key == False:
			compression_enabled = False
		main_menu()
	else:
		# Clear screen
		click.clear()
		# Window Title
		click.echo(click.style(emoji.emojize('  Lottie Animation Manager Setup Wizard  '), bg='green', fg="bright_white"))
		click.echo('\n')
		# Initial instructions
		click.echo(click.style('Thanks for downloading Lottie Animation Manager!', fg="green"))
		click.echo(click.style('LAM depends on a few services:', fg="green"))
		click.echo(click.style('- Amazon Web Services S3 + Cloudfront', fg="bright_cyan"))
		click.echo(click.style('Follow the instructions in our docs on setting up these services.', fg="bright_cyan"))
		click.echo(click.style('LAM utilizes your local default AWS configuration/profile keys to upload media. You\'ll need to download the AWS CLI locally and configure it correctly.', fg="bright_cyan"))
		click.echo(click.style('- TinyPNG (optional)', fg="bright_cyan"))
		click.echo(click.style('Easily compress images in your lottie assets folder before uploading to them your CDN.  API key needed for this.', fg="bright_cyan"))

		# Please enter your bucket name 
		bucket_set = False
		while(bucket_set == False):
			bucket_name = click.prompt('Please enter the name of your AWS bucket where assets will be stored')
			try:
				bucket = conn.get_bucket(bucket_name)
				keyring.set_password(LOTTIE_KEYRING_SERVICE_ID, 's3_bucket_name', bucket_name)
				bucket_set = True
			except:
				click.echo(click.style("Could not connect to '{}' bucket, please try again".format(bucket_name), fg="red"))

		# Please enter your tinyPNG stuff
		tiny_png_key = click.prompt('Please enter your TinyPNG Key or enter "skip" to disable image compression')
		if(tiny_png_key.lower() != 'skip'):
			keyring.set_password(LOTTIE_KEYRING_SERVICE_ID, 'tiny_png_credentials', tiny_png_key)
			configured_tiny_png_key = tiny_png_key
			compression_enabled = True
		else:
			compression_enabled = False
			keyring.set_password(LOTTIE_KEYRING_SERVICE_ID, 'tiny_png_credentials', "false")

		# Mark configuration as complete now
		keyring.set_password(LOTTIE_KEYRING_SERVICE_ID, 'lottie_animation_manager_config_complete', "true")
		main_menu()

# Main Menu Screen
@click.command()
def main_menu():
	# Clear screen
	click.clear()
	# Quick "Up top logo"
	click.echo(click.style("--------------------------------------------------------\n", fg='bright_green'))
	click.echo(click.style(f.renderText("Lottie CDN"), fg='bright_green'))
	click.echo(click.style("--------------------------------------------------------", fg='bright_green'))
	# Welcome and project description
	click.echo(click.style(emoji.emojize('Thanks for using Lottie Animation Manager :thumbs_up:'), fg='bright_green'))
	click.echo(click.style("Lottie Animation Manager makes it easy to manage, compress, and upload Lottie assets to a CDN. \n", fg='bright_green'))
	# Main menu with 3 options
	click.echo(click.style("Choose an option below to get started: ", bold=True))
	click.echo(click.style("1) Create a New Animation / Upload Current Directory", fg='bright_cyan'))
	click.echo(click.style("2) List Hosted Animations", fg='bright_cyan'))
	click.echo(click.style("3) Exit Lottie Animation Manager", fg='bright_cyan'))

	# Ask the user what menu option they want
	menu_choice = click.prompt('Please enter a value between 1-3', type=int)
	
	# Option 2: Create a new animation ie. upload the current working directory
	if(menu_choice == 1):
		upload_current_lottie_directory()
	elif(menu_choice == 2):
		list_hosted_animations()
	elif(menu_choice == 3):
		click.echo(click.style(emoji.emojize("Thanks for using Lottie Animation Manager, have a nice day :sun: \n"), fg='bright_green'))
		click.Abort()
	else:
		click.echo(click.style("Please enter a valid menu choice number.", fg="red"))


if __name__ == '__main__':
	initialize_configuration()