import global_variables

from os import getcwd
from sys import platform
from discord import Client, Intents

from bot_tasks import *
from bot_functions import *
from status_logging import *
from global_variables import *
from secret_variables import *
from string_processing import *


# declare bot intents
# all() enables everything, including the privileged intents: presences, members and message_content
intents = Intents.all()

# initialise client
bot = Client(intents=intents)
global_variables.BOT_INSTANCE = bot


@bot.event
async def on_ready():
	# on_ready() can be called more than once, typically whenever the bot momentarily loses connection to Discord 
	# check if this is first time bot is calling on_ready()
	if not global_variables.MAIN_CHANNEL:
		print(f'{bot.user} is online.\n')

		# initialise global main channel object
		global_variables.MAIN_CHANNEL = bot.get_channel(MAIN_CHANNEL_ID)

		if DEBUG_MODE:
			return await burgl_message('debug')

		rotate_status.start()
		monitor_app_info.start()
		clear_cache_weekly.start()

		# activate self-updating task if running on Linux cloud instance
		if platform == 'linux':
			monitor_repository.start()

		await burgl_message('hello')

	else:  # do not start tasks again if they are alreayd ongoing as it will throw RuntimeError
		print(f'{bot.user} has reconnected to Discord.\n')


@bot.event
async def on_message(message):
	prefix_length = len(BOT_COMMAND_PREFIX)  # prefix might not always be single character

	# ignore any messages if bot is not ready, messages sent from the bot itself, or messages that don't start with the command prefix
	if not bot.is_ready() or message.author == bot.user or message.content[:prefix_length] != BOT_COMMAND_PREFIX:
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
		return await eval(command_method)(message, user_input, flag_presence)

	# log any unexpected errors if not in debug mode
	try:
		await eval(command_method)(message, user_input, flag_presence)

	except Exception as e:  # log any errors if command fails in any unexpected way
		await global_variables.MAIN_CHANNEL.send(f'WARNING: {e}\n')


# initialise logging module
if platform == 'linux': filepath = LINUX_ABSOLUTE_PATH
else: filepath = getcwd()
init_logger(filepath)

# start bot
bot.run(DISCORD_BOT_TOKEN)
