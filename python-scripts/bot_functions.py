from json import dumps, loads
from asyncio import TimeoutError
from discord import DMChannel, Embed
from collections import Counter

from card_search import *
from object_search import *
from bind_functions import *
from chop_functions import *
from dynamodb_methods import *
from global_variables import *
from secret_variables import *
from storage_functions import *
from string_processing import *


# returns True if message author is elevated, otherwise False
def check_user_elevation(message):
	return message.author.id in ELEVATED_USERS


# all bot methods below have to correspond to an item in BOT_COMMAND_LIST
# and must share the same name, followed by '_method'

# help menu method
async def help_method(bot, message, user_input, flag_presence):
	embed_list = []
	category_names = ['Main', 'Utility']

	for page in range(len(category_names)):
		category = category_names[page]
		help_embed = Embed(title='**Command List**', description=f'**{category}**', color=EMBED_COLOR_CODE)

		for command in BOT_HELP_MENU[category]:
			help_embed.add_field(name=command[0], value='\n'.join(command[1:]), inline=False)

		help_embed.set_footer(text=f'Page {page + 1}/{len(category_names)}')
		embed_list.append(help_embed)

	return await multipage_embed_handler(bot, message, embed_list)


# object search method
async def search_method(bot, message, user_input, flag_presence):
	if user_input == '':
		return await message.channel.send(burgl_message('empty'))

	result = process_object_input(user_input, flag_presence)

	if isinstance(result, list):
		# item page format is not supported
		if result[0] == 102:
			return await message.channel.send(burgl_message(102).replace('VAR1', result[1]))

	# unable to locate item page URL
	elif result == 101:
		user_input = capitalise_object_name(user_input)
		return await message.channel.send(burgl_message(101).replace('VAR1', user_input))

	# daily quota for Google API exhausted
	elif result == 103:
		return await message.channel.send(burgl_message(103))

	else:
		return await message.channel.send(embed=format_object_info(result))


# creature card search method
async def card_method(bot, message, user_input, flag_presence):
	if user_input == '':
		return await message.channel.send(burgl_message('empty'))

	# check for existing shortcut binding in database if no -f flag
	if not flag_presence['force_search']:
		full_name = retrieve_full_name(user_input)

	result = get_creature_card(full_name, flag_presence['get_gold'])

	# daily quota for Google API exhausted
	if result == 103:
		return await message.channel.send(burgl_message(103))

	# card cannot be found
	elif result == 104:
		user_input = capitalise_object_name(user_input)
		return await message.channel.send(burgl_message(104).replace('VAR1', user_input))

	else:
		embedded_card = Embed(title=f'{result[0]}', color=EMBED_COLOR_CODE)
		embedded_card.set_image(url=result[1])
		embedded_card.set_footer(text='Creature Card')

		return await message.channel.send(embed=embedded_card)


# shortcut binding method
async def bind_method(bot, message, user_input, flag_presence):
	if flag_presence['view_bindings']:
		return await bind_view(bot, message, user_input)

	# allow non-elevated users to view bindings
	if not check_user_elevation(message):
		return await message.channel.send(burgl_message('unauthorised'))

	if flag_presence['delete_binding']:
		if user_input == '':
			return await message.channel.send(burgl_message('empty'))
		else:
			return await bind_delete(message, user_input)
	else:
		return await bind_default(message, user_input)


# cache clearing method
async def clear_method(bot, message, user_input, flag_presence):
	if not check_user_elevation(message):
		return await message.channel.send(burgl_message('unauthorised'))
	else:
		clear_cache()
		return await message.channel.send(burgl_message('cleared'))


# message purging method
async def purge_method(bot, message, user_input, flag_presence):
	message_history = [old_message async for old_message in message.channel.history()]

	# if message is from a server channel
	if not isinstance(message.channel, DMChannel):
		return await message.channel.delete_messages(message_history)

	else:  # if message is from a private message
		for old_message in message_history:
			if old_message.author == bot.user:
				await old_message.delete()


# chopping list method
async def chop_method(bot, message, user_input, flag_presence):
	if user_input == '':
		return await message.channel.send(burgl_message('empty'))

	# process user input into dictionary of items and their desired quantities
	inputted_items = process_chop_input(user_input)
	total_count = Counter()

	for item, quantity in inputted_items.items():
		added_items = process_chop_components(item, quantity)
		total_count += added_items
		await message.channel.send(added_items)

	await message.channel.send(total_count)
