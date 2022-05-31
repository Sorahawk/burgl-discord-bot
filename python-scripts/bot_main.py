import global_variables

from sys import platform
from discord import Client, Intents

from bot_tasks import *
from bot_functions import *
from global_variables import *
from secret_variables import *
from string_processing import *


# declare bot intents
# all() enables everything, including the privileged intents: presences, members and message_content
intents = Intents.all()

# initialise client
bot = Client(intents=intents)


@bot.event
async def on_ready():
	print(f'{bot.user} is online.\n')

	# initialise global main channel object
	global_variables.MAIN_CHANNEL = bot.get_channel(MAIN_CHANNEL_ID)

	if DEBUG_MODE:
		return await burgl_message('debug')

	await burgl_message('hello')
	rotate_status.start(bot)

	# if script becomes inactive for any reason, on_ready will be called again when reactivated
	# but tasks with specific timings can't be started more than once
	try:
		clear_cache_weekly.start()
	except Exception as e:
		print(f'WARNING: {e}.\n')

	# activate self-updating if running on linux cloud instance
	if platform == 'linux':
		monitor_repository.start()
		print('INFO: Watching project repository for updates.')


@bot.event
async def on_message(message):
	prefix_length = len(BOT_COMMAND_PREFIX)  # prefix might not always be single character

	# ignore any messages sent from the bot itself, or messages that don't start with the command prefix
	if message.author == bot.user or message.content[:prefix_length] != BOT_COMMAND_PREFIX:
		return

	# check for any valid command if the message starts with the prefix symbol
	result = check_command(message.content[prefix_length:])

	if not result:
		return

	command_method, user_input = result[0], result[1]

	# check for presence of any command flags
	# in the process also removes any excess whitespace
	flag_presence, user_input = check_flags(user_input)

	if DEBUG_MODE:
		return await eval(command_method)(bot, message, user_input, flag_presence)

	# log any unexpected errors if not in debug mode
	try:
		await eval(command_method)(bot, message, user_input, flag_presence)

	except Exception as e:  # log any errors if command fails in any unexpected way
		print(f'WARNING: {e}.\n')


bot.run(DISCORD_BOT_TOKEN)
