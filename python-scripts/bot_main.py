import discord, requests

from random import choice
from discord.ext import tasks
from datetime import datetime, time, timedelta, timezone

from bot_functions import *
from dynamodb_methods import *
from global_variables import *
from secret_variables import *
from string_processing import *


# declare bot intents
# all() enables everything, including the privileged intents: presences, members and message_content
intents = discord.Intents.all()

# initialise client
bot = discord.Client(intents=intents)


@bot.event
async def on_ready():
	print(f'{bot.user} is online.\n')

	channel = bot.get_channel(MAIN_CHANNEL_ID)

	if DEBUG_MODE:
		return await channel.send(burgl_message('debug'))

	await channel.send(burgl_message('hello'))

	# if script becomes inactive for any reason, on_ready will be called again once active
	# but tasks with specific timings can't be started more than once
	try:
		rotate_status.start()
		clear_cache_weekly.start()
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

	if DEBUG_MODE:
		await eval(command_method)(bot, message, user_input, flag_presence)

	# log any unexpected errors if not in debug mode
	else:
		try:
			await eval(command_method)(bot, message, user_input, flag_presence)

		except Exception as e:  # log any errors if command fails in any unexpected way
			print(f'WARNING: {e}.\n')


# automatically rotate bot's Discord status every 10 minutes
@tasks.loop(minutes=10)
async def rotate_status():
	activity, activity_type = choice(list(ACTIVITY_STATUSES.items()))

	if isinstance(activity_type, str):
		activity_status = discord.Streaming(url=activity_type, name=activity)
	else:
		activity_status = discord.Activity(type=activity_type, name=activity)

	await bot.change_presence(activity=activity_status)


# automatically clear caches once a week
timezone = timezone(timedelta(hours=TIMEZONE_OFFSET))
@tasks.loop(time=time(hour=CACHE_CLEAR_HOUR, tzinfo=timezone))
async def clear_cache_weekly():
	if datetime.today().weekday() == CACHE_CLEAR_DAY:
		clear_cache()

		channel = bot.get_channel(MAIN_CHANNEL_ID)
		await channel.send(burgl_message('cleared'))


# monitors project repository for new code
# updates cloud code and restarts bot service after updates
@tasks.loop(seconds=15)
async def monitor_repository():
	url = 'https://api.github.com/repos/Sorahawk/burgl-discord-bot/commits'

	headers = {}
	#headers = {'If-None-Match': 'W/"2698553f004ce0bfa9c27fd11ff59972a30f4d648d7fd63ad5cb4399f6951a90"'}

	for x in range(2):
		response = requests.get(url, headers=headers)

		if response.status_code == 200:
			etag = response.headers['ETag']
			headers = {'If-None-Match': etag}

		elif response.status_code == 304:
			print(response.headers)


bot.run(DISCORD_BOT_TOKEN)
