import discord

from bot_functions import search_function
from secret_variables import DISCORD_BOT_TOKEN


client = discord.Client()

@client.event
async def on_ready():
	print(f'{client.user} is online.')


@client.event
async def on_message(message):
	if message.author == client.user:
		return

	bot_prefix = '.'

	search_command = f'{bot_prefix}search'
	if message.content.lower().startswith(search_command):
		search_query = message.content[len(search_command):].strip()
		await search_function(message, search_query)


client.run(DISCORD_BOT_TOKEN)
