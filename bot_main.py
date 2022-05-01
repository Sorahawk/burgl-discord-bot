import discord

from secret_variables import DISCORD_BOT_TOKEN
from bot_functions import search_function, card_function


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
	card_command = f'{bot_prefix}card'

	if message.content.lower().startswith(search_command):
		search_query = message.content[len(search_command):].strip()
		await search_function(message, search_query)

	elif message.content.lower().startswith(card_command):
		search_query = message.content[len(card_command):].strip()
		await card_function(message, search_query)


client.run(DISCORD_BOT_TOKEN)
