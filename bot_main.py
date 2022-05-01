import discord

from bot_functions import *
from secret_variables import DISCORD_BOT_TOKEN
from global_variables import BOT_COMMAND_PREFIX
from helper_functions import remove_command_prefix


client = discord.Client()

@client.event
async def on_ready():
	print(f'{client.user} is online.')


@client.event
async def on_message(message):
	if message.author == client.user:
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


client.run(DISCORD_BOT_TOKEN)
