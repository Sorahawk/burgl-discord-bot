import discord

from bot_functions import *
from secret_variables import DISCORD_BOT_TOKEN
from helper_functions import remove_command_prefix
from global_variables import MAIN_CHANNEL_ID, BOT_COMMAND_PREFIX, CUSTOM_EMOJIS


bot = discord.Client()

@bot.event
async def on_ready():
	print(f'{bot.user} is online.')

	channel = bot.get_channel(MAIN_CHANNEL_ID)
	await channel.send(f"{CUSTOM_EMOJIS['BURG.L']} B-B-BURG.L is online!")
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='the backyard'))


@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	help_command = f'{BOT_COMMAND_PREFIX}help'
	search_command = f'{BOT_COMMAND_PREFIX}search'
	card_command = f'{BOT_COMMAND_PREFIX}card'

	lowered_content = message.content.lower()

	if lowered_content.startswith(help_command):
		await help_function(message)

	elif lowered_content.startswith(search_command):
		search_query = remove_command_prefix(message.content, search_command)
		await search_function(message, search_query)

	elif lowered_content.startswith(card_command):
		search_query = remove_command_prefix(message.content, card_command)
		await card_function(message, search_query)


bot.run(DISCORD_BOT_TOKEN)
