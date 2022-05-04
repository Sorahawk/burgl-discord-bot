import discord, random

from bot_functions import *
from discord.ext import tasks
from global_variables import *
from secret_variables import DISCORD_BOT_TOKEN
from helper_functions import remove_command_prefix


bot = discord.Client()

@bot.event
async def on_ready():
	await bot.wait_until_ready()

	print(f'{bot.user} is online.')

	channel = bot.get_channel(MAIN_CHANNEL_ID)
	await channel.send(f"{CUSTOM_EMOJIS['BURG.L']} B-B-BURG.L is online!")

	rotate_status.start()


@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	# add a whitespace behind the commands so it won't recognise invalid commands, e.g. .helpp
	help_command = f'{BOT_COMMAND_PREFIX}help '
	search_command = f'{BOT_COMMAND_PREFIX}search '
	card_command = f'{BOT_COMMAND_PREFIX}card '

	lowered_content = message.content.lower() + ' '

	if lowered_content.startswith(help_command):
		await help_function(message)

	elif lowered_content.startswith(search_command):
		search_query = remove_command_prefix(message.content, search_command)
		await search_function(message, search_query)

	elif lowered_content.startswith(card_command):
		search_query = remove_command_prefix(message.content, card_command)
		await card_function(message, search_query)


# automatically rotate bot's Discord status every 10 minutes
@tasks.loop(seconds=600)
async def rotate_status():
	chosen_activity, activity_info = random.choice(list(ACTIVITY_STATUSES.items()))

	if activity_info[0] == 1:
		activity = discord.Streaming(name=chosen_activity, url=activity_info[1])
	else:
		activity = discord.Activity(type=activity_info[0], name=chosen_activity)
	
	await bot.change_presence(activity=activity)


bot.run(DISCORD_BOT_TOKEN)
