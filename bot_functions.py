import json, string

from object_search import *
from global_variables import *
from storage_functions import *
from card_search import get_creature_card
from dynamodb_methods import ddb_insert_item


# object search method
async def search_method(message, search_query, flag_presence):
	result = None

	# if user forces search of actual query, then bypass both shortcut as well as cache
	if not flag_presence['force_search']:

		# check if corresponding object info exists in cache
		result = retrieve_from_cache(OBJECT_INFO_CACHE, search_query)

		if result:
			# load dictionary from stored string
			result = json.loads(result)

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
			full_name = search_query
		else:
			full_name = retrieve_full_name(search_query)

		# extract object info
		result = get_object_info(full_name, flag_presence['modifier'])

		# cache results except Google API error (the API could become available again at any time) and -f searches
		if result != 103 and not flag_presence['force_search']:
			ddb_insert_item(OBJECT_INFO_CACHE, search_query, json.dumps(result))

	if isinstance(result, list):
		# item page format is not supported
		if result[0] == 102:
			await message.channel.send(f"{CUSTOM_EMOJIS['BURG.L']} **ERROR 102:** Wiki page for '{result[1]}' has an unsupported layout.")

	# unable to locate item page URL
	elif result == 101:
		search_query = search_query.title().replace("'S", "'s")
		await message.channel.send(f"{CUSTOM_EMOJIS['BURG.L']} **ERROR 101:** Unable to locate '{search_query}'. Try typing in the object's full name.")

	# daily quota for Google API exhausted
	elif result == 103:
		await message.channel.send(f"{CUSTOM_EMOJIS['BURG.L']} **ERROR 103:** Google API daily limit exceeded. Type in the exact name of the object.")

	else:
		await message.channel.send(result['picture_url'])
		await message.channel.send(format_object_info(result))


# creature card search method
async def card_method(message, search_query, flag_presence):

	# check for existing shortcut binding in database if no -f flag
	if not flag_presence['force_search']:
		full_name = retrieve_full_name(search_query)

	result = get_creature_card(full_name)

	if result == 103:
		await message.channel.send(f"{CUSTOM_EMOJIS['BURG.L']} **ERROR 103:** Google API daily limit exceeded. Type in the exact name of the object.")

	# card cannot be found
	elif result == 104:
		if '.' in search_query:
			search_query = search_query.upper()
		else:
			search_query = search_query.title().replace("'S", "'s")

		await message.channel.send(f"{CUSTOM_EMOJIS['BURG.L']} **ERROR 104:** Unable to locate Creature Card for '{search_query}'. Type in the exact name of the creature.")

	else:
		await message.channel.send(f'**Creature Name:** {result[0]}')
		await message.channel.send(result[1])


# linking shortcut query method
async def bind_method(message, user_input, flag_presence):

	# remove any edge commas before splitting by comma
	user_input = user_input.lower().strip(',').split(',')

	if len(user_input) < 2:
		await message.channel.send(f"{CUSTOM_EMOJIS['BURG.L']} A minimum of two parameters are required.")
		return

	formatted_string = bind_query_name(user_input[0], user_input[1:])
	await message.channel.send(formatted_string)
