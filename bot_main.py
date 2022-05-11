import discord, random

from bot_functions import *
from discord.ext import tasks
from global_variables import *
from storage_functions import purge_cache
from dynamodb_methods import ddb_remove_all
from datetime import time, timedelta, timezone
from secret_variables import DISCORD_BOT_TOKEN
from helper_functions import check_command_flags, remove_command


# declare bot intents
intents = discord.Intents.default()
intents.message_content = True

# initialise client
bot = discord.Client(intents=intents)


@bot.event
async def on_ready():
	print(f'{bot.user} is online.')

	channel = bot.get_channel(MAIN_CHANNEL_ID)
	await channel.send(f"{CUSTOM_EMOJIS['BURG.L']} Hello there! Acting science manager B-B-B-BURG.L at your service!")

	rotate_status.start()

	# if script becomes inactive for any reason, on_ready will be called again once active
	# but tasks with specific timings can't be started more than once
	try:
		daily_purge_cache.start()
	except:
		pass


@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	# check for presence of any command flags
	# in the process also removes any excess whitespace
	user_input, flag_presence = check_command_flags(message.content)

	lowered_content = user_input.lower() + ' '

	# help method
	if lowered_content.startswith(BOT_COMMAND_LIST['help_method']):
		await message.channel.send('\n\n'.join(BOT_HELP_MESSAGE))

	# purge method
	elif lowered_content.startswith(BOT_COMMAND_LIST['purge_method']):
		purge_cache()
		await message.channel.send(f"{CUSTOM_EMOJIS['BURG.L']} Data caches have been purged.")
	
	else:
		for function, command in BOT_COMMAND_LIST.items():
			if lowered_content.startswith(command):
				user_input = remove_command(user_input, command)

				if user_input == '':
					await message.channel.send(f"{CUSTOM_EMOJIS['BURG.L']} Please provide input parameters.")
				else:
					await eval(function)(message, user_input, flag_presence)


# automatically rotate bot's Discord status every 10 minutes
@tasks.loop(minutes=10)
async def rotate_status():
	chosen_activity, activity_info = random.choice(list(ACTIVITY_STATUSES.items()))

	if activity_info[0] == 1:
		activity = discord.Streaming(name=chosen_activity, url=activity_info[1])
	else:
		activity = discord.Activity(type=activity_info[0], name=chosen_activity)
	
	await bot.change_presence(activity=activity)


# automatically purges caches at 6am UTC+8
timezone = timezone(timedelta(hours=8))
@tasks.loop(time=time(hour=6, tzinfo=timezone))
async def daily_purge_cache():
	purge_cache()

	channel = bot.get_channel(MAIN_CHANNEL_ID)
	await channel.send(f"{CUSTOM_EMOJIS['BURG.L']} Data caches have been purged.")


bot.run(DISCORD_BOT_TOKEN)
