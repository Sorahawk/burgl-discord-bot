from object_search import *
from bind_functions import *
from global_variables import *
from storage_functions import *

from discord import Embed
from json import dumps, loads
from card_search import get_creature_card
from dynamodb_methods import ddb_insert_item
from string_processing import burgl_message, capitalise_object_name


# all bot methods here have to correspond to an item in BOT_COMMAND_LIST
# and must share the same name, followed by '_method'


# help menu method
async def help_method(bot, message, user_input, flag_presence):
	help_menu = Embed(description=f"{CUSTOM_EMOJIS['BURG.L']} **Command List**", colour=0x6542E1)

	for command in BOT_HELP_MESSAGE:
		help_menu.add_field(name=command[0], value='\n'.join(command[1:]), inline=False)

	await message.channel.send(embed=help_menu)


# object search method
async def search_method(bot, message, user_input, flag_presence):
	if user_input == '':
		return await message.channel.send(burgl_message('empty'))

	result = None

	# if user forces search of actual query, then bypass both shortcut as well as cache
	if not flag_presence['force_search']:

		# check if corresponding object info exists in cache
		result = retrieve_from_cache(OBJECT_INFO_CACHE, user_input)

		if result:
			# load dictionary from stored string
			result = loads(result)

			if isinstance(result, dict):
				# reinitialise collections.Counter for relevant attributes
				counter_list = ['recipe', 'repair_cost']

				for attribute in counter_list:
					if attribute in result:
						result[attribute] = Counter(result[attribute])

			elif flag_presence['modifier']:
				# if user searches for a modifier without the -m flag, it will cache 101 or 102 error, which will make any subsequent queries with the -m flag to fail as well
				# thus if cache stored an error, but query has -m flag, override cache and extract modifier info
				result = None

	# if query not in cache, -f flag present or -m flag present with error stored in cache
	if not result:
		if flag_presence['force_search']:
			full_name = user_input
		else:
			full_name = retrieve_full_name(user_input)

		# extract object info
		result = get_object_info(full_name, flag_presence['modifier'])

		# cache results except Google API error (the API could become available again at any time) and -f searches
		if result != 103 and not flag_presence['force_search']:
			ddb_insert_item(OBJECT_INFO_CACHE, user_input, dumps(result))

	if isinstance(result, list):
		# item page format is not supported
		if result[0] == 102:
			await message.channel.send(burgl_message(102).replace('VAR1', result[1]))

	# unable to locate item page URL
	elif result == 101:
		user_input = capitalise_object_name(user_input)
		await message.channel.send(burgl_message(101).replace('VAR1', user_input))

	# daily quota for Google API exhausted
	elif result == 103:
		await message.channel.send(burgl_message(103))

	else:
		await message.channel.send(result['picture_url'])
		await message.channel.send(format_object_info(result))


# creature card search method
async def card_method(bot, message, user_input, flag_presence):
	if user_input == '':
		return await message.channel.send(burgl_message('empty'))

	# check for existing shortcut binding in database if no -f flag
	if not flag_presence['force_search']:
		full_name = retrieve_full_name(user_input)

	result = get_creature_card(full_name)

	if result == 103:
		await message.channel.send(burgl_message(103))

	# card cannot be found
	elif result == 104:
		user_input = capitalise_object_name(user_input)
		await message.channel.send(burgl_message(104).replace('VAR1', user_input))

	else:
		embedded_card = Embed(title=f'{result[0]}', colour=0x6542E1)
		embedded_card.set_image(url=result[1])
		embedded_card.set_footer(text='Creature Card')

		await message.channel.send(embed=embedded_card)


# shortcut binding method
async def bind_method(bot, message, user_input, flag_presence):
	if flag_presence['view_bindings']:
		await bind_view(bot, message, user_input)

	elif flag_presence['delete_binding']:
		if user_input == '':
			return await message.channel.send(burgl_message('empty'))

		await bind_delete(message, user_input)

	else:
		await bind_default(message, user_input)


# purge cache method
async def purge_method(bot, message, user_input, flag_presence):
	purge_cache()

	await message.channel.send(burgl_message('purged'))
