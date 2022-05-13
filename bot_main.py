import discord

from bot_functions import *
from global_variables import *

from random import choice
from discord.ext import tasks
from dynamodb_methods import ddb_remove_all
from datetime import time, timedelta, timezone
from secret_variables import DISCORD_BOT_TOKEN
from string_processing import check_command, check_flags


# declare bot intents
intents = discord.Intents.default()
intents.message_content = True

# initialise client
bot = discord.Client(intents=intents)


@bot.event
async def on_ready():
	print(f'{bot.user} is online.')

	channel = bot.get_channel(MAIN_CHANNEL_ID)
	await channel.send(burgl_message('hello'))

	rotate_status.start()

	# if script becomes inactive for any reason, on_ready will be called again once active
	# but tasks with specific timings can't be started more than once
	try:
		daily_purge_cache.start()
	except:
		pass


@bot.event
async def on_message(message):
	prefix_length = len(BOT_COMMAND_PREFIX)  # prefix might not always be single character

	# ignore any messages sent from the bot itself, or messages that don't start with the command prefix
	if message.author == bot.user or message.content[:prefix_length] != BOT_COMMAND_PREFIX:
		return

	# check for any valid command if the message starts with the prefix symbol
	result = check_command(message.content[prefix_length:])

	if result:
		command_method, user_input = result[0], result[1]
	else:
		return

	# check for presence of any command flags
	# in the process also removes any excess whitespace
	flag_presence, user_input = check_flags(user_input)

	# call corresponding method
	await eval(command_method)(bot, message, user_input, flag_presence)


# automatically rotate bot's Discord status every 10 minutes
@tasks.loop(minutes=10)
async def rotate_status():
	activity, activity_type = choice(list(ACTIVITY_STATUSES.items()))

	if isinstance(activity_type, str):
		activity_status = discord.Streaming(url=activity_type, name=activity)
	else:
		activity_status = discord.Activity(type=activity_type, name=activity)

	await bot.change_presence(activity=activity_status)


# automatically purge caches at 6am UTC+8
timezone = timezone(timedelta(hours=8))
@tasks.loop(time=time(hour=6, tzinfo=timezone))
async def daily_purge_cache():
	purge_cache()

	channel = bot.get_channel(MAIN_CHANNEL_ID)
	await channel.send(burgl_message('purged'))


bot.run(DISCORD_BOT_TOKEN)
